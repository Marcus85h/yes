from django.urls import path

from . import views

app_name = "security"

urlpatterns = [
    # 防录屏检测
    path(
        "detect/",
        views.detect_screen_recording,
        name="detect_screen_recording",
    ),
    # 安全状态
    path("status/", views.get_security_status, name="get_security_status"),
    # 检测历史
    path("history/", views.get_detection_history, name="get_detection_history"),
    # 安全警报
    path("alerts/", views.get_security_alerts, name="get_security_alerts"),
    path(
        "alerts/mark-read/",
        views.mark_alert_as_read,
        name="mark_alert_as_read",
    ),
    # 误报报告
    path(
        "false-positive/",
        views.report_false_positive,
        name="report_false_positive",
    ),
]
