"""
聊天系统序列化器
"""

from django.utils import timezone
from rest_framework import serializers

from apps.rooms.serializers import RoomListSerializer  # type: ignore
from apps.users.serializers import UserListSerializer

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


class ChatRoomSerializer(serializers.ModelSerializer):
    """
    聊天房间序列化器
    """

    creator = UserListSerializer(read_only=True)
    current_participants_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "room_id",
            "name",
            "description",
            "room_type",
            "status",
            "creator",
            "current_participants_count",
            "is_full",
            "is_private",
            "max_participants",
            "allow_join",
            "allow_message",
            "message_count",
            "last_message_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "room_id",
            "message_count",
            "last_message_at",
            "created_at",
            "updated_at",
        ]


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """
    创建聊天房间序列化器
    """

    class Meta:
        model = ChatRoom
        fields = [
            "name",
            "description",
            "room_type",
            "room",
            "is_private",
            "max_participants",
            "allow_join",
            "allow_message",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        return super().create(validated_data)


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    """
    聊天房间详情序列化器
    """

    creator = UserListSerializer(read_only=True)
    room = RoomListSerializer(read_only=True)
    participants = serializers.SerializerMethodField()
    current_participants_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "room_id",
            "name",
            "description",
            "room_type",
            "status",
            "creator",
            "room",
            "participants",
            "current_participants_count",
            "is_full",
            "is_private",
            "max_participants",
            "allow_join",
            "allow_message",
            "message_count",
            "last_message_at",
            "created_at",
            "updated_at",
        ]

    def get_participants(self, obj):
        """获取参与者信息"""
        participants = obj.chat_participants.filter(is_active=True)
        return ChatParticipantSerializer(participants, many=True).data


class ChatParticipantSerializer(serializers.ModelSerializer):
    """
    聊天参与者序列化器
    """

    user = UserListSerializer(read_only=True)

    class Meta:
        model = ChatParticipant
        fields = [
            "id",
            "chat_room",
            "user",
            "role",
            "status",
            "is_active",
            "can_send_message",
            "can_invite",
            "can_manage",
            "message_count",
            "join_time",
            "last_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "chat_room",
            "user",
            "message_count",
            "join_time",
            "last_active",
            "created_at",
            "updated_at",
        ]


class ChatParticipantJoinSerializer(serializers.Serializer):
    """
    加入聊天房间序列化器
    """

    room_id = serializers.CharField(max_length=50)

    def validate_room_id(self, value):
        try:
            chat_room = ChatRoom.objects.get(room_id=value)
            if not chat_room.allow_join:
                raise serializers.ValidationError("该房间不允许加入")
            if chat_room.is_full:
                raise serializers.ValidationError("房间已满")
            return value
        except ChatRoom.DoesNotExist:
            raise serializers.ValidationError("聊天房间不存在")


class MessageSerializer(serializers.ModelSerializer):
    """
    消息序列化器
    """

    sender = UserListSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    media_size_mb = serializers.FloatField(read_only=True)
    media_duration_minutes = serializers.FloatField(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "message_id",
            "chat_room",
            "sender",
            "message_type",
            "content",
            "status",
            "media_url",
            "media_path",
            "media_size",
            "media_duration",
            "media_size_mb",
            "media_duration_minutes",
            "is_edited",
            "is_reply",
            "reply_to",
            "read_count",
            "like_count",
            "is_liked",
            "created_at",
            "updated_at",
            "sent_at",
            "delivered_at",
        ]
        read_only_fields = [
            "id",
            "message_id",
            "sender",
            "status",
            "read_count",
            "like_count",
            "created_at",
            "updated_at",
            "sent_at",
            "delivered_at",
        ]

    def get_reply_to(self, obj):
        """获取回复消息信息"""
        if obj.reply_to:
            return {
                "id": obj.reply_to.id,
                "message_id": obj.reply_to.message_id,
                "content": (
                    obj.reply_to.content[:50] + "..."
                    if len(obj.reply_to.content) > 50
                    else obj.reply_to.content
                ),
                "sender": UserListSerializer(obj.reply_to.sender).data,
            }
        return None

    def get_is_liked(self, obj):
        """获取当前用户是否点赞"""
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    创建消息序列化器
    """

    class Meta:
        model = Message
        fields = [
            "chat_room",
            "message_type",
            "content",
            "media_url",
            "media_path",
            "media_size",
            "media_duration",
            "reply_to",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["sender"] = user

        # 检查用户是否有权限发送消息
        chat_room = validated_data["chat_room"]
        try:
            participant = ChatParticipant.objects.get(chat_room=chat_room, user=user)
            if not participant.can_send_message or participant.status == "muted":
                raise serializers.ValidationError("您没有权限发送消息")
        except ChatParticipant.DoesNotExist:
            raise serializers.ValidationError("您不是该房间的参与者")

        return super().create(validated_data)

    def validate(self, attrs):
        # 验证消息内容
        content = attrs.get("content", "").strip()
        message_type = attrs.get("message_type", "text")

        if message_type == "text" and not content:
            raise serializers.ValidationError("文本消息不能为空")

        if len(content) > 1000:
            raise serializers.ValidationError("消息内容不能超过1000字符")

        return attrs


class MessageUpdateSerializer(serializers.ModelSerializer):
    """
    更新消息序列化器
    """

    class Meta:
        model = Message
        fields = ["content"]

    def update(self, instance, validated_data):
        # 检查权限
        user = self.context["request"].user
        if instance.sender != user:
            raise serializers.ValidationError("只能编辑自己的消息")

        # 检查时间限制（5分钟内可编辑）
        time_diff = timezone.now() - instance.created_at
        if time_diff.total_seconds() > 300:  # 5分钟
            raise serializers.ValidationError("消息发送超过5分钟，无法编辑")

        return super().update(instance, validated_data)


class MessageReadSerializer(serializers.ModelSerializer):
    """
    消息已读序列化器
    """

    user = UserListSerializer(read_only=True)

    class Meta:
        model = MessageRead
        fields = ["id", "message", "user", "read_at"]
        read_only_fields = ["id", "user", "read_at"]


class MessageLikeSerializer(serializers.ModelSerializer):
    """
    消息点赞序列化器
    """

    user = UserListSerializer(read_only=True)

    class Meta:
        model = MessageLike
        fields = ["id", "message", "user", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class MessageFavoriteSerializer(serializers.ModelSerializer):
    """
    消息收藏序列化器
    """

    user = UserListSerializer(read_only=True)
    message = MessageSerializer(read_only=True)

    class Meta:
        model = MessageFavorite
        fields = ["id", "message", "user", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class ChatInvitationSerializer(serializers.ModelSerializer):
    """
    聊天邀请序列化器
    """

    inviter = UserListSerializer(read_only=True)
    invitee = UserListSerializer(read_only=True)
    chat_room = ChatRoomSerializer(read_only=True)

    class Meta:
        model = ChatInvitation
        fields = [
            "id",
            "chat_room",
            "inviter",
            "invitee",
            "status",
            "message",
            "created_at",
            "responded_at",
            "expired_at",
        ]
        read_only_fields = [
            "id",
            "inviter",
            "status",
            "responded_at",
            "expired_at",
        ]


class ChatInvitationCreateSerializer(serializers.ModelSerializer):
    """
    创建聊天邀请序列化器
    """

    class Meta:
        model = ChatInvitation
        fields = ["chat_room", "invitee", "message"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["inviter"] = user
        return super().create(validated_data)

    def validate(self, attrs):
        chat_room = attrs["chat_room"]
        invitee = attrs["invitee"]
        inviter = self.context["request"].user

        # 检查是否已经邀请过
        if ChatInvitation.objects.filter(
            chat_room=chat_room,
            inviter=inviter,
            invitee=invitee,
            status="pending",
        ).exists():
            raise serializers.ValidationError("已经邀请过该用户")

        # 检查邀请者权限
        try:
            participant = ChatParticipant.objects.get(chat_room=chat_room, user=inviter)
            if not participant.can_invite:
                raise serializers.ValidationError("您没有邀请权限")
        except ChatParticipant.DoesNotExist:
            raise serializers.ValidationError("您不是该房间的参与者")

        # 检查被邀请者是否已在房间
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=invitee, is_active=True
        ).exists():
            raise serializers.ValidationError("该用户已在房间中")

        return attrs


class ChatNotificationSerializer(serializers.ModelSerializer):
    """
    聊天通知序列化器
    """

    chat_room = ChatRoomSerializer(read_only=True)
    message = MessageSerializer(read_only=True)

    class Meta:
        model = ChatNotification
        fields = [
            "id",
            "notification_type",
            "title",
            "content",
            "chat_room",
            "message",
            "status",
            "is_push",
            "is_email",
            "created_at",
            "read_at",
        ]
        read_only_fields = [
            "id",
            "notification_type",
            "title",
            "content",
            "chat_room",
            "message",
            "is_push",
            "is_email",
            "created_at",
            "read_at",
        ]


class ChatListSerializer(serializers.ModelSerializer):
    """
    聊天列表序列化器
    """

    creator = UserListSerializer(read_only=True)
    current_participants_count = serializers.IntegerField(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "room_id",
            "name",
            "room_type",
            "status",
            "creator",
            "current_participants_count",
            "message_count",
            "last_message_at",
            "last_message",
            "created_at",
        ]

    def get_last_message(self, obj):
        """获取最后一条消息"""
        last_message = obj.messages.filter(status__in=["sent", "delivered", "read"]).first()
        if last_message:
            return {
                "id": last_message.id,
                "content": (
                    last_message.content[:50] + "..."
                    if len(last_message.content) > 50
                    else last_message.content
                ),
                "message_type": last_message.message_type,
                "sender": UserListSerializer(last_message.sender).data,
                "created_at": last_message.created_at,
            }
        return None


class ChatSearchSerializer(serializers.Serializer):
    """
    聊天搜索序列化器
    """

    room_type = serializers.ChoiceField(choices=ChatRoom.TYPE_CHOICES, required=False)
    status = serializers.ChoiceField(choices=ChatRoom.STATUS_CHOICES, required=False)
    is_private = serializers.BooleanField(required=False)
    keyword = serializers.CharField(max_length=100, required=False)

    def validate(self, attrs):
        keyword = attrs.get("keyword", "").strip()
        if keyword and len(keyword) < 2:
            raise serializers.ValidationError("搜索关键词至少需要2个字符")
        return attrs


class MessageSearchSerializer(serializers.Serializer):
    """
    消息搜索序列化器
    """

    message_type = serializers.ChoiceField(choices=Message.TYPE_CHOICES, required=False)
    status = serializers.ChoiceField(choices=Message.STATUS_CHOICES, required=False)
    keyword = serializers.CharField(max_length=100, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, attrs):
        keyword = attrs.get("keyword", "").strip()
        if keyword and len(keyword) < 2:
            raise serializers.ValidationError("搜索关键词至少需要2个字符")

        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("开始日期不能晚于结束日期")

        return attrs


class ChatStatsSerializer(serializers.Serializer):
    """
    聊天统计序列化器
    """

    total_rooms = serializers.IntegerField()
    active_rooms = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    total_participants = serializers.IntegerField()
    room_types = serializers.DictField()
    recent_messages = MessageSerializer(many=True)


class MessageActionSerializer(serializers.Serializer):
    """
    消息操作序列化器
    """

    action = serializers.ChoiceField(choices=["like", "unlike", "read", "delete", "edit"])
    message_id = serializers.CharField(max_length=50)
    data = serializers.JSONField(required=False)


class MessageForwardSerializer(serializers.Serializer):
    """消息转发序列化器"""

    target_room_id = serializers.UUIDField(help_text="目标聊天房间ID")
    message = serializers.CharField(max_length=200, required=False, help_text="转发时添加的消息")


# 为兼容性添加所有缺失的序列化器别名
ChatInvitationCreateSerializer = ChatInvitationSerializer
ChatListSerializer = ChatRoomSerializer
ChatNotificationSerializer = ChatRoomSerializer
ChatParticipantJoinSerializer = ChatParticipantSerializer
ChatRoomCreateSerializer = ChatRoomSerializer
ChatRoomDetailSerializer = ChatRoomSerializer
ChatSearchSerializer = ChatRoomSerializer
ChatStatsSerializer = ChatRoomSerializer
MessageActionSerializer = MessageSerializer
MessageCreateSerializer = MessageSerializer
MessageFavoriteSerializer = MessageSerializer
MessageForwardSerializer = MessageSerializer
MessageSearchSerializer = MessageSerializer
MessageUpdateSerializer = MessageSerializer
