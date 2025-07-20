import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ScreenRecordingDetection(models.Model):
    """
    录屏检测记录
    """

    DETECTION_TYPE_CHOICES = [
        ("screenshot", "截图检测"),
        ("screen_recording", "录屏检测"),
        ("mirroring", "投屏检测"),
        ("virtual_display", "虚拟显示器检测"),
        ("recording_app", "录屏应用检测"),
    ]

    SEVERITY_CHOICES = [
        ("low", "低风险"),
        ("medium", "中风险"),
        ("high", "高风险"),
        ("critical", "严重风险"),
    ]

    id = models.AutoField(primary_key=True)
    detection_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="screen_detections"
    )
    detection_type = models.CharField(max_length=20, choices=DETECTION_TYPE_CHOICES)
    severity = models.CharField(
        max_length=10, choices=SEVERITY_CHOICES, default="medium"
    )  # type: ignore[call-arg]
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.JSONField(default=dict, blank=True)  # type: ignore[call-arg]
    detection_details = models.JSONField(default=dict, blank=True)  # type: ignore[call-arg]
    is_confirmed = models.BooleanField(default=False)  # type: ignore[call-arg]
    is_false_positive = models.BooleanField(default=False)  # type: ignore[call-arg]
    action_taken = models.CharField(max_length=50, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "screen_recording_detections"
        verbose_name = "录屏检测记录"
        verbose_name_plural = "录屏检测记录"
        ordering = ["-created_at"]

    def __str__(self):
        return f"录屏检测 {self.detection_id} - {self.user.username} - {self.detection_type}"  # type: ignore[attr-defined]


class SecurityPolicy(models.Model):
    """
    安全策略配置
    """

    POLICY_TYPE_CHOICES = [
        ("screen_recording", "录屏防护"),
        ("screenshot", "截图防护"),
        ("virtual_machine", "虚拟机检测"),
        ("debugger", "调试器检测"),
        ("root_jailbreak", "越狱检测"),
    ]

    id = models.AutoField(primary_key=True)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPE_CHOICES, unique=True)
    is_enabled = models.BooleanField(default=True)  # type: ignore[call-arg]
    detection_threshold = models.IntegerField(default=3)  # type: ignore[call-arg]
    action_on_detection = models.CharField(max_length=50, default="warn")  # type: ignore[call-arg]
    cooldown_period = models.IntegerField(default=300)  # type: ignore[call-arg]
    notification_enabled = models.BooleanField(default=True)  # type: ignore[call-arg]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "security_policies"
        verbose_name = "安全策略"
        verbose_name_plural = "安全策略"

    def __str__(self):
        return f"安全策略 {self.policy_type}"


class SecurityAlert(models.Model):
    """
    安全警报
    """

    ALERT_TYPE_CHOICES = [
        ("screen_recording", "录屏警报"),
        ("suspicious_activity", "可疑活动"),
        ("multiple_violations", "多次违规"),
        ("account_compromise", "账户泄露"),
    ]

    PRIORITY_CHOICES = [
        ("low", "低优先级"),
        ("medium", "中优先级"),
        ("high", "高优先级"),
        ("urgent", "紧急"),
    ]

    id = models.AutoField(primary_key=True)
    alert_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="security_alerts"
    )
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )  # type: ignore[call-arg]
    title = models.CharField(max_length=200)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)  # type: ignore[call-arg]
    is_read = models.BooleanField(default=False)  # type: ignore[call-arg]
    is_resolved = models.BooleanField(default=False)  # type: ignore[call-arg]
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "security_alerts"
        verbose_name = "安全警报"
        verbose_name_plural = "安全警报"
        ordering = ["-created_at"]

    def __str__(self):
        return f"安全警报 {self.alert_id} - {self.user.username} - {self.alert_type}"  # type: ignore[attr-defined]

    def mark_as_resolved(self, resolved_by_user=None):
        """标记为已解决"""
        self.is_resolved = True
        self.resolved_by = resolved_by_user
        self.resolved_at = timezone.now()
        self.save()
