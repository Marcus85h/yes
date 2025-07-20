"""
聊天应用URL配置
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "chat"

# 创建路由器
router = DefaultRouter()
router.register(r"rooms", views.ChatRoomViewSet, basename="chat_room")
router.register(r"messages", views.MessageViewSet, basename="message")

urlpatterns = [
    # 聊天房间管理
    path("", include(router.urls)),
    # 聊天邀请
    path(
        "invitations/",
        views.ChatInvitationView.as_view(),
        name="chat_invitation",
    ),
    path(
        "invitations/<uuid:invitation_id>/accept/",
        views.accept_chat_invitation,
        name="accept_chat_invitation",
    ),
    path(
        "invitations/<uuid:invitation_id>/reject/",
        views.reject_chat_invitation,
        name="reject_chat_invitation",
    ),
    # 聊天通知
    path(
        "notifications/",
        views.ChatNotificationView.as_view(),
        name="chat_notification",
    ),
    # 我的聊天
    path("my-chats/", views.my_chats, name="my_chats"),
    # 消息操作
    path("message-action/", views.message_action, name="message_action"),
    # 聊天消息
    path(
        "rooms/<str:room_id>/messages/",
        views.chat_messages,
        name="chat_messages",
    ),
    # 文件上传
    path("rooms/<str:room_id>/upload/", views.upload_file, name="upload_file"),
    # 搜索功能
    path("search/messages/", views.search_messages, name="search_messages"),
    path("search/rooms/", views.search_rooms, name="search_rooms"),
    # 私聊功能
    path("private-chat/", views.create_private_chat, name="create_private_chat"),
    path("user-chats/", views.get_user_chats, name="get_user_chats"),
    # 收藏功能
    path("favorites/", views.get_favorite_messages, name="get_favorite_messages"),
    # 消息撤回和转发（通过ViewSet的action自动生成）
]
