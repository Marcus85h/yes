import pytest
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta

from apps.chat.models import Message, ChatNotification, ChatInvitation

@pytest.mark.django_db
def test_cleanup_chat_dry_run():
    # 创建测试数据
    old_time = timezone.now() - timedelta(days=40)
    msg = Message.objects.create(status="deleted", created_at=old_time)
    notif = ChatNotification.objects.create(status="read", created_at=old_time)
    inv = ChatInvitation.objects.create(status="accepted", created_at=old_time)

    # dry-run 不应删除数据
    call_command("cleanup_chat", "--days=30", "--type=all", "--dry-run")
    assert Message.objects.filter(id=msg.id).exists()
    assert ChatNotification.objects.filter(id=notif.id).exists()
    assert ChatInvitation.objects.filter(id=inv.id).exists()

@pytest.mark.django_db
def test_cleanup_chat_real_delete():
    old_time = timezone.now() - timedelta(days=40)
    msg = Message.objects.create(status="deleted", created_at=old_time)
    notif = ChatNotification.objects.create(status="read", created_at=old_time)
    inv = ChatInvitation.objects.create(status="accepted", created_at=old_time)

    # 实际删除
    call_command("cleanup_chat", "--days=30", "--type=all")
    assert not Message.objects.filter(id=msg.id).exists()
    assert not ChatNotification.objects.filter(id=notif.id).exists()
    assert not ChatInvitation.objects.filter(id=inv.id).exists()

@pytest.mark.django_db
def test_cleanup_chat_type_messages():
    old_time = timezone.now() - timedelta(days=40)
    msg = Message.objects.create(status="deleted", created_at=old_time)
    notif = ChatNotification.objects.create(status="read", created_at=old_time)
    inv = ChatInvitation.objects.create(status="accepted", created_at=old_time)

    call_command("cleanup_chat", "--days=30", "--type=messages")
    assert not Message.objects.filter(id=msg.id).exists()
    assert ChatNotification.objects.filter(id=notif.id).exists()
    assert ChatInvitation.objects.filter(id=inv.id).exists()

@pytest.mark.django_db
def test_cleanup_chat_days_param():
    # 20天前的数据不应被清理
    mid_time = timezone.now() - timedelta(days=20)
    msg = Message.objects.create(status="deleted", created_at=mid_time)
    call_command("cleanup_chat", "--days=30", "--type=messages")
    assert Message.objects.filter(id=msg.id).exists() 