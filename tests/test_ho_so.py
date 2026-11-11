"""
Education Management - Unit Tests for Dossier & Archival Service (Ho So Luu Tru)
Kiểm tra nghiệp vụ lập hồ sơ, đóng gói văn bản, tính hạn bảo quản và chuyển giao lưu trữ.
"""

from datetime import date
from django.test import TestCase

from authentication.models import NguoiDung
from ho_so.models import HoSoLuuTru, VanBanBanHanh
from ho_so.services import (
    DossierCodeService,
    DossierManagementService,
    RetentionPolicyService,
)
from common.constants import VaiTroNguoiDung, TrangThaiHoSo, ThoiHanBaoQuan


class HoSoServiceTestCase(TestCase):
    """Kiểm tra dịch vụ quản lý hồ sơ lưu trữ"""

    def setUp(self):
        self.van_thu = NguoiDung.objects.create(
            ten_dang_nhap="vanthu_hs",
            ho_va_ten="Văn Thư Lưu Trữ",
            email="luutru@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.VAN_THU,
            phong_ban="Văn phòng Sở"
        )
        self.van_thu.set_password("Pass@123")
        self.van_thu.save()

    def test_dossier_code_generation(self):
        code = DossierCodeService.generate_next_code(2026)
        self.assertTrue(code.startswith("HS-2026-"))
        self.assertEqual(len(code), 11)  # HS-2026-001

    def test_create_dossier_and_add_document(self):
        dossier = DossierManagementService.create_dossier(
            tieu_de="Hồ sơ tuyển sinh đầu cấp các lớp 1, 6, 10 năm học 2026 - 2027",
            creator=self.van_thu,
            don_vi="Phòng Giáo dục Trung học",
            nam_tai_lieu=2026,
            thoi_han_bao_quan=ThoiHanBaoQuan.MUOI_NAM
        )
        self.assertEqual(dossier.so_luong_van_ban, 0)
        self.assertEqual(dossier.tinh_trang, TrangThaiHoSo.DANG_THU_THAP)

        # Tạo văn bản ban hành đưa vào hồ sơ
        doc = VanBanBanHanh.objects.create(
            so_ky_hieu="12/QĐ-SGDĐT",
            trich_yeu="Quyết định ban hành kế hoạch tuyển sinh đầu cấp",
            loai_van_ban="Quyết định",
            nguoi_ky="Lê Thị Bích Thuận",
            chuc_vu_nguoi_ky="Giám đốc Sở",
            ngay_ky=date(2026, 2, 20),
            ngay_ban_hanh=date(2026, 2, 20),
            nam_luu_tru=2026
        )

        ok, msg = DossierManagementService.add_document_to_dossier(dossier.ho_so_id, doc.van_ban_id)
        self.assertTrue(ok)

        dossier.refresh_from_db()
        self.assertEqual(dossier.so_luong_van_ban, 1)

        # Nộp lưu trữ cơ quan
        submit_ok, submit_msg = DossierManagementService.submit_to_archive(dossier.ho_so_id, self.van_thu)
        self.assertTrue(submit_ok)
        dossier.refresh_from_db()
        self.assertEqual(dossier.tinh_trang, TrangThaiHoSo.DA_NOP_LUU_TRU)

    def test_calculate_expiration_year(self):
        exp_10 = RetentionPolicyService.calculate_expiration_year(2026, ThoiHanBaoQuan.MUOI_NAM)
        self.assertEqual(exp_10, 2036)

        exp_5 = RetentionPolicyService.calculate_expiration_year(2026, ThoiHanBaoQuan.NAM_NAM)
        self.assertEqual(exp_5, 2031)

        exp_perm = RetentionPolicyService.calculate_expiration_year(2026, ThoiHanBaoQuan.VINH_VIEN)
        self.assertIsNone(exp_perm)
