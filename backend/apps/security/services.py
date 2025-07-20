import json
import logging
import re
from typing import Dict, List, Optional, Tuple

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

from .models import ScreenRecordingDetection, SecurityAlert, SecurityPolicy

logger = logging.getLogger(__name__)


class ScreenRecordingDetector:
    """
    录屏检测器
    """

    def __init__(self):
        self.suspicious_patterns = {
            "recording_apps": [
                "obs",
                "bandicam",
                "fraps",
                "camtasia",
                "screencast",
                "recordit",
                "licecap",
                "gifox",
                "kap",
                "screencastify",
                "loom",
                "zoom",
                "teams",
                "skype",
                "discord",
                "录屏",
                "录制",
                "屏幕录制",
                "录屏软件",
                "录制软件",
            ],
            "virtual_machines": [
                "vmware",
                "virtualbox",
                "parallels",
                "hyper-v",
                "qemu",
                "xen",
                "kvm",
                "docker",
                "container",
            ],
            "debugging_tools": [
                "fiddler",
                "charles",
                "burp",
                "wireshark",
                "tcpdump",
                "debugger",
                "ida",
                "ollydbg",
                "x64dbg",
                "ghidra",
            ],
            "suspicious_processes": [
                "cheatengine",
                "artmoney",
                "gamehack",
                "trainer",
                "hack",
                "cheat",
                "bot",
                "auto",
                "macro",
            ],
        }

    def detect_screen_recording(self, user: User, request_data: Dict) -> Dict:
        """
        检测录屏行为

        Args:
            user: 用户对象
            request_data: 请求数据

        Returns:
            检测结果
        """
        detection_result: dict = {
            "detected": False,
            "detection_type": None,
            "severity": "low",
            "details": {},
            "action_required": False,
        }

        # 1. 检测用户代理字符串
        user_agent = request_data.get("user_agent", "")
        if user_agent:
            ua_detection = self._detect_user_agent(user_agent)
            if ua_detection["detected"]:
                detection_result.update(ua_detection)

        # 2. 检测设备信息
        device_info = request_data.get("device_info", {})
        if device_info:
            device_detection = self._detect_device_info(device_info)
            if device_detection["detected"]:
                detection_result.update(device_detection)

        # 3. 检测屏幕属性
        screen_info = request_data.get("screen_info", {})
        if screen_info:
            screen_detection = self._detect_screen_properties(screen_info)
            if screen_detection["detected"]:
                detection_result.update(screen_detection)

        # 4. 检测运行进程
        processes = request_data.get("processes", [])
        if processes:
            process_detection = self._detect_suspicious_processes(processes)
            if process_detection["detected"]:
                detection_result.update(process_detection)

        # 5. 检测网络连接
        network_info = request_data.get("network_info", {})
        if network_info:
            network_detection = self._detect_network_anomalies(network_info)
            if network_detection["detected"]:
                detection_result.update(network_detection)

        # 6. 检测行为模式
        behavior_pattern = request_data.get("behavior_pattern", {})
        if behavior_pattern:
            behavior_detection = self._detect_behavior_pattern(behavior_pattern)
            if behavior_detection["detected"]:
                detection_result.update(behavior_detection)

        return detection_result

    def _detect_user_agent(self, user_agent: str) -> Dict:
        """检测用户代理字符串"""
        user_agent_lower = user_agent.lower()

        for category, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if pattern.lower() in user_agent_lower:
                    return {
                        "detected": True,
                        "detection_type": "recording_app",
                        "severity": "medium",
                        "details": {
                            "category": category,
                            "pattern": pattern,
                            "user_agent": user_agent,
                        },
                    }

        return {"detected": False}

    def _detect_device_info(self, device_info: Dict) -> Dict:
        """检测设备信息"""
        # 检测虚拟机特征
        vm_indicators = [
            "vmware",
            "virtualbox",
            "parallels",
            "hyper-v",
            "qemu",
            "xen",
            "kvm",
            "docker",
        ]

        device_name = device_info.get("device_name", "").lower()
        platform = device_info.get("platform", "").lower()
        manufacturer = device_info.get("manufacturer", "").lower()

        for indicator in vm_indicators:
            if indicator in device_name or indicator in platform or indicator in manufacturer:
                return {
                    "detected": True,
                    "detection_type": "virtual_display",
                    "severity": "high",
                    "details": {
                        "indicator": indicator,
                        "device_info": device_info,
                    },
                }

        return {"detected": False}

    def _detect_screen_properties(self, screen_info: Dict) -> Dict:
        """检测屏幕属性"""
        # 检测异常屏幕分辨率
        width = screen_info.get("width", 0)
        height = screen_info.get("height", 0)

        # 检测过大的分辨率（可能是虚拟显示器）
        if width > 7680 or height > 4320:  # 8K
            return {
                "detected": True,
                "detection_type": "virtual_display",
                "severity": "medium",
                "details": {
                    "reason": "异常屏幕分辨率",
                    "resolution": f"{width}x{height}",
                    "screen_info": screen_info,
                },
            }

        # 检测异常的色彩深度
        color_depth = screen_info.get("colorDepth", 24)
        if color_depth < 16 or color_depth > 32:
            return {
                "detected": True,
                "detection_type": "virtual_display",
                "severity": "low",
                "details": {
                    "reason": "异常色彩深度",
                    "color_depth": color_depth,
                    "screen_info": screen_info,
                },
            }

        return {"detected": False}

    def _detect_suspicious_processes(self, processes: List[str]) -> Dict:
        """检测可疑进程"""
        processes_lower = [p.lower() for p in processes]

        for category, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                for process in processes_lower:
                    if pattern in process:
                        return {
                            "detected": True,
                            "detection_type": "recording_app",
                            "severity": "high",
                            "details": {
                                "category": category,
                                "pattern": pattern,
                                "process": process,
                                "all_processes": processes,
                            },
                        }

        return {"detected": False}

    def _detect_network_anomalies(self, network_info: Dict) -> Dict:
        """检测网络异常"""
        # 检测异常的连接数
        connection_count = network_info.get("connection_count", 0)
        if connection_count > 100:  # 异常多的连接
            return {
                "detected": True,
                "detection_type": "suspicious_activity",
                "severity": "medium",
                "details": {
                    "reason": "异常网络连接数",
                    "connection_count": connection_count,
                    "network_info": network_info,
                },
            }

        return {"detected": False}

    def _detect_behavior_pattern(self, behavior_pattern: Dict) -> Dict:
        """检测行为模式"""
        # 检测频繁的截图行为
        screenshot_count = behavior_pattern.get("screenshot_count", 0)
        time_window = behavior_pattern.get("time_window", 3600)  # 1小时

        if screenshot_count > 10 and time_window <= 3600:  # 1小时内超过10次截图
            return {
                "detected": True,
                "detection_type": "screenshot",
                "severity": "medium",
                "details": {
                    "reason": "频繁截图行为",
                    "screenshot_count": screenshot_count,
                    "time_window": time_window,
                    "behavior_pattern": behavior_pattern,
                },
            }

        return {"detected": False}


class SecurityManager:
    """
    安全管理器
    """

    def __init__(self):
        self.detector = ScreenRecordingDetector()

    def process_detection(self, user: User, request_data: Dict) -> Dict:
        """
        处理检测结果

        Args:
            user: 用户对象
            request_data: 请求数据

        Returns:
            处理结果
        """
        # 执行检测
        detection_result = self.detector.detect_screen_recording(user, request_data)

        if detection_result["detected"]:
            # 记录检测
            detection_record = self._record_detection(user, request_data, detection_result)

            # 检查策略
            policy_action = self._check_policy(user, detection_result)

            # 创建警报
            if policy_action.get("create_alert", False):
                self._create_security_alert(user, detection_result, detection_record)

            # 执行防护措施
            protection_result = self._apply_protection(user, detection_result, policy_action)

            return {
                "detected": True,
                "action_taken": policy_action.get("action", "warn"),
                "message": policy_action.get("message", "检测到可疑行为"),
                "detection_id": str(detection_record.detection_id),
                "protection_applied": protection_result,
            }

        return {"detected": False}

    def _record_detection(
        self, user: User, request_data: Dict, detection_result: Dict
    ) -> ScreenRecordingDetection:
        """记录检测结果"""
        return ScreenRecordingDetection.objects.create(
            user=user,
            detection_type=detection_result["detection_type"],
            severity=detection_result["severity"],
            ip_address=request_data.get("ip_address", ""),
            user_agent=request_data.get("user_agent", ""),
            device_info=request_data.get("device_info", {}),
            detection_details=detection_result["details"],
        )

    def _check_policy(self, user: User, detection_result: Dict) -> Dict:
        """检查安全策略"""
        try:
            policy = SecurityPolicy.objects.get(policy_type="screen_recording")
        except SecurityPolicy.DoesNotExist:
            # 使用默认策略
            policy = SecurityPolicy.objects.create(
                policy_type="screen_recording",
                is_enabled=True,
                detection_threshold=3,
                action_on_detection="warn",
                cooldown_period=300,
            )

        if not policy.is_enabled:
            return {"action": "ignore", "message": "防护已禁用"}

        # 检查检测次数
        recent_detections = ScreenRecordingDetection.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timezone.timedelta(seconds=policy.cooldown_period),
        ).count()

        if recent_detections >= policy.detection_threshold:
            return {
                "action": policy.action_on_detection,
                "message": f"检测到{recent_detections}次可疑行为",
                "create_alert": True,
            }

        return {
            "action": "warn",
            "message": "检测到可疑行为",
            "create_alert": False,
        }

    def _create_security_alert(
        self,
        user: User,
        detection_result: Dict,
        detection_record: ScreenRecordingDetection,
    ):
        """创建安全警报"""
        alert_type = "screen_recording"
        priority = "high" if detection_result["severity"] in ["high", "critical"] else "medium"

        SecurityAlert.objects.create(
            user=user,
            alert_type=alert_type,
            priority=priority,
            title=f'检测到录屏行为 - {detection_result["detection_type"]}',
            message="系统检测到可疑的录屏行为，请确认是否为本人操作。",
            details={
                "detection_id": str(detection_record.detection_id),
                "detection_type": detection_result["detection_type"],
                "severity": detection_result["severity"],
                "details": detection_result["details"],
            },
        )

    def _apply_protection(self, user: User, detection_result: Dict, policy_action: Dict) -> Dict:
        """应用防护措施"""
        action = policy_action.get("action", "warn")
        protection_result = {"action_applied": action, "measures": []}

        if action == "block":
            # 临时阻止用户访问
            cache_key = f"user_blocked_{user.id}"
            cache.set(cache_key, True, timeout=3600)  # 1小时
            protection_result["measures"].append("用户访问被临时阻止")

        elif action == "ban":
            # 永久封禁用户
            user.is_active = False
            user.save()
            protection_result["measures"].append("用户账户已被封禁")

        # 记录防护措施
        detection_record = (
            ScreenRecordingDetection.objects.filter(user=user).order_by("-created_at").first()
        )

        if detection_record:
            detection_record.action_taken = action
            detection_record.save()

        return protection_result

    def get_user_security_status(self, user: User) -> Dict:
        """获取用户安全状态"""
        recent_detections = ScreenRecordingDetection.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timezone.timedelta(days=7),
        )

        active_alerts = SecurityAlert.objects.filter(user=user, is_resolved=False)

        return {
            "recent_detections_count": recent_detections.count(),
            "active_alerts_count": active_alerts.count(),
            "is_blocked": cache.get(f"user_blocked_{user.id}", False),
            "last_detection": (
                recent_detections.first().created_at if recent_detections.exists() else None
            ),
        }
