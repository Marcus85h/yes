from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class User(AbstractUser):
    """用户表"""
    
    ROLE_CHOICES = [
        ('user', '普通用户'),
        ('host', '主播'),
        ('admin', '管理员'),
        ('moderator', '版主'),
    ]
    
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    
    # 基本信息
    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    avatar = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 扩展字段
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return f"{self.username} ({self.id})"


class Room(models.Model):
    """房间表"""
    
    ROOM_STATUS_CHOICES = [
        ('waiting', '等待中'),
        ('active', '通话中'),
        ('ended', '已结束'),
        ('cancelled', '已取消'),
    ]
    
    id = models.AutoField(primary_key=True)
    host_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 扩展字段
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    max_participants = models.IntegerField(default=2)
    
    class Meta:
        db_table = 'rooms'
        verbose_name = '房间'
        verbose_name_plural = '房间'
    
    def __str__(self):
        return f"房间 {self.id} - {self.host_id.username}"


class CallSession(models.Model):
    """通话会话表"""
    
    QUALITY_CHOICES = [
        ('low', '低质量'),
        ('medium', '中等质量'),
        ('high', '高质量'),
        ('hd', '高清'),
    ]
    
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='call_sessions')
    caller_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='call_sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)  # 通话时长（秒）
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='medium')
    
    # 扩展字段
    is_active = models.BooleanField(default=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        db_table = 'call_sessions'
        verbose_name = '通话会话'
        verbose_name_plural = '通话会话'
    
    def __str__(self):
        return f"通话 {self.id} - {self.caller_id.username}"
    
    def end_call(self):
        """结束通话"""
        if self.is_active:
            self.end_time = timezone.now()
            self.is_active = False
            
            # 计算通话时长
            if self.start_time:
                duration = (self.end_time - self.start_time).total_seconds()
                self.duration = int(duration)
            
            self.save(update_fields=['end_time', 'is_active', 'duration'])


class Gift(models.Model):
    """礼物表"""
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()  # 价格（分）
    icon = models.URLField(max_length=500)
    animation_url = models.URLField(max_length=500, null=True, blank=True)
    
    # 扩展字段
    description = models.TextField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'gift'
        verbose_name = '礼物'
        verbose_name_plural = '礼物'
    
    def __str__(self):
        return f"{self.name} ({self.price}分)"


class GiftTransaction(models.Model):
    """礼物交易表"""
    
    id = models.AutoField(primary_key=True)
    gift_id = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name='transactions')
    session_id = models.ForeignKey(CallSession, on_delete=models.CASCADE, related_name='gift_transactions')
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_gifts')
    price_at_time = models.IntegerField()  # 当时价格（分）
    
    # 扩展字段
    quantity = models.IntegerField(default=1)
    total_amount = models.IntegerField()  # 总金额（分）
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'gift_transactions'
        verbose_name = '礼物交易'
        verbose_name_plural = '礼物交易'
    
    def __str__(self):
        return f"礼物交易 {self.id} - {self.sender_id.username} -> {self.gift_id.name}"


class BillingRecord(models.Model):
    """计费记录表"""
    
    id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey(CallSession, on_delete=models.CASCADE, related_name='billing_records')
    amount_charged = models.IntegerField()  # 计费金额（分）
    billed_at = models.DateTimeField()
    
    # 扩展字段
    billing_type = models.CharField(max_length=20, default='per_minute')  # 计费类型
    rate_per_minute = models.IntegerField(default=100)  # 每分钟费率（分）
    
    class Meta:
        db_table = 'billing_records'
        verbose_name = '计费记录'
        verbose_name_plural = '计费记录'
    
    def __str__(self):
        return f"计费记录 {self.id} - {self.amount_charged}分"


class UserBehaviorLog(models.Model):
    """用户行为日志表"""
    
    ACTION_TYPE_CHOICES = [
        ('login_fail', '登录失败'),
        ('screen_record_attempt', '录屏尝试'),
        ('api_abuse', 'API滥用'),
        ('suspicious_activity', '可疑活动'),
        ('login_success', '登录成功'),
        ('logout', '登出'),
        ('call_start', '开始通话'),
        ('call_end', '结束通话'),
        ('gift_sent', '发送礼物'),
    ]
    
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavior_logs')
    ip = models.GenericIPAddressField()
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 扩展字段
    details = models.JSONField(default=dict, blank=True)
    severity = models.CharField(max_length=20, default='info')  # info, warning, error
    
    class Meta:
        db_table = 'user_behavior_logs'
        verbose_name = '用户行为日志'
        verbose_name_plural = '用户行为日志'
    
    def __str__(self):
        return f"行为日志 {self.id} - {self.user_id.username} - {self.action_type}"


class UserBlacklist(models.Model):
    """用户黑名单表"""
    
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklist_records')
    reason = models.TextField()
    banned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # 扩展字段
    banned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='banned_users')
    duration = models.IntegerField(null=True, blank=True)  # 封禁时长（小时），null表示永久
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_blacklist'
        verbose_name = '用户黑名单'
        verbose_name_plural = '用户黑名单'
    
    def __str__(self):
        return f"黑名单 {self.id} - {self.user_id.username}"
    
    def is_expired(self):
        """检查是否过期"""
        if not self.is_active:
            return True
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False


class Recharge(models.Model):
    """充值记录表"""
    
    METHOD_CHOICES = [
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('bank_card', '银行卡'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ]
    
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recharges')
    amount = models.IntegerField()  # 充值金额（分）
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    recharged_at = models.DateTimeField(auto_now_add=True)
    
    # 扩展字段
    status = models.CharField(max_length=20, default='pending')  # pending, completed, failed
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = 'recharges'
        verbose_name = '充值记录'
        verbose_name_plural = '充值记录'
    
    def __str__(self):
        return f"充值 {self.id} - {self.user_id.username} - {self.amount}分"


class Message(models.Model):
    """消息表"""
    
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # 扩展字段
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=20, default='text')  # text, image, audio, video
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'messages'
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['sent_at']
    
    def __str__(self):
        return f"消息 {self.id} - {self.sender.username}"


# 设置自定义用户模型
AUTH_USER_MODEL = 'User' 