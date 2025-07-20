"""
聊天应用配置
"""

from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat"
    verbose_name = "聊天系统"

    def ready(self):
        """应用启动时的初始化"""
        import apps.chat.signals
