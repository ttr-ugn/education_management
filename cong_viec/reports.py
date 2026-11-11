"""
Education Management - Task Analytics & Performance Reporting (Cong Viec Reports)
Cung cấp các công cụ tổng hợp đánh giá chỉ số hoàn thành công việc của từng đơn vị và cá nhân.
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from django.db.models import Count, Avg, Q

from cong_viec.models import CongViec
from common.constants import TrangThaiCongViec, MucDoUuTien


class TaskPerformanceReporter:
    """
    Bộ tổng hợp báo cáo chỉ số hoàn thành nhiệm vụ và tiến độ giải quyết công vụ.
    """

    @classmethod
    def get_weekly_progress_overview(cls) -> Dict[str, Any]:
        """
        Tổng quan tình hình thực hiện công việc trong 7 ngày gần nhất.
        """
        today = date.today()
        week_ago = today - timedelta(days=7)

        recent_tasks = CongViec.objects.filter(ngay_tao__date__gte=week_ago)
        completed_recently = CongViec.objects.filter(
            trang_thai=TrangThaiCongViec.HOAN_THANH,
            ngay_cap_nhat__date__gte=week_ago
        )

        return {
            'new_tasks_count': recent_tasks.count(),
            'completed_recently_count': completed_recently.count(),
            'period': f"{week_ago.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')}"
        }

    @classmethod
    def get_priority_task_matrix(cls) -> Dict[str, Any]:
        """
        Ma trận phân bố công việc theo mức độ ưu tiên (Hỏa tốc, Cao, Trung bình, Thấp).
        """
        matrix = {}
        for prio, label in MucDoUuTien.CHOICES:
            tasks = CongViec.objects.filter(do_uu_tien=prio)
            matrix[prio] = {
                'label': label,
                'total': tasks.count(),
                'completed': tasks.filter(trang_thai=TrangThaiCongViec.HOAN_THANH).count(),
                'in_progress': tasks.filter(trang_thai=TrangThaiCongViec.DANG_THUC_HIEN).count(),
                'overdue': tasks.filter(trang_thai=TrangThaiCongViec.QUA_HAN).count(),
            }
        return matrix

    @classmethod
    def get_individual_officer_kpi(cls, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Bảng xếp hạng hiệu suất thực hiện nhiệm vụ của các chuyên viên.
        """
        qs = CongViec.objects.all()
        if department:
            qs = qs.filter(phong_ban=department)

        officers = (
            qs.exclude(nguoi_xu_ly__isnull=True)
            .values('nguoi_xu_ly__nguoi_dung_id', 'nguoi_xu_ly__ho_va_ten', 'phong_ban')
            .annotate(
                total_assigned=Count('cong_viec_id'),
                completed_count=Count('cong_viec_id', filter=Q(trang_thai=TrangThaiCongViec.HOAN_THANH)),
                overdue_count=Count('cong_viec_id', filter=Q(trang_thai=TrangThaiCongViec.QUA_HAN)),
                avg_progress=Avg('tien_do')
            )
            .order_by('-completed_count')
        )

        results = []
        for off in officers:
            total = off['total_assigned']
            completed = off['completed_count']
            rate = round((completed / total * 100), 1) if total > 0 else 0.0

            results.append({
                'officer_id': off['nguoi_xu_ly__nguoi_dung_id'],
                'full_name': off['nguoi_xu_ly__ho_va_ten'],
                'department': off['phong_ban'],
                'total_tasks': total,
                'completed': completed,
                'overdue': off['overdue_count'],
                'completion_rate': rate,
                'avg_progress': round(off['avg_progress'] or 0, 1)
            })
        return results
