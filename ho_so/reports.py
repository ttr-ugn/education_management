"""
Education Management - Archival Compliance & Dossier Reports (Ho So Reports)
Cung cấp công cụ lập biểu thống kê hồ sơ nộp lưu và biên bản kiểm kê tài liệu lưu trữ cơ quan.
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
from django.db.models import Count, Sum

from ho_so.models import HoSoLuuTru, VanBanBanHanh
from common.constants import TrangThaiHoSo, ThoiHanBaoQuan


class ArchivalReportGenerator:
    """
    Bộ tổng hợp báo cáo kiểm kê tài liệu lưu trữ cơ quan theo biểu mẫu Cục Văn thư và Lưu trữ Nhà nước.
    """

    @classmethod
    def get_annual_inventory_summary(cls, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Lập bảng tổng hợp kiểm kê hồ sơ tài liệu theo năm hình thành tài liệu.
        """
        target_year = year or datetime.now().year
        dossiers = HoSoLuuTru.objects.filter(nam_tai_lieu=target_year)

        total_dossiers = dossiers.count()
        total_documents = dossiers.aggregate(Sum('so_luong_van_ban'))['so_luong_van_ban__sum'] or 0

        submitted_count = dossiers.filter(
            tinh_trang__in=[TrangThaiHoSo.DA_NOP_LUU_TRU, TrangThaiHoSo.HOAN_TAT]
        ).count()

        submission_rate = round((submitted_count / total_dossiers * 100), 1) if total_dossiers > 0 else 0.0

        return {
            'year': target_year,
            'total_dossiers': total_dossiers,
            'total_documents': total_documents,
            'submitted_count': submitted_count,
            'submission_rate': submission_rate
        }

    @classmethod
    def get_dossier_status_breakdown(cls) -> List[Dict[str, Any]]:
        """
        Báo cáo phân bổ tình trạng hồ sơ toàn cơ quan.
        """
        breakdown = (
            HoSoLuuTru.objects.values('tinh_trang')
            .annotate(count=Count('ho_so_id'))
            .order_by('-count')
        )

        labels = {
            TrangThaiHoSo.DANG_THU_THAP: 'Đang thu thập',
            TrangThaiHoSo.DA_NOP_LUU_TRU: 'Đã nộp lưu trữ',
            TrangThaiHoSo.HOAN_TAT: 'Đã hoàn tất đóng băng',
            TrangThaiHoSo.HUY_LUC: 'Đã tiêu hủy / Hết hạn',
        }

        return [
            {
                'status_code': item['tinh_trang'],
                'status_name': labels.get(item['tinh_trang'], item['tinh_trang']),
                'total_dossiers': item['count']
            }
            for item in breakdown
        ]

    @classmethod
    def get_handover_readiness_list(cls) -> List[Dict[str, Any]]:
        """
        Danh sách các hồ sơ đã đủ điều kiện nộp vào kho lưu trữ lịch sử hoặc lưu trữ cơ quan.
        """
        ready_dossiers = HoSoLuuTru.objects.filter(
            so_luong_van_ban__gt=0,
            tinh_trang=TrangThaiHoSo.DANG_THU_THAP
        )

        return [
            {
                'ho_so_id': hs.ho_so_id,
                'ma_ho_so': hs.ma_ho_so,
                'tieu_de': hs.tieu_de,
                'don_vi': hs.don_vi,
                'so_luong_van_ban': hs.so_luong_van_ban,
                'thoi_han_bao_quan': hs.thoi_han_bao_quan
            }
            for hs in ready_dossiers
        ]
