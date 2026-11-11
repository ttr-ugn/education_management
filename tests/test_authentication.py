"""
Education Management - Unit Tests for Authentication & User Service
Kiểm tra nghiệp vụ đăng nhập, đăng ký, khóa tài khoản tạm thời và đổi mật khẩu.
"""

from datetime import timedelta
from django.test import TestCase
from django.utils import timezone

from authentication.models import NguoiDung
from authentication.services import UserService
from common.constants import VaiTroNguoiDung, TrangThaiNguoiDung


class AuthenticationServiceTestCase(TestCase):
    """Kiểm tra dịch vụ xác thực người dùng"""

    def setUp(self):
        # Tạo sẵn tài khoản Văn thư mẫu
        self.van_thu = NguoiDung.objects.create(
            ten_dang_nhap="vanthu_test",
            ho_va_ten="Văn Thư Test",
            email="vanthu_test@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.VAN_THU,
            trang_thai=TrangThaiNguoiDung.HOAT_DONG,
            phong_ban="Văn phòng Sở"
        )
        self.van_thu.set_password("Admin@123456")
        self.van_thu.save()

    def test_authenticate_success(self):
        user, err = UserService.authenticate_user("vanthu_test", "Admin@123456")
        self.assertIsNotNone(user)
        self.assertIsNone(err)
        self.assertEqual(user.ten_dang_nhap, "vanthu_test")
        self.assertEqual(user.so_lan_dang_nhap_sai, 0)

    def test_authenticate_wrong_password(self):
        user, err = UserService.authenticate_user("vanthu_test", "WrongPassword@123")
        self.assertIsNone(user)
        self.assertIn("Mật khẩu không chính xác", err)
        self.van_thu.refresh_from_db()
        self.assertEqual(self.van_thu.so_lan_dang_nhap_sai, 1)

    def test_lockout_after_max_attempts(self):
        for _ in range(5):
            user, err = UserService.authenticate_user("vanthu_test", "WrongPass@123")
        
        self.assertIsNone(user)
        self.assertIn("tạm khóa", err)
        self.van_thu.refresh_from_db()
        self.assertIsNotNone(self.van_thu.khoa_den)
        self.assertGreater(self.van_thu.khoa_den, timezone.now())

    def test_register_user_success(self):
        new_user, err = UserService.register_user(
            ten_dang_nhap="chuyenvien_test",
            mat_khau="ChuyenVien@2026",
            ho_va_ten="Trần Thị Kiểm Thử",
            email="chuyenvien_test@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.CHUYEN_VIEN,
            phong_ban="Phòng Giáo dục Trung học",
            auto_activate=True
        )
        self.assertIsNotNone(new_user)
        self.assertIsNone(err)
        self.assertEqual(new_user.trang_thai, TrangThaiNguoiDung.HOAT_DONG)

    def test_register_duplicate_username(self):
        new_user, err = UserService.register_user(
            ten_dang_nhap="vanthu_test",
            mat_khau="ChuyenVien@2026",
            ho_va_ten="Trùng Lặp",
            email="trunglap@danang.edu.vn",
            vai_tro=VaiTroNguoiDung.CHUYEN_VIEN
        )
        self.assertIsNone(new_user)
        self.assertIn("đã tồn tại", err)

    def test_change_password(self):
        success, msg = UserService.change_password(
            user_id=self.van_thu.nguoi_dung_id,
            old_password="Admin@123456",
            new_password="NewSecurePassword@2026",
            confirm_password="NewSecurePassword@2026"
        )
        self.assertTrue(success)
        self.van_thu.refresh_from_db()
        self.assertTrue(self.van_thu.check_password("NewSecurePassword@2026"))

    def test_admin_reset_password(self):
        success, msg, temp_pw = UserService.reset_password_by_admin(
            user_id=self.van_thu.nguoi_dung_id,
            admin_user=self.van_thu
        )
        self.assertTrue(success)
        self.assertIsNotNone(temp_pw)
        self.van_thu.refresh_from_db()
        self.assertTrue(self.van_thu.check_password(temp_pw))
        self.assertEqual(self.van_thu.bat_buoc_doi_mat_khau, 1)
