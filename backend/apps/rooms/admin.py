"""
房间管理后台
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Room, RoomParticipant, RoomRating, RoomReport


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    房间管理
    """

    list_display = [
        "room_id",
        "name",
        "room_type",
        "status",
        "current_participants_count",
        "max_participants",
        "is_active",
        "is_featured",
        "average_rating",
        "total_visitors",
        "created_at",
    ]
    list_filter = [
        "room_type",
        "status",
        "is_active",
        "is_featured",
        "created_at",
    ]
    search_fields = ["room_id", "name", "description"]
    readonly_fields = [
        "room_id",
        "total_visitors",
        "total_connections",
        "average_rating",
        "created_at",
        "updated_at",
        "last_activity",
    ]
    list_editable = ["is_active", "is_featured"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "基础信息",
            {
                "fields": (
                    "room_id",
                    "name",
                    "description",
                    "room_type",
                    "status",
                )
            },
        ),
        (
            "房间配置",
            {
                "fields": (
                    "max_participants",
                    "target_gender",
                    "min_age",
                    "max_age",
                    "location_preference",
                )
            },
        ),
        ("房间设置", {"fields": ("is_private", "is_featured", "is_active")}),
        (
            "统计信息",
            {
                "fields": (
                    "total_visitors",
                    "total_connections",
                    "average_rating",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "时间信息",
            {
                "fields": ("created_at", "updated_at", "last_activity"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_room_type_display(self, obj):  # type: ignore[no-untyped-def]
        return obj.get_room_type_display()

    get_room_type_display.short_description = "房间类型"  # type: ignore[attr-defined]

    def get_status_display(self, obj):  # type: ignore[no-untyped-def]
        return obj.get_status_display()

    get_status_display.short_description = "状态"  # type: ignore[attr-defined]

    def get_creator_display(self, obj):  # type: ignore[no-untyped-def]
        return obj.creator.username if obj.creator else "-"

    get_creator_display.short_description = "创建者"  # type: ignore[attr-defined]

    def get_participants_count(self, obj):  # type: ignore[no-untyped-def]
        return obj.current_participants_count

    get_participants_count.short_description = "当前人数"  # type: ignore[attr-defined]

    def get_rating_display(self, obj):  # type: ignore[no-untyped-def]
        return f"{obj.average_rating:.1f}" if obj.average_rating else "-"

    get_rating_display.short_description = "平均评分"  # type: ignore[attr-defined]

    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).prefetch_related("participants")

    actions = [
        "activate_rooms",
        "deactivate_rooms",
        "feature_rooms",
        "unfeature_rooms",
    ]

    def activate_rooms(self, request, queryset):
        """激活房间"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"成功激活 {updated} 个房间")

    activate_rooms.short_description = "激活选中的房间"  # type: ignore

    def deactivate_rooms(self, request, queryset):
        """停用房间"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"成功停用 {updated} 个房间")

    deactivate_rooms.short_description = "停用选中的房间"  # type: ignore

    def feature_rooms(self, request, queryset):
        """推荐房间"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"成功推荐 {updated} 个房间")

    feature_rooms.short_description = "推荐选中的房间"  # type: ignore

    def unfeature_rooms(self, request, queryset):
        """取消推荐房间"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"成功取消推荐 {updated} 个房间")

    unfeature_rooms.short_description = "取消推荐选中的房间"  # type: ignore

    def get_participant_count(self, obj):  # type: ignore
        return obj.participants.count()

    get_participant_count.short_description = "参与者数量"  # type: ignore

    def get_match_count(self, obj):  # type: ignore
        return obj.matches.count()

    get_match_count.short_description = "匹配数量"  # type: ignore  # type: ignore

    def get_rating_count(self, obj):  # type: ignore
        return obj.ratings.count()

    get_rating_count.short_description = "评分数量"  # type: ignore  # type: ignore

    def get_average_rating(self, obj):  # type: ignore
        ratings = obj.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0

    get_average_rating.short_description = "平均评分"  # type: ignore  # type: ignore

    def get_report_count(self, obj):  # type: ignore
        return obj.reports.count()

    get_report_count.short_description = "举报数量"  # type: ignore  # type: ignore


@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    """
    房间参与者管理
    """

    list_display = [
        "id",
        "room_link",
        "user_link",
        "role",
        "status",
        "is_active",
        "total_time",
        "joined_at",
    ]
    list_filter = ["role", "status", "is_active", "joined_at"]
    search_fields = ["room__room_id", "user__username", "user__nickname"]
    readonly_fields = ["joined_at", "updated_at", "total_time"]
    ordering = ["-joined_at"]

    def room_link(self, obj):
        """房间链接"""
        if obj.room:
            url = reverse("admin:rooms_room_change", args=[obj.room.id])
            return format_html('<a href="{}">{}</a>', url, obj.room.room_id)
        return "-"

    room_link.short_description = "房间"  # type: ignore[attr-defined]

    def user_link(self, obj):
        """用户链接"""
        if obj.user:
            url = reverse("admin:users_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.display_name)
        return "-"

    user_link.short_description = "用户"  # type: ignore[attr-defined]

    def total_time(self, obj):
        """总参与时间"""
        if obj.total_time:
            minutes = obj.total_time // 60
            seconds = obj.total_time % 60
            return f"{minutes}分{seconds}秒"
        return "0秒"

    total_time.short_description = "总时间"  # type: ignore[attr-defined]

    def get_role_display(self, obj):  # type: ignore[no-untyped-def]
        return obj.get_role_display()

    get_role_display.short_description = "角色"  # type: ignore[attr-defined]

    def get_status_display(self, obj):  # type: ignore[no-untyped-def]
        return obj.get_status_display()

    get_status_display.short_description = "状态"  # type: ignore[attr-defined]

    def get_user_display(self, obj):  # type: ignore[no-untyped-def]
        return obj.user.username if obj.user else "-"

    get_user_display.short_description = "用户"  # type: ignore[attr-defined]

    def get_room_display(self, obj):  # type: ignore[no-untyped-def]
        return obj.room.name if obj.room else "-"

    get_room_display.short_description = "房间"  # type: ignore[attr-defined]


@admin.register(RoomRating)
class RoomRatingAdmin(admin.ModelAdmin):
    """
    房间评分管理
    """

    list_display = [
        "id",
        "room_link",
        "from_user_link",
        "to_user_link",
        "rating",
        "comment_preview",
        "created_at",
    ]
    list_filter = ["rating", "created_at"]
    search_fields = [
        "room__room_id",
        "from_user__username",
        "to_user__username",
        "comment",
    ]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

    def room_link(self, obj):
        """房间链接"""
        if obj.room:
            url = reverse("admin:rooms_room_change", args=[obj.room.id])
            return format_html('<a href="{}">{}</a>', url, obj.room.room_id)
        return "-"

    room_link.short_description = "房间"  # type: ignore[attr-defined]

    def from_user_link(self, obj):
        """评分用户链接"""
        if obj.from_user:
            url = reverse("admin:users_user_change", args=[obj.from_user.id])
            return format_html('<a href="{}">{}</a>', url, obj.from_user.display_name)
        return "-"

    from_user_link.short_description = "评分用户"  # type: ignore[attr-defined]

    def to_user_link(self, obj):
        """被评分用户链接"""
        if obj.to_user:
            url = reverse("admin:users_user_change", args=[obj.to_user.id])
            return format_html('<a href="{}">{}</a>', url, obj.to_user.display_name)
        return "-"

    to_user_link.short_description = "被评分用户"  # type: ignore[attr-defined]

    def comment_preview(self, obj):
        """评论预览"""
        if obj.comment:
            return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
        return "-"

    comment_preview.short_description = "评论"  # type: ignore[attr-defined]


@admin.register(RoomReport)
class RoomReportAdmin(admin.ModelAdmin):
    """
    房间举报管理
    """

    list_display = [
        "id",
        "room_link",
        "reporter_link",
        "reported_user_link",
        "report_type",
        "status",
        "created_at",
        "handled_at",
    ]
    list_filter = ["report_type", "status", "created_at"]
    search_fields = [
        "room__room_id",
        "reporter__username",
        "reported_user__username",
        "description",
    ]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "举报信息",
            {
                "fields": (
                    "room",
                    "reporter",
                    "reported_user",
                    "report_type",
                    "description",
                    "evidence",
                )
            },
        ),
        (
            "处理信息",
            {"fields": ("status", "admin_notes", "handled_by", "handled_at")},
        ),
        ("时间信息", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def room_link(self, obj):
        """房间链接"""
        if obj.room:
            url = reverse("admin:rooms_room_change", args=[obj.room.id])
            return format_html('<a href="{}">{}</a>', url, obj.room.room_id)
        return "-"

    room_link.short_description = "房间"  # type: ignore[attr-defined]

    def reporter_link(self, obj):
        """举报人链接"""
        if obj.reporter:
            url = reverse("admin:users_user_change", args=[obj.reporter.id])
            return format_html('<a href="{}">{}</a>', url, obj.reporter.display_name)
        return "-"

    reporter_link.short_description = "举报人"  # type: ignore[attr-defined]

    def reported_user_link(self, obj):
        """被举报人链接"""
        if obj.reported_user:
            url = reverse("admin:users_user_change", args=[obj.reported_user.id])
            return format_html('<a href="{}">{}</a>', url, obj.reported_user.display_name)
        return "-"

    reported_user_link.short_description = "被举报人"  # type: ignore[attr-defined]

    actions = ["mark_investigating", "mark_resolved", "mark_dismissed"]

    def mark_investigating(self, request, queryset):
        """标记为调查中"""
        updated = queryset.update(status="investigating")
        self.message_user(request, f"成功标记 {updated} 个举报为调查中")

    mark_investigating.short_description = "标记为调查中"  # type: ignore[attr-defined]

    def mark_resolved(self, request, queryset):
        """标记为已处理"""
        updated = queryset.update(status="resolved")
        self.message_user(request, f"成功标记 {updated} 个举报为已处理")

    mark_resolved.short_description = "标记为已处理"  # type: ignore[attr-defined]

    def mark_dismissed(self, request, queryset):
        """标记为已驳回"""
        updated = queryset.update(status="dismissed")
        self.message_user(request, f"成功标记 {updated} 个举报为已驳回")

    mark_dismissed.short_description = "标记为已驳回"  # type: ignore[attr-defined]
