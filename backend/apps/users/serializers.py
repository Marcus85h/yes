"""
用户序列化器
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User, UserDevice, UserProfile, UserVerification


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    verification_code = serializers.CharField(write_only=True, max_length=6)

    class Meta:
        model = User
        fields = [
            "phone",
            "username",
            "password",
            "password_confirm",
            "verification_code",
            "nickname",
            "gender",
        ]
        extra_kwargs = {
            "phone": {"required": True},
            "username": {"required": True},
            "nickname": {"required": False},
            "gender": {"required": False},
        }

    def validate(self, attrs):
        # 验证密码确认
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("两次输入的密码不一致")

        # 验证手机号是否已存在
        if User.objects.filter(phone=attrs["phone"]).exists():
            raise serializers.ValidationError("该手机号已被注册")

        # 验证用户名是否已存在
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError("该用户名已被使用")

        # 验证验证码
        from .services import SMSService

        if not SMSService.verify_code(attrs["phone"], attrs["verification_code"]):
            raise serializers.ValidationError("验证码错误或已过期")

        return attrs

    def create(self, validated_data):
        # 移除不需要的字段
        validated_data.pop("password_confirm")
        validated_data.pop("verification_code")

        # 创建用户
        user = User.objects.create_user(**validated_data)

        # 创建用户资料
        UserProfile.objects.create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    """

    phone = serializers.CharField(max_length=11)
    password = serializers.CharField(max_length=128, write_only=True)
    device_id = serializers.CharField(max_length=100, required=False)
    device_type = serializers.ChoiceField(choices=UserDevice.DEVICE_TYPE_CHOICES, required=False)
    fcm_token = serializers.CharField(max_length=255, required=False)

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")

        if phone and password:
            user = authenticate(phone=phone, password=password)
            if not user:
                raise serializers.ValidationError("手机号或密码错误")
            if not user.is_active:
                raise serializers.ValidationError("账户已被禁用")

            attrs["user"] = user
        else:
            raise serializers.ValidationError("请提供手机号和密码")

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户资料序列化器
    """

    user_id = serializers.UUIDField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    avatar = serializers.CharField(source="user.get_avatar_url", read_only=True)
    gender = serializers.CharField(source="user.gender", read_only=True)
    birthday = serializers.DateField(source="user.birthday", read_only=True)
    bio = serializers.CharField(source="user.bio", read_only=True)
    location = serializers.CharField(source="user.location", read_only=True)
    is_verified = serializers.BooleanField(source="user.is_verified", read_only=True)
    is_online = serializers.BooleanField(source="user.is_online", read_only=True)
    total_calls = serializers.IntegerField(source="user.total_calls", read_only=True)
    total_duration = serializers.IntegerField(source="user.total_duration", read_only=True)
    total_earnings = serializers.DecimalField(
        source="user.total_earnings",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    total_spent = serializers.DecimalField(
        source="user.total_spent",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "user_id",
            "username",
            "phone",
            "nickname",
            "avatar",
            "gender",
            "birthday",
            "bio",
            "location",
            "is_verified",
            "is_online",
            "total_calls",
            "total_duration",
            "total_earnings",
            "total_spent",
            "height",
            "weight",
            "education",
            "occupation",
            "income",
            "hobbies",
            "languages",
            "wechat",
            "qq",
            "is_host",
            "host_level",
            "host_score",
            "host_tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户信息更新序列化器
    """

    class Meta:
        model = User
        fields = [
            "nickname",
            "avatar",
            "gender",
            "birthday",
            "bio",
            "location",
        ]

    def validate_username(self, value):
        # 检查用户名是否已被其他用户使用
        user = self.context["request"].user
        if User.objects.exclude(id=user.id).filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被使用")
        return value


class UserVerificationSerializer(serializers.ModelSerializer):
    """
    用户认证序列化器
    """

    class Meta:
        model = UserVerification
        fields = [
            "real_name",
            "id_card",
            "id_card_front",
            "id_card_back",
            "selfie",
        ]

    def validate_id_card(self, value):
        # 验证身份证号格式
        if len(value) != 18:
            raise serializers.ValidationError("身份证号必须是18位")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        # 检查是否已有认证申请
        if UserVerification.objects.filter(user=user).exists():
            raise serializers.ValidationError("您已有认证申请，请勿重复提交")

        validated_data["user"] = user
        return super().create(validated_data)


class UserDeviceSerializer(serializers.ModelSerializer):
    """
    用户设备序列化器
    """

    class Meta:
        model = UserDevice
        fields = [
            "device_id",
            "device_type",
            "device_name",
            "device_model",
            "os_version",
            "app_version",
            "fcm_token",
            "is_active",
            "last_login",
            "created_at",
        ]
        read_only_fields = ["last_login", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        device_id = validated_data["device_id"]

        # 更新或创建设备记录
        device, created = UserDevice.objects.update_or_create(
            user=user, device_id=device_id, defaults=validated_data
        )

        return device


class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表序列化器
    """

    avatar = serializers.CharField(source="get_avatar_url", read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "avatar",
            "gender",
            "age",
            "location",
            "is_online",
            "is_verified",
            "role",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class PasswordChangeSerializer(serializers.Serializer):
    """
    密码修改序列化器
    """

    old_password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(
        max_length=128, write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("两次输入的新密码不一致")
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("原密码错误")
        return value


class PhoneVerificationSerializer(serializers.Serializer):
    """
    手机验证序列化器
    """

    phone = serializers.CharField(max_length=11)
    verification_code = serializers.CharField(max_length=6)

    def validate_phone(self, value):
        # 验证手机号格式
        import re

        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("请输入正确的手机号码")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """
    重置密码序列化器
    """

    phone = serializers.CharField(max_length=11)
    verification_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(
        max_length=128, write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("两次输入的新密码不一致")
        return attrs
