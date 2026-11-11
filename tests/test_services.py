"""
Education Management - Unit Tests for Reports & Serialization Services
Kiểm tra module tuần tự hóa dữ liệu và trích xuất báo cáo thống kê chuyên sâu.
"""

from django.test import TestCase
from authentication.models import NguoiDung
from van_ban.models import VanBanDi
from cong_viec.models import CongViec
from ho_so.models import HoSoLuuTru
from common.serializers import ModelSerializer
from van_ban.reports import DocumentReportGenerator
from cong_viec.reports import TaskPerformanceReporter
from ho_so.reports import ArchivalReportGenerator
from common.constants import VaiTroNguoiDung, TrangThaiVanBanDi, TrangThaiCongViec


class SerializersTestCase(TestCase):
    """Kiểm tra module ModelSerializer"""

    def setUp(self):
        self.user = NguoiDung.objects.create(
            ten_dang_nhap="serialize_user",
            ho_va_ten="Người Dùng Tuần Tự Hóa",
            email="serial@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.CHUYEN_VIEN
        )

    def test_serialize_instance_with_fields(self):
        data = ModelSerializer.serialize_instance(
            self.user,
            fields=['ten_dang_nhap', 'ho_va_ten', 'email']
        )
        self.assertEqual(data['ten_dang_nhap'], "serialize_user")
        self.assertEqual(data['ho_va_ten'], "Người Dùng Tuần Tự Hóa")
        self.assertNotIn('mat_khau_hash', data)

    def test_serialize_instance_to_json(self):
        json_str = ModelSerializer.to_json({'user': self.user})
        self.assertIn("serialize_user", json_str)


class ReportsTestCase(TestCase):
    """Kiểm tra các bộ sinh báo cáo nghiệp vụ"""

    def setUp(self):
        self.user = NguoiDung.objects.create(
            ten_dang_nhap="report_user",
            ho_va_ten="Cán Bộ Báo Cáo",
            email="report@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.CHUYEN_VIEN,
            phong_ban="Phòng Giáo dục Trung học"
        )
        VanBanDi.objects.create(
            trich_yeu="Văn bản báo cáo kiểm thử",
            loai_van_ban="Quyết định",
            don_vi_soan_thao="Phòng Giáo dục Trung học",
            nguoi_soan=self.user,
            trang_thai=TrangThaiVanBanDi.DA_BAN_HANH
        )

    def test_document_report_distribution(self):
        dist = DocumentReportGenerator.get_document_type_distribution()
        self.assertIsInstance(dist, list)
        self.assertGreaterEqual(len(dist), 1)
        self.assertEqual(dist[0]['loai_van_ban'], "Quyết định")

    def test_document_department_ranking(self):
        ranking = DocumentReportGenerator.get_department_outbound_ranking()
        self.assertIsInstance(ranking, list)
        self.assertGreaterEqual(len(ranking), 1)

    def test_task_weekly_progress(self):
        overview = TaskPerformanceReporter.get_weekly_progress_overview()
        self.assertIn('new_tasks_count', overview)
        self.assertIn('completed_recently_count', overview)

    def test_priority_task_matrix(self):
        matrix = TaskPerformanceReporter.get_priority_task_matrix()
        self.assertIn('CAO', matrix)
        self.assertIn('TRUNG_BINH', matrix)

    def test_archival_inventory_summary(self):
        summary = ArchivalReportGenerator.get_annual_inventory_summary()
        self.assertIn('total_dossiers', summary)
        self.assertIn('submission_rate', summary)
