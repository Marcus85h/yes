"""
用户应用URL配置
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

urlpatterns = [
    # 认证相关
    path("auth/register/", views.UserRegistrationView.as_view(), name="register"),
    path("auth/login/", views.UserLoginView.as_view(), name="login"),
    path("auth/logout/", views.UserLogoutView.as_view(), name="logout"),
    path(
        "auth/send-code/",
        views.send_verification_code,
        name="send_verification_code",
    ),
    path("auth/reset-password/", views.reset_password, name="reset_password"),
    path(
        "auth/change-password/",
        views.PasswordChangeView.as_view(),
        name="change_password",
    ),
    # JWT Token
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # 用户资料
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path(
        "verification/",
        views.UserVerificationView.as_view(),
        name="verification",
    ),
    path("device/", views.UserDeviceView.as_view(), name="device"),
    path("stats/", views.user_stats, name="user_stats"),
    # 每周免费体验视频
    path("weekly_free_video/claim/", views.claim_weekly_free_video, name="claim_weekly_free_video"),
    path("weekly_free_video/status/", views.weekly_free_video_status, name="weekly_free_video_status"),
]
