"""
统一API响应格式
"""

from typing import Any, Dict, List, Optional, Union

from rest_framework import status
from rest_framework.response import Response


class APIResponse:
    """统一API响应类"""

    @staticmethod
    def success(
        data: Any = None, message: str = "操作成功", status_code: int = status.HTTP_200_OK, **kwargs
    ) -> Response:
        """
        成功响应

        Args:
            data: 响应数据
            message: 响应消息
            status_code: HTTP状态码
            **kwargs: 额外参数

        Returns:
            Response: DRF响应对象
        """
        response_data = {"success": True, "message": message, "data": data, **kwargs}
        return Response(response_data, status=status_code)

    @staticmethod
    def error(
        message: str = "操作失败",
        error_code: str = "UNKNOWN_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors: Optional[Dict[str, List[str]]] = None,
        **kwargs,
    ) -> Response:
        """
        错误响应

        Args:
            message: 错误消息
            error_code: 错误代码
            status_code: HTTP状态码
            errors: 字段错误信息
            **kwargs: 额外参数

        Returns:
            Response: DRF响应对象
        """
        response_data = {"success": False, "message": message, "error_code": error_code, **kwargs}

        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=status_code)

    @staticmethod
    def validation_error(
        errors: Dict[str, List[str]],
        message: str = "数据验证失败",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> Response:
        """
        验证错误响应

        Args:
            errors: 字段错误信息
            message: 错误消息
            status_code: HTTP状态码

        Returns:
            Response: DRF响应对象
        """
        return APIResponse.error(
            message=message, error_code="VALIDATION_ERROR", status_code=status_code, errors=errors
        )

    @staticmethod
    def not_found(message: str = "资源不存在", error_code: str = "NOT_FOUND") -> Response:
        """
        资源不存在响应

        Args:
            message: 错误消息
            error_code: 错误代码

        Returns:
            Response: DRF响应对象
        """
        return APIResponse.error(
            message=message, error_code=error_code, status_code=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def unauthorized(message: str = "未授权访问", error_code: str = "UNAUTHORIZED") -> Response:
        """
        未授权响应

        Args:
            message: 错误消息
            error_code: 错误代码

        Returns:
            Response: DRF响应对象
        """
        return APIResponse.error(
            message=message, error_code=error_code, status_code=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def forbidden(message: str = "权限不足", error_code: str = "FORBIDDEN") -> Response:
        """
        权限不足响应

        Args:
            message: 错误消息
            error_code: 错误代码

        Returns:
            Response: DRF响应对象
        """
        return APIResponse.error(
            message=message, error_code=error_code, status_code=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def server_error(
        message: str = "服务器内部错误", error_code: str = "INTERNAL_ERROR"
    ) -> Response:
        """
        服务器错误响应

        Args:
            message: 错误消息
            error_code: 错误代码

        Returns:
            Response: DRF响应对象
        """
        return APIResponse.error(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @staticmethod
    def paginated(
        data: List[Any], total: int, page: int, page_size: int, message: str = "获取成功"
    ) -> Response:
        """
        分页响应

        Args:
            data: 数据列表
            total: 总数量
            page: 当前页码
            page_size: 每页数量
            message: 响应消息

        Returns:
            Response: DRF响应对象
        """
        pagination_data = {
            "items": data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
                "has_next": page * page_size < total,
                "has_previous": page > 1,
            },
        }

        return APIResponse.success(data=pagination_data, message=message)


class ErrorCodes:
    """错误代码常量"""

    # 通用错误
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # 用户相关错误
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"
    PHONE_NOT_VERIFIED = "PHONE_NOT_VERIFIED"

    # 聊天相关错误
    CHAT_ROOM_NOT_FOUND = "CHAT_ROOM_NOT_FOUND"
    MESSAGE_NOT_FOUND = "MESSAGE_NOT_FOUND"
    ROOM_FULL = "ROOM_FULL"
    NOT_ROOM_MEMBER = "NOT_ROOM_MEMBER"

    # 通话相关错误
    CALL_NOT_FOUND = "CALL_NOT_FOUND"
    CALL_ALREADY_ACTIVE = "CALL_ALREADY_ACTIVE"
    CALL_ENDED = "CALL_ENDED"
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"

    # 房间相关错误
    ROOM_NOT_FOUND = "ROOM_NOT_FOUND"
    ROOM_ALREADY_EXISTS = "ROOM_ALREADY_EXISTS"
    ROOM_CLOSED = "ROOM_CLOSED"
    ROOM_PRIVATE = "ROOM_PRIVATE"

    # 文件相关错误
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"

    # 支付相关错误
    PAYMENT_FAILED = "PAYMENT_FAILED"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    PAYMENT_CANCELLED = "PAYMENT_CANCELLED"

    # 安全相关错误
    CONTENT_VIOLATION = "CONTENT_VIOLATION"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
