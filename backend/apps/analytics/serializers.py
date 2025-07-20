from rest_framework import serializers

from .models import (
    AnalyticsEvent,
    AnalyticsSummary,
    PerformanceMetrics,
    SystemAlert,
    UserBehavior,
    UserSession,
)


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """分析事件序列化器"""

    class Meta:
        model = AnalyticsEvent
        fields = [
            "event_id",
            "event_type",
            "name",
            "properties",
            "timestamp",
            "priority",
            "user",
            "session_id",
            "device_info",
            "app_info",
        ]
        read_only_fields = ["ip_address", "user_agent"]

    def validate_event_id(self, value):
        """验证事件ID唯一性"""
        if AnalyticsEvent.objects.filter(event_id=value).exists():
            raise serializers.ValidationError("事件ID已存在")
        return value

    def validate_event_type(self, value):
        """验证事件类型"""
        valid_types = [choice[0] for choice in AnalyticsEvent.EVENT_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError(f"无效的事件类型: {value}")
        return value

    def validate_priority(self, value):
        """验证优先级"""
        valid_priorities = [choice[0] for choice in AnalyticsEvent.PRIORITY_LEVELS]
        if value not in valid_priorities:
            raise serializers.ValidationError(f"无效的优先级: {value}")
        return value


class UserSessionSerializer(serializers.ModelSerializer):
    """用户会话序列化器"""

    class Meta:
        model = UserSession
        fields = [
            "session_id",
            "user",
            "start_time",
            "end_time",
            "duration",
            "device_info",
            "app_info",
            "events_count",
            "is_active",
        ]
        read_only_fields = ["ip_address", "user_agent", "duration"]

    def validate_session_id(self, value):
        """验证会话ID唯一性"""
        if UserSession.objects.filter(session_id=value).exists():
            raise serializers.ValidationError("会话ID已存在")
        return value

    def validate(self, data):
        """验证会话数据"""
        if data.get("end_time") and data.get("start_time"):
            if data["end_time"] <= data["start_time"]:
                raise serializers.ValidationError("结束时间必须晚于开始时间")
        return data


class PerformanceMetricsSerializer(serializers.ModelSerializer):
    """性能指标序列化器"""

    class Meta:
        model = PerformanceMetrics
        fields = [
            "user",
            "session_id",
            "timestamp",
            "cpu_usage",
            "memory_usage",
            "battery_level",
            "network_latency",
            "frame_rate",
            "error_count",
            "device_info",
            "app_version",
        ]

    def validate_cpu_usage(self, value):
        """验证CPU使用率"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("CPU使用率必须在0-100之间")
        return value

    def validate_memory_usage(self, value):
        """验证内存使用率"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("内存使用率必须在0-100之间")
        return value

    def validate_battery_level(self, value):
        """验证电池电量"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("电池电量必须在0-100之间")
        return value

    def validate_frame_rate(self, value):
        """验证帧率"""
        if value < 0 or value > 120:
            raise serializers.ValidationError("帧率必须在0-120之间")
        return value

    def validate_network_latency(self, value):
        """验证网络延迟"""
        if value < 0 or value > 10000:
            raise serializers.ValidationError("网络延迟必须在0-10000ms之间")
        return value


class UserBehaviorSerializer(serializers.ModelSerializer):
    """用户行为序列化器"""

    class Meta:
        model = UserBehavior
        fields = [
            "user",
            "date",
            "session_count",
            "total_duration",
            "events_count",
            "feature_usage",
            "error_count",
            "call_count",
            "call_duration",
            "message_count",
            "payment_count",
            "payment_amount",
        ]

    def validate_session_count(self, value):
        """验证会话次数"""
        if value < 0:
            raise serializers.ValidationError("会话次数不能为负数")
        return value

    def validate_total_duration(self, value):
        """验证总时长"""
        if value < 0:
            raise serializers.ValidationError("总时长不能为负数")
        return value

    def validate_call_count(self, value):
        """验证通话次数"""
        if value < 0:
            raise serializers.ValidationError("通话次数不能为负数")
        return value

    def validate_payment_amount(self, value):
        """验证支付金额"""
        if value < 0:
            raise serializers.ValidationError("支付金额不能为负数")
        return value


class AnalyticsSummarySerializer(serializers.ModelSerializer):
    """分析汇总序列化器"""

    class Meta:
        model = AnalyticsSummary
        fields = [
            "date",
            "total_users",
            "active_users",
            "new_users",
            "total_sessions",
            "total_events",
            "total_calls",
            "total_messages",
            "total_payments",
            "total_revenue",
            "error_count",
            "avg_session_duration",
            "avg_cpu_usage",
            "avg_memory_usage",
            "avg_frame_rate",
        ]

    def validate_total_users(self, value):
        """验证总用户数"""
        if value < 0:
            raise serializers.ValidationError("总用户数不能为负数")
        return value

    def validate_active_users(self, value):
        """验证活跃用户数"""
        if value < 0:
            raise serializers.ValidationError("活跃用户数不能为负数")
        return value

    def validate_new_users(self, value):
        """验证新用户数"""
        if value < 0:
            raise serializers.ValidationError("新用户数不能为负数")
        return value


class SystemAlertSerializer(serializers.ModelSerializer):
    """系统警报序列化器"""

    class Meta:
        model = SystemAlert
        fields = [
            "id",
            "title",
            "message",
            "alert_type",
            "level",
            "timestamp",
            "is_resolved",
            "resolved_at",
            "resolved_by",
            "metadata",
        ]
        read_only_fields = ["id", "timestamp", "resolved_at"]

    def validate_alert_type(self, value):
        """验证警报类型"""
        valid_types = [choice[0] for choice in SystemAlert.ALERT_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError(f"无效的警报类型: {value}")
        return value

    def validate_level(self, value):
        """验证警报级别"""
        valid_levels = [choice[0] for choice in SystemAlert.ALERT_LEVELS]
        if value not in valid_levels:
            raise serializers.ValidationError(f"无效的警报级别: {value}")
        return value


# 简化的序列化器用于API响应


class AnalyticsEventListSerializer(serializers.ModelSerializer):
    """分析事件列表序列化器"""

    user_name = serializers.CharField(source="user.username", read_only=True)
    event_type_display = serializers.CharField(source="get_event_type_display", read_only=True)

    class Meta:
        model = AnalyticsEvent
        fields = [
            "event_id",
            "event_type",
            "event_type_display",
            "name",
            "timestamp",
            "priority",
            "user_name",
            "session_id",
        ]


class PerformanceMetricsListSerializer(serializers.ModelSerializer):
    """性能指标列表序列化器"""

    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = PerformanceMetrics
        fields = [
            "id",
            "user_name",
            "timestamp",
            "cpu_usage",
            "memory_usage",
            "frame_rate",
            "network_latency",
            "error_count",
        ]


class SystemAlertListSerializer(serializers.ModelSerializer):
    """系统警报列表序列化器"""

    alert_type_display = serializers.CharField(source="get_alert_type_display", read_only=True)
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    resolved_by_name = serializers.CharField(source="resolved_by.username", read_only=True)

    class Meta:
        model = SystemAlert
        fields = [
            "id",
            "title",
            "message",
            "alert_type",
            "alert_type_display",
            "level",
            "level_display",
            "timestamp",
            "is_resolved",
            "resolved_at",
            "resolved_by_name",
        ]


# 统计数据的序列化器


class EventStatsSerializer(serializers.Serializer):
    """事件统计序列化器"""

    event_type = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class DailyStatsSerializer(serializers.Serializer):
    """每日统计序列化器"""

    date = serializers.DateField()
    count = serializers.IntegerField()
    unique_users = serializers.IntegerField()


class PerformanceStatsSerializer(serializers.Serializer):
    """性能统计序列化器"""

    avg_cpu_usage = serializers.FloatField()
    avg_memory_usage = serializers.FloatField()
    avg_frame_rate = serializers.FloatField()
    avg_latency = serializers.FloatField()
    max_cpu_usage = serializers.FloatField()
    max_memory_usage = serializers.FloatField()
    min_frame_rate = serializers.FloatField()
    total_metrics = serializers.IntegerField()


class UserBehaviorStatsSerializer(serializers.Serializer):
    """用户行为统计序列化器"""

    total_sessions = serializers.IntegerField()
    total_duration = serializers.IntegerField()
    total_events = serializers.IntegerField()
    call_count = serializers.IntegerField()
    message_count = serializers.IntegerField()
    payment_count = serializers.IntegerField()
    payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class AdminStatsSerializer(serializers.Serializer):
    """管理后台统计序列化器"""

    total_users = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    active_users_yesterday = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    total_events_today = serializers.IntegerField()
    total_sessions_today = serializers.IntegerField()
    error_count_today = serializers.IntegerField()


class ChartDataSerializer(serializers.Serializer):
    """图表数据序列化器"""

    date = serializers.CharField()
    value = serializers.FloatField()


class AdminChartsSerializer(serializers.Serializer):
    """管理后台图表序列化器"""

    user_growth = ChartDataSerializer(many=True)
    active_users = ChartDataSerializer(many=True)
    events = ChartDataSerializer(many=True)
