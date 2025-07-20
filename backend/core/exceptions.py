"""
统一异常处理
"""

import logging
from typing import Any, Dict, List, Optional

from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .responses import APIResponse, ErrorCodes

logger = logging.getLogger(__name__)


class BaseAPIException(APIException):
    """基础API异常类"""

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Any = None,
    ):
        self.message = message or self.default_message
        self.error_code = error_code or self.default_error_code
        self.status_code = status_code or self.default_status_code
        self.details = details
        super().__init__(self.message)


class ValidationException(BaseAPIException):
    """数据验证异常"""

    default_message = "数据验证失败"
    default_error_code = ErrorCodes.VALIDATION_ERROR
    default_status_code = status.HTTP_400_BAD_REQUEST


class NotFoundException(BaseAPIException):
    """资源不存在异常"""

    default_message = "资源不存在"
    default_error_code = ErrorCodes.NOT_FOUND
    default_status_code = status.HTTP_404_NOT_FOUND


class UnauthorizedException(BaseAPIException):
    """未授权异常"""

    default_message = "未授权访问"
    default_error_code = ErrorCodes.UNAUTHORIZED
    default_status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(BaseAPIException):
    """权限不足异常"""

    default_message = "权限不足"
    default_error_code = ErrorCodes.FORBIDDEN
    default_status_code = status.HTTP_403_FORBIDDEN


class ConflictException(BaseAPIException):
    """资源冲突异常"""

    default_message = "资源冲突"
    default_error_code = "CONFLICT"
    default_status_code = status.HTTP_409_CONFLICT


class RateLimitException(BaseAPIException):
    """频率限制异常"""

    default_message = "请求过于频繁"
    default_error_code = ErrorCodes.RATE_LIMIT_EXCEEDED
    default_status_code = status.HTTP_429_TOO_MANY_REQUESTS


class BusinessLogicException(BaseAPIException):
    """业务逻辑异常"""

    default_message = "业务逻辑错误"
    default_error_code = "BUSINESS_ERROR"
    default_status_code = status.HTTP_400_BAD_REQUEST


def custom_exception_handler(exc, context):
    """
    自定义异常处理器

    Args:
        exc: 异常对象
        context: 上下文信息

    Returns:
        Response: 统一格式的响应
    """
    # 调用DRF默认异常处理器
    response = exception_handler(exc, context)

    if response is not None:
        # 处理DRF内置异常
        return handle_drf_exception(exc, response)

    # 处理自定义异常
    if isinstance(exc, BaseAPIException):
        return handle_custom_exception(exc)

    # 处理Django异常
    if isinstance(exc, Http404):
        return handle_http404_exception(exc)

    if isinstance(exc, ValidationError):
        return handle_validation_exception(exc)

    # 处理其他未捕获的异常
    return handle_unexpected_exception(exc, context)


def handle_drf_exception(exc, response):
    """处理DRF内置异常"""
    if isinstance(exc, DRFValidationError):
        return APIResponse.validation_error(errors=response.data, message="数据验证失败")

    # 其他DRF异常
    error_message = str(exc)
    if hasattr(exc, "detail"):
        error_message = str(exc.detail)

    return APIResponse.error(
        message=error_message,
        error_code=getattr(exc, "error_code", ErrorCodes.UNKNOWN_ERROR),
        status_code=response.status_code,
    )


def handle_custom_exception(exc):
    """处理自定义异常"""
    return APIResponse.error(
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        **({"details": exc.details} if exc.details else {}),
    )


def handle_http404_exception(exc):
    """处理404异常"""
    return APIResponse.not_found(message="请求的资源不存在", error_code=ErrorCodes.NOT_FOUND)


def handle_validation_exception(exc):
    """处理Django验证异常"""
    errors = {}
    if hasattr(exc, "message_dict"):
        errors = exc.message_dict
    elif hasattr(exc, "messages"):
        errors = {"non_field_errors": exc.messages}
    else:
        errors = {"non_field_errors": [str(exc)]}

    return APIResponse.validation_error(errors)


def handle_unexpected_exception(exc, context):
    """处理未预期的异常"""
    # 记录异常日志
    logger.error(
        f"未捕获的异常: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={
            "view": context.get("view"),
            "request": context.get("request"),
        },
    )

    # 生产环境不暴露详细错误信息
    if context.get("request") and hasattr(context["request"], "META"):
        is_debug = context["request"].META.get("HTTP_X_DEBUG", "").lower() == "true"
    else:
        is_debug = False

    message = str(exc) if is_debug else "服务器内部错误"

    return APIResponse.server_error(message=message, error_code=ErrorCodes.INTERNAL_ERROR)


class ExceptionMiddleware:
    """异常处理中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """处理异常"""
        # 只处理API请求的异常
        if not request.path.startswith("/api/"):
            return None

        # 记录异常日志
        logger.error(
            f"中间件捕获异常: {type(exception).__name__}: {str(exception)}",
            exc_info=True,
            extra={"request": request},
        )

        # 返回统一格式的错误响应
        return APIResponse.server_error(
            message="服务器内部错误", error_code=ErrorCodes.INTERNAL_ERROR
        )


# 异常工具函数
def raise_validation_error(message: str, field_errors: Optional[Dict[str, List[str]]] = None):
    """抛出验证异常"""
    if field_errors:
        raise ValidationException(
            message=message, error_code=ErrorCodes.VALIDATION_ERROR, details=field_errors
        )
    else:
        raise ValidationException(message=message)


def raise_not_found_error(message: Optional[str] = None, error_code: Optional[str] = None):
    """抛出资源不存在异常"""
    raise NotFoundException(
        message=message or "资源不存在", error_code=error_code or ErrorCodes.NOT_FOUND
    )


def raise_unauthorized_error(message: Optional[str] = None):
    """抛出未授权异常"""
    raise UnauthorizedException(message=message or "未授权访问")


def raise_forbidden_error(message: Optional[str] = None):
    """抛出权限不足异常"""
    raise ForbiddenException(message=message or "权限不足")


def raise_business_error(message: str, error_code: Optional[str] = None):
    """抛出业务逻辑异常"""
    raise BusinessLogicException(message=message, error_code=error_code or "BUSINESS_ERROR")
