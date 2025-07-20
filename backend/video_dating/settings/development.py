"""
开发环境设置
"""

import os
from typing import Any, Dict, cast

from .base import *
from .base import LOGGING

# 开发环境配置
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# 数据库配置（开发环境）
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }
}

# Redis配置（开发环境）
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 日志配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# 确保日志目录存在
os.makedirs("logs", exist_ok=True)

# 开发工具
INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Debug Toolbar配置
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# 禁用Sentry（开发环境）
SENTRY_DSN = ""

# 文件存储（开发环境使用本地存储）
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# CORS配置（开发环境）
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# 禁用安全设置（开发环境）
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# 邮件配置（开发环境）
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# 缓存配置（开发环境）
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# 会话配置（开发环境）
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# 禁用Django Axes（开发环境）
# AXES_ENABLED = False
