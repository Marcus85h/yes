"""
聊天系统模型
"""

import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from apps.rooms.models import Room
from apps.users.models import User


class ChatRoom(models.Model):
    """
    聊天房间模型
    """

    # 房间类型
    TYPE_CHOICES = (
        ("private", "私聊"),
        ("group", "群聊"),
        ("room", "房间聊天"),
        ("system", "系统消息"),
    )

    # 房间状态
    STATUS_CHOICES = (
        ("active", "活跃"),
        ("archived", "已归档"),
        ("deleted", "已删除"),
    )

    # 基础信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_room_id = models.CharField(max_length=50, unique=True, verbose_name="房间ID")
    name = models.CharField(max_length=100, verbose_name="房间名称")
    description = models.TextField(blank=True, verbose_name="房间描述")

    # 房间信息
    room_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="private",  # type: ignore[call-arg]
        verbose_name="房间类型",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",  # type: ignore[call-arg]
        verbose_name="房间状态",
    )

    # 关联信息
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="chat_rooms",
        verbose_name="关联房间",
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_chat_rooms",
        verbose_name="创建者",
    )
    participants = models.ManyToManyField(
        User,
        through="ChatParticipant",
        related_name="chat_rooms",
        verbose_name="参与者",
    )

    # 房间设置
    is_private = models.BooleanField(default=False, verbose_name="是否私密")  # type: ignore[call-arg]
    max_participants = models.IntegerField(default=100, verbose_name="最大参与人数")  # type: ignore[call-arg]
    allow_join = models.BooleanField(default=True, verbose_name="允许加入")  # type: ignore[call-arg]
    allow_message = models.BooleanField(default=True, verbose_name="允许发送消息")  # type: ignore[call-arg]

    # 统计信息
    message_count = models.IntegerField(default=0, verbose_name="消息数量")  # type: ignore[call-arg]
    last_message_at = models.DateTimeField(blank=True, null=True, verbose_name="最后消息时间")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "chat_rooms"
        verbose_name = "聊天房间"
        verbose_name_plural = "聊天房间"
        ordering = ["-last_message_at", "-created_at"]
        indexes = [
            models.Index(fields=["custom_room_id"]),
            models.Index(fields=["room_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["last_message_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"  # type: ignore[attr-defined]

    def save(self, *args, **kwargs):
        # 自动生成房间ID
        if not self.custom_room_id:
            self.custom_room_id = self.generate_room_id()
        super().save(*args, **kwargs)

    def generate_room_id(self):
        """生成房间ID"""
        import secrets
        import string

        return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))

    @property
    def current_participants_count(self):
        """当前参与人数"""
        return self.participants.filter(chatparticipant__is_active=True).count()

    @property
    def is_full(self):
        """是否已满"""
        return self.current_participants_count >= self.max_participants


class ChatParticipant(models.Model):
    """
    聊天参与者
    """

    # 参与者角色
    ROLE_CHOICES = (
        ("owner", "房主"),
        ("admin", "管理员"),
        ("member", "成员"),
        ("guest", "访客"),
    )

    # 参与者状态
    STATUS_CHOICES = (
        ("active", "活跃"),
        ("muted", "禁言"),
        ("banned", "封禁"),
        ("left", "已离开"),
    )

    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="chat_participants",
        verbose_name="聊天房间",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_participations",
        verbose_name="用户",
    )

    # 参与信息
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="member",  # type: ignore[call-arg]
        verbose_name="角色",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",  # type: ignore[call-arg]
        verbose_name="状态",
    )
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")  # type: ignore[call-arg]

    # 权限设置
    can_send_message = models.BooleanField(default=True, verbose_name="可发送消息")  # type: ignore[call-arg]
    can_invite = models.BooleanField(default=True, verbose_name="可邀请用户")  # type: ignore[call-arg]
    can_manage = models.BooleanField(default=False, verbose_name="可管理房间")  # type: ignore[call-arg]

    # 统计信息
    message_count = models.IntegerField(default=0, verbose_name="发送消息数")  # type: ignore[call-arg]
    join_time = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")
    last_active = models.DateTimeField(auto_now=True, verbose_name="最后活跃时间")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "chat_participants"
        verbose_name = "聊天参与者"
        verbose_name_plural = "聊天参与者"
        unique_together = ["chat_room", "user"]
        indexes = [
            models.Index(fields=["chat_room", "user"]),
            models.Index(fields=["role"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["join_time"]),
        ]

    def __str__(self):
        return f"{self.user.display_name} 在 {self.chat_room.name}"  # type: ignore[attr-defined]

    def mute(self, duration_minutes=None):
        """禁言用户"""
        self.status = "muted"
        self.can_send_message = False
        if duration_minutes:
            self.muted_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save()

    def unmute(self):
        """取消禁言"""
        self.status = "active"
        self.can_send_message = True
        self.muted_until = None
        self.save()

    def ban(self):
        """封禁用户"""
        self.status = "banned"
        self.is_active = False
        self.save()

    def leave(self):
        """离开房间"""
        self.status = "left"
        self.is_active = False
        self.save()


class Message(models.Model):
    """
    聊天消息
    """

    # 消息类型
    TYPE_CHOICES = (
        ("text", "文本"),
        ("image", "图片"),
        ("video", "视频"),
        ("audio", "音频"),
        ("file", "文件"),
        ("location", "位置"),
        ("system", "系统消息"),
        ("gift", "礼物"),
        ("call", "通话"),
    )

    # 消息状态
    STATUS_CHOICES = (
        ("sent", "已发送"),
        ("delivered", "已送达"),
        ("read", "已读"),
        ("failed", "发送失败"),
        ("deleted", "已删除"),
        ("recalled", "已撤回"),
    )

    # 基础信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message_id = models.CharField(max_length=50, unique=True, verbose_name="消息ID")
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="聊天房间",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="发送者",
    )

    # 消息内容
    message_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="text",  # type: ignore[call-arg]
        verbose_name="消息类型",
    )
    content = models.TextField(verbose_name="消息内容")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="sent",  # type: ignore[call-arg]
        verbose_name="消息状态",
    )

    # 媒体信息
    media_url = models.URLField(blank=True, verbose_name="媒体URL")
    media_path = models.CharField(max_length=500, blank=True, verbose_name="媒体路径")
    media_size = models.BigIntegerField(default=0, verbose_name="媒体大小(字节)")  # type: ignore[call-arg]
    media_duration = models.IntegerField(default=0, verbose_name="媒体时长(秒)")  # type: ignore[call-arg]

    # 消息属性
    is_edited = models.BooleanField(default=False, verbose_name="是否编辑")  # type: ignore[call-arg]
    is_reply = models.BooleanField(default=False, verbose_name="是否回复")  # type: ignore[call-arg]
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="replies",
        verbose_name="回复消息",
    )
    is_forwarded = models.BooleanField(default=False, verbose_name="是否转发")  # type: ignore[call-arg]
    original_message = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forwarded_messages",
        verbose_name="原消息",
    )
    forwarded_from = models.CharField(max_length=255, blank=True, verbose_name="转发来源")

    # 统计信息
    read_count = models.IntegerField(default=0, verbose_name="已读人数")  # type: ignore[call-arg]
    like_count = models.IntegerField(default=0, verbose_name="点赞数")  # type: ignore[call-arg]

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name="送达时间")

    class Meta:
        db_table = "messages"
        verbose_name = "聊天消息"
        verbose_name_plural = "聊天消息"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["message_id"]),
            models.Index(fields=["chat_room", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
            models.Index(fields=["message_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.sender.display_name}: {self.content[:50]}"  # type: ignore[attr-defined]

    def save(self, *args, **kwargs):
        # 自动生成消息ID
        if not self.message_id:
            self.message_id = self.generate_message_id()

        # 更新房间统计信息
        if not self.pk:  # 新消息
            self.chat_room.message_count += 1
            self.chat_room.last_message_at = timezone.now()
            self.chat_room.save(update_fields=["message_count", "last_message_at"])

            # 更新发送者统计
            participant = ChatParticipant.objects.get(chat_room=self.chat_room, user=self.sender)
            participant.message_count += 1
            participant.save(update_fields=["message_count"])

        super().save(*args, **kwargs)

    def generate_message_id(self):
        """生成消息ID"""
        import secrets
        import string

        return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))

    def mark_as_delivered(self):
        """标记为已送达"""
        self.status = "delivered"
        self.delivered_at = timezone.now()
        self.save(update_fields=["status", "delivered_at"])

    def mark_as_read(self):
        """标记为已读"""
        self.status = "read"
        self.read_count += 1
        self.save(update_fields=["status", "read_count"])

    def edit_message(self, new_content):
        """编辑消息"""
        self.content = new_content
        self.is_edited = True
        self.save(update_fields=["content", "is_edited", "updated_at"])

    def delete_message(self):
        """删除消息"""
        self.status = "deleted"
        self.save(update_fields=["status"])

    def recall_message(self):
        """撤回消息"""
        # 检查是否可以撤回（2分钟内）
        time_diff = timezone.now() - self.created_at
        if time_diff.total_seconds() > 120:  # 2分钟
            raise ValueError("消息发送超过2分钟，无法撤回")

        self.status = "recalled"
        self.save(update_fields=["status"])

    def forward_to_room(self, target_room, sender):
        """转发消息到指定房间"""
        from .models import Message

        # 创建新消息
        new_message = Message.objects.create(
            chat_room=target_room,
            sender=sender,
            content=self.content,
            message_type=self.message_type,
            media_url=self.media_url,
            media_type=self.media_type,
            media_size=self.media_size,
            is_forwarded=True,
            original_message=self,
        )

        return new_message

    @property
    def media_size_mb(self):
        """媒体大小(MB)"""
        return round(self.media_size / (1024 * 1024), 2)

    @property
    def media_duration_minutes(self):
        """媒体时长(分钟)"""
        return round(self.media_duration / 60, 1)


class MessageRead(models.Model):
    """
    消息已读记录
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="read_records",
        verbose_name="消息",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="read_messages",
        verbose_name="用户",
    )
    read_at = models.DateTimeField(auto_now_add=True, verbose_name="阅读时间")

    class Meta:
        db_table = "message_reads"
        verbose_name = "消息已读记录"
        verbose_name_plural = "消息已读记录"
        unique_together = ["message", "user"]
        indexes = [
            models.Index(fields=["message", "user"]),
            models.Index(fields=["read_at"]),
        ]

    def __str__(self):
        return f"{self.user.display_name} 阅读了 {self.message.message_id}"


class MessageLike(models.Model):
    """
    消息点赞
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="消息",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="liked_messages",
        verbose_name="用户",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        db_table = "message_likes"
        verbose_name = "消息点赞"
        verbose_name_plural = "消息点赞"
        unique_together = ["message", "user"]
        indexes = [
            models.Index(fields=["message", "user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.display_name} 点赞了 {self.message.content[:20]}"

    def save(self, *args, **kwargs):
        # 更新消息点赞数
        super().save(*args, **kwargs)
        self.message.like_count = self.message.likes.count()
        self.message.save(update_fields=["like_count"])

    def delete(self, *args, **kwargs):
        # 减少消息点赞数
        super().delete(*args, **kwargs)
        self.message.like_count = self.message.likes.count()
        self.message.save(update_fields=["like_count"])


class MessageFavorite(models.Model):
    """
    消息收藏
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="消息",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_messages",
        verbose_name="用户",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        db_table = "message_favorites"
        verbose_name = "消息收藏"
        verbose_name_plural = "消息收藏"
        unique_together = ["message", "user"]
        indexes = [
            models.Index(fields=["message", "user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.display_name} 收藏了 {self.message.content[:20]}"


class ChatInvitation(models.Model):
    """
    聊天邀请
    """

    # 邀请状态
    STATUS_CHOICES = (
        ("pending", "待处理"),
        ("accepted", "已接受"),
        ("rejected", "已拒绝"),
        ("expired", "已过期"),
    )

    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="聊天房间",
    )
    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_chat_invitations",
        verbose_name="邀请者",
    )
    invitee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_chat_invitations",
        verbose_name="被邀请者",
    )

    # 邀请信息
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",  # type: ignore[call-arg]
        verbose_name="状态",
    )
    message = models.TextField(max_length=200, blank=True, verbose_name="邀请消息")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    responded_at = models.DateTimeField(blank=True, null=True, verbose_name="响应时间")
    expired_at = models.DateTimeField(blank=True, null=True, verbose_name="过期时间")

    class Meta:
        db_table = "chat_invitations"
        verbose_name = "聊天邀请"
        verbose_name_plural = "聊天邀请"
        unique_together = ["chat_room", "inviter", "invitee"]
        indexes = [
            models.Index(fields=["chat_room", "inviter", "invitee"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.inviter.display_name} 邀请 {self.invitee.display_name} 加入 {self.chat_room.name}"

    def accept(self):
        """接受邀请"""
        self.status = "accepted"
        self.responded_at = timezone.now()
        self.save()

        # 创建参与者记录
        ChatParticipant.objects.create(chat_room=self.chat_room, user=self.invitee, role="member")

    def reject(self):
        """拒绝邀请"""
        self.status = "rejected"
        self.responded_at = timezone.now()
        self.save()

    def expire(self):
        """过期邀请"""
        self.status = "expired"
        self.expired_at = timezone.now()
        self.save()


class ChatNotification(models.Model):
    """
    聊天通知
    """

    # 通知类型
    TYPE_CHOICES = (
        ("message", "新消息"),
        ("mention", "提及"),
        ("invitation", "邀请"),
        ("system", "系统通知"),
    )

    # 通知状态
    STATUS_CHOICES = (
        ("unread", "未读"),
        ("read", "已读"),
        ("archived", "已归档"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_notifications",
        verbose_name="用户",
    )
    notification_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, verbose_name="通知类型"
    )
    title = models.CharField(max_length=100, verbose_name="通知标题")
    content = models.TextField(verbose_name="通知内容")

    # 关联信息
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="notifications",
        verbose_name="聊天房间",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="notifications",
        verbose_name="消息",
    )

    # 通知状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="unread",  # type: ignore[call-arg]
        verbose_name="状态",
    )
    is_push = models.BooleanField(default=True, verbose_name="推送通知")  # type: ignore[call-arg]
    is_email = models.BooleanField(default=False, verbose_name="邮件通知")  # type: ignore[call-arg]

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    read_at = models.DateTimeField(blank=True, null=True, verbose_name="阅读时间")

    class Meta:
        db_table = "chat_notifications"
        verbose_name = "聊天通知"
        verbose_name_plural = "聊天通知"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["notification_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.display_name}"  # type: ignore[attr-defined]

    def mark_as_read(self):
        """标记为已读"""
        self.status = "read"
        self.read_at = timezone.now()
        self.save(update_fields=["status", "read_at"])

    def archive(self):
        """归档通知"""
        self.status = "archived"
        self.save(update_fields=["status"])
