"""
房间服务（字段严格与 Room 和 RoomParticipant 模型一致）
"""
from typing import Any, Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from .models import Room, RoomParticipant, RoomRating
from django.db.models import Avg, Count, Q
import logging

logger = logging.getLogger(__name__)

class RoomService:
    """
    房间服务
    """
    def create_room(
        self,
        creator_id: str,
        name: str,
        description: str = "",
        room_type: str = "random",
        max_participants: int = 2,
        is_private: bool = False,
    ) -> Optional[Room]:
        try:
            with transaction.atomic():
                room = Room.objects.create(
                    name=name,
                    description=description,
                    room_type=room_type,
                    max_participants=max_participants,
                    is_private=is_private,
                )
                RoomParticipant.objects.create(
                    room=room,
                    user_id=creator_id,
                    role="host",
                    status="connected",
                    is_active=True,
                )
                logger.info(f"创建房间成功: {room.id}")
                return room
        except Exception as e:
            logger.error(f"创建房间失败: {e}")
            return None

    def join_room(self, room_id: str, user_id: str) -> Dict[str, Any]:
        try:
            room = Room.objects.get(id=room_id)
            if room.current_participants_count >= room.max_participants:
                return {"success": False, "error": "房间已满"}
            existing = RoomParticipant.objects.filter(room=room, user_id=user_id).first()
            if existing:
                if existing.status == "connected" and existing.is_active:
                    return {"success": False, "error": "您已在房间中"}
                existing.status = "connected"
                existing.is_active = True
                existing.connection_time = timezone.now()
                existing.save()
                return {"success": True, "message": "重新加入房间成功", "participant": existing}
            participant = RoomParticipant.objects.create(
                room=room,
                user_id=user_id,
                role="participant",
                status="connected",
                is_active=True,
                connection_time=timezone.now(),
            )
            return {"success": True, "message": "加入房间成功", "participant": participant}
        except Room.DoesNotExist:
            return {"success": False, "error": "房间不存在"}
        except Exception as e:
            logger.error(f"加入房间失败: {e}")
            return {"success": False, "error": "加入房间失败"}

    def leave_room(self, room_id: str, user_id: str) -> Dict[str, Any]:
        try:
            room = Room.objects.get(id=room_id)
            participant = RoomParticipant.objects.get(room=room, user_id=user_id)
            participant.status = "left"
            participant.is_active = False
            participant.disconnect_time = timezone.now()
            participant.save()
            if room.participants.filter(is_active=True).count() == 0:
                room.status = "closed"
                room.save(update_fields=["status"])
            return {"success": True, "message": "离开房间成功"}
        except Room.DoesNotExist:
            return {"success": False, "error": "房间不存在"}
        except RoomParticipant.DoesNotExist:
            return {"success": False, "error": "您不在房间中"}
        except Exception as e:
            logger.error(f"离开房间失败: {e}")
            return {"success": False, "error": "离开房间失败"}

    def get_room_participants(self, room_id: str) -> List[Dict[str, Any]]:
        try:
            participants = RoomParticipant.objects.filter(room_id=room_id, is_active=True).select_related("user")
            return [
                {
                    "user_id": p.user_id,
                    "username": getattr(p.user, "username", ""),
                    "role": p.role,
                    "status": p.status,
                    "joined_at": p.joined_at,
                }
                for p in participants
            ]
        except Exception as e:
            logger.error(f"获取房间参与者失败: {e}")
            return []

    def get_room_stats(self, room_id: str) -> Dict[str, Any]:
        try:
            room = Room.objects.get(id=room_id)
            participant_stats = RoomParticipant.objects.filter(room=room).aggregate(
                total_participants=Count("id"),
                active_participants=Count("id", filter=Q(is_active=True)),
            )
            rating_stats = RoomRating.objects.filter(room=room).aggregate(
                total_ratings=Count("id"),
                average_rating=Avg("rating"),
            )
            return {
                "room_id": room_id,
                "total_participants": participant_stats["total_participants"],
                "active_participants": participant_stats["active_participants"],
                "total_ratings": rating_stats["total_ratings"] or 0,
                "average_rating": rating_stats["average_rating"] or 0.0,
                "created_at": room.created_at,
                "last_activity": room.last_activity,
            }
        except Room.DoesNotExist:
            return {"error": "房间不存在"}
        except Exception as e:
            logger.error(f"获取房间统计失败: {e}")
            return {"error": "获取统计失败"} 