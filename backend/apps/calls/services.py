"""
通话系统WebRTC服务
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg, Q
from django.utils import timezone

from .models import (
    Call,
    CallInvitation,
    CallParticipant,
    CallQualityLog,
    CallRecording,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class WebRTCService:
    """
    WebRTC服务
    """

    def __init__(self):
        self.active_connections = {}

    def create_peer_connection(self, call_id: str, user_id: str, connection_id: str) -> Dict:
        """
        创建对等连接
        """
        try:
            call = Call.objects.get(id=call_id)
            participant = CallParticipant.objects.get(call=call, user_id=user_id)

            # 更新连接信息
            participant.connection_id = connection_id
            participant.save(update_fields=["connection_id"])

            # 缓存连接信息
            if call_id not in self.active_connections:
                self.active_connections[call_id] = {}

            self.active_connections[call_id][user_id] = {
                "connection_id": connection_id,
                "participant": participant,
                "created_at": timezone.now(),
            }

            logger.info(f"创建对等连接: call={call_id}, user={user_id}, connection={connection_id}")

            return {
                "success": True,
                "call_id": call_id,
                "connection_id": connection_id,
                "participants": self.get_call_participants(call_id),
            }

        except (Call.DoesNotExist, CallParticipant.DoesNotExist) as e:
            logger.error(f"创建对等连接失败: {e}")
            return {"success": False, "error": "通话或参与者不存在"}

    def remove_peer_connection(self, call_id: str, user_id: str) -> Dict:
        """
        移除对等连接
        """
        try:
            # 从缓存中移除
            if call_id in self.active_connections:
                if user_id in self.active_connections[call_id]:
                    del self.active_connections[call_id][user_id]

                # 如果通话没有活跃连接，清理通话缓存
                if not self.active_connections[call_id]:
                    del self.active_connections[call_id]

            # 更新参与者状态
            participant = CallParticipant.objects.get(call_id=call_id, user_id=user_id)
            participant.status = "disconnected"
            participant.left_at = timezone.now()
            participant.save()

            logger.info(f"移除对等连接: call={call_id}, user={user_id}")

            return {"success": True, "message": "连接已移除"}

        except CallParticipant.DoesNotExist:
            logger.warning(f"参与者不存在: call={call_id}, user={user_id}")
            return {"success": True, "message": "连接已移除"}

    def forward_signaling_message(
        self, call_id: str, from_user_id: str, message_type: str, data: Dict
    ) -> Dict:
        """
        转发信令消息
        """
        try:
            # 获取通话中的所有其他参与者
            participants = CallParticipant.objects.filter(
                call_id=call_id,
                user_id__ne=from_user_id,
                status="connected",
            )

            target_connections = []
            for participant in participants:
                if hasattr(participant, "connection_id") and participant.connection_id:
                    target_connections.append(
                        {
                            "user_id": participant.user_id,
                            "connection_id": participant.connection_id,
                        }
                    )

            # 这里应该通过WebSocket发送消息给目标连接
            # 暂时返回目标连接信息
            logger.info(
                f"转发信令消息: call={call_id}, from={from_user_id}, type={message_type}, targets={len(target_connections)}"
            )

            return {
                "success": True,
                "target_connections": target_connections,
                "message_type": message_type,
                "data": data,
            }

        except Exception as e:
            logger.error(f"转发信令消息失败: {e}")
            return {"success": False, "error": "转发消息失败"}

    def get_call_participants(self, call_id: str) -> List[Dict]:
        """
        获取通话参与者信息
        """
        try:
            participants = CallParticipant.objects.filter(
                call_id=call_id, status="connected"
            ).select_related("user")

            return [
                {
                    "user_id": p.user_id,
                    "username": p.user.username,
                    "display_name": getattr(p.user, "display_name", p.user.username),
                    "role": p.role,
                    "status": p.status,
                    "connection_id": getattr(p, "connection_id", None),
                    "is_video_enabled": p.is_video_enabled,
                    "is_muted": p.is_muted,
                    "is_screen_sharing": p.is_screen_sharing,
                }
                for p in participants
            ]

        except Exception as e:
            logger.error(f"获取通话参与者失败: {e}")
            return []

    def update_participant_media_state(self, call_id: str, user_id: str, media_state: Dict) -> Dict:
        """
        更新参与者媒体状态
        """
        try:
            participant = CallParticipant.objects.get(call_id=call_id, user_id=user_id)

            # 更新媒体状态
            if "is_video_enabled" in media_state:
                participant.is_video_enabled = media_state["is_video_enabled"]
            if "is_muted" in media_state:
                participant.is_muted = media_state["is_muted"]
            if "is_screen_sharing" in media_state:
                participant.is_screen_sharing = media_state["is_screen_sharing"]

            participant.save()

            # 通知其他参与者
            self.notify_participants_state_change(call_id, user_id, media_state)

            return {"success": True, "message": "媒体状态已更新"}

        except CallParticipant.DoesNotExist:
            return {"success": False, "error": "参与者不存在"}

    def notify_participants_state_change(self, call_id: str, user_id: str, state_change: Dict):
        """
        通知参与者状态变化
        """
        try:
            participants = CallParticipant.objects.filter(
                call_id=call_id,
                user_id__ne=user_id,
                status="connected",
            )

            for participant in participants:
                if hasattr(participant, "connection_id") and participant.connection_id:
                    # 这里应该通过WebSocket发送状态变化通知
                    logger.info(
                        f"通知状态变化: call={call_id}, to={participant.user_id}, state={state_change}"
                    )

        except Exception as e:
            logger.error(f"通知状态变化失败: {e}")


class CallQualityService:
    """
    通话质量服务
    """

    @staticmethod
    def record_quality_data(call_id: str, user_id: str, quality_data: Dict) -> Dict:
        """
        记录质量数据
        """
        try:
            call = Call.objects.get(id=call_id)
            participant = CallParticipant.objects.get(call=call, user_id=user_id)

            # 创建质量日志
            CallQualityLog.objects.create(
                call=call,
                participant=participant,
                audio_quality=quality_data.get("audio_quality", 0.0),
                video_quality=quality_data.get("video_quality", 0.0),
                network_quality=quality_data.get("network_quality", 0.0),
                packet_loss=quality_data.get("packet_loss", 0.0),
                latency=quality_data.get("latency", 0.0),
                jitter=quality_data.get("jitter", 0.0),
                bandwidth=quality_data.get("bandwidth", 0.0),
                cpu_usage=quality_data.get("cpu_usage", 0.0),
                memory_usage=quality_data.get("memory_usage", 0.0),
                battery_level=quality_data.get("battery_level", 0.0),
            )

            # 更新参与者的质量指标
            participant.network_quality = quality_data.get("network_quality", 0.0)
            participant.audio_level = quality_data.get("audio_level", 0.0)
            participant.video_quality = quality_data.get("video_quality", {})
            participant.save(
                update_fields=[
                    "network_quality",
                    "audio_level",
                    "video_quality",
                ]
            )

            logger.info(f"记录质量数据: call={call_id}, user={user_id}")

            return {"success": True, "message": "质量数据已记录"}

        except (Call.DoesNotExist, CallParticipant.DoesNotExist) as e:
            logger.error(f"记录质量数据失败: {e}")
            return {"success": False, "error": "通话或参与者不存在"}

    @staticmethod
    def get_call_quality_stats(call_id: str) -> Dict:
        """
        获取通话质量统计
        """
        try:
            call = Call.objects.get(id=call_id)
            quality_logs = CallQualityLog.objects.filter(call=call)

            if not quality_logs.exists():
                return {
                    "call_id": call_id,
                    "total_records": 0,
                    "average_audio_quality": 0.0,
                    "average_video_quality": 0.0,
                    "average_network_quality": 0.0,
                    "average_packet_loss": 0.0,
                    "average_latency": 0.0,
                    "average_jitter": 0.0,
                    "average_bandwidth": 0.0,
                }

            stats = quality_logs.aggregate(
                total_records=models.Count("id"),
                average_audio_quality=Avg("audio_quality"),
                average_video_quality=Avg("video_quality"),
                average_network_quality=Avg("network_quality"),
                average_packet_loss=Avg("packet_loss"),
                average_latency=Avg("latency"),
                average_jitter=Avg("jitter"),
                average_bandwidth=Avg("bandwidth"),
            )

            stats["call_id"] = call_id
            return stats

        except Call.DoesNotExist:
            return {"error": "通话不存在"}


class CallRecordingService:
    """
    通话录制服务
    """

    @staticmethod
    def start_recording(call_id: str, recording_config: Dict) -> Dict:
        """
        开始录制
        """
        try:
            call = Call.objects.get(id=call_id)

            # 创建录制记录
            recording = CallRecording.objects.create(
                call=call,
                format=recording_config.get("format", "mp4"),
                quality=recording_config.get("quality", "medium"),
            )

            # 更新通话状态
            call.is_recording = True
            call.save(update_fields=["is_recording"])

            logger.info(f"开始录制: call={call_id}, recording={recording.id}")

            return {
                "success": True,
                "recording_id": recording.id,
                "message": "录制已开始",
            }

        except Call.DoesNotExist:
            return {"success": False, "error": "通话不存在"}

    @staticmethod
    def stop_recording(recording_id: str) -> Dict:
        """
        停止录制
        """
        try:
            recording = CallRecording.objects.get(id=recording_id)
            call = recording.call

            # 更新录制状态
            recording.is_processed = True
            recording.save(update_fields=["is_processed"])

            # 更新通话状态
            call.is_recording = False
            call.save(update_fields=["is_recording"])

            logger.info(f"停止录制: recording={recording_id}")

            return {
                "success": True,
                "recording_id": recording_id,
                "message": "录制已停止",
            }

        except CallRecording.DoesNotExist:
            return {"success": False, "error": "录制记录不存在"}

    def get_call_recording(self, call_id: str) -> Optional[Dict]:
        """
        获取通话录制
        """
        try:
            recording = CallRecording.objects.get(call_id=call_id)
            return {
                "id": recording.id,
                "file_path": recording.file_path,
                "file_url": recording.file_url,
                "file_size": recording.file_size,
                "duration": recording.duration,
                "format": recording.format,
                "quality": recording.quality,
                "created_at": recording.created_at,
            }
        except CallRecording.DoesNotExist:
            return None

    def delete_call_recording(self, call_id: str) -> bool:
        """
        删除通话录制
        """
        try:
            recording = CallRecording.objects.get(call_id=call_id)
            recording.delete()
            return True
        except CallRecording.DoesNotExist:
            return False

    def list_call_recordings(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        列出通话录制
        """
        recordings = CallRecording.objects.filter(call__initiator_id=user_id).order_by(
            "-created_at"
        )[:limit]

        return [
            {
                "id": r.id,
                "call_id": r.call_id,
                "file_path": r.file_path,
                "file_url": r.file_url,
                "file_size": r.file_size,
                "duration": r.duration,
                "format": r.format,
                "quality": r.quality,
                "created_at": r.created_at,
            }
            for r in recordings
        ]

    def get_recording_url(self, recording_id: str) -> Optional[str]:
        """
        获取录制文件URL
        """
        try:
            recording = CallRecording.objects.get(id=recording_id)
            return recording.file_url
        except CallRecording.DoesNotExist:
            return None
