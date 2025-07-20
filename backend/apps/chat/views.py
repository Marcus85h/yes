"""
聊天系统视图
"""

from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .content_filter import ContentModeration
from .models import (
    ChatInvitation,
    ChatNotification,
    ChatParticipant,
    ChatRoom,
    Message,
    MessageFavorite,
    MessageLike,
    MessageRead,
)
from .serializers import (
    ChatInvitationCreateSerializer,
    ChatInvitationSerializer,
    ChatListSerializer,
    ChatNotificationSerializer,
    ChatParticipantJoinSerializer,
    ChatParticipantSerializer,
    ChatRoomCreateSerializer,
    ChatRoomDetailSerializer,
    ChatRoomSerializer,
    ChatSearchSerializer,
    ChatStatsSerializer,
    MessageActionSerializer,
    MessageCreateSerializer,
    MessageFavoriteSerializer,
    MessageForwardSerializer,
    MessageSearchSerializer,
    MessageSerializer,
    MessageUpdateSerializer,
)
from .services import (
    ChatRoomService,
    FileUploadService,
    MessageSearchService,
    NotificationService,
)

User = get_user_model()


class ChatRoomViewSet(ModelViewSet):
    """
    聊天房间视图集
    """

    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["room_type", "status", "is_private"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "last_message_at", "message_count"]
    ordering = ["-last_message_at", "-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return ChatRoomCreateSerializer
        elif self.action == "retrieve":
            return ChatRoomDetailSerializer
        elif self.action == "list":
            return ChatListSerializer
        return ChatRoomSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 搜索过滤
        search_serializer = ChatSearchSerializer(data=self.request.query_params)
        if search_serializer.is_valid():
            data = search_serializer.validated_data

            if data.get("room_type"):
                queryset = queryset.filter(room_type=data["room_type"])

            if data.get("status"):
                queryset = queryset.filter(status=data["status"])

            if data.get("is_private") is not None:
                queryset = queryset.filter(is_private=data["is_private"])

            if data.get("keyword"):
                keyword = data["keyword"]
                queryset = queryset.filter(
                    Q(name__icontains=keyword) | Q(description__icontains=keyword)
                )

        # 用户只能看到自己参与的房间或公开房间
        return queryset.filter(Q(participants=user) | Q(is_private=False)).distinct()

    @swagger_auto_schema(
        operation_description="创建聊天房间",
        request_body=ChatRoomCreateSerializer,
        responses={201: ChatRoomSerializer},
    )
    def create(self, request, *args, **kwargs):
        """创建聊天房间"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            chat_room = serializer.save()

            # 创建创建者参与者记录
            ChatParticipant.objects.create(
                chat_room=chat_room,
                user=request.user,
                role="owner",
                can_manage=True,
            )

            return Response(
                {
                    "message": "聊天房间创建成功",
                    "chat_room": ChatRoomDetailSerializer(
                        chat_room, context={"request": request}
                    ).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="获取聊天房间详情",
        responses={200: ChatRoomDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        """获取聊天房间详情"""
        chat_room = self.get_object()
        serializer = ChatRoomDetailSerializer(chat_room, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(
        operation_description="加入聊天房间",
        request_body=ChatParticipantJoinSerializer,
        responses={200: ChatParticipantSerializer},
    )
    def join(self, request, pk=None):
        """加入聊天房间"""
        chat_room = self.get_object()
        serializer = ChatParticipantJoinSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            # 检查是否已经是参与者
            if ChatParticipant.objects.filter(
                chat_room=chat_room, user=user, is_active=True
            ).exists():
                return Response(
                    {"error": "您已经是该房间的参与者"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 创建参与者记录
            participant = ChatParticipant.objects.create(
                chat_room=chat_room, user=user, role="member"
            )

            return Response(
                {
                    "message": "成功加入聊天房间",
                    "participant": ChatParticipantSerializer(participant).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="离开聊天房间", responses={200: "离开成功"})
    def leave(self, request, pk=None):
        """离开聊天房间"""
        chat_room = self.get_object()
        user = request.user

        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=user, is_active=True
            )
            participant.leave()

            return Response({"message": "已离开聊天房间"}, status=status.HTTP_200_OK)
        except ChatParticipant.DoesNotExist:
            return Response(
                {"error": "您不是该房间的参与者"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"])
    @swagger_auto_schema(
        operation_description="获取聊天统计信息",
        responses={200: ChatStatsSerializer},
    )
    def stats(self, request):
        """获取聊天统计信息"""
        user = request.user

        # 用户参与的聊天房间
        user_rooms = ChatRoom.objects.filter(participants=user)

        total_rooms = user_rooms.count()
        active_rooms = user_rooms.filter(status="active").count()
        total_messages = user_rooms.aggregate(total=Sum("message_count"))["total"] or 0
        total_participants = ChatParticipant.objects.filter(
            chat_room__in=user_rooms, is_active=True
        ).count()

        # 房间类型统计
        room_types = user_rooms.values("room_type").annotate(count=Count("id"))
        room_type_stats = {item["room_type"]: item["count"] for item in room_types}

        # 最近消息
        recent_messages = Message.objects.filter(chat_room__participants=user).order_by(
            "-created_at"
        )[:10]

        data = {
            "total_rooms": total_rooms,
            "active_rooms": active_rooms,
            "total_messages": total_messages,
            "total_participants": total_participants,
            "room_types": room_type_stats,
            "recent_messages": MessageSerializer(
                recent_messages, many=True, context={"request": request}
            ).data,
        }

        return Response(data, status=status.HTTP_200_OK)


class MessageViewSet(ModelViewSet):
    """
    消息视图集
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["message_type", "status", "sender"]
    search_fields = ["content"]
    ordering_fields = ["created_at", "sent_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return MessageCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return MessageUpdateSerializer
        return MessageSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 搜索过滤
        search_serializer = MessageSearchSerializer(data=self.request.query_params)
        if search_serializer.is_valid():
            data = search_serializer.validated_data

            if data.get("message_type"):
                queryset = queryset.filter(message_type=data["message_type"])

            if data.get("status"):
                queryset = queryset.filter(status=data["status"])

            if data.get("keyword"):
                keyword = data["keyword"]
                queryset = queryset.filter(content__icontains=keyword)

            if data.get("date_from"):
                queryset = queryset.filter(created_at__date__gte=data["date_from"])

            if data.get("date_to"):
                queryset = queryset.filter(created_at__date__lte=data["date_to"])

        # 用户只能看到自己参与房间的消息
        return queryset.filter(chat_room__participants=user)

    @swagger_auto_schema(
        operation_description="发送消息",
        request_body=MessageCreateSerializer,
        responses={201: MessageSerializer},
    )
    def create(self, request, *args, **kwargs):
        """发送消息"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 内容审核
            content = serializer.validated_data.get("content", "")
            moderation = ContentModeration()
            moderation_result = moderation.moderate_message(content, str(request.user.id))

            if not moderation_result["passed"]:
                if moderation_result["action"] == "block":
                    return Response(
                        {
                            "error": "消息内容违规",
                            "detected_issues": moderation_result["detected_issues"],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif moderation_result["action"] == "filter":
                    # 使用过滤后的内容
                    serializer.validated_data["content"] = moderation_result["filtered_text"]

            message = serializer.save()

            # 标记为已送达
            message.mark_as_delivered()

            return Response(
                {
                    "message": "消息发送成功",
                    "message_data": MessageSerializer(message, context={"request": request}).data,
                    "moderation": moderation_result,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="标记消息为已读", responses={200: "标记成功"})
    def mark_read(self, request, pk=None):
        """标记消息为已读"""
        message = self.get_object()
        user = request.user

        # 创建或更新已读记录
        MessageRead.objects.get_or_create(message=message, user=user)
        message.mark_as_read()

        return Response({"message": "消息已标记为已读"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="点赞消息", responses={200: "点赞成功"})
    def like(self, request, pk=None):
        """点赞消息"""
        message = self.get_object()
        user = request.user

        # 检查是否已经点赞
        if MessageLike.objects.filter(message=message, user=user).exists():
            return Response(
                {"error": "您已经点赞过这条消息"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 创建点赞记录
        MessageLike.objects.create(message=message, user=user)

        return Response({"message": "点赞成功"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="取消点赞", responses={200: "取消成功"})
    def unlike(self, request, pk=None):
        """取消点赞"""
        message = self.get_object()
        user = request.user

        try:
            like = MessageLike.objects.get(message=message, user=user)
            like.delete()
            return Response({"message": "取消点赞成功"}, status=status.HTTP_200_OK)
        except MessageLike.DoesNotExist:
            return Response(
                {"error": "您没有点赞过这条消息"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["delete"])
    @swagger_auto_schema(operation_description="删除消息", responses={200: "删除成功"})
    def delete_message(self, request, pk=None):
        """删除消息"""
        message = self.get_object()
        user = request.user

        # 检查权限
        if message.sender != user:
            return Response(
                {"error": "只能删除自己的消息"},
                status=status.HTTP_403_FORBIDDEN,
            )

        message.delete_message()

        return Response({"message": "消息已删除"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="收藏消息", responses={200: "收藏成功"})
    def favorite(self, request, pk=None):
        """收藏消息"""
        message = self.get_object()
        user = request.user

        # 检查是否已经收藏
        if MessageFavorite.objects.filter(message=message, user=user).exists():
            return Response(
                {"error": "已经收藏过该消息"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 创建收藏记录
        MessageFavorite.objects.create(message=message, user=user)

        return Response({"message": "消息收藏成功"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="取消收藏", responses={200: "取消成功"})
    def unfavorite(self, request, pk=None):
        """取消收藏"""
        message = self.get_object()
        user = request.user

        try:
            favorite = MessageFavorite.objects.get(message=message, user=user)
            favorite.delete()
            return Response({"message": "取消收藏成功"}, status=status.HTTP_200_OK)
        except MessageFavorite.DoesNotExist:
            return Response({"error": "未收藏该消息"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(operation_description="撤回消息", responses={200: "撤回成功"})
    def recall(self, request, pk=None):
        """撤回消息"""
        message = self.get_object()
        user = request.user

        # 检查权限
        if message.sender != user:
            return Response(
                {"error": "只能撤回自己的消息"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 检查消息状态
        if message.status in ["deleted", "recalled"]:
            return Response(
                {"error": "消息已被删除或撤回"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            message.recall_message()
            return Response({"message": "消息撤回成功"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    @swagger_auto_schema(
        operation_description="转发消息",
        request_body=MessageForwardSerializer,
        responses={200: "转发成功"},
    )
    def forward(self, request, pk=None):
        """转发消息"""
        message = self.get_object()
        user = request.user

        serializer = MessageForwardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        target_room_id = serializer.validated_data["target_room_id"]

        try:
            target_room = ChatRoom.objects.get(id=target_room_id)
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "目标聊天房间不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 检查用户是否为目标房间的参与者
        try:
            participant = ChatParticipant.objects.get(
                chat_room=target_room, user=user, is_active=True
            )
            if not participant.can_send_message:
                return Response(
                    {"error": "您在目标房间没有发送消息的权限"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except ChatParticipant.DoesNotExist:
            return Response(
                {"error": "您不是目标房间的参与者"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 转发消息
        try:
            new_message = message.forward_to_room(target_room, user)
            new_message.forwarded_from = f"{message.chat_room.name} - {message.sender.display_name}"
            new_message.save()

            return Response(
                {
                    "message": "消息转发成功",
                    "forwarded_message": MessageSerializer(
                        new_message, context={"request": request}
                    ).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"转发失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChatInvitationView(APIView):
    """
    聊天邀请视图
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="发送聊天邀请",
        request_body=ChatInvitationCreateSerializer,
        responses={201: ChatInvitationSerializer},
    )
    def post(self, request):
        """发送聊天邀请"""
        serializer = ChatInvitationCreateSerializer(data=request.data)
        if serializer.is_valid():
            invitation = serializer.save()

            return Response(
                {
                    "message": "邀请发送成功",
                    "invitation": ChatInvitationSerializer(invitation).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="获取邀请列表",
        responses={200: ChatInvitationSerializer},
    )
    def get(self, request):
        """获取邀请列表"""
        user = request.user

        # 获取用户的邀请
        invitations = ChatInvitation.objects.filter(invitee=user, status="pending").order_by(
            "-created_at"
        )

        serializer = ChatInvitationSerializer(invitations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_chat_invitation(request, invitation_id):
    """
    接受聊天邀请
    """
    try:
        invitation = ChatInvitation.objects.get(
            id=invitation_id, invitee=request.user, status="pending"
        )
    except ChatInvitation.DoesNotExist:
        return Response({"error": "邀请不存在或已处理"}, status=status.HTTP_404_NOT_FOUND)

    invitation.accept()

    return Response({"message": "邀请已接受"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_chat_invitation(request, invitation_id):
    """
    拒绝聊天邀请
    """
    try:
        invitation = ChatInvitation.objects.get(
            id=invitation_id, invitee=request.user, status="pending"
        )
    except ChatInvitation.DoesNotExist:
        return Response({"error": "邀请不存在或已处理"}, status=status.HTTP_404_NOT_FOUND)

    invitation.reject()

    return Response({"message": "邀请已拒绝"}, status=status.HTTP_200_OK)


class ChatNotificationView(APIView):
    """
    聊天通知视图
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="获取通知列表",
        responses={200: ChatNotificationSerializer},
    )
    def get(self, request):
        """获取通知列表"""
        user = request.user

        # 获取用户的通知
        notifications = ChatNotification.objects.filter(user=user).order_by("-created_at")

        serializer = ChatNotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="标记通知为已读", responses={200: "标记成功"})
    def post(self, request):
        """标记通知为已读"""
        notification_id = request.data.get("notification_id")

        if notification_id:
            # 标记单个通知
            try:
                notification = ChatNotification.objects.get(id=notification_id, user=request.user)
                notification.mark_as_read()
                return Response({"message": "通知已标记为已读"}, status=status.HTTP_200_OK)
            except ChatNotification.DoesNotExist:
                return Response({"error": "通知不存在"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # 标记所有通知为已读
            ChatNotification.objects.filter(user=request.user, status="unread").update(
                status="read", read_at=timezone.now()
            )

            return Response({"message": "所有通知已标记为已读"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_chats(request):
    """
    获取我的聊天记录
    """
    user = request.user

    # 我参与的聊天房间
    chat_rooms = ChatRoom.objects.filter(participants=user).order_by("-last_message_at")

    return Response(
        {
            "chat_rooms": ChatListSerializer(
                chat_rooms, many=True, context={"request": request}
            ).data
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def message_action(request):
    """
    消息操作（点赞、已读、删除等）
    """
    serializer = MessageActionSerializer(data=request.data)
    if serializer.is_valid():
        action = serializer.validated_data["action"]
        message_id = serializer.validated_data["message_id"]
        data = serializer.validated_data.get("data", {})

        try:
            message = Message.objects.get(id=message_id)  # type: ignore[attr-defined]
        except Message.DoesNotExist:
            return Response({"error": "消息不存在"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        # 执行操作
        if action == "like":
            if MessageLike.objects.filter(message=message, user=user).exists():  # type: ignore[operator]
                return Response(
                    {"error": "您已经点赞过这条消息"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            MessageLike.objects.create(message=message, user=user)
            message = "点赞成功"
        elif action == "unlike":
            try:
                like = MessageLike.objects.get(message=message, user=user)
                like.delete()
                message = "取消点赞成功"
            except MessageLike.DoesNotExist:
                return Response(
                    {"error": "您没有点赞过这条消息"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif action == "read":
            MessageRead.objects.get_or_create(message=message, user=user)
            message.mark_as_read()
            message = "消息已标记为已读"
        elif action == "delete":
            if message.sender != user:
                return Response(
                    {"error": "只能删除自己的消息"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            message.delete_message()
            message = "消息已删除"
        elif action == "edit":
            new_content = data.get("content")
            if not new_content:
                return Response(
                    {"error": "新内容不能为空"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if message.sender != user:
                return Response(
                    {"error": "只能编辑自己的消息"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            message.edit_message(new_content)
            message = "消息已编辑"
        else:
            return Response({"error": "不支持的操作"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": message,
                "message_data": MessageSerializer(message, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chat_messages(request, room_id):
    """
    获取聊天房间的消息
    """
    try:
        chat_room = ChatRoom.objects.get(id=room_id)  # type: ignore[attr-defined]
    except ChatRoom.DoesNotExist:
        return Response({"error": "聊天房间不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 检查用户是否是参与者
    if not ChatParticipant.objects.filter(
        chat_room=chat_room, user=request.user, is_active=True
    ).exists():
        return Response({"error": "您不是该房间的参与者"}, status=status.HTTP_403_FORBIDDEN)

    # 获取消息
    messages = Message.objects.filter(
        chat_room=chat_room, status__in=["sent", "delivered", "read"]
    ).order_by("-created_at")

    # 分页
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 20))
    start = (page - 1) * page_size
    end = start + page_size

    messages = messages[start:end]

    return Response(
        {
            "messages": MessageSerializer(messages, many=True, context={"request": request}).data,
            "page": page,
            "page_size": page_size,
            "total": messages.count(),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_file(request, room_id):
    """
    上传文件到聊天房间
    """
    try:
        chat_room = ChatRoom.objects.get(id=room_id)  # type: ignore[attr-defined]
    except ChatRoom.DoesNotExist:
        return Response({"error": "聊天房间不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 检查用户是否是参与者
    if not ChatParticipant.objects.filter(
        chat_room=chat_room, user=request.user, is_active=True
    ).exists():
        return Response({"error": "您不是该房间的参与者"}, status=status.HTTP_403_FORBIDDEN)

    # 检查是否有文件上传
    if "file" not in request.FILES:
        return Response({"error": "请选择要上传的文件"}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES["file"]
    message_type = request.POST.get("message_type", "file")

    # 上传文件
    upload_service = FileUploadService()
    result = upload_service.upload_file(
        file=file,
        chat_room_id=str(chat_room.id),
        sender_id=str(request.user.id),
        message_type=message_type,
    )

    if not result["success"]:
        return Response({"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

    # 创建消息
    message_data = result["message_data"]
    message = Message.objects.create(
        chat_room=chat_room,
        sender=request.user,
        content=message_data["content"],
        message_type=message_data["message_type"],
        media_url=message_data["media_url"],
        media_size=message_data["media_size"],
        media_duration=message_data["media_duration"],
        status="sent",
    )

    # 更新房间统计信息
    chat_room.message_count += 1
    chat_room.last_message_at = timezone.now()
    chat_room.save(update_fields=["message_count", "last_message_at"])

    # 发送通知
    notification_service = NotificationService()
    notification_service.send_message_notification(message)

    return Response(
        {
            "message": "文件上传成功",
            "message_data": MessageSerializer(message, context={"request": request}).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_messages(request):
    """
    搜索消息
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return Response({"error": "请输入搜索关键词"}, status=status.HTTP_400_BAD_REQUEST)

    # 构建过滤条件
    filters = {}
    if request.GET.get("room_type"):
        filters["room_type"] = request.GET.get("room_type")
    if request.GET.get("message_type"):
        filters["message_type"] = request.GET.get("message_type")
    if request.GET.get("date_from"):
        filters["date_from"] = request.GET.get("date_from")
    if request.GET.get("date_to"):
        filters["date_to"] = request.GET.get("date_to")

    # 执行搜索
    search_service = MessageSearchService()
    results = search_service.search_messages(
        user_id=str(request.user.id), query=query, filters=filters
    )

    return Response(
        {"results": results, "total": len(results), "query": query},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_rooms(request):
    """
    搜索聊天房间
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return Response({"error": "请输入搜索关键词"}, status=status.HTTP_400_BAD_REQUEST)

    # 构建过滤条件
    filters = {}
    if request.GET.get("room_type"):
        filters["room_type"] = request.GET.get("room_type")
    if request.GET.get("is_private") is not None:
        filters["is_private"] = request.GET.get("is_private") == "true"

    # 执行搜索
    search_service = MessageSearchService()
    results = search_service.search_rooms(
        user_id=str(request.user.id), query=query, filters=filters
    )

    return Response(
        {"results": results, "total": len(results), "query": query},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_private_chat(request):
    """
    创建私聊房间
    """
    other_user_id = request.data.get("other_user_id")

    if not other_user_id:
        return Response({"error": "需要指定对方用户ID"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        other_user = User.objects.get(id=other_user_id)
    except User.DoesNotExist:
        return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 不能和自己创建私聊
    if str(request.user.id) == str(other_user_id):
        return Response({"error": "不能和自己创建私聊"}, status=status.HTTP_400_BAD_REQUEST)

    # 获取其他用户信息
    other_user = get_object_or_404(User, id=other_user_id)

    # 检查是否已经存在聊天会话
    existing_room = (
        ChatRoom.objects.filter(room_type="private", participants=request.user)
        .filter(participants=other_user)
        .first()
    )

    if existing_room:
        return Response(
            {
                "message": "私聊房间已存在",
                "chat_room": ChatRoomDetailSerializer(
                    existing_room, context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    # 创建私聊房间
    chat_service = ChatRoomService()
    chat_room = chat_service.create_private_chat(
        user1_id=str(request.user.id), user2_id=str(other_user_id)
    )

    if not chat_room:
        return Response(
            {"error": "创建私聊房间失败"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "message": "私聊房间创建成功",
            "chat_room": ChatRoomDetailSerializer(chat_room, context={"request": request}).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_chats(request):
    """
    获取用户的聊天列表
    """
    chat_service = ChatRoomService()
    chats = chat_service.get_user_chats(user_id=str(request.user.id))

    return Response({"chats": chats, "total": len(chats)}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_favorite_messages(request):
    """
    获取用户收藏的消息列表
    """
    user = request.user

    # 获取用户收藏的消息
    favorites = MessageFavorite.objects.filter(user=user).order_by("-created_at")

    # 分页
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 20))
    start = (page - 1) * page_size
    end = start + page_size

    favorites = favorites[start:end]

    return Response(
        {
            "favorites": MessageFavoriteSerializer(
                favorites, many=True, context={"request": request}
            ).data,
            "page": page,
            "page_size": page_size,
            "total": favorites.count(),
        },
        status=status.HTTP_200_OK,
    )
