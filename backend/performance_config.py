"""
性能优化配置
"""

import os
from typing import Any, Dict

# 数据库连接池配置
DATABASE_POOL_CONFIG = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "video_dating"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            "MAX_CONNS": 20,
            "MIN_CONNS": 5,
            "CONN_MAX_AGE": 600,
            "CONN_HEALTH_CHECKS": True,
        },
    }
}

# Redis缓存配置
CACHE_CONFIG = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        },
        "KEY_PREFIX": "video_dating",
        "TIMEOUT": 300,
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/2"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "session",
    },
    "celery": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/3"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "celery",
    },
}

# Celery配置
CELERY_CONFIG = {
    "broker_url": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/4"),
    "result_backend": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/4"),
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 30 * 60,
    "task_soft_time_limit": 25 * 60,
    "worker_prefetch_multiplier": 1,
    "worker_max_tasks_per_child": 1000,
    "broker_connection_retry_on_startup": True,
    "broker_connection_max_retries": 10,
    "broker_connection_retry": True,
    "broker_connection_retry_delay": 0.2,
    "broker_transport_options": {
        "visibility_timeout": 3600,
        "fanout_prefix": True,
        "fanout_patterns": True,
    },
}

# 静态文件配置
STATICFILES_CONFIG = {
    "STATICFILES_STORAGE": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    "STATICFILES_FINDERS": [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    ],
    "STATICFILES_DIRS": [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    ],
    "STATIC_ROOT": os.path.join(os.path.dirname(os.path.dirname(__file__)), "staticfiles"),
}

# 媒体文件配置
MEDIA_CONFIG = {
    "MEDIA_URL": "/media/",
    "MEDIA_ROOT": os.path.join(os.path.dirname(os.path.dirname(__file__)), "media"),
    "DEFAULT_FILE_STORAGE": "django.core.files.storage.FileSystemStorage",
}

# 日志配置
LOGGING_CONFIG = {
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
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(os.path.dirname(__file__), "logs", "app.log"),
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "apps": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# 安全配置
SECURITY_CONFIG = {
    "SECURE_BROWSER_XSS_FILTER": True,
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
    "SECURE_HSTS_SECONDS": 31536000,
    "SECURE_HSTS_PRELOAD": True,
    "SECURE_REFERRER_POLICY": "strict-origin-when-cross-origin",
    "SECURE_SSL_REDIRECT": os.getenv("SECURE_SSL_REDIRECT", "False").lower() == "true",
    "SESSION_COOKIE_SECURE": os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true",
    "CSRF_COOKIE_SECURE": os.getenv("CSRF_COOKIE_SECURE", "False").lower() == "true",
    "X_FRAME_OPTIONS": "DENY",
    "SECURE_CROSS_ORIGIN_OPENER_POLICY": "same-origin",
}

# 中间件配置
MIDDLEWARE_CONFIG = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_axes.middleware.AxesMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

# 模板配置
TEMPLATES_CONFIG = {
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
    ],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
        "loaders": [
            (
                "django.template.loaders.cached.Loader",
                [
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
            ),
        ],
    },
}

# 应用配置
INSTALLED_APPS_CONFIG = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    # 第三方应用
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "django_extensions",
    "debug_toolbar",
    "django_storages",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "django_prometheus",
    "sentry_sdk",
    "django_ratelimit",
    "axes",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "two_factor",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "knox",
    "django_rest_passwordreset",
    "django_rest_registration",
    # 本地应用
    "apps.users",
    "apps.chat",
    "apps.calls",
    "apps.rooms",
    "apps.analytics",
    "apps.security",
]

# REST Framework配置
REST_FRAMEWORK_CONFIG = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "knox.auth.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

# 认证配置
AUTH_CONFIG = {
    "AUTH_USER_MODEL": "users.User",
    "AUTHENTICATION_BACKENDS": [
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    ],
    "LOGIN_URL": "/accounts/login/",
    "LOGIN_REDIRECT_URL": "/",
    "LOGOUT_REDIRECT_URL": "/",
    "PASSWORD_RESET_TIMEOUT": 3600,
    "PASSWORD_HASHERS": [
        "django.contrib.auth.hashers.Argon2PasswordHasher",
        "django.contrib.auth.hashers.PBKDF2PasswordHasher",
        "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
        "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    ],
}

# 国际化配置
I18N_CONFIG = {
    "LANGUAGE_CODE": "zh-hans",
    "TIME_ZONE": "Asia/Shanghai",
    "USE_I18N": True,
    "USE_L10N": True,
    "USE_TZ": True,
    "LANGUAGES": [
        ("zh-hans", "简体中文"),
        ("en", "English"),
        ("ja", "日本語"),
        ("ko", "한국어"),
    ],
    "LOCALE_PATHS": [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale"),
    ],
}

# 邮件配置
EMAIL_CONFIG = {
    "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
    "EMAIL_HOST": os.getenv("EMAIL_HOST", "smtp.gmail.com"),
    "EMAIL_PORT": int(os.getenv("EMAIL_PORT", "587")),
    "EMAIL_USE_TLS": os.getenv("EMAIL_USE_TLS", "True").lower() == "true",
    "EMAIL_HOST_USER": os.getenv("EMAIL_HOST_USER", ""),
    "EMAIL_HOST_PASSWORD": os.getenv("EMAIL_HOST_PASSWORD", ""),
    "DEFAULT_FROM_EMAIL": os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com"),
}

# 文件上传配置
FILE_UPLOAD_CONFIG = {
    "FILE_UPLOAD_HANDLERS": [
        "django.core.files.uploadhandler.MemoryFileUploadHandler",
        "django.core.files.uploadhandler.TemporaryFileUploadHandler",
    ],
    "FILE_UPLOAD_MAX_MEMORY_SIZE": 2621440,  # 2.5MB
    "FILE_UPLOAD_TEMP_DIR": os.path.join(os.path.dirname(__file__), "temp"),
    "DATA_UPLOAD_MAX_MEMORY_SIZE": 2621440,  # 2.5MB
    "DATA_UPLOAD_MAX_NUMBER_FIELDS": 1000,
}

# 会话配置
SESSION_CONFIG = {
    "SESSION_ENGINE": "django.contrib.sessions.backends.cache",
    "SESSION_CACHE_ALIAS": "sessions",
    "SESSION_COOKIE_AGE": 1209600,  # 2 weeks
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SAMESITE": "Lax",
    "SESSION_EXPIRE_AT_BROWSER_CLOSE": False,
    "SESSION_SAVE_EVERY_REQUEST": False,
}

# 监控配置
MONITORING_CONFIG = {
    "SENTRY_DSN": os.getenv("SENTRY_DSN", ""),
    "PROMETHEUS_EXPORT_MIGRATIONS": False,
    "PROMETHEUS_EXPORT_ADDRESS": "127.0.0.1",
    "PROMETHEUS_EXPORT_PORT": 8000,
}

# 限流配置
RATE_LIMIT_CONFIG = {
    "AXES_ENABLED": True,
    "AXES_FAILURE_LIMIT": 5,
    "AXES_LOCK_OUT_AT_FAILURE": True,
    "AXES_COOLOFF_TIME": 1,  # hours
    "AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP": True,
    "AXES_RESET_ON_SUCCESS": True,
    "AXES_VERBOSE": True,
}

# WebSocket配置
CHANNELS_CONFIG = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("REDIS_URL", "redis://127.0.0.1:6379/5")],
        },
    },
}

# 性能优化配置
PERFORMANCE_CONFIG = {
    "DEBUG": False,
    "ALLOWED_HOSTS": ["*"],
    "INTERNAL_IPS": ["127.0.0.1"],
    "WSGI_APPLICATION": "video_dating.wsgi.application",
    "ASGI_APPLICATION": "video_dating.asgi.application",
    "ROOT_URLCONF": "video_dating.urls",
    "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
    "SITE_ID": 1,
    "USE_X_FORWARDED_HOST": True,
    "USE_X_FORWARDED_PORT": True,
    "SECURE_PROXY_SSL_HEADER": ("HTTP_X_FORWARDED_PROTO", "https"),
}
