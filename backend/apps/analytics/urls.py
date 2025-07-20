from django.urls import path

from .views import (  # type: ignore
    AdminAnalyticsView,
    get_analytics_summary,
    get_event_analytics,
    get_performance_stats,
    get_system_alerts,
    get_user_behavior_stats,
    report_performance_metrics,
    resolve_alert,
    track_event,
    track_events_batch,
    track_session,
)

app_name = "analytics"

urlpatterns = [
    # 事件追踪API
    path("events/track/", track_event, name="track_event"),
    path("events/track/batch/", track_events_batch, name="track_events_batch"),
    path("sessions/track/", track_session, name="track_session"),
    # 性能监控API
    path(
        "performance/report/",
        report_performance_metrics,
        name="report_performance_metrics",
    ),
    path(
        "performance/stats/",
        get_performance_stats,
        name="get_performance_stats",
    ),
    # 数据分析API
    path("summary/", get_analytics_summary, name="get_analytics_summary"),
    path(
        "user-behavior/",
        get_user_behavior_stats,
        name="get_user_behavior_stats",
    ),
    path("events/analytics/", get_event_analytics, name="get_event_analytics"),
    # 系统警报API
    path("alerts/", get_system_alerts, name="get_system_alerts"),
    path("alerts/resolve/", resolve_alert, name="resolve_alert"),
    # 管理后台API
    path(
        "admin/dashboard/",
        AdminAnalyticsView.as_view(),
        name="admin_dashboard",
    ),
]
