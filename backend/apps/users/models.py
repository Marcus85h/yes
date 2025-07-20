"""
用户模型
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    自定义用户模型
    """

    # 用户角色
    ROLE_CHOICES = (
        ("user", "普通用户"),
        ("host", "主播"),
        ("admin", "管理员"),
    )

    # 性别选择
    GENDER_CHOICES = (
        ("male", "男"),
        ("female", "女"),
        ("other", "其他"),
    )

    # 用户状态
    STATUS_CHOICES = (
        ("active", "正常"),
        ("inactive", "未激活"),
        ("banned", "封禁"),
        ("deleted", "已删除"),
    )

    # 基础字段
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(regex=r"^1[3-9]\d{9}$", message="请输入正确的手机号码")],
        verbose_name="手机号",
    )
    username = models.CharField(max_length=50, unique=True, verbose_name="用户名")
    email = models.EmailField(blank=True, default="", verbose_name="邮箱")

    # 用户信息
    nickname = models.CharField(max_length=50, blank=True, verbose_name="昵称")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="头像")
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name="性别"
    )
    birthday = models.DateField(blank=True, null=True, verbose_name="生日")
    bio = models.TextField(max_length=500, blank=True, verbose_name="个人简介")
    location = models.CharField(max_length=100, blank=True, verbose_name="所在地")

    # 用户角色和状态
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="user",  # type: ignore[call-arg]
        verbose_name="用户角色",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active",  # type: ignore[call-arg]
        verbose_name="用户状态",
    )

    # 认证相关
    is_verified = models.BooleanField(default=False, verbose_name="是否实名认证")  # type: ignore[call-arg]
    is_online = models.BooleanField(default=False, verbose_name="是否在线")  # type: ignore[call-arg]
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="最后登录IP")
    last_activity = models.DateTimeField(blank=True, null=True, verbose_name="最后活动时间")

    # 统计信息
    total_calls = models.IntegerField(default=0, verbose_name="总通话次数")  # type: ignore[call-arg]
    total_duration = models.IntegerField(default=0, verbose_name="总通话时长(分钟)")  # type: ignore[call-arg]
    total_earnings = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="总收益"  # type: ignore[call-arg]
    )
    total_spent = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="总消费"  # type: ignore[call-arg]
    )

    # 每日免费体验视频
    daily_free_video_date = models.DateField(blank=True, null=True, verbose_name="每日免费体验日期")
    daily_free_video_used = models.BooleanField(default=False, verbose_name="今日免费体验已用")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # 设置字段
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        verbose_name = "用户"
        verbose_name_plural = "用户"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["username"]),
            models.Index(fields=["role"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_online"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.nickname or self.username} ({self.phone})"

    @property
    def display_name(self):
        """显示名称"""
        return self.nickname or self.username

    @property
    def age(self):
        """计算年龄"""
        if self.birthday:
            today = timezone.now().date()
            return (
                today.year
                - self.birthday.year
                - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
            )
        return None

    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = timezone.now()
        self.save(update_fields=["last_activity"])

    def get_avatar_url(self):
        """获取头像URL"""
        if self.avatar:
            return self.avatar.url
        return None


class UserProfile(models.Model):
    """
    用户详细资料
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="用户",
    )

    # 基本信息
    height = models.IntegerField(blank=True, null=True, verbose_name="身高(cm)")
    weight = models.IntegerField(blank=True, null=True, verbose_name="体重(kg)")
    education = models.CharField(max_length=50, blank=True, verbose_name="学历")
    occupation = models.CharField(max_length=100, blank=True, verbose_name="职业")
    income = models.CharField(max_length=50, blank=True, verbose_name="收入水平")

    # 兴趣爱好
    hobbies = models.JSONField(default=list, verbose_name="兴趣爱好")
    languages = models.JSONField(default=list, verbose_name="语言能力")

    # 社交信息
    wechat = models.CharField(max_length=50, blank=True, verbose_name="微信号")
    qq = models.CharField(max_length=20, blank=True, verbose_name="QQ号")

    # 认证信息
    real_name = models.CharField(max_length=50, blank=True, verbose_name="真实姓名")
    id_card = models.CharField(max_length=18, blank=True, verbose_name="身份证号")
    id_card_front = models.ImageField(
        upload_to="id_cards/", blank=True, null=True, verbose_name="身份证正面"
    )
    id_card_back = models.ImageField(
        upload_to="id_cards/", blank=True, null=True, verbose_name="身份证背面"
    )

    # 主播信息
    is_host = models.BooleanField(default=False, verbose_name="是否主播")  # type: ignore[call-arg]
    host_level = models.IntegerField(default=1, verbose_name="主播等级")  # type: ignore[call-arg]
    host_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.0,  # type: ignore[call-arg]
        verbose_name="主播评分",
    )
    host_tags = models.JSONField(default=list, verbose_name="主播标签")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "user_profiles"
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

    def __str__(self):
        return f"{self.user.display_name}的资料"


class UserVerification(models.Model):
    """
    用户实名认证
    """

    VERIFICATION_STATUS = (
        ("pending", "待审核"),
        ("approved", "已通过"),
        ("rejected", "已拒绝"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="verification",
        verbose_name="用户",
    )
    real_name = models.CharField(max_length=50, verbose_name="真实姓名")
    id_card = models.CharField(max_length=18, verbose_name="身份证号")
    id_card_front = models.ImageField(upload_to="verifications/", verbose_name="身份证正面")
    id_card_back = models.ImageField(upload_to="verifications/", verbose_name="身份证背面")
    selfie = models.ImageField(upload_to="verifications/", verbose_name="自拍照")

    status = models.CharField(
        max_length=10,
        choices=VERIFICATION_STATUS,
        default="pending",  # type: ignore[call-arg]
        verbose_name="审核状态",
    )
    admin_notes = models.TextField(blank=True, verbose_name="管理员备注")

    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name="审核时间")
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="审核人",
    )

    class Meta:
        db_table = "user_verifications"
        verbose_name = "用户认证"
        verbose_name_plural = "用户认证"

    def __str__(self):
        return f"{self.user.display_name}的认证申请"


class UserDevice(models.Model):
    """
    用户设备信息
    """

    DEVICE_TYPE_CHOICES = (
        ("android", "Android"),
        ("ios", "iOS"),
        ("web", "Web"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name="用户",
    )
    device_id = models.CharField(max_length=100, verbose_name="设备ID")
    device_type = models.CharField(
        max_length=10, choices=DEVICE_TYPE_CHOICES, verbose_name="设备类型"
    )
    device_name = models.CharField(max_length=100, blank=True, verbose_name="设备名称")
    device_model = models.CharField(max_length=100, blank=True, verbose_name="设备型号")
    os_version = models.CharField(max_length=50, blank=True, verbose_name="系统版本")
    app_version = models.CharField(max_length=20, blank=True, verbose_name="应用版本")

    fcm_token = models.CharField(max_length=255, blank=True, verbose_name="FCM推送令牌")
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")  # type: ignore[call-arg]

    last_login = models.DateTimeField(auto_now_add=True, verbose_name="最后登录时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "user_devices"
        verbose_name = "用户设备"
        verbose_name_plural = "用户设备"
        unique_together = ["user", "device_id"]

    def __str__(self):
        return f"{self.user.display_name}的{self.device_type}设备"
