"""
聊天系统服务层
"""

import logging
import os
import uuid
from typing import Any, Dict, List, Optional

import magic
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q
from django.utils import timezone
from PIL import Image

from .models import ChatNotification, ChatParticipant, ChatRoom, Message

logger = logging.getLogger(__name__)


class FileUploadService:
    """
    文件上传服务
    """

    ALLOWED_IMAGE_TYPES = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    ]
    ALLOWED_VIDEO_TYPES = ["video/mp4", "video/avi", "video/mov", "video/webm"]
    ALLOWED_AUDIO_TYPES = ["audio/mp3", "audio/wav", "audio/aac", "audio/m4a"]
    ALLOWED_FILE_TYPES = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
    ]

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_AUDIO_SIZE = 20 * 1024 * 1024  # 20MB

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def upload_file(
        self, file, chat_room_id: str, sender_id: str, message_type: str
    ) -> Dict[str, Any]:
        """
        上传文件并创建消息

        Args:
            file: 上传的文件
            chat_room_id: 聊天房间ID
            sender_id: 发送者ID
            message_type: 消息类型

        Returns:
            包含文件信息和消息数据的字典
        """
        try:
            # 验证文件
            validation_result = self._validate_file(file, message_type)
            if not validation_result["valid"]:
                return validation_result

            # 生成文件名
            file_extension = self._get_file_extension(file.name)
            filename = f"{uuid.uuid4()}{file_extension}"

            # 确定存储路径
            storage_path = self._get_storage_path(message_type, filename)

            # 保存文件
            file_path = default_storage.save(storage_path, ContentFile(file.read()))

            # 获取文件信息
            file_info = self._get_file_info(file, file_path, message_type)

            # 创建消息
            message_data = self._create_message_data(
                chat_room_id, sender_id, message_type, file_info
            )

            return {
                "success": True,
                "file_path": file_path,
                "file_url": default_storage.url(file_path),
                "file_info": file_info,
                "message_data": message_data,
            }

        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return {"success": False, "error": "文件上传失败"}

    def _validate_file(self, file, message_type: str) -> Dict[str, Any]:
        """验证文件"""
        # 检查文件大小
        if file.size > self.MAX_FILE_SIZE:
            return {"valid": False, "error": "文件大小超过限制"}

        # 检查文件类型
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # 重置文件指针

        allowed_types = []
        max_size = self.MAX_FILE_SIZE

        if message_type == "image":
            allowed_types = self.ALLOWED_IMAGE_TYPES
            max_size = self.MAX_IMAGE_SIZE
        elif message_type == "video":
            allowed_types = self.ALLOWED_VIDEO_TYPES
            max_size = self.MAX_VIDEO_SIZE
        elif message_type == "audio":
            allowed_types = self.ALLOWED_AUDIO_TYPES
            max_size = self.MAX_AUDIO_SIZE
        elif message_type == "file":
            allowed_types = self.ALLOWED_FILE_TYPES

        if mime_type not in allowed_types:
            return {"valid": False, "error": "不支持的文件类型"}

        if file.size > max_size:
            return {
                "valid": False,
                "error": f"文件大小超过{max_size // (1024*1024)}MB限制",
            }

        return {"valid": True}

    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(filename)[1]

    def _get_storage_path(self, message_type: str, filename: str) -> str:
        """获取存储路径"""
        return f"chat/{message_type}/{timezone.now().strftime('%Y/%m/%d')}/{filename}"

    def _get_file_info(self, file, file_path: str, message_type: str) -> Dict[str, Any]:
        """获取文件信息"""
        file_info = {"size": file.size, "path": file_path, "name": file.name}

        if message_type == "image":
            file_info.update(self._get_image_info(file))
        elif message_type == "video":
            file_info.update(self._get_video_info(file))
        elif message_type == "audio":
            file_info.update(self._get_audio_info(file))

        return file_info

    def _get_image_info(self, file) -> Dict[str, Any]:
        """获取图片信息"""
        try:
            with Image.open(file) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                }
        except Exception as e:
            logger.error(f"获取图片信息失败: {e}")
            return {}

    def _get_video_info(self, file) -> Dict[str, Any]:
        """获取视频信息"""
        # 这里可以集成ffmpeg来获取视频信息
        # 暂时返回空字典
        return {}

    def _get_audio_info(self, file) -> Dict[str, Any]:
        """获取音频信息"""
        # 这里可以集成音频处理库来获取音频信息
        # 暂时返回空字典
        return {}

    def _create_message_data(
        self,
        chat_room_id: str,
        sender_id: str,
        message_type: str,
        file_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """创建消息数据"""
        return {
            "chat_room_id": chat_room_id,
            "sender_id": sender_id,
            "message_type": message_type,
            "content": f"发送了{message_type}文件",
            "media_url": file_info.get("path", ""),
            "media_size": file_info.get("size", 0),
            "media_duration": file_info.get("duration", 0),
        }


class MessageSearchService:
    """
    消息搜索服务
    """

    def search_messages(
        self,
        user_id: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        搜索消息

        Args:
            user_id: 用户ID
            query: 搜索关键词
            filters: 过滤条件

        Returns:
            消息列表
        """
        try:
            # 获取用户参与的聊天房间
            user_rooms = ChatRoom.objects.filter(participants=user_id)

            # 构建查询
            q_objects: Q = Q(content__icontains=query)
            if filters is None:
                filters = {}

            if filters.get("room_type"):
                q_objects &= Q(chat_room__room_type=filters["room_type"])

                if filters.get("message_type"):
                    q_objects &= Q(message_type=filters["message_type"])

                if filters.get("date_from"):
                    q_objects &= Q(created_at__date__gte=filters["date_from"])

                if filters.get("date_to"):
                    q_objects &= Q(created_at__date__lte=filters["date_to"])

            # 执行搜索
            messages = (
                Message.objects.filter(
                    chat_room__in=user_rooms,
                    status__in=["sent", "delivered", "read"],
                )
                .filter(q_objects)
                .order_by("-created_at")
            )

            # 限制结果数量
            messages = messages[:100]

            # 序列化结果
            results = []
            for message in messages:
                results.append(
                    {
                        "id": str(message.id),
                        "content": message.content,
                        "message_type": message.message_type,
                        "sender": {
                            "id": str(message.sender.id),
                            "name": message.sender.display_name or message.sender.username,
                        },
                        "chat_room": {
                            "id": str(message.chat_room.id),
                            "name": message.chat_room.name,
                        },
                        "created_at": message.created_at.isoformat(),
                        "media_url": message.media_url or "",
                        "media_size": message.media_size,
                    }
                )

            return results

        except Exception as e:
            logger.error(f"消息搜索失败: {e}")
            return []

    def search_rooms(
        self,
        user_id: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        搜索聊天房间

        Args:
            user_id: 用户ID
            query: 搜索关键词
            filters: 过滤条件

        Returns:
            聊天房间列表
        """
        try:
            # 构建查询
            q_objects = Q(name__icontains=query) | Q(description__icontains=query)

            if filters:
                if filters.get("room_type"):
                    q_objects &= Q(room_type=filters["room_type"])

                if filters.get("is_private") is not None:
                    q_objects &= Q(is_private=filters["is_private"])

            # 获取用户参与的或公开的房间
            rooms = (
                ChatRoom.objects.filter(Q(participants=user_id) | Q(is_private=False))
                .filter(q_objects)
                .distinct()
                .order_by("-last_message_at")
            )

            # 序列化结果
            results = []
            for room in rooms:
                results.append(
                    {
                        "id": str(room.id),
                        "room_id": room.room_id,
                        "name": room.name,
                        "description": room.description,
                        "room_type": room.room_type,
                        "message_count": room.message_count,
                        "last_message_at": (
                            room.last_message_at.isoformat() if room.last_message_at else None
                        ),
                        "current_participants_count": room.current_participants_count,
                    }
                )

            return results

        except Exception as e:
            logger.error(f"聊天房间搜索失败: {e}")
            return []


class NotificationService:
    """
    通知服务
    """

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        content: str,
        chat_room_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> bool:
        """
        发送通知

        Args:
            user_id: 用户ID
            notification_type: 通知类型
            title: 通知标题
            content: 通知内容
            chat_room_id: 聊天房间ID
            message_id: 消息ID

        Returns:
            是否发送成功
        """
        try:
            # 创建通知记录
            notification = ChatNotification.objects.create(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                content=content,
                chat_room_id=chat_room_id,
                message_id=message_id,
            )

            # 通过WebSocket发送实时通知
            async_to_sync(self.channel_layer.group_send)(
                f"user_{user_id}_notifications",
                {
                    "type": "notification_message",
                    "notification_id": str(notification.id),
                    "notification_type": notification_type,
                    "title": title,
                    "content": content,
                    "timestamp": notification.created_at.isoformat(),
                },
            )

            return True

        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return False

    def send_message_notification(self, message: Message) -> None:
        """
        发送消息通知

        Args:
            message: 消息对象
        """
        try:
            # 获取房间内其他参与者
            participants = ChatParticipant.objects.filter(
                chat_room=message.chat_room,
                user__ne=message.sender,
                is_active=True,
            )

            for participant in participants:
                # 检查用户是否在线（这里可以扩展为检查用户在线状态）
                self.send_notification(
                    user_id=participant.user.id,
                    notification_type="message",
                    title=f"新消息 - {message.chat_room.name}",
                    content=f"{message.sender.display_name or message.sender.username}: {message.content[:50]}...",
                    chat_room_id=str(message.chat_room.id),
                    message_id=str(message.id),
                )

        except Exception as e:
            logger.error(f"发送消息通知失败: {e}")

    def send_invitation_notification(self, invitation) -> None:
        """
        发送邀请通知

        Args:
            invitation: 邀请对象
        """
        try:
            self.send_notification(
                user_id=invitation.invitee.id,
                notification_type="invitation",
                title="聊天邀请",
                content=f'{invitation.inviter.display_name or invitation.inviter.username} 邀请您加入聊天房间 "{invitation.chat_room.name}"',
                chat_room_id=str(invitation.chat_room.id),
            )

        except Exception as e:
            logger.error(f"发送邀请通知失败: {e}")


class ChatRoomService:
    """
    聊天房间服务
    """

    def create_private_chat(self, user1_id: str, user2_id: str) -> Optional[ChatRoom]:
        """
        创建私聊房间

        Args:
            user1_id: 用户1 ID
            user2_id: 用户2 ID

        Returns:
            聊天房间对象
        """
        try:
            # 检查是否已存在私聊房间
            existing_room = (
                ChatRoom.objects.filter(room_type="private", participants=user1_id)
                .filter(participants=user2_id)
                .first()
            )

            if existing_room:
                return existing_room

            # 创建新的私聊房间
            room_name = f"私聊_{user1_id}_{user2_id}"
            chat_room = ChatRoom.objects.create(
                name=room_name,
                room_type="private",
                is_private=True,
                creator_id=user1_id,
            )

            # 添加参与者
            ChatParticipant.objects.bulk_create(
                [
                    ChatParticipant(chat_room=chat_room, user_id=user1_id, role="member"),
                    ChatParticipant(chat_room=chat_room, user_id=user2_id, role="member"),
                ]
            )

            return chat_room

        except Exception as e:
            logger.error(f"创建私聊房间失败: {e}")
            return None

    def get_user_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的聊天列表

        Args:
            user_id: 用户ID

        Returns:
            聊天列表
        """
        try:
            # 获取用户参与的聊天房间
            chat_rooms = ChatRoom.objects.filter(participants=user_id).order_by("-last_message_at")

            results = []
            for room in chat_rooms:
                # 获取最后一条消息
                last_message = room.messages.order_by("-created_at").first()

                # 获取未读消息数
                unread_count = room.messages.filter(
                    ~Q(sender_id=user_id), ~Q(read_records__user_id=user_id)
                ).count()

                results.append(
                    {
                        "id": str(room.id),
                        "room_id": room.room_id,
                        "name": room.name,
                        "room_type": room.room_type,
                        "last_message": (
                            {
                                "content": (last_message.content if last_message else ""),
                                "sender_name": (
                                    last_message.sender.display_name if last_message else ""
                                ),
                                "timestamp": (
                                    last_message.created_at.isoformat() if last_message else None
                                ),
                            }
                            if last_message
                            else None
                        ),
                        "unread_count": unread_count,
                        "participants_count": room.current_participants_count,
                        "last_message_at": (
                            room.last_message_at.isoformat() if room.last_message_at else None
                        ),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"获取用户聊天列表失败: {e}")
            return []
