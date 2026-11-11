"""
Education Management - Unit Tests for Task Dispatch & Progress Service (Cong Viec)
Kiểm tra nghiệp vụ phân công nhiệm vụ, cập nhật tiến độ, đánh giá hoàn thành và rà soát quá hạn.
"""

from datetime import date, timedelta
from django.test import TestCase

from authentication.models import NguoiDung
from cong_viec.models import CongViec, NhatKyCongViec
from cong_viec.services import (
    TaskDispatchService,
    TaskProgressService,
    TaskAnalyticsService,
)
from common.constants import VaiTroNguoiDung, TrangThaiCongViec, MucDoUuTien


class CongViecServiceTestCase(TestCase):
    """Kiểm tra dịch vụ quản lý công việc và nhiệm vụ"""

    def setUp(self):
        self.lanh_dao = NguoiDung.objects.create(
            ten_dang_nhap="lanhdao_cv",
            ho_va_ten="Võ Ngọc Đồng",
            email="dong.vn@danang.gov.vn",
            vai_tro=VaiTroNguoiDung.LANH_DAO,
            phong_ban="Ban Giám đốc Sở"
        )
        self.lanh_dao.set_password("Pass@123")
        self.lanh_dao.save()

        self.chuyen_vien = NguoiDung.objects.create(
            ten_dang_nhap="chuyenvien_cv",
            ho_va_ten="Phạm Thị Thùy Dung",
            email="dung.ptt@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.CHUYEN_VIEN,
            phong_ban="Phòng Tổ chức cán bộ"
        )
        self.chuyen_vien.set_password("Pass@123")
        self.chuyen_vien.save()

    def test_create_task(self):
        deadline = date.today() + timedelta(days=10)
        task = TaskDispatchService.create_task(
            creator=self.lanh_dao,
            ten_cong_viec="Rà soát quy hoạch cán bộ quản lý các đơn vị sự nghiệp trực thuộc Sở",
            assignee=self.chuyen_vien,
            han_hoan_thanh=deadline,
            do_uu_tien=MucDoUuTien.CAO,
            so_ky_hieu_vb="125/TB-SGDĐT"
        )
        self.assertEqual(task.tien_do, 0)
        self.assertEqual(task.trang_thai, TrangThaiCongViec.CHUA_THUC_HIEN)
        self.assertEqual(task.nhat_ky.count(), 1)

    def test_update_progress_to_in_progress(self):
        deadline = date.today() + timedelta(days=5)
        task = TaskDispatchService.create_task(
            creator=self.lanh_dao,
            ten_cong_viec="Tổ chức tập huấn CNTT cho giáo viên cốt cán",
            assignee=self.chuyen_vien,
            han_hoan_thanh=deadline
        )

        success, msg = TaskProgressService.update_progress(
            task_id=task.cong_viec_id,
            updater=self.chuyen_vien,
            new_progress=40,
            ghi_chu="Đã hoàn thành dự thảo chương trình tập huấn và danh sách đại biểu"
        )
        self.assertTrue(success)
        task.refresh_from_db()
        self.assertEqual(task.tien_do, 40)
        self.assertEqual(task.trang_thai, TrangThaiCongViec.DANG_THUC_HIEN)

    def test_update_progress_to_100_percent_triggers_review(self):
        deadline = date.today() + timedelta(days=5)
        task = TaskDispatchService.create_task(
            creator=self.lanh_dao,
            ten_cong_viec="Báo cáo công tác thanh tra quý 1",
            assignee=self.chuyen_vien,
            han_hoan_thanh=deadline
        )

        success, msg = TaskProgressService.update_progress(
            task_id=task.cong_viec_id,
            updater=self.chuyen_vien,
            new_progress=100,
            ghi_chu="Đã hoàn thành toàn bộ nội dung báo cáo nghiệm thu"
        )
        self.assertTrue(success)
        task.refresh_from_db()
        self.assertEqual(task.trang_thai, TrangThaiCongViec.CHO_DANH_GIA)

        # Lãnh đạo đánh giá đạt yêu cầu
        eval_ok, eval_msg = TaskProgressService.evaluate_task(
            task_id=task.cong_viec_id,
            evaluator=self.lanh_dao,
            is_approved=True,
            nhan_xet="Báo cáo chi tiết, số liệu chính xác. Đồng ý nghiệm thu."
        )
        self.assertTrue(eval_ok)
        task.refresh_from_db()
        self.assertEqual(task.trang_thai, TrangThaiCongViec.HOAN_THANH)

    def test_check_and_update_overdue_tasks(self):
        yesterday = date.today() - timedelta(days=2)
        # Tạo công việc có hạn hoàn thành trong quá khứ
        task = CongViec.objects.create(
            ten_cong_viec="Công việc đã bị quá hạn",
            nguoi_giao=self.lanh_dao,
            nguoi_xu_ly=self.chuyen_vien,
            phong_ban="Phòng Tổ chức cán bộ",
            han_hoan_thanh=yesterday,
            tien_do=30,
            trang_thai=TrangThaiCongViec.DANG_THUC_HIEN
        )

        overdue_count = TaskAnalyticsService.check_and_update_overdue_tasks()
        self.assertGreaterEqual(overdue_count, 1)

        task.refresh_from_db()
        self.assertEqual(task.trang_thai, TrangThaiCongViec.QUA_HAN)
