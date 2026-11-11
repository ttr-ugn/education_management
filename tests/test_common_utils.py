"""
Education Management - Unit Tests for Common Utilities
Kiểm tra tính chính xác của các bộ kiểm tra hợp lệ, bảo mật, ký số và xuất báo cáo dữ liệu.
"""

from datetime import date, datetime
from django.test import SimpleTestCase

from common.validators import (
    validate_email_address,
    validate_phone_number,
    validate_so_ky_hieu,
    validate_password_strength,
    validate_file_upload,
    validate_date_range,
    validate_cccd,
)
from common.security import (
    sanitize_input_text,
    generate_secure_token,
    generate_secure_password,
    check_sql_injection_keywords,
    SimpleRateLimiter,
)
from common.pdf_signer import PDFSignerService
from common.excel_exporter import ExcelExporter
from common.pagination import build_page_range


class CommonValidatorsTestCase(SimpleTestCase):
    """Kiểm tra các hàm validate dữ liệu chuẩn hành chính"""

    def test_validate_email_address(self):
        self.assertTrue(validate_email_address("admin@danang.edu.vn"))
        self.assertTrue(validate_email_address("nguyenvannam.gdth@danang.gov.vn"))
        self.assertFalse(validate_email_address("invalid-email"))
        self.assertFalse(validate_email_address("@nodomain.com"))
        self.assertFalse(validate_email_address(""))

    def test_validate_phone_number(self):
        self.assertTrue(validate_phone_number("0905123456"))
        self.assertTrue(validate_phone_number("0912345678"))
        self.assertTrue(validate_phone_number("0389998888"))
        self.assertFalse(validate_phone_number("0123456789"))  # Đầu số cũ 11 số
        self.assertFalse(validate_phone_number("abcdef"))
        self.assertFalse(validate_phone_number("12345"))

    def test_validate_so_ky_hieu(self):
        valid, _ = validate_so_ky_hieu("125/QĐ-SGDĐT")
        self.assertTrue(valid)
        valid, _ = validate_so_ky_hieu("45/TB-VP")
        self.assertTrue(valid)
        valid, _ = validate_so_ky_hieu("1024/KH-SGDĐT-GDTrH")
        self.assertTrue(valid)

        invalid, err = validate_so_ky_hieu("125-QD-SGDDT")
        self.assertFalse(invalid)
        self.assertIsNotNone(err)

    def test_validate_password_strength(self):
        valid, errors = validate_password_strength("Danang@2026")
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Mật khẩu yếu: chỉ có chữ thường
        valid, errors = validate_password_strength("weakpassword")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_validate_file_upload(self):
        valid, _ = validate_file_upload("ke-hoach.pdf", 1024 * 1024)
        self.assertTrue(valid)

        # File exe bị cấm
        invalid, err = validate_file_upload("virus.exe", 1024)
        self.assertFalse(invalid)
        self.assertIn("không được phép", err)

        # Vượt quá 25MB
        invalid_size, err_size = validate_file_upload("huge.pdf", 30 * 1024 * 1024)
        self.assertFalse(invalid_size)
        self.assertIn("vượt quá", err_size)

    def test_validate_date_range(self):
        valid, _ = validate_date_range(date(2026, 1, 1), date(2026, 1, 15))
        self.assertTrue(valid)

        invalid, err = validate_date_range(date(2026, 2, 1), date(2026, 1, 15))
        self.assertFalse(invalid)
        self.assertIn("không thể trước", err)

    def test_validate_cccd(self):
        self.assertTrue(validate_cccd("048098001234"))
        self.assertFalse(validate_cccd("04809800123"))  # 11 số
        self.assertFalse(validate_cccd("0480980012345"))  # 13 số


class CommonSecurityTestCase(SimpleTestCase):
    """Kiểm tra các hàm phòng chống tấn công bảo mật"""

    def test_sanitize_input_text(self):
        raw = "<script>alert('hack');</script>Văn bản số 1"
        sanitized = sanitize_input_text(raw)
        self.assertNotIn("<script>", sanitized)
        self.assertIn("&lt;script&gt;", sanitized)

    def test_generate_secure_token(self):
        token1 = generate_secure_token(32)
        token2 = generate_secure_token(32)
        self.assertNotEqual(token1, token2)
        self.assertGreaterEqual(len(token1), 32)

    def test_generate_secure_password(self):
        pw = generate_secure_password(14)
        self.assertEqual(len(pw), 14)
        valid, _ = validate_password_strength(pw)
        self.assertTrue(valid)

    def test_check_sql_injection_keywords(self):
        self.assertTrue(check_sql_injection_keywords("' UNION SELECT * FROM users --"))
        self.assertTrue(check_sql_injection_keywords("1; DROP TABLE nguoi_dung;"))
        self.assertFalse(check_sql_injection_keywords("Kế hoạch năm học 2026 - 2027"))

    def test_simple_rate_limiter(self):
        limiter = SimpleRateLimiter(max_requests=3, time_window_seconds=10)
        ip = "192.168.1.100"
        self.assertTrue(limiter.is_allowed(ip))
        self.assertTrue(limiter.is_allowed(ip))
        self.assertTrue(limiter.is_allowed(ip))
        self.assertFalse(limiter.is_allowed(ip))  # Yêu cầu thứ 4 bị chặn


class PDFSignerTestCase(SimpleTestCase):
    """Kiểm tra dịch vụ ký số tài liệu"""

    def test_calculate_text_hash(self):
        content = "Sở Giáo dục và Đào tạo TP Đà Nẵng - Quyết định 125"
        h1 = PDFSignerService.calculate_text_hash(content)
        h2 = PDFSignerService.calculate_text_hash(content)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)  # SHA-256 có 64 ký tự hex

    def test_apply_digital_signature(self):
        sig = PDFSignerService.apply_digital_signature(
            document_id=99,
            signer_name="Lê Thị Bích Thuận",
            signer_title="Giám đốc Sở",
            x=350,
            y=700
        )
        self.assertTrue(sig['success'])
        self.assertIn('signature', sig)
        self.assertEqual(sig['signature']['signer_name'], "Lê Thị Bích Thuận")
        self.assertEqual(sig['signature']['x_coord'], 350)


class PaginationHelperTestCase(SimpleTestCase):
    """Kiểm tra dải phân trang trượt"""

    def test_build_page_range_short(self):
        pages = build_page_range(current_page=2, total_pages=5)
        self.assertEqual(pages, [1, 2, 3, 4, 5])

    def test_build_page_range_long(self):
        pages = build_page_range(current_page=10, total_pages=20)
        self.assertIn(1, pages)
        self.assertIn(20, pages)
        self.assertIn('...', pages)
        self.assertIn(10, pages)


class ExcelExporterTestCase(SimpleTestCase):
    """Kiểm tra module xuất báo cáo CSV UTF-8 BOM"""

    def test_export_to_csv_bom(self):
        headers = ['STT', 'Tiêu đề', 'Đơn vị']
        rows = [[1, 'Kế hoạch công tác năm 2026', 'Văn phòng Sở']]
        csv_data = ExcelExporter.export_to_csv_bom(headers, rows, title="Báo cáo kiểm thử")
        self.assertTrue(csv_data.startswith('\ufeff'))  # Chứa UTF-8 BOM
        self.assertIn('BÁO CÁO KIỂM THỬ', csv_data)
        self.assertIn('Kế hoạch công tác năm 2026', csv_data)
