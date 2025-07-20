import json

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class AnalyticsEvent(models.Model):
    """分析事件模型"""

    EVENT_TYPES = [
        ("app_launch", "应用启动"),
        ("app_close", "应用关闭"),
        ("user_login", "用户登录"),
        ("user_logout", "用户登出"),
        ("user_register", "用户注册"),
        ("profile_update", "资料更新"),
        ("chat_start", "开始聊天"),
        ("chat_message_sent", "发送消息"),
        ("chat_message_received", "接收消息"),
        ("chat_file_shared", "分享文件"),
        ("chat_emoji_used", "使用表情"),
        ("call_initiated", "发起通话"),
        ("call_answered", "接听通话"),
        ("call_ended", "结束通话"),
        ("call_missed", "未接通话"),
        ("call_duration", "通话时长"),
        ("call_quality", "通话质量"),
        ("payment_initiated", "发起支付"),
        ("payment_completed", "支付完成"),
        ("payment_failed", "支付失败"),
        ("subscription_started", "订阅开始"),
        ("subscription_cancelled", "订阅取消"),
        ("content_viewed", "查看内容"),
        ("content_liked", "点赞内容"),
        ("content_shared", "分享内容"),
        ("content_reported", "举报内容"),
        ("performance_issue", "性能问题"),
        ("error_occurred", "发生错误"),
        ("crash_occurred", "应用崩溃"),
        ("feature_used", "使用功能"),
        ("setting_changed", "设置变更"),
        ("notification_received", "接收通知"),
        ("notification_clicked", "点击通知"),
    ]

    PRIORITY_LEVELS = [
        ("low", "低"),
        ("normal", "普通"),
        ("high", "高"),
        ("critical", "严重"),
    ]

    event_id = models.CharField(max_length=100, unique=True, verbose_name="事件ID")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="事件类型")
    name = models.CharField(max_length=200, verbose_name="事件名称")
    properties = models.JSONField(default=dict, verbose_name="事件属性")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="时间戳")
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default="normal",
        verbose_name="优先级",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="用户",
    )
    session_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="会话ID")
    device_info = models.JSONField(default=dict, verbose_name="设备信息")
    app_info = models.JSONField(default=dict, verbose_name="应用信息")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    user_agent = models.TextField(null=True, blank=True, verbose_name="用户代理")

    class Meta:
        db_table = "analytics_events"
        verbose_name = "分析事件"
        verbose_name_plural = "分析事件"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["event_type", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["session_id", "timestamp"]),
            models.Index(fields=["priority", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.event_type}: {self.name} ({self.timestamp})"

    @property
    def formatted_properties(self):
        """格式化属性为可读字符串"""
        return json.dumps(self.properties, ensure_ascii=False, indent=2)


class UserSession(models.Model):
    """用户会话模型"""

    session_id = models.CharField(max_length=100, unique=True, verbose_name="会话ID")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="用户",
    )
    start_time = models.DateTimeField(default=timezone.now, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    duration = models.IntegerField(default=0, verbose_name="持续时间(秒)")
    device_info = models.JSONField(default=dict, verbose_name="设备信息")
    app_info = models.JSONField(default=dict, verbose_name="应用信息")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    user_agent = models.TextField(null=True, blank=True, verbose_name="用户代理")
    events_count = models.IntegerField(default=0, verbose_name="事件数量")
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")

    class Meta:
        db_table = "analytics_sessions"
        verbose_name = "用户会话"
        verbose_name_plural = "用户会话"
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["user", "start_time"]),
            models.Index(fields=["session_id"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"Session {self.session_id} ({self.user.username if self.user else 'Anonymous'})"

    def calculate_duration(self):
        """计算会话持续时间"""
        if self.end_time:
            self.duration = int((self.end_time - self.start_time).total_seconds())
        else:
            self.duration = int((timezone.now() - self.start_time).total_seconds())
        self.save(update_fields=["duration"])


class PerformanceMetrics(models.Model):
    """性能指标模型"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="用户",
    )
    session_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="会话ID")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="时间戳")
    cpu_usage = models.FloatField(default=0.0, verbose_name="CPU使用率")
    memory_usage = models.FloatField(default=0.0, verbose_name="内存使用率")
    battery_level = models.FloatField(default=0.0, verbose_name="电池电量")
    network_latency = models.FloatField(default=0.0, verbose_name="网络延迟")
    frame_rate = models.FloatField(default=0.0, verbose_name="帧率")
    error_count = models.IntegerField(default=0, verbose_name="错误数量")
    device_info = models.JSONField(default=dict, verbose_name="设备信息")
    app_version = models.CharField(max_length=50, null=True, blank=True, verbose_name="应用版本")

    class Meta:
        db_table = "performance_metrics"
        verbose_name = "性能指标"
        verbose_name_plural = "性能指标"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["session_id", "timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"Performance {self.user.username if self.user else 'Anonymous'} - {self.timestamp}"


class UserBehavior(models.Model):
    """用户行为模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    date = models.DateField(default=timezone.now, verbose_name="日期")
    session_count = models.IntegerField(default=0, verbose_name="会话次数")
    total_duration = models.IntegerField(default=0, verbose_name="总时长(秒)")
    events_count = models.IntegerField(default=0, verbose_name="事件数量")
    feature_usage = models.JSONField(default=dict, verbose_name="功能使用情况")
    error_count = models.IntegerField(default=0, verbose_name="错误数量")
    call_count = models.IntegerField(default=0, verbose_name="通话次数")
    call_duration = models.IntegerField(default=0, verbose_name="通话时长(秒)")
    message_count = models.IntegerField(default=0, verbose_name="消息数量")
    payment_count = models.IntegerField(default=0, verbose_name="支付次数")
    payment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="支付金额"
    )

    class Meta:
        db_table = "user_behaviors"
        verbose_name = "用户行为"
        verbose_name_plural = "用户行为"
        ordering = ["-date"]
        unique_together = ["user", "date"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class AnalyticsSummary(models.Model):
    """分析汇总模型"""

    date = models.DateField(unique=True, verbose_name="日期")
    total_users = models.IntegerField(default=0, verbose_name="总用户数")
    active_users = models.IntegerField(default=0, verbose_name="活跃用户数")
    new_users = models.IntegerField(default=0, verbose_name="新用户数")
    total_sessions = models.IntegerField(default=0, verbose_name="总会话数")
    total_events = models.IntegerField(default=0, verbose_name="总事件数")
    total_calls = models.IntegerField(default=0, verbose_name="总通话数")
    total_messages = models.IntegerField(default=0, verbose_name="总消息数")
    total_payments = models.IntegerField(default=0, verbose_name="总支付数")
    total_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="总收入"
    )
    error_count = models.IntegerField(default=0, verbose_name="错误数量")
    avg_session_duration = models.FloatField(default=0.0, verbose_name="平均会话时长")
    avg_cpu_usage = models.FloatField(default=0.0, verbose_name="平均CPU使用率")
    avg_memory_usage = models.FloatField(default=0.0, verbose_name="平均内存使用率")
    avg_frame_rate = models.FloatField(default=0.0, verbose_name="平均帧率")

    class Meta:
        db_table = "analytics_summaries"
        verbose_name = "分析汇总"
        verbose_name_plural = "分析汇总"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"Summary - {self.date}"


class SystemAlert(models.Model):
    """系统警报模型"""

    ALERT_LEVELS = [
        ("info", "信息"),
        ("warning", "警告"),
        ("critical", "严重"),
    ]

    ALERT_TYPES = [
        ("performance", "性能问题"),
        ("security", "安全问题"),
        ("error", "错误"),
        ("user_behavior", "用户行为"),
        ("system", "系统"),
    ]

    title = models.CharField(max_length=200, verbose_name="标题")
    message = models.TextField(verbose_name="消息")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name="警报类型")
    level = models.CharField(max_length=20, choices=ALERT_LEVELS, verbose_name="警报级别")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="时间戳")
    is_resolved = models.BooleanField(default=False, verbose_name="是否已解决")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="解决时间")
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="解决人",
    )
    metadata = models.JSONField(default=dict, verbose_name="元数据")

    class Meta:
        db_table = "system_alerts"
        verbose_name = "系统警报"
        verbose_name_plural = "系统警报"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["alert_type", "level"]),
            models.Index(fields=["is_resolved"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.alert_type}: {self.title} ({self.level})"

    def resolve(self, resolved_by=None):
        """解决警报"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        if resolved_by:
            self.resolved_by = resolved_by
        self.save()
