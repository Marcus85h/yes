"""
通话系统序列化器
"""

from django.utils import timezone
from rest_framework import serializers

from apps.users.serializers import UserListSerializer

from .models import (
    Call,
    CallInvitation,
    CallParticipant,
    CallQualityLog,
    CallRecording,
)


class CallSerializer(serializers.ModelSerializer):
    """
    通话序列化器
    """

    initiator = UserListSerializer(read_only=True)
    receiver = UserListSerializer(read_only=True)
    current_participants_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Call
        fields = [
            "id",
            "call_type",
            "status",
            "initiator",
            "receiver",
            "room_id",
            "title",
            "description",
            "start_time",
            "end_time",
            "duration",
            "max_participants",
            "is_recording",
            "recording_url",
            "is_screen_sharing",
            "screen_sharer",
            "quality_metrics",
            "metadata",
            "current_participants_count",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "initiator",
            "start_time",
            "end_time",
            "duration",
            "recording_url",
            "quality_metrics",
        ]


class CallCreateSerializer(serializers.ModelSerializer):
    """
    创建通话序列化器
    """

    class Meta:
        model = Call
        fields = [
            "call_type",
            "receiver",
            "room_id",
            "title",
            "description",
            "max_participants",
            "is_recording",
            "is_screen_sharing",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["initiator"] = user
        return super().create(validated_data)


class CallParticipantSerializer(serializers.ModelSerializer):
    """
    通话参与者序列化器
    """

    user = UserListSerializer(read_only=True)

    class Meta:
        model = CallParticipant
        fields = [
            "id",
            "call",
            "user",
            "role",
            "status",
            "joined_at",
            "left_at",
            "duration",
            "is_muted",
            "is_video_enabled",
            "is_screen_sharing",
            "network_quality",
            "audio_level",
            "video_quality",
            "metadata",
        ]
        read_only_fields = [
            "id",
            "joined_at",
            "left_at",
            "duration",
            "network_quality",
            "audio_level",
            "video_quality",
        ]


class CallParticipantJoinSerializer(serializers.Serializer):
    """
    加入通话序列化器
    """

    call_id = serializers.UUIDField()
    role = serializers.ChoiceField(choices=CallParticipant.PARTICIPANT_ROLES, required=False)

    def validate_call_id(self, value):
        try:
            call = Call.objects.get(id=value)
            if call.status not in ["initiating", "ringing", "connected"]:
                raise serializers.ValidationError("通话已结束")
            return value
        except Call.DoesNotExist:
            raise serializers.ValidationError("通话不存在")


class CallInvitationSerializer(serializers.ModelSerializer):
    """
    通话邀请序列化器
    """

    inviter = UserListSerializer(read_only=True)
    invitee = UserListSerializer(read_only=True)
    call = CallSerializer(read_only=True)

    class Meta:
        model = CallInvitation
        fields = [
            "id",
            "call",
            "inviter",
            "invitee",
            "status",
            "message",
            "sent_at",
            "responded_at",
            "expires_at",
        ]
        read_only_fields = [
            "id",
            "inviter",
            "status",
            "responded_at",
            "expires_at",
        ]


class CallInvitationCreateSerializer(serializers.ModelSerializer):
    """
    创建通话邀请序列化器
    """

    class Meta:
        model = CallInvitation
        fields = ["call", "invitee", "message"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["inviter"] = user
        return super().create(validated_data)

    def validate(self, attrs):
        call = attrs["call"]
        invitee = attrs["invitee"]
        inviter = self.context["request"].user

        # 检查是否已经邀请过
        if CallInvitation.objects.filter(
            call=call,
            inviter=inviter,
            invitee=invitee,
            status="pending",
        ).exists():
            raise serializers.ValidationError("已经邀请过该用户")

        # 检查邀请者是否是通话发起者
        if call.initiator != inviter:
            raise serializers.ValidationError("只有通话发起者可以邀请用户")

        return attrs


class CallQualityLogSerializer(serializers.ModelSerializer):
    """
    通话质量日志序列化器
    """

    participant = CallParticipantSerializer(read_only=True)

    class Meta:
        model = CallQualityLog
        fields = [
            "id",
            "call",
            "participant",
            "timestamp",
            "audio_quality",
            "video_quality",
            "network_quality",
            "packet_loss",
            "latency",
            "jitter",
            "bandwidth",
            "cpu_usage",
            "memory_usage",
            "battery_level",
        ]
        read_only_fields = ["id", "timestamp"]


class CallRecordingSerializer(serializers.ModelSerializer):
    """
    通话录制序列化器
    """

    call = CallSerializer(read_only=True)

    class Meta:
        model = CallRecording
        fields = [
            "id",
            "call",
            "file_path",
            "file_url",
            "file_size",
            "duration",
            "format",
            "quality",
            "created_at",
            "is_processed",
            "metadata",
        ]
        read_only_fields = [
            "id",
            "file_path",
            "file_url",
            "file_size",
            "duration",
            "created_at",
            "is_processed",
        ]


class CallRecordingCreateSerializer(serializers.ModelSerializer):
    """
    创建通话录制序列化器
    """

    class Meta:
        model = CallRecording
        fields = [
            "call",
            "format",
            "quality",
        ]


class CallListSerializer(serializers.ModelSerializer):
    """
    通话列表序列化器
    """

    initiator = UserListSerializer(read_only=True)
    current_participants_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Call
        fields = [
            "id",
            "call_type",
            "status",
            "initiator",
            "current_participants_count",
            "is_active",
            "duration",
            "start_time",
        ]


class CallStatsSerializer(serializers.Serializer):
    """
    通话统计序列化器
    """

    total_calls = serializers.IntegerField()
    active_calls = serializers.IntegerField()
    total_duration = serializers.IntegerField()
    average_quality = serializers.DecimalField(max_digits=3, decimal_places=2)
    call_types = serializers.DictField()
    recent_calls = CallListSerializer(many=True)


class CallActionSerializer(serializers.Serializer):
    """
    通话操作序列化器
    """

    action = serializers.ChoiceField(
        choices=[
            "start",
            "end",
            "reject",
            "accept",
            "mute",
            "unmute",
            "camera_on",
            "camera_off",
        ]
    )
    call_id = serializers.UUIDField()


class WebRTCOfferSerializer(serializers.Serializer):
    """
    WebRTC Offer序列化器
    """

    call_id = serializers.UUIDField()
    offer = serializers.CharField()
    participant_id = serializers.IntegerField()


class WebRTCAnswerSerializer(serializers.Serializer):
    """
    WebRTC Answer序列化器
    """

    call_id = serializers.UUIDField()
    answer = serializers.CharField()
    participant_id = serializers.IntegerField()


class WebRTCIceCandidateSerializer(serializers.Serializer):
    """
    WebRTC ICE Candidate序列化器
    """

    call_id = serializers.UUIDField()
    candidate = serializers.CharField()
    participant_id = serializers.IntegerField()


class CallSearchSerializer(serializers.Serializer):
    """
    通话搜索序列化器
    """

    call_type = serializers.ChoiceField(choices=Call.CALL_TYPES, required=False)
    status = serializers.ChoiceField(choices=Call.CALL_STATUS, required=False)
    is_recording = serializers.BooleanField(required=False)
    is_screen_sharing = serializers.BooleanField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    initiator = serializers.IntegerField(required=False)
    receiver = serializers.IntegerField(required=False)

    def validate(self, attrs):
        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("开始日期不能晚于结束日期")
        return attrs


# 为兼容性添加所有缺失的序列化器别名
# 已移除别名覆盖，所有序列化器已独立定义，详见上方各类定义
