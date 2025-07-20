"""
聊天系统WebSocket消费者
"""

import json
import logging
from typing import Any, Dict

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    ChatNotification,
    ChatParticipant,
    ChatRoom,
    Message,
    MessageRead,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    聊天房间WebSocket消费者
    """

    async def connect(self):
        """建立WebSocket连接"""
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope["user"]

        # 检查用户是否已认证
        if not self.user.is_authenticated:
            await self.close()
            return

        # 检查用户是否是房间参与者
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return

        # 加入房间组
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # 发送连接成功消息
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "room_id": self.room_id,
                    "user_id": str(self.user.id),
                    "timestamp": timezone.now().isoformat(),
                }
            )
        )

        # 通知其他用户有新用户加入
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_joined",
                "user_id": str(self.user.id),
                "username": self.user.display_name or self.user.username,
                "timestamp": timezone.now().isoformat(),
            },
        )

    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        # 离开房间组
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # 通知其他用户有用户离开
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_left",
                "user_id": str(self.user.id),
                "username": self.user.display_name or self.user.username,
                "timestamp": timezone.now().isoformat(),
            },
        )

    async def receive(self, text_data):
        """接收WebSocket消息"""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "chat_message":
                await self.handle_chat_message(data)
            elif message_type == "typing":
                await self.handle_typing(data)
            elif message_type == "read_receipt":
                await self.handle_read_receipt(data)
            else:
                logger.warning(f"未知的消息类型: {message_type}")

        except json.JSONDecodeError:
            logger.error("无效的JSON格式")
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")

    async def handle_chat_message(self, data):
        """处理聊天消息"""
        content = data.get("content", "").strip()
        message_type = data.get("message_type", "text")

        if not content:
            return

        # 保存消息到数据库
        message = await self.save_message(content, message_type)

        # 广播消息给房间内所有用户
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_id": str(message.id),
                "content": message.content,
                "message_type": message.message_type,
                "sender_id": str(message.sender.id),
                "sender_name": message.sender.display_name or message.sender.username,
                "timestamp": message.created_at.isoformat(),
                "media_url": message.media_url or "",
                "media_size": message.media_size,
                "media_duration": message.media_duration,
            },
        )

    async def handle_typing(self, data):
        """处理正在输入状态"""
        is_typing = data.get("is_typing", False)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_typing",
                "user_id": str(self.user.id),
                "username": self.user.display_name or self.user.username,
                "is_typing": is_typing,
                "timestamp": timezone.now().isoformat(),
            },
        )

    async def handle_read_receipt(self, data):
        """处理已读回执"""
        message_id = data.get("message_id")
        if message_id:
            await self.mark_message_read(message_id)

    async def chat_message(self, event):
        """发送聊天消息给WebSocket"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat_message",
                    "message_id": event["message_id"],
                    "content": event["content"],
                    "message_type": event["message_type"],
                    "sender_id": event["sender_id"],
                    "sender_name": event["sender_name"],
                    "timestamp": event["timestamp"],
                    "media_url": event["media_url"],
                    "media_size": event["media_size"],
                    "media_duration": event["media_duration"],
                }
            )
        )

    async def user_typing(self, event):
        """发送用户正在输入状态"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_typing",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "is_typing": event["is_typing"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def user_joined(self, event):
        """发送用户加入通知"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_joined",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def user_left(self, event):
        """发送用户离开通知"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_left",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    @database_sync_to_async
    def check_participant(self):
        """检查用户是否是房间参与者"""
        try:
            chat_room = ChatRoom.objects.get(room_id=self.room_id)
            return ChatParticipant.objects.filter(
                chat_room=chat_room, user=self.user, is_active=True
            ).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content, message_type):
        """保存消息到数据库"""
        chat_room = ChatRoom.objects.get(room_id=self.room_id)

        message = Message.objects.create(
            chat_room=chat_room,
            sender=self.user,
            content=content,
            message_type=message_type,
            status="sent",
        )

        # 更新房间统计信息
        chat_room.message_count += 1
        chat_room.last_message_at = timezone.now()
        chat_room.save(update_fields=["message_count", "last_message_at"])

        return message

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """标记消息为已读"""
        try:
            message = Message.objects.get(id=message_id)
            MessageRead.objects.get_or_create(message=message, user=self.user)
            message.read_count = message.read_records.count()
            message.save(update_fields=["read_count"])
        except Message.DoesNotExist:
            pass


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    通知WebSocket消费者
    """

    async def connect(self):
        """建立WebSocket连接"""
        self.user = self.scope["user"]

        # 检查用户是否已认证
        if not self.user.is_authenticated:
            await self.close()
            return

        self.user_group_name = f"user_{self.user.id}_notifications"

        # 加入用户通知组
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()

        # 发送连接成功消息
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification_connection_established",
                    "user_id": str(self.user.id),
                    "timestamp": timezone.now().isoformat(),
                }
            )
        )

    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data):
        """接收WebSocket消息"""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "mark_read":
                await self.handle_mark_read(data)
            else:
                logger.warning(f"未知的通知消息类型: {message_type}")

        except json.JSONDecodeError:
            logger.error("无效的JSON格式")
        except Exception as e:
            logger.error(f"处理通知消息时出错: {e}")

    async def handle_mark_read(self, data):
        """处理标记已读"""
        notification_id = data.get("notification_id")
        if notification_id:
            await self.mark_notification_read(notification_id)

    async def notification_message(self, event):
        """发送通知消息"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",
                    "notification_id": event["notification_id"],
                    "notification_type": event["notification_type"],
                    "title": event["title"],
                    "content": event["content"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """标记通知为已读"""
        try:
            notification = ChatNotification.objects.get(id=notification_id, user=self.user)
            notification.mark_as_read()
        except ChatNotification.DoesNotExist:
            pass
