"""
房间系统视图
"""

from django.db.models import Avg, Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Room, RoomParticipant, RoomRating, RoomReport
from .serializers import (  # type: ignore
    RoomCreateSerializer,
    RoomDetailSerializer,
    RoomJoinSerializer,
    RoomListSerializer,
    RoomParticipantSerializer,
    RoomRatingSerializer,
    RoomReportSerializer,
    RoomSearchSerializer,
    RoomSerializer,
    RoomStatsSerializer,
    RoomUpdateSerializer,
)


class RoomViewSet(ModelViewSet):
    """
    房间视图集
    """

    queryset = Room.objects.filter(is_active=True)
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "room_type",
        "status",
        "target_gender",
        "is_private",
        "is_featured",
    ]
    search_fields = ["name", "description"]
    ordering_fields = [
        "created_at",
        "last_activity",
        "total_visitors",
        "average_rating",
    ]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return RoomCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return RoomUpdateSerializer
        elif self.action == "list":
            return RoomListSerializer
        elif self.action == "retrieve":
            return RoomDetailSerializer
        return RoomSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # 搜索过滤
        search_serializer = RoomSearchSerializer(data=self.request.query_params)
        if search_serializer.is_valid():
            data = search_serializer.validated_data

            if data.get("room_type"):
                queryset = queryset.filter(room_type=data["room_type"])

            if data.get("target_gender"):
                queryset = queryset.filter(target_gender=data["target_gender"])

            if data.get("min_age") or data.get("max_age"):
                age_filter = Q()
                if data.get("min_age"):
                    age_filter &= Q(min_age__gte=data["min_age"])
                if data.get("max_age"):
                    age_filter &= Q(max_age__lte=data["max_age"])
                queryset = queryset.filter(age_filter)

            if data.get("location"):
                queryset = queryset.filter(location_preference__icontains=data["location"])

            if data.get("is_featured") is not None:
                queryset = queryset.filter(is_featured=data["is_featured"])

            if data.get("is_private") is not None:
                queryset = queryset.filter(is_private=data["is_private"])

        return queryset

    @swagger_auto_schema(
        operation_description="创建房间",
        request_body=RoomCreateSerializer,
        responses={201: RoomSerializer},
    )
    def create(self, request, *args, **kwargs):
        """创建房间"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response(
                {
                    "message": "房间创建成功",
                    "room": RoomDetailSerializer(room, context={"request": request}).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="获取房间详情",
        responses={200: RoomDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        """获取房间详情"""
        room = self.get_object()

        # 增加访客数
        room.total_visitors += 1
        room.save(update_fields=["total_visitors"])

        serializer = RoomDetailSerializer(room, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(
        operation_description="加入房间",
        request_body=RoomJoinSerializer,
        responses={200: "加入成功", 400: "加入失败"},
    )
    def join(self, request, pk=None):
        """加入房间"""
        room = self.get_object()
        serializer = RoomJoinSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            role = serializer.validated_data["role"]

            # 检查是否可以加入
            can_join, message = room.can_join(user)
            if not can_join:
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

            # 检查是否已经是参与者
            if room.participants.filter(user=user).exists():
                return Response(
                    {"error": "您已经是该房间的参与者"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 创建参与者记录
            participant = RoomParticipant.objects.create(
                room=room, user=user, role=role, status="waiting"
            )

            return Response(
                {
                    "message": "成功加入房间",
                    "participant": RoomParticipantSerializer(participant).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="离开房间", responses={200: "离开成功"})
    def leave(self, request, pk=None):
        """离开房间"""
        room = self.get_object()
        user = request.user

        try:
            participant = room.participants.get(user=user)
            participant.leave()

            return Response({"message": "成功离开房间"}, status=status.HTTP_200_OK)
        except RoomParticipant.DoesNotExist:
            return Response(
                {"error": "您不是该房间的参与者"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    @swagger_auto_schema(
        operation_description="获取房间统计信息",
        responses={200: RoomStatsSerializer},
    )
    def stats(self, request):
        """获取房间统计信息"""
        total_rooms = Room.objects.filter(is_active=True).count()
        active_rooms = Room.objects.filter(status="connected").count()
        total_participants = RoomParticipant.objects.filter(is_active=True).count()
        online_users = RoomParticipant.objects.filter(status="connected").count()

        # 计算平均评分
        avg_rating = RoomRating.objects.aggregate(avg=Avg("rating"))["avg"] or 5.0

        # 获取热门房间
        popular_rooms = (
            Room.objects.filter(is_active=True)
            .annotate(participant_count=Count("participants"))
            .order_by("-participant_count", "-total_visitors")[:10]
        )

        data = {
            "total_rooms": total_rooms,
            "active_rooms": active_rooms,
            "total_participants": total_participants,
            "online_users": online_users,
            "average_rating": avg_rating,
            "popular_rooms": RoomListSerializer(popular_rooms, many=True).data,
        }

        return Response(data, status=status.HTTP_200_OK)


class RoomRatingView(APIView):
    """
    房间评分视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="提交评分",
        request_body=RoomRatingSerializer,
        responses={201: RoomRatingSerializer},
    )
    def post(self, request):
        """提交评分"""
        serializer = RoomRatingSerializer(data=request.data)
        if serializer.is_valid():
            rating = serializer.save()

            # 更新房间平均评分
            room = rating.room
            avg_rating = room.ratings.aggregate(avg=Avg("rating"))["avg"]
            room.average_rating = avg_rating
            room.save(update_fields=["average_rating"])

            return Response(
                {
                    "message": "评分提交成功",
                    "rating": RoomRatingSerializer(rating).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomReportView(APIView):
    """
    房间举报视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="提交举报",
        request_body=RoomReportSerializer,
        responses={201: RoomReportSerializer},
    )
    def post(self, request):
        """提交举报"""
        serializer = RoomReportSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.save()

            return Response(
                {
                    "message": "举报提交成功，我们会尽快处理",
                    "report": RoomReportSerializer(report).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_rooms(request):
    """
    获取我的房间
    """
    user = request.user

    # 我创建的房间
    created_rooms = Room.objects.filter(
        participants__user=user, participants__role="host"
    ).order_by("-created_at")

    # 我参与的房间
    participated_rooms = Room.objects.filter(
        participants__user=user,
        participants__role__in=["participant", "spectator"],
    ).order_by("-created_at")

    return Response(
        {
            "created_rooms": RoomListSerializer(created_rooms, many=True).data,
            "participated_rooms": RoomListSerializer(participated_rooms, many=True).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def connect_room(request, room_id):
    """
    连接房间（WebSocket连接）
    """
    try:
        room = Room.objects.get(room_id=room_id)
        user = request.user

        # 检查是否是房间参与者
        try:
            participant = room.participants.get(user=user)
        except RoomParticipant.DoesNotExist:
            return Response(
                {"error": "您不是该房间的参与者"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 更新参与者状态
        participant.connect()

        # 更新房间状态
        if room.status == "waiting":
            room.status = "connected"
            room.save(update_fields=["status"])

        # 增加连接数
        room.total_connections += 1
        room.save(update_fields=["total_connections"])

        return Response(
            {
                "message": "连接成功",
                "room": RoomDetailSerializer(room, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

    except Room.DoesNotExist:
        return Response({"error": "房间不存在"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def disconnect_room(request, room_id):
    """
    断开房间连接
    """
    try:
        room = Room.objects.get(room_id=room_id)
        user = request.user

        try:
            participant = room.participants.get(user=user)
            participant.disconnect()

            # 检查房间是否还有其他连接的用户
            active_participants = room.participants.filter(status="connected").count()
            if active_participants == 0:
                room.status = "disconnected"
                room.save(update_fields=["status"])

            return Response({"message": "断开连接成功"}, status=status.HTTP_200_OK)

        except RoomParticipant.DoesNotExist:
            return Response(
                {"error": "您不是该房间的参与者"},
                status=status.HTTP_403_FORBIDDEN,
            )

    except Room.DoesNotExist:
        return Response({"error": "房间不存在"}, status=status.HTTP_404_NOT_FOUND)
