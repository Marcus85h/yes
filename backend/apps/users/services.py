"""
用户服务模块
"""

import logging
import secrets
import string
from datetime import timedelta
from typing import Dict, Optional

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class SMSService:
    """短信服务"""

    @staticmethod
    def generate_verification_code() -> str:
        """生成6位数字验证码"""
        return "".join(secrets.choice(string.digits) for _ in range(6))

    @staticmethod
    def send_verification_code(phone: str) -> Dict[str, any]:  # type: ignore[valid-type]
        """发送验证码"""
        try:
            # 生成验证码
            code = SMSService.generate_verification_code()

            # 检查发送频率限制
            cache_key = f"sms_rate_limit:{phone}"
            if cache.get(cache_key):
                return {"success": False, "error": "发送过于频繁，请稍后再试"}

            # 模拟短信发送（实际项目中集成阿里云、腾讯云等短信服务）
            if settings.SMS_PROVIDER == "aliyun":
                # 阿里云短信服务
                success = SMSService._send_aliyun_sms(phone, code)
            elif settings.SMS_PROVIDER == "tencent":
                # 腾讯云短信服务
                success = SMSService._send_tencent_sms(phone, code)
            else:
                # 开发环境模拟发送
                success = SMSService._send_mock_sms(phone, code)

            if success:
                # 存储验证码到缓存（5分钟有效期）
                cache.set(f"sms_code:{phone}", code, 300)
                # 设置发送频率限制（1分钟内只能发送一次）
                cache.set(cache_key, True, 60)

                logger.info(f"验证码发送成功: {phone}")
                return {
                    "success": True,
                    "message": "验证码已发送",
                    "code": (code if settings.DEBUG else None),  # 开发环境返回验证码
                }
            else:
                return {"success": False, "error": "短信发送失败"}

        except Exception as e:
            logger.error(f"短信发送异常: {e}")
            return {"success": False, "error": "短信服务异常"}

    @staticmethod
    def verify_code(phone: str, code: str) -> bool:
        """验证验证码"""
        try:
            cache_key = f"sms_code:{phone}"
            stored_code = cache.get(cache_key)

            if stored_code and stored_code == code:
                # 验证成功后删除缓存
                cache.delete(cache_key)
                return True
            return False

        except Exception as e:
            logger.error(f"验证码验证异常: {e}")
            return False

    @staticmethod
    def _send_aliyun_sms(phone: str, code: str) -> bool:
        """阿里云短信服务"""
        try:
            # 这里集成阿里云短信SDK
            # from aliyunsdkcore.client import AcsClient
            # from aliyunsdkcore.request import CommonRequest

            logger.info(f"阿里云短信发送: {phone} -> {code}")
            return True
        except Exception as e:
            logger.error(f"阿里云短信发送失败: {e}")
            return False

    @staticmethod
    def _send_tencent_sms(phone: str, code: str) -> bool:
        """腾讯云短信服务"""
        try:
            # 这里集成腾讯云短信SDK
            # from tencentcloud.common import credential
            # from tencentcloud.sms.v20210111 import sms_client, models

            logger.info(f"腾讯云短信发送: {phone} -> {code}")
            return True
        except Exception as e:
            logger.error(f"腾讯云短信发送失败: {e}")
            return False

    @staticmethod
    def _send_mock_sms(phone: str, code: str) -> bool:
        """模拟短信发送（开发环境）"""
        logger.info(f"模拟短信发送: {phone} -> {code}")
        return True


class UserService:
    """用户服务"""

    @staticmethod
    def create_user_profile(user, **kwargs) -> Dict[str, any]:  # type: ignore[valid-type]
        """创建用户资料"""
        try:
            from .models import UserProfile

            profile_data = {
                "user": user,
                "nickname": kwargs.get("nickname", user.username),
                "gender": kwargs.get("gender", "unknown"),
                "birth_date": kwargs.get("birth_date"),
                "bio": kwargs.get("bio", ""),
                "location": kwargs.get("location", ""),
                "avatar": kwargs.get("avatar"),
            }

            profile = UserProfile.objects.create(**profile_data)  # type: ignore[attr-defined]

            logger.info(f"用户资料创建成功: {user.id}")
            return {"success": True, "profile": profile}

        except Exception as e:
            logger.error(f"用户资料创建失败: {e}")
            return {"success": False, "error": "用户资料创建失败"}

    @staticmethod
    def update_user_profile(user, **kwargs) -> Dict[str, any]:  # type: ignore[valid-type]
        """更新用户资料"""
        try:
            profile = user.profile
            update_fields = []

            for field, value in kwargs.items():
                if hasattr(profile, field) and value is not None:
                    setattr(profile, field, value)
                    update_fields.append(field)

            if update_fields:
                profile.save(update_fields=update_fields)
                logger.info(f"用户资料更新成功: {user.id} -> {update_fields}")

            return {"success": True, "profile": profile}

        except Exception as e:
            logger.error(f"用户资料更新失败: {e}")
            return {"success": False, "error": "用户资料更新失败"}
