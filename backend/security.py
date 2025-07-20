"""
安全配置模块
包含所有安全相关的配置和工具函数
"""

import hashlib
import logging
import secrets
from typing import Optional

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest

logger = logging.getLogger(__name__)


class SecurityManager:
    """安全管理器"""

    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"加密失败: {e}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"解密失败: {e}")
            raise

    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """哈希密码"""
        if not salt:
            salt = secrets.token_hex(16)

        # 使用PBKDF2进行密码哈希
        hash_obj = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  # 迭代次数
        )
        return hash_obj.hex(), salt

    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """验证密码"""
        try:
            new_hash, _ = self.hash_password(password, salt)
            return secrets.compare_digest(new_hash, hashed_password)
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False


class RateLimiter:
    """速率限制器"""

    def __init__(self, key_prefix: str, max_requests: int, window_seconds: int):
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, identifier: str) -> bool:
        """检查是否允许请求"""
        cache_key = f"{self.key_prefix}:{identifier}"

        # 获取当前请求次数
        current_requests = cache.get(cache_key, 0)

        if current_requests >= self.max_requests:
            return False

        # 增加请求次数
        cache.set(cache_key, current_requests + 1, self.window_seconds)
        return True

    def get_remaining_requests(self, identifier: str) -> int:
        """获取剩余请求次数"""
        cache_key = f"{self.key_prefix}:{identifier}"
        current_requests = cache.get(cache_key, 0)
        return max(0, self.max_requests - current_requests)


class SecurityMiddleware:
    """安全中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # 添加安全头
        response = self.get_response(request)

        # 安全头设置
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        )

        return response


# 创建全局实例
security_manager = SecurityManager()

# 速率限制器实例
login_rate_limiter = RateLimiter("login", 5, 300)  # 5次/5分钟
api_rate_limiter = RateLimiter("api", 100, 60)  # 100次/分钟
sms_rate_limiter = RateLimiter("sms", 3, 300)  # 3次/5分钟


def audit_log(action: str, user_id: Optional[int], details: dict):
    """审计日志"""
    logger.info(
        f"安全审计 - 动作: {action}, 用户ID: {user_id}, 详情: {details}",
        extra={
            "action": action,
            "user_id": user_id,
            "details": details,
            "ip_address": getattr(settings, "CLIENT_IP", "unknown"),
            "user_agent": getattr(settings, "USER_AGENT", "unknown"),
        },
    )


def validate_file_upload(file, allowed_types: list, max_size: int) -> tuple[bool, str]:
    """验证文件上传"""
    # 检查文件大小
    if file.size > max_size:
        return False, "文件大小超过限制"

    # 检查文件类型
    import magic

    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # 重置文件指针

    if mime not in allowed_types:
        return False, "不支持的文件类型"

    return True, "验证通过"


def sanitize_input(text: str) -> str:
    """清理用户输入"""
    import html
    import re

    # HTML转义
    text = html.escape(text)

    # 移除危险字符
    text = re.sub(r'[<>"\']', "", text)

    # 移除多余空格
    text = re.sub(r"\s+", " ", text).strip()

    return text
