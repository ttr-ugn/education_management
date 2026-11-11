"""
Management Command: cleanup_locked_accounts
Tự động mở khóa các tài khoản cán bộ đã hết thời gian phạt khóa tạm thời (30 phút).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from authentication.models import NguoiDung


class Command(BaseCommand):
    help = 'Mở khóa tự động cho các tài khoản người dùng đã hết thời gian bị khóa tạm thời'

    def handle(self, *args, **options):
        now = timezone.now()
        locked_users = NguoiDung.objects.filter(khoa_den__lte=now)

        unlocked_count = 0
        for user in locked_users:
            user.khoa_den = None
            user.so_lan_dang_nhap_sai = 0
            user.save(update_fields=['khoa_den', 'so_lan_dang_nhap_sai'])
            unlocked_count += 1
            self.stdout.write(f"Đã mở khóa tự động cho tài khoản: {user.ten_dang_nhap} ({user.ho_va_ten})")

        self.stdout.write(self.style.SUCCESS(
            f"Hoàn tất: Đã mở khóa thành công cho {unlocked_count} tài khoản."
        ))
