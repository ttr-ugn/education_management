"""
Education Management - Security & Data Protection Module
Cung cấp các cơ chế phòng chống XSS, kiểm tra ký tự độc hại, tạo chữ ký số và token bảo mật.
"""

import html
import hmac
import hashlib
import secrets
import string
import time
from typing import Dict, Any, Optional


class SecurityCheckException(Exception):
    """Ngoại lệ khi phát hiện tấn công hoặc dữ liệu không an toàn"""
    pass


def sanitize_input_text(raw_text: Optional[str], allow_newlines: bool = True) -> str:
    """
    Loại bỏ các ký tự có nguy cơ gây lỗi bảo mật XSS, escape HTML an toàn.
    """
    if raw_text is None:
        return ""
    
    sanitized = html.escape(str(raw_text).strip())
    if not allow_newlines:
        sanitized = sanitized.replace('\n', ' ').replace('\r', '')
    return sanitized


def generate_secure_token(length: int = 32) -> str:
    """
    Tạo token bảo mật ngẫu nhiên dùng cho reset mật khẩu, CSRF token hoặc xác thực phiên.
    """
    return secrets.token_urlsafe(length)


def generate_secure_password(length: int = 12) -> str:
    """
    Tạo mật khẩu ngẫu nhiên tuân thủ quy chuẩn bảo mật (chữ hoa, chữ thường, số, ký tự đặc biệt).
    """
    if length < 8:
        length = 8
    
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*"

    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]
    all_chars = uppercase + lowercase + digits + special
    password += [secrets.choice(all_chars) for _ in range(length - 4)]
    
    # Xáo trộn các ký tự
    temp_list = list(password)
    secrets.SystemRandom().shuffle(temp_list)
    return ''.join(temp_list)


def check_sql_injection_keywords(query_str: str) -> bool:
    """
    Phát hiện các từ khóa SQL injection tiềm ẩn trong tham số tìm kiếm hoặc chuỗi truy vấn.
    """
    if not query_str or not isinstance(query_str, str):
        return False

    suspicious_patterns = [
        r"(--|/\*|\*/)",
        r"\b(union\s+select|select\s+.*\s+from|insert\s+into|drop\s+table|delete\s+from|update\s+.*\s+set)\b",
        r"\b(or\s+1=1|or\s+'1'='1'|and\s+1=1)\b",
        r"\b(exec\s*\(|execute\s*\(|xp_cmdshell)\b",
    ]

    import re
    lower_query = query_str.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, lower_query):
            return True
    return False


class SimpleRateLimiter:
    """
    Bộ đếm giới hạn tốc độ truy cập trong bộ nhớ (Rate limiter) theo địa chỉ IP hoặc tên đăng nhập.
    """
    def __init__(self, max_requests: int = 60, time_window_seconds: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window_seconds
        self.records: Dict[str, list] = {}

    def is_allowed(self, identifier: str) -> bool:
        current_time = time.time()
        timestamps = self.records.get(identifier, [])
        # Lọc các timestamp nằm trong khung thời gian
        valid_timestamps = [t for t in timestamps if current_time - t < self.time_window]
        
        if len(valid_timestamps) >= self.max_requests:
            self.records[identifier] = valid_timestamps
            return False
        
        valid_timestamps.append(current_time)
        self.records[identifier] = valid_timestamps
        return True

    def reset(self, identifier: str) -> None:
        if identifier in self.records:
            del self.records[identifier]
