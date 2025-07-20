"""
用户视图
"""

from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date

from .models import User, UserDevice, UserProfile, UserVerification
from .serializers import (
    PasswordChangeSerializer,
    PhoneVerificationSerializer,
    ResetPasswordSerializer,
    UserDeviceSerializer,
    UserListSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    UserVerificationSerializer,
)


class UserRegistrationView(APIView):
    """
    用户注册视图
    """

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response("注册成功", UserRegistrationSerializer),
            400: "注册失败",
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "注册成功",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "phone": user.phone,
                        "nickname": user.nickname,
                    },
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    用户登录视图
    """

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={200: openapi.Response("登录成功"), 400: "登录失败"},
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # 更新用户状态
            user.is_online = True
            user.last_login_ip = self.get_client_ip(request)
            user.last_activity = timezone.now()
            user.save()

            # 处理设备信息
            device_data = {
                "device_id": serializer.validated_data.get("device_id"),
                "device_type": serializer.validated_data.get("device_type"),
                "fcm_token": serializer.validated_data.get("fcm_token"),
            }

            if device_data["device_id"]:
                UserDevice.objects.update_or_create(
                    user=user,
                    device_id=device_data["device_id"],
                    defaults=device_data,
                )

            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "登录成功",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "phone": user.phone,
                        "nickname": user.nickname,
                        "avatar": user.get_avatar_url(),
                        "is_verified": user.is_verified,
                    },
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class UserLogoutView(APIView):
    """
    用户登出视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: "登出成功"})
    def post(self, request):
        user = request.user
        user.is_online = False
        user.save()

        return Response({"message": "登出成功"}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    用户资料视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: UserProfileSerializer})
    def get(self, request):
        """获取用户资料"""
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            # 如果用户资料不存在，创建一个
            profile = UserProfile.objects.create(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UserUpdateSerializer,
        responses={200: UserUpdateSerializer},
    )
    def put(self, request):
        """更新用户资料"""
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "资料更新成功", "user": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserVerificationView(APIView):
    """
    用户认证视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserVerificationSerializer,
        responses={201: "认证申请提交成功", 400: "认证申请失败"},
    )
    def post(self, request):
        """提交认证申请"""
        serializer = UserVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                verification = serializer.save()
                return Response(
                    {
                        "message": "认证申请提交成功，请等待审核",
                        "verification_id": verification.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: UserVerificationSerializer})
    def get(self, request):
        """获取认证状态"""
        try:
            verification = request.user.verification
            serializer = UserVerificationSerializer(verification)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserVerification.DoesNotExist:
            return Response({"message": "暂无认证申请"}, status=status.HTTP_404_NOT_FOUND)


class UserDeviceView(APIView):
    """
    用户设备视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserDeviceSerializer,
        responses={200: UserDeviceSerializer},
    )
    def post(self, request):
        """注册设备"""
        serializer = UserDeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "设备注册成功", "device": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """
    用户列表视图
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["gender", "role", "is_online", "is_verified"]

    def get_queryset(self):
        queryset = User.objects.filter(status="active")

        # 搜索功能
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(nickname__icontains=search)
                | Q(location__icontains=search)
            )

        # 年龄范围过滤
        min_age = self.request.query_params.get("min_age", None)
        max_age = self.request.query_params.get("max_age", None)

        if min_age or max_age:
            # 这里需要根据生日计算年龄，简化处理
            pass

        return queryset.exclude(id=self.request.user.id)


class PasswordChangeView(APIView):
    """
    密码修改视图
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=PasswordChangeSerializer,
        responses={200: "密码修改成功", 400: "密码修改失败"},
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response({"message": "密码修改成功"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def send_verification_code(request):
    """
    发送验证码
    """
    serializer = PhoneVerificationSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data["phone"]

        # 调用短信服务发送验证码
        from .services import SMSService

        result = SMSService.send_verification_code(phone)

        if result["success"]:
            return Response(
                {
                    "message": result["message"],
                    "phone": phone,
                    "code": result.get("code"),  # 开发环境返回验证码
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """
    重置密码
    """
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data["phone"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(phone=phone)
            user.set_password(new_password)
            user.save()

            return Response({"message": "密码重置成功"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """
    获取用户统计信息
    """
    user = request.user

    return Response(
        {
            "total_calls": user.total_calls,
            "total_duration": user.total_duration,
            "total_earnings": float(user.total_earnings),
            "total_spent": float(user.total_spent),
            "is_online": user.is_online,
            "last_activity": user.last_activity,
        },
        status=status.HTTP_200_OK,
    )


def is_this_week(d: date):
    if not d:
        return False
    today = timezone.now().date()
    return today.isocalendar()[1] == d.isocalendar()[1] and today.year == d.year

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def claim_weekly_free_video(request):
    """
    领取每周免费体验1分钟视频
    """
    user = request.user
    today = timezone.now().date()
    if is_this_week(user.daily_free_video_date):
        return Response({"message": "本周已领取"}, status=400)
    user.daily_free_video_date = today
    user.daily_free_video_used = False
    user.save(update_fields=["daily_free_video_date", "daily_free_video_used"])
    return Response({"message": "领取成功", "free_time": 60})

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def weekly_free_video_status(request):
    """
    查询本周免费体验状态
    """
    user = request.user
    claimed = is_this_week(user.daily_free_video_date)
    used = user.daily_free_video_used if claimed else False
    return Response({"claimed": claimed, "used": used})
