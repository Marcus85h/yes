from django.contrib import admin

from apps.calls.models import Call, CallParticipant, CallRecording
from apps.chat.models import ChatRoom, Message
from apps.rooms.models import Room, RoomParticipant
from apps.security.models import SecurityAlert
from apps.users.models import User, UserProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "phone",
        "nickname",
        "role",
        "status",
        "is_online",
        "is_verified",
        "created_at",
    )
    list_filter = (
        "role",
        "status",
        "gender",
        "is_online",
        "is_verified",
        "created_at",
    )
    search_fields = ("username", "phone", "nickname", "email")
    ordering = ("-created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "is_host",
        "host_level",
        "host_score",
        "real_name",
        "created_at",
    )
    list_filter = (
        "is_host",
        "host_level",
        "education",
        "occupation",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__phone",
        "real_name",
        "wechat",
        "qq",
    )
    ordering = ("-created_at",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "room_id",
        "name",
        "room_type",
        "status",
        "max_participants",
        "is_active",
        "created_at",
    )
    list_filter = (
        "room_type",
        "status",
        "is_private",
        "is_featured",
        "is_active",
        "created_at",
    )
    search_fields = ("room_id", "name", "description")
    ordering = ("-created_at",)


@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "role", "status", "is_active", "joined_at")
    list_filter = ("role", "status", "is_active", "joined_at")
    search_fields = ("room__room_id", "user__username", "user__phone")
    ordering = ("-joined_at",)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = (
        "room_id",
        "name",
        "room_type",
        "status",
        "creator",
        "message_count",
        "created_at",
    )
    list_filter = (
        "room_type",
        "status",
        "is_private",
        "allow_join",
        "allow_message",
        "created_at",
    )
    search_fields = ("room_id", "name", "description", "creator__username")
    ordering = ("-created_at",)


@admin.register(Message)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "message_id",
        "chat_room",
        "sender",
        "message_type",
        "status",
        "created_at",
    )
    list_filter = ("message_type", "status", "is_deleted", "created_at")
    search_fields = (
        "message_id",
        "content",
        "sender__username",
        "chat_room__name",
    )
    ordering = ("-created_at",)


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = (
        "call_id",
        "room",
        "call_type",
        "status",
        "initiator",
        "duration",
        "created_at",
    )
    list_filter = (
        "call_type",
        "status",
        "is_private",
        "is_recorded",
        "created_at",
    )
    search_fields = ("call_id", "initiator__username", "room__room_id")
    ordering = ("-created_at",)


@admin.register(CallParticipant)
class CallParticipantAdmin(admin.ModelAdmin):
    list_display = ("call_session", "user", "role", "status", "joined_at")
    list_filter = ("role", "status", "joined_at")
    search_fields = ("call_session__session_id", "user__username")


@admin.register(CallRecording)
class CallRecordingAdmin(admin.ModelAdmin):
    list_display = (
        "recording_id",
        "call_session",
        "file_path",
        "file_size_mb",
        "duration_minutes",
        "created_at",
    )
    list_filter = (
        "status",
        "include_video",
        "include_audio",
        "is_public",
        "can_download",
        "created_at",
    )
    search_fields = ("recording_id", "call_session__session_id")
    ordering = ("-created_at",)


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = (
        "alert_id",
        "user",
        "alert_type",
        "priority",
        "is_read",
        "is_resolved",
        "created_at",
    )
    list_filter = (
        "alert_type",
        "priority",
        "is_read",
        "is_resolved",
        "created_at",
    )
    search_fields = ("alert_id", "user__username", "title", "message")
    ordering = ("-created_at",)
