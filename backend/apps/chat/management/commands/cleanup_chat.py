"""
清理聊天数据的管理命令
"""

import logging

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.chat.models import ChatInvitation, ChatNotification, Message


STATUS_DELETED = "deleted"
STATUS_READ = "read"
STATUS_ACCEPTED = "accepted"
STATUS_REJECTED = "rejected"

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "清理过期的聊天数据"

    BATCH_SIZE = 1000

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="删除多少天前的数据（默认30天）",
        )
        parser.add_argument(
            "--type",
            choices=["messages", "notifications", "invitations", "all"],
            default="all",
            help="清理的数据类型",
        )
        parser.add_argument("--dry-run", action="store_true", help="试运行，不实际删除数据")

    def handle(self, *args, **options):
        try:
            days = options["days"]
            cleanup_type = options["type"]
            dry_run = options["dry_run"]

            cutoff_date = timezone.now() - timedelta(days=days)

            logger.info(f"开始清理{days}天前的聊天数据，类型: {cleanup_type}, dry_run: {dry_run}")
            self.stdout.write(f"开始清理{days}天前的聊天数据...")

            if cleanup_type in ["messages", "all"]:
                self._cleanup_messages(cutoff_date, dry_run)

            if cleanup_type in ["notifications", "all"]:
                self._cleanup_notifications(cutoff_date, dry_run)

            if cleanup_type in ["invitations", "all"]:
                self._cleanup_invitations(cutoff_date, dry_run)

            self.stdout.write(self.style.SUCCESS("数据清理完成！"))
            logger.info("数据清理完成！")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"清理过程中发生错误: {e}"))
            logger.error(f"清理过程中发生错误: {e}", exc_info=True)

    def _cleanup_messages(self, cutoff_date, dry_run):
        """清理过期消息（分批删除）"""
        try:
            total_count = 0
            while True:
                deleted_messages = Message.objects.filter(status=STATUS_DELETED, created_at__lt=cutoff_date)[:self.BATCH_SIZE]
                count = deleted_messages.count()
                if count == 0:
                    break
                total_count += count
                logger.info(f"本批次待清理已删除消息数量: {count}")
                if not dry_run:
                    deleted_messages.delete()
                    logger.info(f"本批次已删除 {count} 条已删除的消息")
                self.stdout.write(f"本批次清理了 {count} 条已删除的消息")
            self.stdout.write(f"总共清理了 {total_count} 条已删除的消息")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"清理消息时发生错误: {e}"))
            logger.error(f"清理消息时发生错误: {e}", exc_info=True)

    def _cleanup_notifications(self, cutoff_date, dry_run):
        """清理过期通知（分批删除）"""
        try:
            total_count = 0
            while True:
                old_notifications = ChatNotification.objects.filter(
                    status=STATUS_READ, created_at__lt=cutoff_date
                )[:self.BATCH_SIZE]
                count = old_notifications.count()
                if count == 0:
                    break
                total_count += count
                logger.info(f"本批次待清理过期通知数量: {count}")
                if not dry_run:
                    old_notifications.delete()
                    logger.info(f"本批次已删除 {count} 条过期通知")
                self.stdout.write(f"本批次清理了 {count} 条过期通知")
            self.stdout.write(f"总共清理了 {total_count} 条过期通知")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"清理通知时发生错误: {e}"))
            logger.error(f"清理通知时发生错误: {e}", exc_info=True)

    def _cleanup_invitations(self, cutoff_date, dry_run):
        """清理过期邀请（分批删除）"""
        try:
            total_count = 0
            while True:
                old_invitations = ChatInvitation.objects.filter(
                    status__in=[STATUS_ACCEPTED, STATUS_REJECTED], created_at__lt=cutoff_date
                )[:self.BATCH_SIZE]
                count = old_invitations.count()
                if count == 0:
                    break
                total_count += count
                logger.info(f"本批次待清理过期邀请数量: {count}")
                if not dry_run:
                    old_invitations.delete()
                    logger.info(f"本批次已删除 {count} 条过期邀请")
                self.stdout.write(f"本批次清理了 {count} 条过期邀请")
            self.stdout.write(f"总共清理了 {total_count} 条过期邀请")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"清理邀请时发生错误: {e}"))
            logger.error(f"清理邀请时发生错误: {e}", exc_info=True)
