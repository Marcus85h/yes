"""
内容过滤服务
"""

import logging
import re
from typing import Any, Dict, List, Tuple

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ContentFilter:
    """
    内容过滤器
    """

    def __init__(self):
        self.sensitive_words = self._load_sensitive_words()
        self.url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )
        self.phone_pattern = re.compile(r"1[3-9]\d{9}")
        self.email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    def _load_sensitive_words(self) -> List[str]:
        """加载敏感词列表"""
        # 从缓存获取
        cache_key = "sensitive_words"
        sensitive_words = cache.get(cache_key)

        if sensitive_words is None:
            # 从文件加载
            try:
                sensitive_words_file = getattr(
                    settings, "SENSITIVE_WORDS_FILE", "sensitive_words.txt"
                )
                with open(sensitive_words_file, "r", encoding="utf-8") as f:
                    sensitive_words = [line.strip() for line in f if line.strip()]

                # 缓存1小时
                cache.set(cache_key, sensitive_words, 3600)
                logger.info(f"加载了 {len(sensitive_words)} 个敏感词")
            except FileNotFoundError:
                # 使用默认敏感词
                sensitive_words = [
                    "傻逼",
                    "垃圾",
                    "废物",
                    "白痴",
                    "智障",
                    "fuck",
                    "shit",
                    "bitch",
                    "asshole",
                    "政治敏感词1",
                    "政治敏感词2",
                ]
                logger.warning("敏感词文件未找到，使用默认敏感词")

        return sensitive_words

    def filter_text(self, text: str) -> Tuple[bool, str, List[str]]:
        """
        过滤文本内容

        Args:
            text: 待过滤的文本

        Returns:
            (是否通过, 过滤后的文本, 检测到的敏感词列表)
        """
        if not text:
            return True, text, []

        detected_words = []
        filtered_text = text

        # 检测敏感词
        for word in self.sensitive_words:
            if word in text:
                detected_words.append(word)
                # 替换为 *
                filtered_text = filtered_text.replace(word, "*" * len(word))

        # 检测URL
        urls = self.url_pattern.findall(text)
        if urls:
            # 检查是否为安全URL
            for url in urls:
                if not self._is_safe_url(url):
                    detected_words.append(f"不安全链接: {url}")
                    filtered_text = filtered_text.replace(url, "[链接已过滤]")

        # 检测手机号
        phones = self.phone_pattern.findall(text)
        if phones:
            detected_words.extend([f"手机号: {phone}" for phone in phones])
            for phone in phones:
                filtered_text = filtered_text.replace(phone, phone[:3] + "****" + phone[-4:])

        # 检测邮箱
        emails = self.email_pattern.findall(text)
        if emails:
            detected_words.extend([f"邮箱: {email}" for email in emails])
            for email in emails:
                parts = email.split("@")
                if len(parts) == 2:
                    masked_email = parts[0][:2] + "***@" + parts[1]
                    filtered_text = filtered_text.replace(email, masked_email)

        # 检查是否通过
        is_passed = len(detected_words) == 0

        return is_passed, filtered_text, detected_words

    def _is_safe_url(self, url: str) -> bool:
        """检查URL是否安全"""
        # 黑名单域名
        unsafe_domains = ["malware.com", "phishing.com", "scam.com"]

        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # 检查黑名单
            for unsafe_domain in unsafe_domains:
                if unsafe_domain in domain:
                    return False

            # 检查白名单（可选）
            # for safe_domain in safe_domains:
            #     if safe_domain in domain:
            #         return True

            return True
        except Exception:
            return False

    def check_spam(self, text: str, user_id: str) -> Tuple[bool, str]:
        """
        检查是否为垃圾消息

        Args:
            text: 消息内容
            user_id: 用户ID

        Returns:
            (是否为垃圾消息, 原因)
        """
        # 检查重复消息
        cache_key = f"user_last_message_{user_id}"
        last_message = cache.get(cache_key)

        if last_message and last_message == text:
            return True, "重复消息"

        # 检查消息频率
        cache_key = f"user_message_count_{user_id}"
        message_count = cache.get(cache_key, 0)

        if message_count > 10:  # 1分钟内超过10条消息
            return True, "消息发送过于频繁"

        # 检查消息长度
        if len(text) > 1000:
            return True, "消息内容过长"

        # 检查特殊字符比例
        special_chars = len(re.findall(r"[^\w\s\u4e00-\u9fff]", text))
        if len(text) > 0 and special_chars / len(text) > 0.5:
            return True, "特殊字符过多"

        # 更新缓存
        cache.set(f"user_last_message_{user_id}", text, 60)
        cache.set(f"user_message_count_{user_id}", message_count + 1, 60)

        return False, ""

    def validate_file_content(self, file_path: str, file_type: str) -> Tuple[bool, str]:
        """
        验证文件内容安全性

        Args:
            file_path: 文件路径
            file_type: 文件类型

        Returns:
            (是否安全, 原因)
        """
        try:
            # 检查文件大小
            import os

            file_size = os.path.getsize(file_path)

            if file_size > 50 * 1024 * 1024:  # 50MB
                return False, "文件过大"

            # 检查文件类型
            if file_type == "image":
                return self._validate_image(file_path)
            elif file_type == "video":
                return self._validate_video(file_path)
            elif file_type == "audio":
                return self._validate_audio(file_path)
            else:
                return self._validate_document(file_path)

        except Exception as e:
            logger.error(f"文件验证失败: {e}")
            return False, "文件验证失败"

    def _validate_image(self, file_path: str) -> Tuple[bool, str]:
        """验证图片文件"""
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                # 检查图片尺寸
                if img.width > 4096 or img.height > 4096:
                    return False, "图片尺寸过大"

                # 检查图片格式
                if img.format not in ["JPEG", "PNG", "GIF", "WEBP"]:
                    return False, "不支持的图片格式"

                return True, ""
        except Exception as e:
            return False, f"图片验证失败: {str(e)}"

    def _validate_video(self, file_path: str) -> Tuple[bool, str]:
        """验证视频文件"""
        # 这里可以集成ffmpeg来验证视频
        # 暂时返回True
        return True, ""

    def _validate_audio(self, file_path: str) -> Tuple[bool, str]:
        """验证音频文件"""
        # 这里可以集成音频处理库来验证音频
        # 暂时返回True
        return True, ""

    def _validate_document(self, file_path: str) -> Tuple[bool, str]:
        """验证文档文件"""
        # 检查文件扩展名
        allowed_extensions = [".pdf", ".doc", ".docx", ".txt", ".rtf"]
        import os

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext not in allowed_extensions:
            return False, "不支持的文档格式"

        return True, ""


class ContentModeration:
    """
    内容审核服务
    """

    def __init__(self):
        self.filter = ContentFilter()

    def moderate_message(self, text: str, user_id: str) -> Dict[str, Any]:
        """
        审核消息内容

        Args:
            text: 消息内容
            user_id: 用户ID

        Returns:
            审核结果
        """
        result: Dict[str, Any] = {
            "passed": True,
            "filtered_text": text,
            "detected_issues": [],
            "action": "allow",
        }

        # 内容过滤
        is_passed, filtered_text, detected_words = self.filter.filter_text(text)
        if not is_passed:
            result["passed"] = False
            result["filtered_text"] = filtered_text
            result["detected_issues"].extend(detected_words)
            result["action"] = "filter"

        # 垃圾消息检测
        is_spam, spam_reason = self.filter.check_spam(text, user_id)
        if is_spam:
            result["passed"] = False
            result["detected_issues"].append(spam_reason)
            result["action"] = "block"

        return result

    def moderate_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        审核文件内容

        Args:
            file_path: 文件路径
            file_type: 文件类型

        Returns:
            审核结果
        """
        result: Dict[str, Any] = {
            "passed": True,
            "detected_issues": [],
            "action": "allow",
        }

        # 文件内容验证
        is_safe, reason = self.filter.validate_file_content(file_path, file_type)
        if not is_safe:
            result["passed"] = False
            result["detected_issues"].append(reason)
            result["action"] = "block"

        return result
