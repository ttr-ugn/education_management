"""
Education Management - Authentication & User Management Service Layer
Chịu trách nhiệm xử lý logic nghiệp vụ xác thực, phân quyền, bảo mật tài khoản và quản trị người dùng.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List
from django.utils import timezone
from django.db import transaction

from authentication.models import NguoiDung
from common.validators import (
    validate_email_address,
    validate_phone_number,
    validate_password_strength,
)
from common.security import sanitize_input_text, generate_secure_password
from common.constants import VaiTroNguoiDung, TrangThaiNguoiDung


class AuthenticationError(Exception):
    """Ngoại lệ riêng cho các lỗi xác thực và phân quyền"""
    pass


class UserService:
    """
    Dịch vụ quản lý thông tin người dùng và tài khoản cán bộ, chuyên viên, lãnh đạo.
    """

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

    @classmethod
    def authenticate_user(
        cls,
        ten_dang_nhap: str,
        mat_khau: str,
        ip_address: Optional[str] = None
    ) -> Tuple[Optional[NguoiDung], Optional[str]]:
        """
        Xác thực thông tin đăng nhập của người dùng kèm cơ chế tự động khóa tài khoản khi nhập sai nhiều lần.
        """
        if not ten_dang_nhap or not mat_khau:
            return None, "Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu."

        cleaned_username = ten_dang_nhap.strip()
        try:
            user = NguoiDung.objects.get(ten_dang_nhap=cleaned_username)
        except NguoiDung.DoesNotExist:
            return None, "Tài khoản hoặc mật khẩu không chính xác."

        # Kiểm tra trạng thái tài khoản
        if user.trang_thai == TrangThaiNguoiDung.CHO_DUYET:
            return None, "Tài khoản của bạn đang chờ quản trị viên xét duyệt. Vui lòng liên hệ Văn thư Sở."
        if user.trang_thai == TrangThaiNguoiDung.TU_CHOI:
            reason = user.ly_do_tu_choi or "Thông tin đăng ký không đáp ứng quy chuẩn."
            return None, f"Tài khoản đã bị từ chối phê duyệt. Lý do: {reason}"

        # Kiểm tra khóa tài khoản tạm thời
        now = timezone.now()
        if user.khoa_den and user.khoa_den > now:
            minutes_left = int((user.khoa_den - now).total_seconds() / 60) + 1
            return None, f"Tài khoản đang bị tạm khóa do nhập sai mật khẩu nhiều lần. Vui lòng thử lại sau {minutes_left} phút."

        # Kiểm tra mật khẩu
        if not user.check_password(mat_khau):
            user.so_lan_dang_nhap_sai += 1
            if user.so_lan_dang_nhap_sai >= cls.MAX_FAILED_ATTEMPTS:
                user.khoa_den = now + timedelta(minutes=cls.LOCKOUT_DURATION_MINUTES)
                user.save(update_fields=['so_lan_dang_nhap_sai', 'khoa_den'])
                return None, f"Đăng nhập sai quá {cls.MAX_FAILED_ATTEMPTS} lần! Tài khoản bị tạm khóa {cls.LOCKOUT_DURATION_MINUTES} phút để bảo đảm an toàn."
            
            user.save(update_fields=['so_lan_dang_nhap_sai'])
            con_lai = cls.MAX_FAILED_ATTEMPTS - user.so_lan_dang_nhap_sai
            return None, f"Mật khẩu không chính xác. Bạn còn {con_lai} lần thử trước khi tài khoản bị khóa."

        # Đăng nhập thành công -> Reset số lần sai và cập nhật thời gian đăng nhập
        user.so_lan_dang_nhap_sai = 0
        user.khoa_den = None
        user.lan_dang_nhap_cuoi = now
        user.save(update_fields=['so_lan_dang_nhap_sai', 'khoa_den', 'lan_dang_nhap_cuoi'])
        return user, None

    @classmethod
    def register_user(
        cls,
        ten_dang_nhap: str,
        mat_khau: str,
        ho_va_ten: str,
        email: str,
        vai_tro: str,
        phong_ban: str = "",
        chuc_vu: str = "",
        sdt: str = "",
        nguoi_tao: Optional[NguoiDung] = None,
        auto_activate: bool = False
    ) -> Tuple[Optional[NguoiDung], Optional[str]]:
        """
        Đăng ký hoặc tạo mới tài khoản người dùng có kiểm tra trùng lặp và độ mạnh mật khẩu.
        """
        ten_dang_nhap = ten_dang_nhap.strip()
        email = email.strip()

        if not ten_dang_nhap or not mat_khau or not ho_va_ten or not email:
            return None, "Vui lòng nhập đầy đủ các trường thông tin bắt buộc."

        if NguoiDung.objects.filter(ten_dang_nhap=ten_dang_nhap).exists():
            return None, f"Tên đăng nhập '{ten_dang_nhap}' đã tồn tại trong hệ thống."

        if not validate_email_address(email):
            return None, "Địa chỉ email không đúng định dạng."

        if NguoiDung.objects.filter(email=email).exists():
            return None, f"Địa chỉ email '{email}' đã được sử dụng cho một tài khoản khác."

        if sdt and not validate_phone_number(sdt):
            return None, "Số điện thoại không đúng chuẩn số di động Việt Nam."

        valid_pw, pw_errors = validate_password_strength(mat_khau)
        if not valid_pw:
            return None, " ".join(pw_errors)

        trang_thai = TrangThaiNguoiDung.HOAT_DONG if auto_activate else TrangThaiNguoiDung.CHO_DUYET

        user = NguoiDung(
            ten_dang_nhap=ten_dang_nhap,
            ho_va_ten=sanitize_input_text(ho_va_ten),
            email=email,
            vai_tro=vai_tro,
            phong_ban=sanitize_input_text(phong_ban),
            chuc_vu=sanitize_input_text(chuc_vu),
            sdt=sdt.strip() if sdt else None,
            trang_thai=trang_thai,
            nguoi_tao=nguoi_tao,
        )
        user.set_password(mat_khau)
        user.save()
        return user, None

    @classmethod
    def change_password(
        cls,
        user_id: int,
        old_password: str,
        new_password: str,
        confirm_password: str
    ) -> Tuple[bool, str]:
        """
        Đổi mật khẩu cho người dùng hiện hành với kiểm tra xác nhận và mật khẩu cũ.
        """
        try:
            user = NguoiDung.objects.get(pk=user_id)
        except NguoiDung.DoesNotExist:
            return False, "Không tìm thấy thông tin tài khoản."

        if not user.check_password(old_password):
            return False, "Mật khẩu hiện tại không chính xác."

        if new_password != confirm_password:
            return False, "Mật khẩu mới và xác nhận mật khẩu không khớp."

        if old_password == new_password:
            return False, "Mật khẩu mới không được trùng với mật khẩu cũ."

        is_valid, errors = validate_password_strength(new_password)
        if not is_valid:
            return False, " ".join(errors)

        user.set_password(new_password)
        user.bat_buoc_doi_mat_khau = 0
        user.save(update_fields=['mat_khau_hash', 'bat_buoc_doi_mat_khau'])
        return True, "Đổi mật khẩu thành công."

    @classmethod
    def reset_password_by_admin(
        cls,
        user_id: int,
        admin_user: NguoiDung,
        provided_password: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Quản trị viên thiết lập lại mật khẩu cho cán bộ.
        """
        if admin_user.vai_tro != VaiTroNguoiDung.VAN_THU:
            return False, "Chỉ Quản trị viên (Văn thư) mới có quyền cấp lại mật khẩu.", None

        try:
            target_user = NguoiDung.objects.get(pk=user_id)
        except NguoiDung.DoesNotExist:
            return False, "Người dùng không tồn tại.", None

        temp_password = provided_password or generate_secure_password(10)
        target_user.set_password(temp_password)
        target_user.bat_buoc_doi_mat_khau = 1
        target_user.so_lan_dang_nhap_sai = 0
        target_user.khoa_den = None
        target_user.save(update_fields=['mat_khau_hash', 'bat_buoc_doi_mat_khau', 'so_lan_dang_nhap_sai', 'khoa_den'])

        return True, f"Đã cấp lại mật khẩu cho tài khoản {target_user.ten_dang_nhap}.", temp_password

    @classmethod
    def approve_registration(
        cls,
        user_id: int,
        approver: NguoiDung
    ) -> Tuple[bool, str]:
        """
        Phê duyệt yêu cầu mở tài khoản cán bộ mới.
        """
        if approver.vai_tro != VaiTroNguoiDung.VAN_THU:
            return False, "Chỉ Quản trị viên/Văn thư mới có thẩm quyền phê duyệt tài khoản."

        try:
            target = NguoiDung.objects.get(pk=user_id)
            target.trang_thai = TrangThaiNguoiDung.HOAT_DONG
            target.ngay_duyet = timezone.now()
            target.save(update_fields=['trang_thai', 'ngay_duyet'])
            return True, f"Đã phê duyệt tài khoản {target.ten_dang_nhap} hoạt động."
        except NguoiDung.DoesNotExist:
            return False, "Người dùng không tồn tại."

    @classmethod
    def get_user_statistics(cls) -> Dict[str, Any]:
        """
        Tổng hợp thống kê số liệu người dùng toàn hệ thống.
        """
        total = NguoiDung.objects.count()
        active = NguoiDung.objects.filter(trang_thai=TrangThaiNguoiDung.HOAT_DONG).count()
        pending = NguoiDung.objects.filter(trang_thai=TrangThaiNguoiDung.CHO_DUYET).count()
        locked = NguoiDung.objects.filter(trang_thai=TrangThaiNguoiDung.BI_KHOA).count()

        by_role = {
            'VAN_THU': NguoiDung.objects.filter(vai_tro=VaiTroNguoiDung.VAN_THU).count(),
            'CHUYEN_VIEN': NguoiDung.objects.filter(vai_tro=VaiTroNguoiDung.CHUYEN_VIEN).count(),
            'LANH_DAO': NguoiDung.objects.filter(vai_tro=VaiTroNguoiDung.LANH_DAO).count(),
        }

        return {
            'total_users': total,
            'active_users': active,
            'pending_users': pending,
            'locked_users': locked,
            'by_role': by_role,
        }
