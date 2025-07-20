"""
核心视图
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    健康检查接口
    """
    return Response(
        {
            "status": "healthy",
            "message": "服务运行正常",
            "timestamp": "2024-01-01T00:00:00Z",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def api_info(request):
    """
    API信息接口
    """
    return Response(
        {
            "name": "视频交友API",
            "version": "1.0.0",
            "description": "视频交友应用后端API",
            "endpoints": {
                "users": "/api/v1/users/",
                "rooms": "/api/v1/rooms/",
                "calls": "/api/v1/calls/",
                "gifts": "/api/v1/gifts/",
                "billing": "/api/v1/billing/",
                "chat": "/api/v1/chat/",
                "security": "/api/v1/security/",
            },
        },
        status=status.HTTP_200_OK,
    )


def handler404(request, exception):
    """
    404错误处理
    """
    return JsonResponse(
        {
            "error": "页面未找到",
            "message": "请求的资源不存在",
            "status_code": 404,
        },
        status=404,
    )


def handler500(request):
    """
    500错误处理
    """
    return JsonResponse(
        {
            "error": "服务器内部错误",
            "message": "服务器发生错误，请稍后重试",
            "status_code": 500,
        },
        status=500,
    )
