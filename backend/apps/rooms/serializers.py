"""
房间序列化器
"""

from rest_framework import serializers

from .models import Room, RoomParticipant, RoomRating, RoomReport


class RoomSerializer(serializers.ModelSerializer):
    """房间序列化器"""

    current_participants_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            "id",
            "room_id",
            "name",
            "description",
            "room_type",
            "status",
            "max_participants",
            "current_participants_count",
            "is_full",
            "target_gender",
            "min_age",
            "max_age",
            "location_preference",
            "is_private",
            "is_featured",
            "is_active",
            "total_visitors",
            "total_connections",
            "average_rating",
            "created_by",
            "created_at",
            "updated_at",
            "last_activity",
        ]
        read_only_fields = [
            "id",
            "room_id",
            "total_visitors",
            "total_connections",
            "average_rating",
            "created_at",
            "updated_at",
            "last_activity",
        ]

    def get_created_by(self, obj):
        """获取房间创建者信息"""
        try:
            participant = obj.participants.filter(role="creator").first()
            return participant.user.username if participant else None
        except Exception:
            return None


# 为兼容性添加别名
RoomListSerializer = RoomSerializer
RoomDetailSerializer = RoomSerializer
RoomJoinSerializer = RoomSerializer
RoomUpdateSerializer = RoomSerializer
RoomSearchSerializer = RoomSerializer
RoomStatsSerializer = RoomSerializer


class RoomCreateSerializer(serializers.ModelSerializer):
    """房间创建序列化器"""

    class Meta:
        model = Room
        fields = [
            "name",
            "description",
            "room_type",
            "max_participants",
            "target_gender",
            "min_age",
            "max_age",
            "location_preference",
            "is_private",
            "is_featured",
        ]


class RoomParticipantSerializer(serializers.ModelSerializer):
    """房间参与者序列化器"""

    class Meta:
        model = RoomParticipant
        fields = [
            "id",
            "room",
            "user",
            "role",
            "status",
            "joined_at",
            "left_at",
        ]
        read_only_fields = ["id", "joined_at", "left_at"]


class RoomRatingSerializer(serializers.ModelSerializer):
    """房间评分序列化器"""

    class Meta:
        model = RoomRating
        fields = ["id", "room", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]


class RoomReportSerializer(serializers.ModelSerializer):
    """房间举报序列化器"""

    class Meta:
        model = RoomReport
        fields = [
            "id",
            "room",
            "reporter",
            "reason",
            "description",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
