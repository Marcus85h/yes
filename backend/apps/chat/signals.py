"""
聊天系统信号处理器
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ChatInvitation, Message
from .services import NotificationService


@receiver(post_save, sender=Message)
def message_post_save(sender, instance, created, **kwargs):
    """
    消息保存后的信号处理
    """
    if created:
        # 新消息创建时发送通知
        notification_service = NotificationService()
        notification_service.send_message_notification(instance)


@receiver(post_save, sender=ChatInvitation)
def invitation_post_save(sender, instance, created, **kwargs):
    """
    邀请保存后的信号处理
    """
    if created:
        # 新邀请创建时发送通知
        notification_service = NotificationService()
        notification_service.send_invitation_notification(instance)
