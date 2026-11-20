"""
Education Management - Unit Tests for Document Workflow Service (Van Ban)
Kiểm tra chu trình luân chuyển văn bản đi và vào sổ văn bản đến theo Nghị định 30/2020/NĐ-CP.
"""

from datetime import date
from django.test import TestCase

from authentication.models import NguoiDung
from van_ban.models import VanBanDi, VanBanDen, LichSuXuLyVanBan
from van_ban.services import (
    DocumentNumberingService,
    OutboundDocumentService,
    InboundDocumentService,
)
from common.constants import (
    VaiTroNguoiDung,
    TrangThaiVanBanDi,
    TrangThaiVanBanDen,
)


class VanBanWorkflowTestCase(TestCase):
    """Kiểm tra toàn bộ luồng xử lý văn bản đi"""

    def setUp(self):
        # Tạo Chuyên viên
        self.chuyen_vien = NguoiDung.objects.create(
            ten_dang_nhap="chuyenvien_vb",
            ho_va_ten="Nguyễn Văn Nam",
            email="nam.nv@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.CHUYEN_VIEN,
            phong_ban="Phòng Giáo dục Trung học"
        )
        self.chuyen_vien.set_password("Pass@123456")
        self.chuyen_vien.save()

        # Tạo Văn thư
        self.van_thu = NguoiDung.objects.create(
            ten_dang_nhap="vanthu_vb",
            ho_va_ten="Nguyễn Thị Thu Hằng",
            email="hang.ntt@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.VAN_THU,
            phong_ban="Văn phòng Sở"
        )
        self.van_thu.set_password("Pass@123456")
        self.van_thu.save()

        # Tạo Lãnh đạo
        self.lanh_dao = NguoiDung.objects.create(
            ten_dang_nhap="lanhdao_vb",
            ho_va_ten="Mai Tấn Linh",
            email="linh.mt@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.LANH_DAO,
            chuc_vu="Phó Giám đốc Sở",
            phong_ban="Ban Giám đốc Sở"
        )
        self.lanh_dao.set_password("Pass@123456")
        self.lanh_dao.save()

    def test_document_numbering_generator(self):
        so_qd = DocumentNumberingService.generate_next_outbound_number("Quyết định", 2026)
        self.assertIn("/QĐ-SGDĐT", so_qd)

        so_kh = DocumentNumberingService.generate_next_outbound_number("Kế hoạch", 2026)
        self.assertIn("/KH-SGDĐT", so_kh)

    def test_complete_outbound_workflow(self):
        # 1. Chuyên viên soạn dự thảo
        doc = OutboundDocumentService.create_draft(
            author=self.chuyen_vien,
            trich_yeu="Về việc phân luồng tuyển sinh vào lớp 10 năm học 2026 - 2027",
            loai_van_ban="Kế hoạch",
            do_khan="Bình thường",
            noi_nhan="Các trường THPT trên địa bàn TP",
            lanh_dao_ky=self.lanh_dao
        )
        self.assertEqual(doc.trang_thai, TrangThaiVanBanDi.DU_THAO)
        self.assertEqual(doc.lich_su.count(), 1)

        # 2. Chuyên viên trình văn thư kiểm tra
        success, _ = OutboundDocumentService.submit_to_clerk(doc.van_ban_id, self.chuyen_vien, "Kính trình văn thư soát thể thức")
        self.assertTrue(success)
        doc.refresh_from_db()
        self.assertEqual(doc.trang_thai, TrangThaiVanBanDi.CHO_VAN_THU_KIEM_TRA)

        # 3. Văn thư kiểm tra duyệt đạt yêu cầu
        success, _ = OutboundDocumentService.clerk_review(doc.van_ban_id, self.van_thu, approved=True, y_kien="Thể thức chuẩn Nghị định 30")
        self.assertTrue(success)
        doc.refresh_from_db()
        self.assertEqual(doc.trang_thai, TrangThaiVanBanDi.CHO_LANH_DAO_DUYET)

        # 4. Lãnh đạo ký số phê duyệt
        success, _, sig_data = OutboundDocumentService.leader_sign_and_approve(
            doc.van_ban_id, self.lanh_dao, approved=True, y_kien="Đồng ý ban hành", x=420, y=680
        )
        self.assertTrue(success)
        self.assertIsNotNone(sig_data)
        doc.refresh_from_db()
        self.assertEqual(doc.trang_thai, TrangThaiVanBanDi.CHO_CAP_SO)
        self.assertIsNotNone(doc.file_da_ky_ten)

        # 5. Văn thư cấp số và ban hành
        success, _, so_ban_hanh = OutboundDocumentService.issue_document(
            doc.van_ban_id, self.van_thu, so_ky_hieu="88/KH-SGDĐT", ngay_ban_hanh=date(2026, 3, 15)
        )
        self.assertTrue(success)
        doc.refresh_from_db()
        self.assertEqual(doc.trang_thai, TrangThaiVanBanDi.DA_BAN_HANH)
        self.assertEqual(doc.so_ky_hieu, "88/KH-SGDĐT")

        # Kiểm tra nhật ký lịch sử luân chuyển
        history = doc.lich_su.all()
        self.assertEqual(history.count(), 5)

    def test_inbound_document_registration_and_assignment(self):
        doc = InboundDocumentService.register_inbound_document(
            clerk=self.van_thu,
            so_ky_hieu="450/BGDĐT-GDTrH",
            co_quan_ban_hanh="Bộ Giáo dục và Đào tạo",
            trich_yeu="Hướng dẫn triển khai đề án giáo dục thông minh giai đoạn 2026-2030",
            loai_van_ban="Hướng dẫn",
            do_khan="Khẩn",
            han_xu_ly=date(2026, 4, 30)
        )
        self.assertIsNotNone(doc.so_den)
        self.assertEqual(doc.trang_thai, TrangThaiVanBanDen.CHO_TIEP_NHAN)

        # Lãnh đạo chỉ đạo và phân công chuyên viên
        ok, msg = InboundDocumentService.assign_directive(
            van_ban_id=doc.van_ban_id,
            leader=self.lanh_dao,
            assignee=self.chuyen_vien,
            directive_text="Giao phòng GDTrH tham mưu kế hoạch chi tiết trước ngày 25/04."
        )
        self.assertTrue(ok)
        doc.refresh_from_db()
        self.assertEqual(doc.trang_thai, TrangThaiVanBanDen.DANG_XU_LY)
        self.assertEqual(doc.nguoi_chu_tri, self.chuyen_vien)

    def test_chung_thuc_chu_ky_so_page_and_api(self):
        """Kiểm tra trang và API Dịch vụ chứng thực chữ ký số."""
        # 1. Kiểm tra tải giao diện chứng thực
        response = self.client.get('/pages/van-ban-di/chung-thuc-chu-ky-so.html')
        self.assertEqual(response.status_code, 200)

        # 2. Tạo một văn bản đã ký số
        doc = VanBanDi.objects.create(
            trich_yeu="Kế hoạch tuyển sinh đầu cấp năm học 2026-2027",
            loai_van_ban="Kế hoạch",
            nguoi_soan=self.chuyen_vien,
            lanh_dao_ky=self.lanh_dao,
            lanh_dao_ky_ten="Mai Tấn Linh",
            trang_thai="DA_KY_CHO_BAN_HANH"
        )

        # 3. Kiểm tra API GET danh sách văn bản và CA
        res_get = self.client.get('/api/van-ban-di/chung-thuc-chu-ky-so')
        self.assertEqual(res_get.status_code, 200)
        data_get = res_get.json()
        self.assertTrue(data_get['thanh_cong'])
        self.assertIn('chung_thu_ca', data_get)
        self.assertIn('danh_sach_van_ban', data_get)
        self.assertGreaterEqual(len(data_get['danh_sach_van_ban']), 1)

        # 4. Kiểm tra API POST thẩm định theo ID văn bản
        res_post_id = self.client.post('/api/van-ban-di/chung-thuc-chu-ky-so', {'van_ban_id': doc.van_ban_id})
        self.assertEqual(res_post_id.status_code, 200)
        data_post_id = res_post_id.json()
        self.assertTrue(data_post_id['thanh_cong'])
        self.assertTrue(data_post_id['hop_le'])
        self.assertEqual(data_post_id['ket_qua']['trang_thai'], 'TOAN_VEN_HOP_LE')
        self.assertIsNotNone(data_post_id['ket_qua']['ma_bam_sha256'])

        # 5. Kiểm tra API POST thẩm định với tệp tải lên
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile("quyet_dinh_signed.pdf", b"%PDF-1.4 Mock signed content with VGCA certificate", content_type="application/pdf")
        res_post_file = self.client.post('/api/van-ban-di/chung-thuc-chu-ky-so', {'file': test_file})
        self.assertEqual(res_post_file.status_code, 200)
        data_post_file = res_post_file.json()
        self.assertTrue(data_post_file['thanh_cong'])
        self.assertTrue(data_post_file['hop_le'])
        self.assertIn('ma_bam_sha256', data_post_file['ket_qua'])

    def test_api_ky_so_phe_duyet(self):
        """Kiểm tra API Ký số văn bản của Lãnh đạo."""
        doc = VanBanDi.objects.create(
            trich_yeu="Quyết định khen thưởng tập thể cán bộ giáo viên",
            loai_van_ban="Quyết định",
            nguoi_soan=self.chuyen_vien,
            trang_thai="CHO_LANH_DAO_KY"
        )
        res = self.client.post(f'/api/van-ban-di/{doc.van_ban_id}/ky-so')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['thanh_cong'])
        doc.refresh_from_db()
        self.assertEqual(doc.trang_thai, 'DA_KY_CHO_BAN_HANH')
        self.assertIsNotNone(doc.thoi_gian_ky)
        self.assertIsNotNone(doc.lanh_dao_ky_ten)

