"""
Education Management - Unit Tests for Task Dispatch & Progress Service (Cong Viec)
Kiểm tra nghiệp vụ phân công nhiệm vụ, cập nhật tiến độ, đánh giá hoàn thành và rà soát quá hạn.
"""

import shutil
import tempfile
from pathlib import Path
from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings

from authentication.models import NguoiDung
from cong_viec.models import CongViec, NhatKyCongViec
from cong_viec.services import (
    TaskDispatchService,
    TaskProgressService,
    TaskAnalyticsService,
    TaskAttachmentService,
    TaskServiceException,
)
from ho_so.models import VanBanBanHanh
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

    def test_create_task_with_attachment_fields(self):
        deadline = date.today() + timedelta(days=7)
        doc_date = date.today() - timedelta(days=2)
        task = TaskDispatchService.create_task(
            creator=self.lanh_dao,
            ten_cong_viec="Triển khai kiểm tra đầu năm học",
            assignee=self.chuyen_vien,
            han_hoan_thanh=deadline,
            so_ky_hieu_vb="1752/QĐ-SGDĐT",
            trich_yeu_vb="Quyết định ban hành kế hoạch kiểm tra",
            ngay_van_ban=doc_date,
            tep_dinh_kem="/media/cong_viec_dinh_kem/sample.pdf",
            ten_tep_dinh_kem="1752_QD.pdf",
        )
        data = task.to_dict()
        self.assertEqual(data['ngay_van_ban'], doc_date.strftime('%Y-%m-%d'))
        self.assertEqual(data['tep_dinh_kem'], "/media/cong_viec_dinh_kem/sample.pdf")
        self.assertEqual(data['ten_tep_dinh_kem'], "1752_QD.pdf")
        self.assertIn('/tai-dinh-kem', data['tai_dinh_kem_url'])
        self.assertIn('xem_truoc=1', data['xem_dinh_kem_url'])

    def test_attachment_normalization_rejects_unsafe_paths(self):
        with self.assertRaises(TaskServiceException):
            TaskAttachmentService.normalize_existing_attachment('https://evil.example/a.pdf')
        with self.assertRaises(TaskServiceException):
            TaskAttachmentService.normalize_existing_attachment('/media/../settings.py')


class CongViecAttachmentApiTestCase(TestCase):
    """Kiểm tra API giao việc đính kèm tệp văn bản và tải/xem trước tệp"""

    def setUp(self):
        self.tmp_media = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.tmp_media, ignore_errors=True))

        self.van_thu = NguoiDung.objects.create(
            ten_dang_nhap="vanthu_cv_attach",
            ho_va_ten="Nguyễn Thị Thu Hằng",
            email="hang.ntt@danang.gov.vn",
            vai_tro=VaiTroNguoiDung.VAN_THU,
            phong_ban="Văn phòng Sở GD&ĐT",
        )
        self.van_thu.set_password("Pass@123")
        self.van_thu.save()

        self.chuyen_vien = NguoiDung.objects.create(
            ten_dang_nhap="chuyenvien_cv_attach",
            ho_va_ten="Nguyễn Văn Nam",
            email="nam.nv@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.CHUYEN_VIEN,
            phong_ban="Phòng Giáo dục Trung học",
        )
        self.chuyen_vien.set_password("Pass@123")
        self.chuyen_vien.save()

        self.client = Client()
        session = self.client.session
        session['user_id'] = self.van_thu.nguoi_dung_id
        session['vai_tro'] = VaiTroNguoiDung.VAN_THU
        session.save()

    def test_create_task_with_multipart_pdf_and_download(self):
        pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        upload = SimpleUploadedFile("cong_van_chi_dao.pdf", pdf_bytes, content_type="application/pdf")

        with override_settings(MEDIA_ROOT=self.tmp_media):
            resp = self.client.post(
                '/api/cong-viec',
                data={
                    'ten_cong_viec': 'Rà soát dữ liệu tuyển sinh lớp 10',
                    'nguoi_xu_ly_id': self.chuyen_vien.nguoi_dung_id,
                    'phong_ban': 'Phòng Giáo dục Trung học',
                    'han_hoan_thanh': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
                    'do_uu_tien': 'CAO',
                    'noi_dung': 'Thực hiện tổng hợp báo cáo theo công văn đính kèm.',
                    'so_ky_hieu_vb': '452/SGDĐT-GDTrH',
                    'ngay_van_ban': date.today().strftime('%Y-%m-%d'),
                    'trich_yeu_vb': 'Hướng dẫn tuyển sinh năm học 2026-2027',
                    'tep_dinh_kem': upload,
                },
            )
            self.assertEqual(resp.status_code, 200)
            payload = resp.json()
            self.assertTrue(payload['thanh_cong'])
            task_id = payload['cong_viec_id']
            task_data = payload['du_lieu']
            self.assertEqual(task_data['ten_tep_dinh_kem'], 'cong_van_chi_dao.pdf')
            self.assertTrue(task_data['tep_dinh_kem'].startswith('/media/cong_viec_dinh_kem/'))

            rel_path = task_data['tep_dinh_kem'].replace('/media/', '', 1)
            self.assertTrue((Path(self.tmp_media) / rel_path).is_file())

            dl_resp = self.client.get(f'/api/cong-viec/{task_id}/tai-dinh-kem')
            self.assertEqual(dl_resp.status_code, 200)
            self.assertIn('attachment;', dl_resp['Content-Disposition'])
            self.assertEqual(b''.join(dl_resp.streaming_content), pdf_bytes)

            preview_resp = self.client.get(f'/api/cong-viec/{task_id}/tai-dinh-kem?xem_truoc=1')
            self.assertEqual(preview_resp.status_code, 200)
            self.assertEqual(preview_resp['Content-Type'], 'application/pdf')
            self.assertNotIn('attachment;', preview_resp.get('Content-Disposition', ''))
            self.assertEqual(b''.join(preview_resp.streaming_content), pdf_bytes)

    def test_create_task_rejects_disallowed_extension(self):
        bad_file = SimpleUploadedFile("script.exe", b"MZ...", content_type="application/octet-stream")
        with override_settings(MEDIA_ROOT=self.tmp_media):
            resp = self.client.post(
                '/api/cong-viec',
                data={
                    'ten_cong_viec': 'Kiểm tra tệp sai định dạng',
                    'nguoi_xu_ly_id': self.chuyen_vien.nguoi_dung_id,
                    'noi_dung': 'Test invalid extension',
                    'tep_dinh_kem': bad_file,
                },
            )
            self.assertEqual(resp.status_code, 400)
            self.assertFalse(resp.json()['thanh_cong'])

    def test_suggested_documents_endpoint(self):
        VanBanBanHanh.objects.create(
            so_ky_hieu='999/QĐ-SGDĐT',
            trich_yeu='Quyết định ban hành quy chế phối hợp',
            loai_van_ban='Quyết định',
            nguoi_ky='Giám đốc',
            chuc_vu_nguoi_ky='Giám đốc Sở',
            ngay_ky=date.today(),
            ngay_ban_hanh=date.today(),
        )
        resp = self.client.get('/api/cong-viec/van-ban-goi-y?q=999')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['thanh_cong'])
        self.assertTrue(any(d['so_ky_hieu'] == '999/QĐ-SGDĐT' for d in data['du_lieu']))
