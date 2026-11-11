"""
Education Management - Document Analytics & Reporting Module (Van Ban Reports)
Cung cấp công cụ tổng hợp số liệu, phân tích thể thức và lập báo cáo định kỳ công tác văn thư lưu trữ.
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
from django.db.models import Count, Q

from van_ban.models import VanBanDi, VanBanDen
from common.constants import TrangThaiVanBanDi, TrangThaiVanBanDen


class DocumentReportGenerator:
    """
    Bộ sinh báo cáo định kỳ tháng, quý, năm về công tác văn bản điều hành theo quy chuẩn Bộ GD&ĐT.
    """

    @classmethod
    def get_document_type_distribution(cls, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Thống kê phân bổ các loại hình văn bản đi được ban hành trong năm.
        """
        target_year = year or datetime.now().year
        qs = VanBanDi.objects.filter(ngay_tao__year=target_year)

        types_count = (
            qs.values('loai_van_ban')
            .annotate(total=Count('van_ban_id'))
            .order_by('-total')
        )

        total_all = qs.count()
        results = []
        for item in types_count:
            name = item['loai_van_ban'] or 'Khác'
            count = item['total']
            percentage = round((count / total_all * 100), 1) if total_all > 0 else 0.0
            results.append({
                'loai_van_ban': name,
                'so_luong': count,
                'ty_le': percentage
            })
        return results

    @classmethod
    def get_sla_compliance_report(cls, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Báo cáo mức độ tuân thủ thời hạn xử lý văn bản hành chính (SLA Compliance).
        """
        target_year = year or datetime.now().year
        total_inbound = VanBanDen.objects.filter(ngay_den__year=target_year).count()
        overdue_inbound = VanBanDen.objects.filter(
            ngay_den__year=target_year,
            han_xu_ly__lt=date.today()
        ).exclude(trang_thai=TrangThaiVanBanDen.HOAN_THANH).count()

        on_time_inbound = total_inbound - overdue_inbound
        compliance_rate = round((on_time_inbound / total_inbound * 100), 1) if total_inbound > 0 else 100.0

        return {
            'year': target_year,
            'total_inbound': total_inbound,
            'on_time': on_time_inbound,
            'overdue': overdue_inbound,
            'compliance_rate': compliance_rate
        }

    @classmethod
    def get_department_outbound_ranking(cls, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Xếp hạng số lượng văn bản đi do từng phòng ban tham mưu ban hành.
        """
        target_year = year or datetime.now().year
        qs = VanBanDi.objects.filter(
            ngay_tao__year=target_year,
            trang_thai=TrangThaiVanBanDi.DA_BAN_HANH
        )

        ranking = (
            qs.values('don_vi_soan_thao')
            .annotate(total=Count('van_ban_id'))
            .order_by('-total')
        )

        return [
            {
                'don_vi': item['don_vi_soan_thao'] or 'Chưa phân loại',
                'so_luong_ban_hanh': item['total']
            }
            for item in ranking
        ]
