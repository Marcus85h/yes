"""
通话系统模型
"""

import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Call(models.Model):
    """通话模型"""

    CALL_TYPES = [
        ("audio", "语音通话"),
        ("video", "视频通话"),
        ("group", "群组通话"),
        ("live", "直播"),
        ("webinar", "网络研讨会"),
    ]

    CALL_STATUS = [
        ("initiating", "发起中"),
        ("ringing", "响铃中"),
        ("connected", "已连接"),
        ("ended", "已结束"),
        ("missed", "未接通"),
        ("rejected", "已拒绝"),
        ("busy", "忙线中"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call_type = models.CharField(max_length=20, choices=CALL_TYPES, verbose_name="通话类型")
    status = models.CharField(
        max_length=20,
        choices=CALL_STATUS,
        default="initiating",
        verbose_name="通话状态",
    )
    initiator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="initiated_calls",
        verbose_name="发起者",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_calls",
        null=True,
        blank=True,
        verbose_name="接收者",
    )
    room_id = models.CharField(max_length=100, unique=True, verbose_name="房间ID")
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name="通话标题")
    description = models.TextField(null=True, blank=True, verbose_name="通话描述")
    start_time = models.DateTimeField(default=timezone.now, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    duration = models.IntegerField(default=0, verbose_name="通话时长(秒)")
    max_participants = models.IntegerField(default=2, verbose_name="最大参与者数")
    is_recording = models.BooleanField(default=False, verbose_name="是否录制")
    recording_url = models.URLField(null=True, blank=True, verbose_name="录制文件URL")
    is_screen_sharing = models.BooleanField(default=False, verbose_name="是否屏幕共享")
    screen_sharer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="screen_shares",
        verbose_name="屏幕共享者",
    )
    quality_metrics = models.JSONField(default=dict, verbose_name="质量指标")
    metadata = models.JSONField(default=dict, verbose_name="元数据")

    class Meta:
        db_table = "calls"
        verbose_name = "通话"
        verbose_name_plural = "通话"
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["call_type", "status"]),
            models.Index(fields=["initiator", "start_time"]),
            models.Index(fields=["room_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.call_type} call {self.id} ({self.status})"

    def calculate_duration(self):
        """计算通话时长"""
        if self.end_time:
            self.duration = int((self.end_time - self.start_time).total_seconds())
        else:
            self.duration = int((timezone.now() - self.start_time).total_seconds())
        self.save(update_fields=["duration"])

    @property
    def is_group_call(self):
        """是否为群组通话"""
        return self.call_type in ["group", "live", "webinar"]

    @property
    def is_active(self):
        """是否活跃"""
        return self.status in ["initiating", "ringing", "connected"]


class CallParticipant(models.Model):
    """通话参与者模型"""

    PARTICIPANT_ROLES = [
        ("host", "主持人"),
        ("co_host", "联席主持人"),
        ("participant", "参与者"),
        ("viewer", "观众"),
    ]

    PARTICIPANT_STATUS = [
        ("joining", "加入中"),
        ("connected", "已连接"),
        ("disconnected", "已断开"),
        ("muted", "已静音"),
        ("video_off", "视频关闭"),
        ("speaking", "正在说话"),
    ]

    call = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name="通话",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    role = models.CharField(
        max_length=20,
        choices=PARTICIPANT_ROLES,
        default="participant",
        verbose_name="角色",
    )
    status = models.CharField(
        max_length=20,
        choices=PARTICIPANT_STATUS,
        default="joining",
        verbose_name="状态",
    )
    joined_at = models.DateTimeField(default=timezone.now, verbose_name="加入时间")
    left_at = models.DateTimeField(null=True, blank=True, verbose_name="离开时间")
    duration = models.IntegerField(default=0, verbose_name="参与时长(秒)")
    is_muted = models.BooleanField(default=False, verbose_name="是否静音")
    is_video_enabled = models.BooleanField(default=True, verbose_name="是否开启视频")
    is_screen_sharing = models.BooleanField(default=False, verbose_name="是否屏幕共享")
    network_quality = models.FloatField(default=0.0, verbose_name="网络质量")
    audio_level = models.FloatField(default=0.0, verbose_name="音频电平")
    video_quality = models.JSONField(default=dict, verbose_name="视频质量")
    metadata = models.JSONField(default=dict, verbose_name="元数据")

    class Meta:
        db_table = "call_participants"
        verbose_name = "通话参与者"
        verbose_name_plural = "通话参与者"
        ordering = ["-joined_at"]
        unique_together = ["call", "user"]
        indexes = [
            models.Index(fields=["call", "status"]),
            models.Index(fields=["user", "joined_at"]),
            models.Index(fields=["role", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} in {self.call.id} ({self.role})"

    def calculate_duration(self):
        """计算参与时长"""
        if self.left_at:
            self.duration = int((self.left_at - self.joined_at).total_seconds())
        else:
            self.duration = int((timezone.now() - self.joined_at).total_seconds())
        self.save(update_fields=["duration"])


class CallInvitation(models.Model):
    """通话邀请模型"""

    INVITATION_STATUS = [
        ("pending", "待处理"),
        ("accepted", "已接受"),
        ("declined", "已拒绝"),
        ("expired", "已过期"),
    ]

    call = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="通话",
    )
    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
        verbose_name="邀请者",
    )
    invitee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_invitations",
        verbose_name="被邀请者",
    )
    status = models.CharField(
        max_length=20,
        choices=INVITATION_STATUS,
        default="pending",
        verbose_name="状态",
    )
    sent_at = models.DateTimeField(default=timezone.now, verbose_name="发送时间")
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name="响应时间")
    message = models.TextField(null=True, blank=True, verbose_name="邀请消息")
    expires_at = models.DateTimeField(verbose_name="过期时间")

    class Meta:
        db_table = "call_invitations"
        verbose_name = "通话邀请"
        verbose_name_plural = "通话邀请"
        ordering = ["-sent_at"]
        unique_together = ["call", "invitee"]
        indexes = [
            models.Index(fields=["invitee", "status"]),
            models.Index(fields=["call", "status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Invitation from {self.inviter.username} to {self.invitee.username}"

    @property
    def is_expired(self):
        """是否已过期"""
        return timezone.now() > self.expires_at


class CallRecording(models.Model):
    """通话录制模型"""

    call = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name="recordings",
        verbose_name="通话",
    )
    file_path = models.CharField(max_length=500, verbose_name="文件路径")
    file_url = models.URLField(null=True, blank=True, verbose_name="文件URL")
    file_size = models.BigIntegerField(default=0, verbose_name="文件大小(字节)")
    duration = models.IntegerField(default=0, verbose_name="录制时长(秒)")
    format = models.CharField(max_length=20, default="mp4", verbose_name="文件格式")
    quality = models.CharField(max_length=20, default="medium", verbose_name="录制质量")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    is_processed = models.BooleanField(default=False, verbose_name="是否已处理")
    metadata = models.JSONField(default=dict, verbose_name="元数据")

    class Meta:
        db_table = "call_recordings"
        verbose_name = "通话录制"
        verbose_name_plural = "通话录制"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["call", "created_at"]),
            models.Index(fields=["is_processed"]),
        ]

    def __str__(self):
        return f"Recording for {self.call.id} ({self.duration}s)"


class CallQualityLog(models.Model):
    """通话质量日志模型"""

    call = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name="quality_logs",
        verbose_name="通话",
    )
    participant = models.ForeignKey(
        CallParticipant,
        on_delete=models.CASCADE,
        related_name="quality_logs",
        verbose_name="参与者",
    )
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="时间戳")
    audio_quality = models.FloatField(default=0.0, verbose_name="音频质量")
    video_quality = models.FloatField(default=0.0, verbose_name="视频质量")
    network_quality = models.FloatField(default=0.0, verbose_name="网络质量")
    packet_loss = models.FloatField(default=0.0, verbose_name="丢包率")
    latency = models.FloatField(default=0.0, verbose_name="延迟")
    jitter = models.FloatField(default=0.0, verbose_name="抖动")
    bandwidth = models.FloatField(default=0.0, verbose_name="带宽")
    cpu_usage = models.FloatField(default=0.0, verbose_name="CPU使用率")
    memory_usage = models.FloatField(default=0.0, verbose_name="内存使用率")
    battery_level = models.FloatField(default=0.0, verbose_name="电池电量")

    class Meta:
        db_table = "call_quality_logs"
        verbose_name = "通话质量日志"
        verbose_name_plural = "通话质量日志"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["call", "timestamp"]),
            models.Index(fields=["participant", "timestamp"]),
        ]

    def __str__(self):
        return f"Quality log for {self.participant.user.username} at {self.timestamp}"


class CallEvent(models.Model):
    """通话事件模型"""

    EVENT_TYPES = [
        ("call_started", "通话开始"),
        ("call_ended", "通话结束"),
        ("participant_joined", "参与者加入"),
        ("participant_left", "参与者离开"),
        ("participant_muted", "参与者静音"),
        ("participant_unmuted", "参与者取消静音"),
        ("video_enabled", "开启视频"),
        ("video_disabled", "关闭视频"),
        ("screen_share_started", "开始屏幕共享"),
        ("screen_share_stopped", "停止屏幕共享"),
        ("recording_started", "开始录制"),
        ("recording_stopped", "停止录制"),
        ("quality_issue", "质量问题"),
        ("network_issue", "网络问题"),
    ]

    call = models.ForeignKey(
        Call,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="通话",
    )
    participant = models.ForeignKey(
        CallParticipant,
        on_delete=models.CASCADE,
        related_name="events",
        null=True,
        blank=True,
        verbose_name="参与者",
    )
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="事件类型")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="时间戳")
    description = models.TextField(null=True, blank=True, verbose_name="事件描述")
    metadata = models.JSONField(default=dict, verbose_name="元数据")

    class Meta:
        db_table = "call_events"
        verbose_name = "通话事件"
        verbose_name_plural = "通话事件"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["call", "event_type"]),
            models.Index(fields=["participant", "timestamp"]),
            models.Index(fields=["event_type", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.event_type} in {self.call.id} at {self.timestamp}"
