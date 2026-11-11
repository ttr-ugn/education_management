"""
Education Management - Task Management & Dispatch Service Layer (Cong Viec)
Chịu trách nhiệm phân công nhiệm vụ, giám sát tiến độ thực hiện, đánh giá KPI và cảnh báo quá hạn.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, Tuple, List
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count, Avg

from cong_viec.models import CongViec, NhatKyCongViec
from authentication.models import NguoiDung
from common.constants import (
    TrangThaiCongViec,
    MucDoUuTien,
    VaiTroNguoiDung,
)
from common.validators import validate_date_range
from common.security import sanitize_input_text


class TaskServiceException(Exception):
    """Ngoại lệ riêng cho quản lý công việc và nhiệm vụ"""
    pass


class TaskDispatchService:
    """
    Dịch vụ khởi tạo, giao việc và điều phối nhiệm vụ giữa các phòng ban.
    """

    @classmethod
    @transaction.atomic
    def create_task(
        cls,
        creator: NguoiDung,
        ten_cong_viec: str,
        assignee: NguoiDung,
        han_hoan_thanh: date,
        phong_ban: Optional[str] = None,
        noi_dung: Optional[str] = None,
        do_uu_tien: str = MucDoUuTien.TRUNG_BINH,
        so_ky_hieu_vb: Optional[str] = None,
        trich_yeu_vb: Optional[str] = None
    ) -> CongViec:
        """
        Giao một công việc / nhiệm vụ mới cho cán bộ thụ lý.
        """
        if not ten_cong_viec:
            raise TaskServiceException("Tên công việc không được để trống.")

        today = date.today()
        if han_hoan_thanh < today:
            raise TaskServiceException(f"Hạn hoàn thành ({han_hoan_thanh.strftime('%d/%m/%Y')}) không thể là ngày trong quá khứ.")

        target_department = phong_ban or assignee.phong_ban or 'Văn phòng Sở'

        task = CongViec.objects.create(
            ten_cong_viec=sanitize_input_text(ten_cong_viec),
            noi_dung=sanitize_input_text(noi_dung) if noi_dung else None,
            nguoi_giao=creator,
            nguoi_xu_ly=assignee,
            phong_ban=target_department,
            han_hoan_thanh=han_hoan_thanh,
            do_uu_tien=do_uu_tien,
            tien_do=0,
            trang_thai=TrangThaiCongViec.CHUA_THUC_HIEN,
            so_ky_hieu_vb=so_ky_hieu_vb.strip() if so_ky_hieu_vb else None,
            trich_yeu_vb=sanitize_input_text(trich_yeu_vb) if trich_yeu_vb else None
        )

        # Ghi nhật ký khởi tạo công việc
        NhatKyCongViec.objects.create(
            cong_viec=task,
            nguoi_cap_nhat=creator,
            tien_do_cu=0,
            tien_do_moi=0,
            noi_dung_ghi_chu=f"Giao nhiệm vụ mới cho đồng chí {assignee.ho_va_ten} (Hạn: {han_hoan_thanh.strftime('%d/%m/%Y')})"
        )

        return task

    @classmethod
    @transaction.atomic
    def reassign_task(
        cls,
        task_id: int,
        new_assignee: NguoiDung,
        actor: NguoiDung,
        ly_do: str = ''
    ) -> Tuple[bool, str]:
        """
        Điều chuyển người phụ trách thực hiện nhiệm vụ.
        """
        try:
            task = CongViec.objects.get(pk=task_id)
        except CongViec.DoesNotExist:
            return False, "Không tìm thấy công việc yêu cầu."

        old_assignee_name = task.nguoi_xu_ly.ho_va_ten if task.nguoi_xu_ly else "Chưa phân công"
        task.nguoi_xu_ly = new_assignee
        task.phong_ban = new_assignee.phong_ban or task.phong_ban
        task.save(update_fields=['nguoi_xu_ly', 'phong_ban', 'ngay_cap_nhat'])

        note = f"Chuyển giao người thực hiện từ [{old_assignee_name}] sang [{new_assignee.ho_va_ten}]. Lý do: {ly_do}"
        NhatKyCongViec.objects.create(
            cong_viec=task,
            nguoi_cap_nhat=actor,
            tien_do_cu=task.tien_do,
            tien_do_moi=task.tien_do,
            noi_dung_ghi_chu=note
        )
        return True, note


class TaskProgressService:
    """
    Dịch vụ cập nhật tiến độ, nộp báo cáo kết quả và xác nhận hoàn thành công việc.
    """

    @classmethod
    @transaction.atomic
    def update_progress(
        cls,
        task_id: int,
        updater: NguoiDung,
        new_progress: int,
        ghi_chu: str,
        tep_dinh_kem: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Cán bộ thụ lý cập nhật phần trăm hoàn thành và báo cáo diễn biến công việc.
        """
        try:
            task = CongViec.objects.get(pk=task_id)
        except CongViec.DoesNotExist:
            return False, "Không tìm thấy công việc."

        if not (0 <= new_progress <= 100):
            return False, "Tiến độ phải là một số nguyên từ 0% đến 100%."

        old_progress = task.tien_do
        task.tien_do = new_progress

        # Tự động chuyển trạng thái dựa trên tiến độ
        if new_progress == 100:
            task.trang_thai = TrangThaiCongViec.CHO_DANH_GIA
            if ghi_chu:
                task.ket_qua_bao_cao = sanitize_input_text(ghi_chu)
        elif new_progress > 0 and task.trang_thai in [TrangThaiCongViec.CHUA_THUC_HIEN, TrangThaiCongViec.QUA_HAN]:
            task.trang_thai = TrangThaiCongViec.DANG_THUC_HIEN

        if tep_dinh_kem:
            task.tep_dinh_kem_ket_qua = tep_dinh_kem

        task.save()

        # Ghi nhật ký
        NhatKyCongViec.objects.create(
            cong_viec=task,
            nguoi_cap_nhat=updater,
            tien_do_cu=old_progress,
            tien_do_moi=new_progress,
            noi_dung_ghi_chu=sanitize_input_text(ghi_chu) or f"Cập nhật tiến độ từ {old_progress}% lên {new_progress}%"
        )

        msg = f"Đã cập nhật tiến độ công việc lên {new_progress}%."
        if new_progress == 100:
            msg += " Nhiệm vụ đã hoàn tất và chuyển sang trạng thái 'Chờ đánh giá'."
        return True, msg

    @classmethod
    @transaction.atomic
    def evaluate_task(
        cls,
        task_id: int,
        evaluator: NguoiDung,
        is_approved: bool,
        nhan_xet: str
    ) -> Tuple[bool, str]:
        """
        Lãnh đạo nghiệm thu, đánh giá kết quả thực hiện nhiệm vụ.
        """
        try:
            task = CongViec.objects.get(pk=task_id)
        except CongViec.DoesNotExist:
            return False, "Không tìm thấy nhiệm vụ."

        sanitized_feedback = sanitize_input_text(nhan_xet)
        task.danh_gia_lanh_dao = sanitized_feedback

        if is_approved:
            task.trang_thai = TrangThaiCongViec.HOAN_THANH
            task.tien_do = 100
            action_desc = f"Lãnh đạo ({evaluator.ho_va_ten}) đánh giá: Đạt yêu cầu. Hoàn thành nhiệm vụ."
        else:
            task.trang_thai = TrangThaiCongViec.DANG_THUC_HIEN
            action_desc = f"Lãnh đạo ({evaluator.ho_va_ten}) yêu cầu làm lại: {sanitized_feedback}"

        task.save()

        NhatKyCongViec.objects.create(
            cong_viec=task,
            nguoi_cap_nhat=evaluator,
            tien_do_cu=task.tien_do,
            tien_do_moi=task.tien_do,
            noi_dung_ghi_chu=action_desc
        )

        return True, action_desc


class TaskAnalyticsService:
    """
    Dịch vụ tổng hợp thống kê KPI, giám sát hạn chót và phát hiện trễ hạn toàn Sở.
    """

    @classmethod
    def check_and_update_overdue_tasks(cls) -> int:
        """
        Rà soát toàn bộ các công việc quá hạn để tự động đánh dấu trạng thái QUA_HAN.
        """
        today = date.today()
        overdue_qs = CongViec.objects.filter(
            han_hoan_thanh__lt=today
        ).exclude(
            trang_thai__in=[TrangThaiCongViec.HOAN_THANH, TrangThaiCongViec.CHO_DANH_GIA, TrangThaiCongViec.QUA_HAN]
        )

        count = overdue_qs.update(trang_thai=TrangThaiCongViec.QUA_HAN)
        return count

    @classmethod
    def get_department_performance(cls, phong_ban: Optional[str] = None) -> Dict[str, Any]:
        """
        Tính toán chỉ số hoàn thành công việc và tỷ lệ đúng hạn của phòng ban.
        """
        qs = CongViec.objects.all()
        if phong_ban:
            qs = qs.filter(phong_ban=phong_ban)

        total = qs.count()
        if total == 0:
            return {
                'total_tasks': 0,
                'completed': 0,
                'in_progress': 0,
                'pending': 0,
                'overdue': 0,
                'completion_rate': 0.0,
                'on_time_rate': 0.0,
            }

        completed = qs.filter(trang_thai=TrangThaiCongViec.HOAN_THANH).count()
        in_progress = qs.filter(trang_thai=TrangThaiCongViec.DANG_THUC_HIEN).count()
        pending = qs.filter(trang_thai=TrangThaiCongViec.CHUA_THUC_HIEN).count()
        overdue = qs.filter(trang_thai=TrangThaiCongViec.QUA_HAN).count()

        completion_rate = round((completed / total) * 100, 1)
        on_time_rate = round(((total - overdue) / total) * 100, 1) if total > 0 else 100.0

        return {
            'total_tasks': total,
            'completed': completed,
            'in_progress': in_progress,
            'pending': pending,
            'overdue': overdue,
            'completion_rate': completion_rate,
            'on_time_rate': on_time_rate,
        }

    @classmethod
    def get_user_task_summary(cls, user_id: int) -> Dict[str, int]:
        """
        Lấy thống kê nhanh các đầu việc mà một cá nhân đang chịu trách nhiệm.
        """
        qs = CongViec.objects.filter(nguoi_xu_ly_id=user_id)
        return {
            'total': qs.count(),
            'pending': qs.filter(trang_thai=TrangThaiCongViec.CHUA_THUC_HIEN).count(),
            'in_progress': qs.filter(trang_thai=TrangThaiCongViec.DANG_THUC_HIEN).count(),
            'reviewing': qs.filter(trang_thai=TrangThaiCongViec.CHO_DANH_GIA).count(),
            'completed': qs.filter(trang_thai=TrangThaiCongViec.HOAN_THANH).count(),
            'overdue': qs.filter(trang_thai=TrangThaiCongViec.QUA_HAN).count(),
        }
