"""
通话系统视图
"""

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import (
    Call,
    CallInvitation,
    CallParticipant,
    CallQualityLog,
    CallRecording,
)
from .serializers import (
    CallActionSerializer,
    CallCreateSerializer,
    CallInvitationCreateSerializer,
    CallInvitationSerializer,
    CallListSerializer,
    CallParticipantSerializer,
    CallRecordingCreateSerializer,
    CallSerializer,
    CallStatsSerializer,
)


class CallSessionViewSet(ModelViewSet):
    """
    通话会话视图集
    """

    queryset = Call.objects.all()
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["call_type", "status", "initiator", "receiver"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "started_at", "ended_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return CallCreateSerializer
        elif self.action == "list":
            return CallListSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            return CallSerializer
        elif self.action == "stats":
            return CallStatsSerializer
        return CallSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 搜索过滤
        search_serializer = CallListSerializer(data=self.request.query_params)
        if search_serializer.is_valid():
            data = search_serializer.validated_data

            if data.get("call_type"):
                queryset = queryset.filter(call_type=data["call_type"])

            if data.get("status"):
                queryset = queryset.filter(status=data["status"])

            if data.get("is_private") is not None:
                queryset = queryset.filter(is_private=data["is_private"])

            if data.get("is_recorded") is not None:
                queryset = queryset.filter(is_recorded=data["is_recorded"])

            if data.get("date_from"):
                queryset = queryset.filter(created_at__date__gte=data["date_from"])

            if data.get("date_to"):
                queryset = queryset.filter(created_at__date__lte=data["date_to"])

        # 用户只能看到自己参与的通话
        return queryset.filter(Q(initiator=user) | Q(participants=user)).distinct()

    @swagger_auto_schema(
        operation_description="创建通话",
        request_body=CallCreateSerializer,
        responses={201: CallSerializer},
    )
    def create(self, request, *args, **kwargs):
        """
        创建通话
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        call = serializer.save(initiator=request.user)

        return Response(
            CallSerializer(call, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_description="获取通话详情",
        responses={200: CallSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        """
        获取通话详情
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="更新通话",
        request_body=CallSerializer,
        responses={200: CallSerializer},
    )
    def update(self, request, *args, **kwargs):
        """
        更新通话
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="部分更新通话",
        request_body=CallSerializer,
        responses={200: CallSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        """
        部分更新通话
        """
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="开始通话", responses={200: "开始成功"})
    def start(self, request, pk=None):
        """开始通话"""
        call_session = self.get_object()

        # 检查权限
        if call_session.initiator != request.user:
            return Response(
                {"error": "只有发起者可以开始通话"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if call_session.status != "initiating":
            return Response(
                {"error": "通话状态不允许开始"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        call_session.start_call()

        return Response(
            {
                "message": "通话已开始",
                "call_session": CallSerializer(call_session, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="结束通话", responses={200: "结束成功"})
    def end(self, request, pk=None):
        """结束通话"""
        call_session = self.get_object()

        # 检查权限
        if call_session.initiator != request.user:
            return Response(
                {"error": "只有发起者可以结束通话"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not call_session.is_active:
            return Response({"error": "通话已经结束"}, status=status.HTTP_400_BAD_REQUEST)

        call_session.end_call()

        return Response(
            {
                "message": "通话已结束",
                "call_session": CallSerializer(call_session, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    @swagger_auto_schema(
        operation_description="获取通话统计信息",
        responses={200: CallStatsSerializer},
    )
    def stats(self, request):
        """获取通话统计信息"""
        user = request.user

        # 用户参与的通话
        user_calls = Call.objects.filter(Q(initiator=user) | Q(participants=user))

        total_calls = user_calls.count()
        active_calls = user_calls.filter(status__in=["initiating", "ringing", "connected"]).count()
        total_duration = user_calls.aggregate(total=Sum("duration"))["total"] or 0
        average_quality = user_calls.aggregate(avg=Avg("quality_score"))["avg"] or 5.0

        # 通话类型统计
        call_types = user_calls.values("call_type").annotate(count=Count("id"))
        call_type_stats = {item["call_type"]: item["count"] for item in call_types}

        # 最近通话
        recent_calls = user_calls.order_by("-created_at")[:10]

        data = {
            "total_calls": total_calls,
            "active_calls": active_calls,
            "total_duration": total_duration,
            "average_quality": average_quality,
            "call_types": call_type_stats,
            "recent_calls": CallListSerializer(recent_calls, many=True).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(
        operation_description="加入通话",
        request_body=CallParticipantSerializer,
        responses={200: CallParticipantSerializer},
    )
    def join(self, request, pk=None):
        """
        加入通话
        """
        call = self.get_object()
        serializer = CallParticipantSerializer(data=request.data)

        if serializer.is_valid():
            participant = serializer.save(
                call=call,
                user=request.user,
                role="participant",
                status="joined",
            )

            return Response(
                {
                    "message": "成功加入通话",
                    "participant": CallParticipantSerializer(
                        participant, context={"request": request}
                    ).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(
        operation_description="离开通话",
        responses={200: "离开成功"},
    )
    def leave(self, request, pk=None):
        """
        离开通话
        """
        call = self.get_object()

        try:
            participant = CallParticipant.objects.get(call=call, user=request.user)
            participant.status = "left"
            participant.left_at = timezone.now()
            participant.save()

            return Response({"message": "成功离开通话"}, status=status.HTTP_200_OK)

        except CallParticipant.DoesNotExist:
            return Response({"error": "您不在通话中"}, status=status.HTTP_400_BAD_REQUEST)


class CallParticipantView(APIView):
    """
    通话参与者视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="加入通话",
        request_body=CallParticipantSerializer,
        responses={200: CallParticipantSerializer},
    )
    def post(self, request):
        """
        加入通话
        """
        serializer = CallParticipantSerializer(data=request.data)

        if serializer.is_valid():
            call_id = serializer.validated_data["call_id"]
            try:
                call = Call.objects.get(id=call_id)
                participant = CallParticipant.objects.get(call=call, user=request.user)
                participant.status = "joined"
                participant.joined_at = timezone.now()
                participant.save()

                return Response(
                    {
                        "message": "成功加入通话",
                        "participant": CallParticipantSerializer(
                            participant, context={"request": request}
                        ).data,
                    },
                    status=status.HTTP_200_OK,
                )

            except (Call.DoesNotExist, CallParticipant.DoesNotExist):
                return Response(
                    {"error": "通话或参与者不存在"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CallInvitationView(APIView):
    """
    通话邀请视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="发送通话邀请",
        request_body=CallInvitationCreateSerializer,
        responses={201: CallInvitationSerializer},
    )
    def post(self, request):
        """发送通话邀请"""
        serializer = CallInvitationCreateSerializer(data=request.data)
        if serializer.is_valid():
            invitation = serializer.save()

            return Response(
                {
                    "message": "邀请发送成功",
                    "invitation": CallInvitationSerializer(invitation).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="获取邀请列表",
        responses={200: CallInvitationSerializer},
    )
    def get(self, request):
        """获取邀请列表"""
        user = request.user

        # 获取用户的邀请
        invitations = CallInvitation.objects.filter(invitee=user, status="pending").order_by(
            "-created_at"
        )

        serializer = CallInvitationSerializer(invitations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def accept_invitation(request, invitation_id):
    """
    接受通话邀请
    """
    try:
        invitation = CallInvitation.objects.get(
            id=invitation_id, invitee=request.user, status="pending"
        )
    except CallInvitation.DoesNotExist:
        return Response({"error": "邀请不存在或已处理"}, status=status.HTTP_404_NOT_FOUND)

    invitation.accept()

    # 创建参与者记录
    CallParticipant.objects.create(
        call_session=invitation.call_session,
        user=request.user,
        role="participant",
        status="joined",
    )

    return Response({"message": "邀请已接受"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reject_invitation(request, invitation_id):
    """
    拒绝通话邀请
    """
    try:
        invitation = CallInvitation.objects.get(
            id=invitation_id, invitee=request.user, status="pending"
        )
    except CallInvitation.DoesNotExist:
        return Response({"error": "邀请不存在或已处理"}, status=status.HTTP_404_NOT_FOUND)

    invitation.reject()

    return Response({"message": "邀请已拒绝"}, status=status.HTTP_200_OK)


class CallQualityView(APIView):
    """
    通话质量视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="提交通话质量数据",
        request_body=CallStatsSerializer,
        responses={201: CallStatsSerializer},
    )
    def post(self, request):
        """提交通话质量数据"""
        serializer = CallStatsSerializer(data=request.data)
        if serializer.is_valid():
            # 处理质量数据
            return Response(
                {
                    "message": "质量数据提交成功",
                    "data": serializer.validated_data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CallRecordingView(APIView):
    """
    通话录制视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="开始录制",
        request_body=CallRecordingCreateSerializer,
        responses={201: CallRecordingCreateSerializer},
    )
    def post(self, request):
        """开始录制"""
        serializer = CallRecordingCreateSerializer(data=request.data)
        if serializer.is_valid():
            recording = serializer.save()
            return Response(
                {
                    "message": "录制开始成功",
                    "recording": CallRecordingCreateSerializer(recording).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="获取录制列表",
        responses={200: CallRecordingCreateSerializer},
    )
    def get(self, request):
        """获取录制列表"""
        recordings = CallRecording.objects.filter(call__initiator=request.user).order_by(
            "-created_at"
        )

        return Response(
            CallRecordingCreateSerializer(recordings, many=True).data,
            status=status.HTTP_200_OK,
        )


class WebRTCView(APIView):
    """
    WebRTC信令视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="处理WebRTC Offer",
        request_body=CallSerializer,
        responses={200: "Offer处理成功"},
    )
    def post(self, request, action):
        """处理WebRTC信令"""
        if action == "offer":
            serializer = CallSerializer(data=request.data)
            if serializer.is_valid():
                # 处理 Offer
                return Response({"message": "Offer处理成功"}, status=status.HTTP_200_OK)
        elif action == "answer":
            serializer = CallSerializer(data=request.data)
            if serializer.is_valid():
                # 处理 Answer
                return Response({"message": "Answer处理成功"}, status=status.HTTP_200_OK)
        elif action == "ice-candidate":
            serializer = CallSerializer(data=request.data)
            if serializer.is_valid():
                # 处理 ICE Candidate
                return Response(
                    {"message": "ICE Candidate处理成功"},
                    status=status.HTTP_200_OK,
                )

        return Response({"error": "无效的操作"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_calls(request):
    """
    获取我的通话记录
    """
    user = request.user

    # 我发起的通话
    initiated_calls = Call.objects.filter(initiator=user).order_by("-created_at")

    # 我参与的通话
    participated_calls = (
        Call.objects.filter(participants=user).exclude(initiator=user).order_by("-created_at")
    )

    return Response(
        {
            "initiated_calls": CallListSerializer(initiated_calls, many=True).data,
            "participated_calls": CallListSerializer(participated_calls, many=True).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def call_action(request):
    """
    通话操作（静音、摄像头等）
    """
    serializer = CallActionSerializer(data=request.data)
    if serializer.is_valid():
        action = serializer.validated_data["action"]
        session_id = serializer.validated_data["session_id"]
        try:
            call_session = Call.objects.get(session_id=session_id)
            participant = CallParticipant.objects.get(call_session=call_session, user=request.user)
        except (Call.DoesNotExist, CallParticipant.DoesNotExist):
            return Response(
                {"error": "通话会话或参与者不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 执行操作
        if action == "mute":
            participant.toggle_mute()
            message = "已静音" if participant.is_muted else "已取消静音"
        elif action == "camera_off":
            participant.toggle_camera()
            message = "摄像头已关闭" if participant.is_camera_off else "摄像头已开启"
        else:
            return Response({"error": "不支持的操作"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": message,
                "participant": CallParticipantSerializer(participant).data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
