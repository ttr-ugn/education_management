"""
Education Management - Unit Tests for Notification Service (Thong Bao)
Kiểm tra nghiệp vụ gửi thông báo, tính số lượng chưa đọc phục vụ badge header (2s polling) và đánh dấu đã xem.
"""

from django.test import TestCase

from authentication.models import NguoiDung
from thong_bao.models import ThongBao, ThongBaoDaDoc
from thong_bao.services import (
    NotificationPushService,
    NotificationReadService,
)
from common.constants import VaiTroNguoiDung, LoaiThongBao, MucDoUuTien


class ThongBaoServiceTestCase(TestCase):
    """Kiểm tra dịch vụ thông báo thời gian thực"""

    def setUp(self):
        self.user1 = NguoiDung.objects.create(
            ten_dang_nhap="chuyenvien_tb",
            ho_va_ten="Trần Văn Minh",
            email="minh.tv@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.CHUYEN_VIEN
        )
        self.user1.set_password("Pass@123")
        self.user1.save()

        self.user2 = NguoiDung.objects.create(
            ten_dang_nhap="lanhdao_tb",
            ho_va_ten="Lê Thị Bích Thuận",
            email="thuan.ltb@danang.gov.vn",
            vai_tro=VaiTroNguoiDung.LANH_DAO
        )
        self.user2.set_password("Pass@123")
        self.user2.save()

    def test_personal_notification_and_unread_count(self):
        # Ban đầu chưa có thông báo
        self.assertEqual(NotificationReadService.get_unread_count(self.user1), 0)

        # Gửi 2 thông báo cá nhân
        n1 = NotificationPushService.push_personal_notification(
            recipient=self.user1,
            title="Nhiệm vụ mới",
            content="Đồng chí vừa được giao nhiệm vụ chuẩn bị báo cáo tháng",
            loai=LoaiThongBao.CONG_VIEC,
            sender=self.user2
        )
        n2 = NotificationPushService.push_personal_notification(
            recipient=self.user1,
            title="Văn bản đến mới",
            content="Văn bản đến số 12/BGDĐT cần xử lý",
            loai=LoaiThongBao.VAN_BAN,
            sender=self.user2
        )

        # Kiểm tra số lượng chưa đọc tăng lên 2
        self.assertEqual(NotificationReadService.get_unread_count(self.user1), 2)

        # Đánh dấu đọc 1 thông báo
        NotificationReadService.mark_as_read(n1.thong_bao_id, self.user1)
        self.assertEqual(NotificationReadService.get_unread_count(self.user1), 1)

        # Đánh dấu đọc tất cả
        NotificationReadService.mark_all_as_read(self.user1)
        self.assertEqual(NotificationReadService.get_unread_count(self.user1), 0)

    def test_broadcast_notification(self):
        # Gửi thông báo chung toàn cơ quan (nguoi_nhan = None)
        NotificationPushService.broadcast_to_all(
            title="Lịch họp giao ban đầu tuần",
            content="Kính mời toàn thể cán bộ dự họp giao ban trực tuyến lúc 8h00 thứ Hai",
            sender=self.user2
        )

        # Cả user1 và user2 đều có 1 thông báo chưa đọc
        self.assertEqual(NotificationReadService.get_unread_count(self.user1), 1)
        self.assertEqual(NotificationReadService.get_unread_count(self.user2), 1)
