"""
房间服务
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import Room, RoomParticipant, RoomRating

User = get_user_model()
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
        room_type: str = "dating",
        max_participants: int = 10,
        is_private: bool = False,
        tags: Optional[List[str]] = None,
    ) -> Optional[Room]:
        """
        创建房间
        """
        try:
            with transaction.atomic():
                # 创建房间
                room = Room.objects.create(
                    name=name,
                    description=description,
                    room_type=room_type,
                    max_participants=max_participants,
                    is_private=is_private,
                    tags=tags or [],
                    creator_id=creator_id,
                )

                # 创建者自动加入房间
                RoomParticipant.objects.create(
                    room=room,
                    user_id=creator_id,
                    role="host",
                    status="active",
                )

                logger.info(f"创建房间成功: {room.id}")
                return room

        except Exception as e:
            logger.error(f"创建房间失败: {e}")
            return None

    def join_room(self, room_id: str, user_id: str) -> Dict[str, Any]:
        """
        加入房间
        """
        try:
            room = Room.objects.get(id=room_id)
            user: Any = User.objects.get(id=user_id)  # type: ignore[valid-type]

            # 检查房间是否已满
            if room.current_participants_count >= room.max_participants:
                return {
                    "success": False,
                    "error": "房间已满",
                }

            # 检查用户是否已在房间中
            existing_participant = RoomParticipant.objects.filter(
                room=room, user_id=user_id
            ).first()

            if existing_participant:
                if existing_participant.status == "active":
                    return {
                        "success": False,
                        "error": "您已在房间中",
                    }
                else:
                    # 重新激活参与者
                    existing_participant.status = "active"
                    existing_participant.joined_at = timezone.now()
                    existing_participant.save()
                    return {
                        "success": True,
                        "message": "重新加入房间成功",
                        "participant": existing_participant,
                    }

            # 检查用户年龄是否符合房间要求
            if hasattr(user, "birthday") and user.birthday:  # type: ignore[attr-defined]
                age = (timezone.now().date() - user.birthday).days // 365  # type: ignore[attr-defined]
                if age < room.min_age or age > room.max_age:
                    return {
                        "success": False,
                        "error": f"年龄不符合要求 ({room.min_age}-{room.max_age}岁)",
                    }

            # 检查地理位置匹配
            if hasattr(user, "location") and user.location and room.location:  # type: ignore[attr-defined]
                # 这里可以添加地理位置匹配逻辑
                pass

            # 创建参与者记录
            participant = RoomParticipant.objects.create(
                room=room,
                user_id=user_id,
                role="member",
                status="active",
            )

            # 更新房间统计
            room.current_participants_count += 1
            room.save(update_fields=["current_participants_count"])

            logger.info(f"用户 {user_id} 加入房间 {room_id}")

            return {
                "success": True,
                "message": "加入房间成功",
                "participant": participant,
            }

        except Room.DoesNotExist:
            return {"success": False, "error": "房间不存在"}
        except User.DoesNotExist:  # type: ignore[valid-type]
            return {"success": False, "error": "用户不存在"}
        except Exception as e:
            logger.error(f"加入房间失败: {e}")
            return {"success": False, "error": "加入房间失败"}

    def leave_room(self, room_id: str, user_id: str) -> Dict[str, Any]:
        """
        离开房间
        """
        try:
            room = Room.objects.get(id=room_id)
            participant = RoomParticipant.objects.get(room=room, user_id=user_id)

            # 更新参与者状态
            participant.status = "left"
            participant.left_at = timezone.now()
            participant.save()

            # 更新房间统计
            room.current_participants_count = max(0, room.current_participants_count - 1)
            room.save(update_fields=["current_participants_count"])

            # 如果房间没有参与者，关闭房间
            if room.current_participants_count == 0:
                room.status = "closed"
                room.closed_at = timezone.now()
                room.save(update_fields=["status", "closed_at"])

            logger.info(f"用户 {user_id} 离开房间 {room_id}")

            return {
                "success": True,
                "message": "离开房间成功",
            }

        except Room.DoesNotExist:
            return {"success": False, "error": "房间不存在"}
        except RoomParticipant.DoesNotExist:
            return {"success": False, "error": "您不在房间中"}
        except Exception as e:
            logger.error(f"离开房间失败: {e}")
            return {"success": False, "error": "离开房间失败"}

    def get_room_participants(self, room_id: str) -> List[Dict[str, Any]]:
        """
        获取房间参与者列表
        """
        try:
            participants = RoomParticipant.objects.filter(
                room_id=room_id, status="active"
            ).select_related("user")

            return [
                {
                    "user_id": p.user_id,
                    "username": p.user.username,
                    "display_name": getattr(p.user, "display_name", p.user.username),
                    "role": p.role,
                    "status": p.status,
                    "joined_at": p.joined_at,
                    "is_online": getattr(p.user, "is_online", False),  # type: ignore[attr-defined]
                    "is_verified": getattr(p.user, "is_verified", False),  # type: ignore[attr-defined]
                }
                for p in participants
            ]

        except Exception as e:
            logger.error(f"获取房间参与者失败: {e}")
            return []

    def rate_room(
        self, room_id: str, user_id: str, rating: int, comment: str = ""
    ) -> Dict[str, Any]:
        """
        评价房间
        """
        try:
            room = Room.objects.get(id=room_id)

            # 检查用户是否参与过该房间
            participant = RoomParticipant.objects.filter(room=room, user_id=user_id).first()

            if not participant:
                return {
                    "success": False,
                    "error": "您未参与过该房间",
                }

            # 检查是否已经评价过
            existing_rating = RoomRating.objects.filter(room=room, user_id=user_id).first()

            if existing_rating:
                # 更新评价
                existing_rating.rating = rating
                existing_rating.comment = comment
                existing_rating.updated_at = timezone.now()
                existing_rating.save()
            else:
                # 创建新评价
                RoomRating.objects.create(
                    room=room,
                    user_id=user_id,
                    rating=rating,
                    comment=comment,
                )

            # 更新房间平均评分
            avg_rating = RoomRating.objects.filter(room=room).aggregate(avg=Avg("rating"))["avg"]

            if avg_rating:
                room.average_rating = avg_rating
                room.save(update_fields=["average_rating"])

            logger.info(f"用户 {user_id} 评价房间 {room_id}: {rating}分")

            return {
                "success": True,
                "message": "评价成功",
            }

        except Room.DoesNotExist:
            return {"success": False, "error": "房间不存在"}
        except Exception as e:
            logger.error(f"评价房间失败: {e}")
            return {"success": False, "error": "评价失败"}

    def get_room_stats(self, room_id: str) -> Dict[str, Any]:
        """
        获取房间统计信息
        """
        try:
            room = Room.objects.get(id=room_id)

            # 获取参与者统计
            participant_stats = RoomParticipant.objects.filter(room=room).aggregate(
                total_participants=Count("id"),
                active_participants=Count("id", filter=Q(status="active")),
                male_count=Count("id", filter=Q(user__gender="male")),
                female_count=Count("id", filter=Q(user__gender="female")),
            )

            # 获取评分统计
            rating_stats = RoomRating.objects.filter(room=room).aggregate(
                total_ratings=Count("id"),
                average_rating=Avg("rating"),
            )

            return {
                "room_id": room_id,
                "total_participants": participant_stats["total_participants"],
                "active_participants": participant_stats["active_participants"],
                "male_count": participant_stats["male_count"],
                "female_count": participant_stats["female_count"],
                "total_ratings": rating_stats["total_ratings"] or 0,
                "average_rating": rating_stats["average_rating"] or 0.0,
                "created_at": room.created_at,
                "last_activity": room.last_activity_at,
            }

        except Room.DoesNotExist:
            return {"error": "房间不存在"}
        except Exception as e:
            logger.error(f"获取房间统计失败: {e}")
            return {"error": "获取统计失败"}
