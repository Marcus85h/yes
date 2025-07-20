"""
聊天系统部署配置
"""

import os
from typing import Any, Dict


class ChatConfig:
    """聊天系统配置"""

    # 消息配置
    MAX_MESSAGE_LENGTH = int(os.getenv("CHAT_MAX_MESSAGE_LENGTH", 1000))
    MESSAGE_EDIT_TIMEOUT = int(os.getenv("CHAT_MESSAGE_EDIT_TIMEOUT", 300))  # 5分钟
    MAX_FILE_SIZE = int(os.getenv("CHAT_MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
    MAX_PARTICIPANTS = int(os.getenv("CHAT_MAX_PARTICIPANTS", 100))

    # 文件上传配置
    UPLOAD_MAX_SIZE = int(os.getenv("UPLOAD_MAX_SIZE", 10 * 1024 * 1024))  # 10MB
    UPLOAD_ALLOWED_TYPES = os.getenv(
        "UPLOAD_ALLOWED_TYPES", "image/*,video/*,audio/*,application/*"
    )
    UPLOAD_STORAGE_PATH = os.getenv("UPLOAD_STORAGE_PATH", "/uploads/chat")

    # 通知配置
    PUSH_NOTIFICATION_ENABLED = os.getenv("PUSH_NOTIFICATION_ENABLED", "true").lower() == "true"
    EMAIL_NOTIFICATION_ENABLED = os.getenv("EMAIL_NOTIFICATION_ENABLED", "false").lower() == "true"

    # WebSocket配置
    WEBSOCKET_HEARTBEAT_INTERVAL = int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", 30))  # 30秒
    WEBSOCKET_CONNECTION_TIMEOUT = int(os.getenv("WEBSOCKET_CONNECTION_TIMEOUT", 300))  # 5分钟

    # 缓存配置
    MESSAGE_CACHE_TTL = int(os.getenv("MESSAGE_CACHE_TTL", 3600))  # 1小时
    ROOM_CACHE_TTL = int(os.getenv("ROOM_CACHE_TTL", 1800))  # 30分钟

    # 搜索配置
    SEARCH_RESULT_LIMIT = int(os.getenv("SEARCH_RESULT_LIMIT", 100))
    SEARCH_CACHE_TTL = int(os.getenv("SEARCH_CACHE_TTL", 300))  # 5分钟

    # 安全配置
    CONTENT_FILTER_ENABLED = os.getenv("CONTENT_FILTER_ENABLED", "true").lower() == "true"
    SENSITIVE_WORDS_FILE = os.getenv("SENSITIVE_WORDS_FILE", "sensitive_words.txt")

    # 性能配置
    MESSAGE_BATCH_SIZE = int(os.getenv("MESSAGE_BATCH_SIZE", 50))
    NOTIFICATION_BATCH_SIZE = int(os.getenv("NOTIFICATION_BATCH_SIZE", 20))

    @classmethod
    def get_allowed_file_types(cls) -> Dict[str, list]:
        """获取允许的文件类型"""
        return {
            "image": ["image/jpeg", "image/png", "image/gif", "image/webp"],
            "video": ["video/mp4", "video/avi", "video/mov", "video/webm"],
            "audio": ["audio/mp3", "audio/wav", "audio/aac", "audio/m4a"],
            "file": [
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "text/plain",
            ],
        }

    @classmethod
    def get_file_size_limits(cls) -> Dict[str, int]:
        """获取文件大小限制"""
        return {
            "image": 5 * 1024 * 1024,  # 5MB
            "video": 50 * 1024 * 1024,  # 50MB
            "audio": 20 * 1024 * 1024,  # 20MB
            "file": cls.MAX_FILE_SIZE,
        }

    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """获取Redis配置"""
        return {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
            "db": int(os.getenv("REDIS_DB", 0)),
            "password": os.getenv("REDIS_PASSWORD"),
            "ssl": os.getenv("REDIS_SSL", "false").lower() == "true",
        }

    @classmethod
    def get_celery_config(cls) -> Dict[str, Any]:
        """获取Celery配置"""
        return {
            "broker_url": os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
            "result_backend": os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": "UTC",
            "enable_utc": True,
            "task_track_started": True,
            "task_time_limit": 30 * 60,  # 30分钟
            "task_soft_time_limit": 25 * 60,  # 25分钟
        }

    @classmethod
    def get_storage_config(cls) -> Dict[str, Any]:
        """获取存储配置"""
        storage_type = os.getenv("STORAGE_TYPE", "local")

        if storage_type == "s3":
            return {
                "type": "s3",
                "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "bucket_name": os.getenv("AWS_S3_BUCKET_NAME"),
                "region": os.getenv("AWS_S3_REGION", "us-east-1"),
                "endpoint_url": os.getenv("AWS_S3_ENDPOINT_URL"),
            }
        elif storage_type == "gcs":
            return {
                "type": "gcs",
                "project_id": os.getenv("GCS_PROJECT_ID"),
                "bucket_name": os.getenv("GCS_BUCKET_NAME"),
                "credentials_file": os.getenv("GCS_CREDENTIALS_FILE"),
            }
        else:
            return {
                "type": "local",
                "path": cls.UPLOAD_STORAGE_PATH,
            }

    @classmethod
    def get_monitoring_config(cls) -> Dict[str, Any]:
        """获取监控配置"""
        return {
            "enabled": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            "metrics_port": int(os.getenv("METRICS_PORT", 9090)),
            "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL", 30)),
            "alert_thresholds": {
                "message_queue_size": int(os.getenv("ALERT_MESSAGE_QUEUE_SIZE", 1000)),
                "response_time_ms": int(os.getenv("ALERT_RESPONSE_TIME_MS", 5000)),
                "error_rate_percent": float(os.getenv("ALERT_ERROR_RATE_PERCENT", 5.0)),
            },
        }


class DevelopmentConfig(ChatConfig):
    """开发环境配置"""

    DEBUG = True
    LOG_LEVEL = "DEBUG"

    # 开发环境使用本地存储
    UPLOAD_STORAGE_PATH = "./uploads/chat"

    # 开发环境禁用某些功能
    PUSH_NOTIFICATION_ENABLED = False
    EMAIL_NOTIFICATION_ENABLED = False
    CONTENT_FILTER_ENABLED = False


class ProductionConfig(ChatConfig):
    """生产环境配置"""

    DEBUG = False
    LOG_LEVEL = "INFO"

    # 生产环境启用所有功能
    PUSH_NOTIFICATION_ENABLED = True
    EMAIL_NOTIFICATION_ENABLED = True
    CONTENT_FILTER_ENABLED = True

    # 生产环境使用更严格的限制
    MAX_PARTICIPANTS = 50
    MESSAGE_BATCH_SIZE = 100
    NOTIFICATION_BATCH_SIZE = 50
