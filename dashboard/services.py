"""
Education Management - Dashboard & Executive Analytics Service Layer (Dashboard)
Chịu trách nhiệm tổng hợp chỉ số KPI, thống kê biểu đồ động, phân tích hiệu suất điều hành của toàn Sở.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from django.db.models import Count, Q
from django.utils import timezone

from van_ban.models import VanBanDi, VanBanDen
from cong_viec.models import CongViec
from ho_so.models import HoSoLuuTru, VanBanBanHanh
from authentication.models import NguoiDung
from dashboard.models import NhatKyHeThong
from common.constants import (
    TrangThaiVanBanDi,
    TrangThaiVanBanDen,
    TrangThaiCongViec,
    TrangThaiHoSo,
)


class DashboardMetricsService:
    """
    Dịch vụ tổng hợp số liệu thời gian thực hiển thị trên Bảng điều khiển lãnh đạo và chuyên viên.
    """

    @classmethod
    def get_summary_cards(cls) -> Dict[str, Any]:
        """
        Lấy các thẻ số liệu thống kê chủ chốt (Key KPI Counters).
        """
        # Thống kê Văn bản đi
        vb_di_total = VanBanDi.objects.count()
        vb_di_issued = VanBanDi.objects.filter(trang_thai=TrangThaiVanBanDi.DA_BAN_HANH).count()
        vb_di_pending = VanBanDi.objects.filter(
            trang_thai__in=[TrangThaiVanBanDi.CHO_VAN_THU_KIEM_TRA, TrangThaiVanBanDi.CHO_LANH_DAO_DUYET, TrangThaiVanBanDi.CHO_CAP_SO]
        ).count()

        # Thống kê Văn bản đến
        vb_den_total = VanBanDen.objects.count()
        vb_den_processing = VanBanDen.objects.filter(trang_thai=TrangThaiVanBanDen.DANG_XU_LY).count()

        # Thống kê Công việc
        cv_total = CongViec.objects.count()
        cv_completed = CongViec.objects.filter(trang_thai=TrangThaiCongViec.HOAN_THANH).count()
        cv_overdue = CongViec.objects.filter(trang_thai=TrangThaiCongViec.QUA_HAN).count()
        cv_in_progress = CongViec.objects.filter(trang_thai=TrangThaiCongViec.DANG_THUC_HIEN).count()

        kpi_rate = round((cv_completed / cv_total * 100), 1) if cv_total > 0 else 100.0

        # Thống kê Hồ sơ lưu trữ
        hs_total = HoSoLuuTru.objects.count()
        docs_archived = VanBanBanHanh.objects.count()

        return {
            'van_ban_di': {
                'total': vb_di_total,
                'issued': vb_di_issued,
                'pending': vb_di_pending,
            },
            'van_ban_den': {
                'total': vb_den_total,
                'processing': vb_den_processing,
            },
            'cong_viec': {
                'total': cv_total,
                'completed': cv_completed,
                'in_progress': cv_in_progress,
                'overdue': cv_overdue,
                'kpi_rate': kpi_rate,
            },
            'ho_so': {
                'total_dossiers': hs_total,
                'archived_docs': docs_archived,
            }
        }

    @classmethod
    def get_monthly_chart_data(cls, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Tổng hợp dữ liệu luân chuyển văn bản theo từng tháng trong năm phục vụ vẽ biểu đồ Chart.js.
        """
        target_year = year or datetime.now().year
        months = list(range(1, 13))

        di_data = []
        den_data = []

        for m in months:
            count_di = VanBanDi.objects.filter(
                ngay_tao__year=target_year,
                ngay_tao__month=m
            ).count()
            count_den = VanBanDen.objects.filter(
                ngay_den__year=target_year,
                ngay_den__month=m
            ).count()
            di_data.append(count_di)
            den_data.append(count_den)

        return {
            'year': target_year,
            'labels': [f"Thg {m}" for m in months],
            'van_ban_di': di_data,
            'van_ban_den': den_data,
        }

    @classmethod
    def get_department_workload(cls) -> List[Dict[str, Any]]:
        """
        Phân tích khối lượng công việc và tỷ lệ hoàn thành theo từng phòng ban chức năng.
        """
        departments = [
            'Phòng Giáo dục Trung học',
            'Phòng Giáo dục Tiểu học',
            'Phòng Kế hoạch - Tài chính',
            'Phòng Tổ chức Cán bộ',
            'Phòng Khảo thí & KĐCLGD',
            'Văn phòng Sở',
        ]

        result = []
        for dept in departments:
            dept_tasks = CongViec.objects.filter(phong_ban=dept)
            total = dept_tasks.count()
            completed = dept_tasks.filter(trang_thai=TrangThaiCongViec.HOAN_THANH).count()
            overdue = dept_tasks.filter(trang_thai=TrangThaiCongViec.QUA_HAN).count()
            pct = round((completed / total * 100), 1) if total > 0 else 0.0

            result.append({
                'phong_ban': dept,
                'total_tasks': total,
                'completed': completed,
                'overdue': overdue,
                'completion_pct': pct,
            })

        return result

    @classmethod
    def get_recent_activities(cls, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Lấy các hoạt động tác nghiệp gần nhất ghi nhận từ nhật ký hệ thống.
        """
        logs = NhatKyHeThong.objects.all().order_by('-thoi_gian')[:limit]
        return [
            {
                'id': log.id,
                'hanh_dong': log.hanh_dong,
                'chi_tiet': log.chi_tiet or '',
                'thoi_gian': log.thoi_gian.strftime('%d/%m/%Y %H:%M:%S') if log.thoi_gian else '',
            }
            for log in logs
        ]
