"""
房间应用URL配置
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "rooms"

# 创建路由器
router = DefaultRouter()
router.register(r"rooms", views.RoomViewSet, basename="room")

urlpatterns = [
    # 房间管理
    path("", include(router.urls)),
    # 房间评分
    path("rating/", views.RoomRatingView.as_view(), name="room_rating"),
    # 房间举报
    path("report/", views.RoomReportView.as_view(), name="room_report"),
    # 我的房间
    path("my-rooms/", views.my_rooms, name="my_rooms"),
    # 房间连接
    path("connect/<str:room_id>/", views.connect_room, name="connect_room"),
    path(
        "disconnect/<str:room_id>/",
        views.disconnect_room,
        name="disconnect_room",
    ),
]
