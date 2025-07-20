"""
通话应用URL配置
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "calls"

# 创建路由器
router = DefaultRouter()
router.register(r"calls", views.CallSessionViewSet, basename="call")

urlpatterns = [
    # 通话会话管理
    path("", include(router.urls)),
    # 通话参与者
    path(
        "participants/",
        views.CallParticipantView.as_view(),
        name="call_participant",
    ),
    # 通话邀请
    path(
        "invitations/",
        views.CallInvitationView.as_view(),
        name="call_invitation",
    ),
    path(
        "invitations/<uuid:invitation_id>/accept/",
        views.accept_invitation,
        name="accept_invitation",
    ),
    path(
        "invitations/<uuid:invitation_id>/reject/",
        views.reject_invitation,
        name="reject_invitation",
    ),
    # 通话质量
    path("quality/", views.CallQualityView.as_view(), name="call_quality"),
    # 通话录制
    path("recordings/", views.CallRecordingView.as_view(), name="call_recording"),
    # WebRTC信令
    path(
        "webrtc/<str:action>/",
        views.WebRTCView.as_view(),
        name="webrtc_signaling",
    ),
    # 我的通话
    path("my-calls/", views.my_calls, name="my_calls"),
    # 通话操作
    path("action/", views.call_action, name="call_action"),
]
