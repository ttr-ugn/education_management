"""
Management Command: archive_expired_records
Rà soát danh mục hồ sơ lưu trữ cơ quan, đối chiếu thời hạn bảo quản
và lập báo cáo các hồ sơ hết hạn lưu trữ cần đánh giá tiêu hủy hoặc chuyển lưu trữ lịch sử.
"""

from datetime import datetime
from django.core.management.base import BaseCommand
from ho_so.models import HoSoLuuTru
from ho_so.services import RetentionPolicyService
from common.constants import TrangThaiHoSo


class Command(BaseCommand):
    help = 'Rà soát danh mục hồ sơ lưu trữ đã hết hạn bảo quản theo quy định lưu trữ'

    def handle(self, *args, **options):
        current_year = datetime.now().year
        self.stdout.write(self.style.NOTICE(f"Đang kiểm tra thời hạn lưu trữ hồ sơ cho năm tính toán {current_year}..."))

        active_dossiers = HoSoLuuTru.objects.exclude(tinh_trang=TrangThaiHoSo.HUY_LUC)
        expired_count = 0

        for dossier in active_dossiers:
            exp_year = RetentionPolicyService.calculate_expiration_year(
                dossier.nam_tai_lieu,
                dossier.thoi_han_bao_quan
            )
            if exp_year and exp_year <= current_year:
                expired_count += 1
                self.stdout.write(
                    f" - [HẾT HẠN LƯU TRỮ] Mã: {dossier.ma_ho_so} | Tiêu đề: {dossier.tieu_de[:50]} "
                    f"| Năm tài liệu: {dossier.nam_tai_lieu} | Thời hạn: {dossier.thoi_han_bao_quan} (Hết hạn năm: {exp_year})"
                )

        self.stdout.write(self.style.SUCCESS(
            f"Hoàn thành rà soát: Tổng cộng có {expired_count} hồ sơ đã hết hạn bảo quản cần lập hội đồng thẩm tra."
        ))
