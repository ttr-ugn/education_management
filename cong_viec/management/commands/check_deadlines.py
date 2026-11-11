"""
Management Command: check_deadlines
Tự động quét và cập nhật trạng thái các công việc quá hạn trong hệ thống,
đồng thời phát cảnh báo đến cán bộ phụ trách và lãnh đạo phòng ban.
"""

from datetime import date
from django.core.management.base import BaseCommand
from cong_viec.models import CongViec
from cong_viec.services import TaskAnalyticsService
from thong_bao.services import NotificationPushService
from common.constants import TrangThaiCongViec, LoaiThongBao, MucDoUuTien


class Command(BaseCommand):
    help = 'Quét toàn bộ nhiệm vụ và tự động chuyển trạng thái QUA_HAN đối với các công việc trễ hạn'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Đang thực hiện rà soát tiến độ và hạn hoàn thành các nhiệm vụ..."))

        updated_count = TaskAnalyticsService.check_and_update_overdue_tasks()

        # Tìm các công việc vừa bị quá hạn để phát cảnh báo
        overdue_tasks = CongViec.objects.filter(trang_thai=TrangThaiCongViec.QUA_HAN)
        notif_sent = 0

        for task in overdue_tasks:
            if task.nguoi_xu_ly:
                notif_sent += 1
                NotificationPushService.push_personal_notification(
                    recipient=task.nguoi_xu_ly,
                    title=f"[Cảnh báo trễ hạn] Nhiệm vụ: {task.ten_cong_viec}",
                    content=f"Công việc '{task.ten_cong_viec}' đã quá hạn vào ngày {task.han_hoan_thanh.strftime('%d/%m/%Y')} nhưng hiện mới đạt {task.tien_do}%. Vui lòng khẩn trương hoàn thành báo cáo.",
                    loai=LoaiThongBao.CANH_BAO,
                    muc_do=MucDoUuTien.CAO,
                    lien_ket="/cong-viec/danh-sach.html"
                )

        self.stdout.write(self.style.SUCCESS(
            f"Đã cập nhật {updated_count} công việc sang trạng thái QUÁ HẠN và gửi {notif_sent} thông báo cảnh báo."
        ))
