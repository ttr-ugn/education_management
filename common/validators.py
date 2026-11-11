"""
Education Management - Common Validators Module
Cung cấp các hàm kiểm tra tính hợp lệ dữ liệu theo quy định hành chính và tiêu chuẩn bảo mật.
"""

import re
from datetime import date, datetime
from typing import Tuple, List, Optional


class ValidationError(Exception):
    """Ngoại lệ khi kiểm tra dữ liệu không hợp lệ"""
    def __init__(self, message: str, code: str = 'invalid'):
        super().__init__(message)
        self.message = message
        self.code = code


def validate_email_address(email: str) -> bool:
    """
    Kiểm tra định dạng email tiêu chuẩn RFC 5322.
    """
    if not email or not isinstance(email, str):
        return False
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email.strip()))


def validate_phone_number(phone: str) -> bool:
    """
    Kiểm tra số điện thoại di động Việt Nam hợp lệ (10 chữ số, bắt đầu bằng 03, 05, 07, 08, 09).
    """
    if not phone or not isinstance(phone, str):
        return False
    clean_phone = re.sub(r'[\s.-]', '', phone.strip())
    vn_phone_regex = r'^(0|\+84)(3[2-9]|5[689]|7[06-9]|8[1-9]|9[0-9])[0-9]{7}$'
    return bool(re.match(vn_phone_regex, clean_phone))


def validate_so_ky_hieu(so_ky_hieu: str) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra định dạng Số và Ký hiệu văn bản hành chính theo Nghị định 30/2020/NĐ-CP.
    Ví dụ:
      - 125/QĐ-SGDĐT
      - 45/TB-VP
      - 1024/KH-SGDĐT-GDTrH
    """
    if not so_ky_hieu or not isinstance(so_ky_hieu, str):
        return False, "Số ký hiệu không được để trống"
    
    cleaned = so_ky_hieu.strip()
    pattern = r'^[0-9]+/[A-Z0-9À-Ỹ]+(-[A-Z0-9À-Ỹ]+)+$'
    if not re.match(pattern, cleaned, re.IGNORECASE):
        return False, f"Số ký hiệu '{so_ky_hieu}' không đúng chuẩn thể thức Nghị định 30/2020/NĐ-CP (Ví dụ: 125/QĐ-SGDĐT)"
    return True, None


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Kiểm tra độ phức tạp của mật khẩu bảo mật cơ quan nhà nước:
    - Độ dài tối thiểu 8 ký tự
    - Có ít nhất một chữ hoa
    - Có ít nhất một chữ thường
    - Có ít nhất một chữ số
    - Có ít nhất một ký tự đặc biệt (!@#$%^&*...)
    """
    errors = []
    if not password or len(password) < 8:
        errors.append("Mật khẩu phải có tối thiểu 8 ký tự.")
    if not re.search(r'[A-Z]', password or ''):
        errors.append("Mật khẩu phải chứa ít nhất 1 chữ cái in hoa (A-Z).")
    if not re.search(r'[a-z]', password or ''):
        errors.append("Mật khẩu phải chứa ít nhất 1 chữ cái thường (a-z).")
    if not re.search(r'[0-9]', password or ''):
        errors.append("Mật khẩu phải chứa ít nhất 1 chữ số (0-9).")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password or ''):
        errors.append("Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (!@#$%^&*...).")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def validate_file_upload(
    filename: str,
    file_size_bytes: int,
    allowed_extensions: Optional[List[str]] = None,
    max_size_mb: int = 25
) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra tính an toàn của tệp tải lên hệ thống.
    Mặc định cho phép PDF, DOCX, DOC, XLSX, XLS, PNG, JPG tối đa 25MB.
    """
    if not allowed_extensions:
        allowed_extensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg']

    if not filename:
        return False, "Tên tệp không được rỗng"

    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    if ext not in allowed_extensions:
        return False, f"Định dạng tệp '.{ext}' không được phép tải lên. Các định dạng hỗ trợ: {', '.join(allowed_extensions)}"

    max_bytes = max_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        return False, f"Kích thước tệp ({file_size_bytes / (1024*1024):.2f}MB) vượt quá giới hạn cho phép {max_size_mb}MB"

    # Kiểm tra tên tệp không chứa ký tự độc hại (path traversal)
    if '..' in filename or '/' in filename or '\\' in filename:
        return False, "Tên tệp chứa ký tự không an toàn"

    return True, None


def validate_date_range(start_date: date, end_date: date) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra khoảng thời gian bắt đầu và kết thúc có hợp lý không.
    """
    if not start_date or not end_date:
        return False, "Ngày bắt đầu và ngày kết thúc không được để trống"
    if end_date < start_date:
        return False, f"Hạn hoàn thành ({end_date.strftime('%d/%m/%Y')}) không thể trước ngày bắt đầu ({start_date.strftime('%d/%m/%Y')})"
    return True, None


def validate_cccd(cccd: str) -> bool:
    """
    Kiểm tra định dạng Căn cước công dân Việt Nam (12 chữ số).
    """
    if not cccd or not isinstance(cccd, str):
        return False
    return bool(re.match(r'^[0-9]{12}$', cccd.strip()))
