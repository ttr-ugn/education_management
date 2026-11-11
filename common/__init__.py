"""
Education Management - Common Utilities Package
Cung cấp các tiện ích dùng chung cho toàn bộ các module trong hệ thống.
"""

from .constants import (
    VaiTroNguoiDung,
    TrangThaiVanBanDi,
    TrangThaiVanBanDen,
    TrangThaiCongViec,
    MucDoUuTien,
    TrangThaiHoSo,
    ThoiHanBaoQuan,
)
from .validators import (
    validate_email_address,
    validate_phone_number,
    validate_so_ky_hieu,
    validate_file_upload,
    validate_password_strength,
)
from .security import (
    sanitize_input_text,
    generate_secure_token,
    SecurityCheckException,
)
from .pagination import (
    build_page_range,
    paginate_queryset,
)
from .audit import (
    log_system_action,
    get_client_ip,
)

__all__ = [
    'VaiTroNguoiDung',
    'TrangThaiVanBanDi',
    'TrangThaiVanBanDen',
    'TrangThaiCongViec',
    'MucDoUuTien',
    'TrangThaiHoSo',
    'ThoiHanBaoQuan',
    'validate_email_address',
    'validate_phone_number',
    'validate_so_ky_hieu',
    'validate_file_upload',
    'validate_password_strength',
    'sanitize_input_text',
    'generate_secure_token',
    'SecurityCheckException',
    'build_page_range',
    'paginate_queryset',
    'log_system_action',
    'get_client_ip',
]
