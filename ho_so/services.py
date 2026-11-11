"""
Education Management - Archival & Dossier Management Service Layer (Ho So Luu Tru)
Chịu trách nhiệm quản lý hồ sơ cơ quan, lập danh mục văn bản lưu trữ, tính hạn bảo quản và bàn giao lưu trữ.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, Tuple, List
from django.utils import timezone
from django.db import transaction
from django.db.models import Max, Count

from ho_so.models import HoSoLuuTru, VanBanBanHanh
from authentication.models import NguoiDung
from common.constants import (
    TrangThaiHoSo,
    ThoiHanBaoQuan,
    VaiTroNguoiDung,
)
from common.security import sanitize_input_text


class DossierCodeService:
    """
    Dịch vụ sinh mã hồ sơ lưu trữ chuẩn hóa theo quy định Cục Văn thư và Lưu trữ Nhà nước:
    Định dạng: HS-{NĂM}-{SỐ THỨ TỰ 3 CHỮ SỐ} (Ví dụ: HS-2026-001)
    """

    @classmethod
    def generate_next_code(cls, year: Optional[int] = None) -> str:
        target_year = year or datetime.now().year
        pattern_prefix = f"HS-{target_year}-"

        existing = HoSoLuuTru.objects.filter(ma_ho_so__startswith=pattern_prefix)
        count = existing.count()
        next_num = count + 1
        return f"{pattern_prefix}{next_num:03d}"


class DossierManagementService:
    """
    Quản trị hồ sơ lưu trữ: Tạo lập hồ sơ -> Thu thập tài liệu -> Nộp lưu chi cục -> Đóng băng hồ sơ.
    """

    @classmethod
    @transaction.atomic
    def create_dossier(
        cls,
        tieu_de: str,
        creator: NguoiDung,
        don_vi: Optional[str] = None,
        nam_tai_lieu: Optional[int] = None,
        thoi_han_bao_quan: str = ThoiHanBaoQuan.MUOI_NAM,
        mo_ta: Optional[str] = None
    ) -> HoSoLuuTru:
        """
        Tạo lập một hồ sơ công việc hoặc hồ sơ tài liệu lưu trữ mới.
        """
        target_year = nam_tai_lieu or datetime.now().year
        code = DossierCodeService.generate_next_code(target_year)
        department = don_vi or creator.phong_ban or 'Văn phòng Sở GD&ĐT'

        dossier = HoSoLuuTru.objects.create(
            ma_ho_so=code,
            tieu_de=sanitize_input_text(tieu_de),
            don_vi=department,
            nguoi_lap=creator,
            nam_tai_lieu=target_year,
            thoi_han_bao_quan=thoi_han_bao_quan,
            so_luong_van_ban=0,
            tinh_trang=TrangThaiHoSo.DANG_THU_THAP,
            mo_ta=sanitize_input_text(mo_ta) if mo_ta else None
        )
        return dossier

    @classmethod
    @transaction.atomic
    def add_document_to_dossier(
        cls,
        ho_so_id: int,
        van_ban_id: int
    ) -> Tuple[bool, str]:
        """
        Đưa một văn bản ban hành vào hồ sơ lưu trữ tương ứng và cập nhật số lượng văn bản.
        """
        try:
            dossier = HoSoLuuTru.objects.get(pk=ho_so_id)
        except HoSoLuuTru.DoesNotExist:
            return False, "Không tìm thấy hồ sơ lưu trữ."

        try:
            doc = VanBanBanHanh.objects.get(pk=van_ban_id)
        except VanBanBanHanh.DoesNotExist:
            return False, "Không tìm thấy văn bản ban hành."

        if doc.ho_so_id == dossier.ho_so_id:
            return False, "Văn bản này đã nằm trong hồ sơ hiện tại."

        doc.ho_so = dossier
        doc.nam_luu_tru = dossier.nam_tai_lieu
        doc.thoi_han_bao_quan = dossier.thoi_han_bao_quan
        doc.save(update_fields=['ho_so', 'nam_luu_tru', 'thoi_han_bao_quan'])

        # Cập nhật số lượng văn bản trong hồ sơ
        count = VanBanBanHanh.objects.filter(ho_so=dossier).count()
        dossier.so_luong_van_ban = count
        dossier.save(update_fields=['so_luong_van_ban', 'ngay_cap_nhat'])

        return True, f"Đã thêm văn bản '{doc.so_ky_hieu}' vào hồ sơ '{dossier.ma_ho_so}'."

    @classmethod
    @transaction.atomic
    def remove_document_from_dossier(
        cls,
        ho_so_id: int,
        van_ban_id: int
    ) -> Tuple[bool, str]:
        """
        Gỡ một văn bản khỏi hồ sơ lưu trữ.
        """
        try:
            dossier = HoSoLuuTru.objects.get(pk=ho_so_id)
            doc = VanBanBanHanh.objects.get(pk=van_ban_id, ho_so=dossier)
        except (HoSoLuuTru.DoesNotExist, VanBanBanHanh.DoesNotExist):
            return False, "Không tìm thấy hồ sơ hoặc văn bản trong hồ sơ."

        doc.ho_so = None
        doc.save(update_fields=['ho_so'])

        count = VanBanBanHanh.objects.filter(ho_so=dossier).count()
        dossier.so_luong_van_ban = count
        dossier.save(update_fields=['so_luong_van_ban', 'ngay_cap_nhat'])

        return True, "Đã tách văn bản ra khỏi hồ sơ thành công."

    @classmethod
    @transaction.atomic
    def submit_to_archive(
        cls,
        ho_so_id: int,
        user: NguoiDung
    ) -> Tuple[bool, str]:
        """
        Nộp hồ sơ vào kho lưu trữ cơ quan.
        """
        try:
            dossier = HoSoLuuTru.objects.get(pk=ho_so_id)
        except HoSoLuuTru.DoesNotExist:
            return False, "Không tìm thấy hồ sơ."

        if dossier.so_luong_van_ban == 0:
            return False, "Hồ sơ chưa có tài liệu/văn bản nào, không thể nộp lưu trữ."

        dossier.tinh_trang = TrangThaiHoSo.DA_NOP_LUU_TRU
        dossier.save(update_fields=['tinh_trang', 'ngay_cap_nhat'])
        return True, f"Hồ sơ {dossier.ma_ho_so} đã được nộp lưu trữ cơ quan thành công."

    @classmethod
    @transaction.atomic
    def freeze_dossier(
        cls,
        ho_so_id: int,
        clerk: NguoiDung
    ) -> Tuple[bool, str]:
        """
        Cán bộ văn thư lưu trữ hoàn tất đóng băng hồ sơ (ngăn chặn chỉnh sửa/thêm bớt văn bản).
        """
        if clerk.vai_tro != VaiTroNguoiDung.VAN_THU:
            return False, "Chỉ cán bộ Lưu trữ / Văn thư mới có quyền hoàn tất đóng băng hồ sơ."

        try:
            dossier = HoSoLuuTru.objects.get(pk=ho_so_id)
        except HoSoLuuTru.DoesNotExist:
            return False, "Không tìm thấy hồ sơ."

        dossier.tinh_trang = TrangThaiHoSo.HOAN_TAT
        dossier.save(update_fields=['tinh_trang', 'ngay_cap_nhat'])
        return True, f"Đã đóng băng hoàn tất hồ sơ {dossier.ma_ho_so} vào kho lưu trữ vĩnh viễn/có thời hạn."


class RetentionPolicyService:
    """
    Quy định thời hạn bảo quản tài liệu lưu trữ và cảnh báo tiêu hủy theo quy định pháp luật.
    """

    RETENTION_YEARS = {
        ThoiHanBaoQuan.MOT_NAM: 1,
        ThoiHanBaoQuan.NAM_NAM: 5,
        ThoiHanBaoQuan.MUOI_NAM: 10,
        ThoiHanBaoQuan.HAI_MUOI_NAM: 20,
        ThoiHanBaoQuan.BA_MUOI_NAM: 30,
        ThoiHanBaoQuan.VINH_VIEN: 9999,
    }

    @classmethod
    def calculate_expiration_year(cls, nam_tai_lieu: int, thoi_han: str) -> Optional[int]:
        """
        Tính năm hết hạn bảo quản của hồ sơ. Trả về None nếu bảo quản vĩnh viễn.
        """
        years = cls.RETENTION_YEARS.get(thoi_han)
        if not years or years >= 9999:
            return None
        return nam_tai_lieu + years

    @classmethod
    def get_archival_statistics(cls) -> Dict[str, Any]:
        """
        Thống kê tổng quan kho hồ sơ lưu trữ toàn cơ quan.
        """
        total_dossiers = HoSoLuuTru.objects.count()
        total_docs = VanBanBanHanh.objects.count()

        by_status = {
            'DANG_THU_THAP': HoSoLuuTru.objects.filter(tinh_trang=TrangThaiHoSo.DANG_THU_THAP).count(),
            'DA_NOP_LUU_TRU': HoSoLuuTru.objects.filter(tinh_trang=TrangThaiHoSo.DA_NOP_LUU_TRU).count(),
            'HOAN_TAT': HoSoLuuTru.objects.filter(tinh_trang=TrangThaiHoSo.HOAN_TAT).count(),
        }

        by_retention = {}
        for r, label in ThoiHanBaoQuan.CHOICES:
            by_retention[label] = HoSoLuuTru.objects.filter(thoi_han_bao_quan=r).count()

        return {
            'total_dossiers': total_dossiers,
            'total_documents': total_docs,
            'by_status': by_status,
            'by_retention': by_retention,
        }
