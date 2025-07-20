import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ScreenRecordingDetection, SecurityAlert
from .services import SecurityManager


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def detect_screen_recording(request):
    """
    检测录屏行为
    """
    try:
        # 获取请求数据
        request_data = {
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "ip_address": request.META.get("REMOTE_ADDR", ""),
            "device_info": request.data.get("device_info", {}),
            "screen_info": request.data.get("screen_info", {}),
            "processes": request.data.get("processes", []),
            "network_info": request.data.get("network_info", {}),
            "behavior_pattern": request.data.get("behavior_pattern", {}),
        }

        # 执行检测
        security_manager = SecurityManager()
        result = security_manager.process_detection(request.user, request_data)

        return Response(
            {
                "success": True,
                "detected": result.get("detected", False),
                "action_taken": result.get("action_taken", "none"),
                "message": result.get("message", ""),
                "detection_id": result.get("detection_id", ""),
                "protection_applied": result.get("protection_applied", {}),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_security_status(request):
    """
    获取用户安全状态
    """
    try:
        security_manager = SecurityManager()
        status_info = security_manager.get_user_security_status(request.user)

        return Response(
            {"success": True, "security_status": status_info},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_detection_history(request):
    """
    获取检测历史
    """
    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))

        detections = ScreenRecordingDetection.objects.filter(user=request.user).order_by(
            "-created_at"
        )

        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        detections_page = detections[start:end]

        detection_list = []
        for detection in detections_page:
            detection_list.append(
                {
                    "id": detection.detection_id,
                    "detection_type": detection.detection_type,
                    "severity": detection.severity,
                    "ip_address": detection.ip_address,
                    "is_confirmed": detection.is_confirmed,
                    "is_false_positive": detection.is_false_positive,
                    "action_taken": detection.action_taken,
                    "created_at": detection.created_at.isoformat(),
                }
            )

        return Response(
            {
                "success": True,
                "detections": detection_list,
                "total_count": detections.count(),
                "page": page,
                "page_size": page_size,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_security_alerts(request):
    """
    获取安全警报
    """
    try:
        alerts = SecurityAlert.objects.filter(user=request.user, is_resolved=False).order_by(
            "-created_at"
        )

        alert_list = []
        for alert in alerts:
            alert_list.append(
                {
                    "id": alert.alert_id,
                    "alert_type": alert.alert_type,
                    "priority": alert.priority,
                    "title": alert.title,
                    "message": alert.message,
                    "is_read": alert.is_read,
                    "created_at": alert.created_at.isoformat(),
                }
            )

        return Response(
            {
                "success": True,
                "alerts": alert_list,
                "total_count": alerts.count(),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_alert_as_read(request):
    """
    标记警报为已读
    """
    try:
        alert_id = request.data.get("alert_id")

        if not alert_id:
            return Response(
                {"success": False, "error": "缺少警报ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            alert = SecurityAlert.objects.get(alert_id=alert_id, user=request.user)
            alert.is_read = True
            alert.save()

            return Response(
                {"success": True, "message": "警报已标记为已读"},
                status=status.HTTP_200_OK,
            )

        except SecurityAlert.DoesNotExist:
            return Response(
                {"success": False, "error": "警报不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report_false_positive(request):
    """
    报告误报
    """
    try:
        detection_id = request.data.get("detection_id")

        if not detection_id:
            return Response(
                {"success": False, "error": "缺少检测ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            detection = ScreenRecordingDetection.objects.get(
                detection_id=detection_id, user=request.user
            )
            detection.is_false_positive = True
            detection.save()

            return Response(
                {"success": True, "message": "误报已报告"},
                status=status.HTTP_200_OK,
            )

        except ScreenRecordingDetection.DoesNotExist:
            return Response(
                {"success": False, "error": "检测记录不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
