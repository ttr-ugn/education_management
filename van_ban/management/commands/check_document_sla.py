"""
Management Command: check_document_sla
Kiểm tra thời gian xử lý văn bản đi và đến so với quy chuẩn SLA (hạn xử lý hành chính).
Tự động gửi thông báo nhắc việc nếu văn bản quá hạn xử lý.
"""

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from van_ban.models import VanBanDi, VanBanDen
from thong_bao.services import NotificationPushService
from common.constants import TrangThaiVanBanDi, TrangThaiVanBanDen, LoaiThongBao, MucDoUuTien


class Command(BaseCommand):
    help = 'Kiểm tra và nhắc nhở các văn bản sắp đến hạn hoặc quá hạn xử lý theo quy định SLA.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Đang quét các văn bản cần xử lý theo quy định SLA..."))
        now = timezone.now()
        warning_delta = timedelta(days=2)

        # 1. Quét văn bản đi đang chờ phê duyệt quá 48 giờ
        stale_outbounds = VanBanDi.objects.filter(
            trang_thai__in=[TrangThaiVanBanDi.CHO_VAN_THU_KIEM_TRA, TrangThaiVanBanDi.CHO_LANH_DAO_DUYET],
            ngay_tao__lt=now - warning_delta
        )

        stale_count = 0
        for doc in stale_outbounds:
            stale_count += 1
            if doc.lanh_dao_ky and doc.trang_thai == TrangThaiVanBanDi.CHO_LANH_DAO_DUYET:
                NotificationPushService.push_personal_notification(
                    recipient=doc.lanh_dao_ky,
                    title=f"[Nhắc việc SLA] Văn bản chờ duyệt ký: {doc.trich_yeu[:60]}...",
                    content=f"Văn bản dự thảo số ID {doc.van_ban_id} do {doc.nguoi_soan.ho_va_ten if doc.nguoi_soan else 'chuyên viên'} trình đã quá 48 giờ chưa ký duyệt.",
                    loai=LoaiThongBao.CANH_BAO,
                    muc_do=MucDoUuTien.CAO,
                    lien_ket="/van-ban-di/danh-sach.html"
                )

        # 2. Quét văn bản đến có hạn xử lý gần kề
        today = datetime.now().date()
        inbound_urgent = VanBanDen.objects.filter(
            trang_thai=TrangThaiVanBanDen.DANG_XU_LY,
            han_xu_ly__lte=today + timedelta(days=1)
        )

        inbound_count = 0
        for doc in inbound_urgent:
            inbound_count += 1
            if doc.nguoi_chu_tri:
                NotificationPushService.push_personal_notification(
                    recipient=doc.nguoi_chu_tri,
                    title=f"[Hỏa tốc] Văn bản đến sắp hết hạn xử lý ({doc.so_ky_hieu})",
                    content=f"Văn bản đến số ký hiệu {doc.so_ky_hieu} từ {doc.co_quan_ban_hanh} có hạn xử lý là {doc.han_xu_ly}. Đồng chí vui lòng khẩn trương hoàn thiện.",
                    loai=LoaiThongBao.CANH_BAO,
                    muc_do=MucDoUuTien.KHAN_CAP
                )

        self.stdout.write(self.style.SUCCESS(
            f"Hoàn tất kiểm tra SLA: Đã phát hiện {stale_count} văn bản đi cần nhắc nhở và {inbound_count} văn bản đến sắp hết hạn."
        ))
