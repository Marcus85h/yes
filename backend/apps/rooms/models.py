"""
房间系统模型
"""

import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models
from django.utils import timezone

from apps.users.models import User


class Room(models.Model):
    """
    房间模型
    """

    # 房间状态
    STATUS_CHOICES = (
        ("waiting", "等待中"),
        ("matching", "匹配中"),
        ("connected", "已连接"),
        ("disconnected", "已断开"),
        ("closed", "已关闭"),
    )

    # 房间类型
    TYPE_CHOICES = (
        ("random", "随机匹配"),
        ("filtered", "条件匹配"),
        ("private", "私密房间"),
        ("group", "群组房间"),
    )

    # 基础信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_id = models.CharField(max_length=20, unique=True, verbose_name="房间ID")
    name = models.CharField(max_length=100, blank=True, verbose_name="房间名称")
    description = models.TextField(max_length=500, blank=True, verbose_name="房间描述")

    # 房间配置
    room_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="random",
        verbose_name="房间类型",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="waiting",
        verbose_name="房间状态",
    )
    max_participants = models.IntegerField(
        default=2,  # type: ignore[call-arg]
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="最大参与人数",
    )

    # 匹配条件
    target_gender = models.CharField(
        max_length=10,
        choices=User.GENDER_CHOICES,
        blank=True,
        verbose_name="目标性别",
    )
    min_age = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(18), MaxValueValidator(65)],
        verbose_name="最小年龄",
    )
    max_age = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(18), MaxValueValidator(65)],
        verbose_name="最大年龄",
    )
    location_preference = models.CharField(max_length=100, blank=True, verbose_name="地区偏好")

    # 房间设置
    is_private = models.BooleanField(default=False, verbose_name="是否私密")  # type: ignore[call-arg]
    is_featured = models.BooleanField(default=False, verbose_name="是否推荐")  # type: ignore[call-arg]
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")  # type: ignore[call-arg]

    # 统计信息
    total_visitors = models.IntegerField(default=0, verbose_name="总访客数")  # type: ignore[call-arg]
    total_connections = models.IntegerField(default=0, verbose_name="总连接数")  # type: ignore[call-arg]
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,  # type: ignore[call-arg]
        verbose_name="平均评分",
    )

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="最后活动时间")

    class Meta:
        db_table = "rooms"
        verbose_name = "房间"
        verbose_name_plural = "房间"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["room_id"]),
            models.Index(fields=["room_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"房间 {self.room_id} ({self.get_room_type_display()})"  # type: ignore[attr-defined]

    def save(self, *args, **kwargs):
        # Ensure unique room_id is generated, handle race condition
        if not self.room_id:
            for _ in range(5):  # 最多尝试5次
                new_id = self.generate_room_id()
                if not Room.objects.filter(room_id=new_id).exists():  # type: ignore[attr-defined]
                    self.room_id = new_id
                    try:
                        super().save(*args, **kwargs)
                        return
                    except IntegrityError:
                        continue
            raise IntegrityError("Failed to generate unique room_id after 5 attempts")
        super().save(*args, **kwargs)

    def generate_room_id(self):
        """生成房间ID"""
        import secrets
        import string

        return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    @property
    def current_participants_count(self):
        """当前参与人数"""
        return self.participants.filter(is_active=True).count()  # type: ignore[attr-defined]

    @property
    def is_full(self):
        """房间是否已满"""
        return self.current_participants_count >= self.max_participants

    def can_join(self, user):
        """Check if a user can join the room. Returns (bool, message)."""
        try:
            if not self.is_active:
                return False, "房间已关闭"
            if self.is_full:
                return False, "房间已满"
            if self.is_private and not self.participants.filter(user=user).exists():  # type: ignore[attr-defined]
                return False, "私密房间，无法加入"
            return True, "可以加入"
        except Exception as e:
            return False, f"加入房间时发生异常: {str(e)}"

    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = timezone.now()
        self.save(update_fields=["last_activity"])


class RoomParticipant(models.Model):
    """
    房间参与者
    """

    # 参与者状态
    STATUS_CHOICES = (
        ("waiting", "等待中"),
        ("connected", "已连接"),
        ("disconnected", "已断开"),
        ("left", "已离开"),
    )

    # 角色
    ROLE_CHOICES = (
        ("host", "房主"),
        ("participant", "参与者"),
        ("spectator", "观众"),
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name="房间",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="room_participations",
        verbose_name="用户",
    )

    # 参与信息
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="participant",
        verbose_name="角色",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="waiting",
        verbose_name="状态",
    )
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")  # type: ignore[call-arg]

    # 连接信息
    session_id = models.CharField(max_length=100, blank=True, verbose_name="会话ID")
    connection_time = models.DateTimeField(blank=True, null=True, verbose_name="连接时间")
    disconnect_time = models.DateTimeField(blank=True, null=True, verbose_name="断开时间")

    # 统计信息
    total_time = models.IntegerField(default=0, verbose_name="总参与时间(秒)")  # type: ignore[call-arg]
    rating_given = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="给出的评分",
    )
    rating_received = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="收到的评分",
    )

    # 时间戳
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "room_participants"
        verbose_name = "房间参与者"
        verbose_name_plural = "房间参与者"
        unique_together = ["room", "user"]
        indexes = [
            models.Index(fields=["room", "user"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["joined_at"]),
        ]

    def __str__(self):
        return f"{self.user.display_name} 在 {self.room.room_id}"  # type: ignore[attr-defined]

    def connect(self, session_id=None):
        """连接房间"""
        self.status = "connected"
        self.is_active = True
        self.connection_time = timezone.now()
        if session_id:
            self.session_id = session_id
        self.save()

    def disconnect(self):
        """Disconnect from room, safely handle missing connection_time."""
        self.status = "disconnected"
        self.is_active = False
        self.disconnect_time = timezone.now()
        # Calculate participation time
        if self.connection_time and self.disconnect_time:
            try:
                duration = (self.disconnect_time - self.connection_time).total_seconds()  # type: ignore[operator]
                self.total_time += int(duration)  # type: ignore[operator]
            except Exception:
                pass  # Optionally log error
        self.save()

    def leave(self):
        """离开房间"""
        self.status = "left"
        self.is_active = False
        self.save()


class RoomRating(models.Model):
    """
    房间评分
    """

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name="房间",
    )
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ratings_given",
        verbose_name="评分用户",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ratings_received",
        verbose_name="被评分用户",
    )

    # 评分信息
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="评分",
    )
    comment = models.TextField(max_length=500, blank=True, verbose_name="评价")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "room_ratings"
        verbose_name = "房间评分"
        verbose_name_plural = "房间评分"
        unique_together = ["room", "from_user", "to_user"]
        indexes = [
            models.Index(fields=["room", "from_user", "to_user"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.from_user.display_name} 给 {self.to_user.display_name} 评分 {self.rating}"  # type: ignore[attr-defined]


class RoomReport(models.Model):
    """
    房间举报
    """

    # 举报类型
    REPORT_TYPE_CHOICES = (
        ("inappropriate", "不当内容"),
        ("harassment", "骚扰行为"),
        ("spam", "垃圾信息"),
        ("fake", "虚假信息"),
        ("other", "其他"),
    )

    # 处理状态
    STATUS_CHOICES = (
        ("pending", "待处理"),
        ("investigating", "调查中"),
        ("resolved", "已处理"),
        ("dismissed", "已驳回"),
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="房间",
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports_filed",
        verbose_name="举报人",
    )
    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports_received",
        verbose_name="被举报用户",
    )

    # 举报信息
    report_type = models.CharField(
        max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name="举报类型"
    )
    description = models.TextField(max_length=1000, verbose_name="举报描述")
    evidence = models.JSONField(default=list, verbose_name="证据")

    # 处理信息
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="处理状态",
    )
    admin_notes = models.TextField(blank=True, verbose_name="管理员备注")
    handled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="处理人",
    )
    handled_at = models.DateTimeField(blank=True, null=True, verbose_name="处理时间")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="举报时间")

    class Meta:
        db_table = "room_reports"
        verbose_name = "房间举报"
        verbose_name_plural = "房间举报"
        indexes = [
            models.Index(fields=["room", "reporter", "reported_user"]),
            models.Index(fields=["report_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.reporter.display_name} 举报 {self.reported_user.display_name}"  # type: ignore[attr-defined]
