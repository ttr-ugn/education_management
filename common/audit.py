"""
Education Management - System Audit & Action Tracing Module
Ghi nhận nhật ký tác vụ hệ thống (audit trail) phục vụ việc thanh tra công vụ và an toàn thông tin.
"""

import functools
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from dashboard.models import NhatKyHeThong

logger = logging.getLogger('education_management.audit')


def get_client_ip(request: Any) -> str:
    """
    Trích xuất địa chỉ IP thực tế của client qua các reverse proxy (X-Forwarded-For).
    """
    if not request:
        return '127.0.0.1'
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def log_system_action(
    hanh_dong: str,
    chi_tiet: Optional[str] = None,
    nguoi_thuc_hien: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Optional[NhatKyHeThong]:
    """
    Ghi nhận một hành vi vào bảng NhatKyHeThong.
    """
    try:
        detail_msg = chi_tiet or ""
        meta_parts = []
        if nguoi_thuc_hien:
            meta_parts.append(f"Người dùng: {nguoi_thuc_hien}")
        if ip_address:
            meta_parts.append(f"IP: {ip_address}")
        
        if meta_parts:
            header = f"[{' | '.join(meta_parts)}] "
            detail_msg = header + detail_msg

        log_entry = NhatKyHeThong.objects.create(
            hanh_dong=hanh_dong,
            chi_tiet=detail_msg
        )
        return log_entry
    except Exception as exc:
        logger.error(f"Lỗi khi ghi nhật ký hệ thống: {exc}")
        return None


def audit_action(action_name: str):
    """
    Decorator dùng để tự động ghi log khi một view hoặc hàm dịch vụ được thực thi.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if hasattr(arg, 'META') and hasattr(arg, 'session'):
                    request = arg
                    break

            username = "System"
            ip = "127.0.0.1"
            if request:
                username = request.session.get('user', {}).get('ho_va_ten') or request.session.get('user', {}).get('ten_dang_nhap') or 'Khách'
                ip = get_client_ip(request)

            try:
                result = func(*args, **kwargs)
                log_system_action(
                    hanh_dong=action_name,
                    chi_tiet=f"Thực hiện thành công hàm {func.__name__}",
                    nguoi_thuc_hien=username,
                    ip_address=ip
                )
                return result
            except Exception as e:
                log_system_action(
                    hanh_dong=action_name,
                    chi_tiet=f"Lỗi thực thi hàm {func.__name__}: {str(e)}",
                    nguoi_thuc_hien=username,
                    ip_address=ip
                )
                raise
        return wrapper
    return decorator
