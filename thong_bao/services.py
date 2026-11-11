"""
Education Management - Realtime Notification & Alert Service Layer (Thong Bao)
Chịu trách nhiệm phát sinh thông báo nghiệp vụ, broadcast diện rộng, và quản lý trạng thái đã đọc/chưa đọc.
"""

from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from thong_bao.models import ThongBao, ThongBaoDaDoc
from authentication.models import NguoiDung
from common.constants import LoaiThongBao, MucDoUuTien
from common.security import sanitize_input_text


class NotificationPushService:
    """
    Dịch vụ phát sinh và điều hướng thông báo đến người nhận đích hoặc toàn thể cơ quan.
    """

    @classmethod
    @transaction.atomic
    def push_personal_notification(
        cls,
        recipient: NguoiDung,
        title: str,
        content: str,
        loai: str = LoaiThongBao.HE_THONG,
        muc_do: str = MucDoUuTien.TRUNG_BINH,
        sender: Optional[NguoiDung] = None,
        lien_ket: Optional[str] = None
    ) -> ThongBao:
        """
        Gửi thông báo riêng đến một cán bộ cụ thể.
        """
        notification = ThongBao.objects.create(
            tieu_de=sanitize_input_text(title),
            noi_dung=sanitize_input_text(content),
            loai=loai,
            muc_do=muc_do,
            nguoi_gui=sender,
            nguoi_nhan=recipient,
            lien_ket=lien_ket
        )
        return notification

    @classmethod
    @transaction.atomic
    def broadcast_to_role(
        cls,
        target_role: str,
        title: str,
        content: str,
        sender: Optional[NguoiDung] = None,
        lien_ket: Optional[str] = None
    ) -> List[ThongBao]:
        """
        Phát sóng thông báo đến tất cả cán bộ theo một nhóm vai trò (Lãnh đạo, Văn thư, hoặc Chuyên viên).
        """
        users = NguoiDung.objects.filter(vai_tro=target_role, trang_thai='HOAT_DONG')
        notifications = []
        for user in users:
            notif = ThongBao.objects.create(
                tieu_de=sanitize_input_text(title),
                noi_dung=sanitize_input_text(content),
                loai=LoaiThongBao.HE_THONG,
                muc_do=MucDoUuTien.TRUNG_BINH,
                nguoi_gui=sender,
                nguoi_nhan=user,
                lien_ket=lien_ket
            )
            notifications.append(notif)
        return notifications

    @classmethod
    @transaction.atomic
    def broadcast_to_all(
        cls,
        title: str,
        content: str,
        sender: Optional[NguoiDung] = None,
        muc_do: str = MucDoUuTien.TRUNG_BINH,
        lien_ket: Optional[str] = None
    ) -> ThongBao:
        """
        Tạo thông báo toàn cơ quan (nguoi_nhan=None mang ý nghĩa thông báo chung cho mọi người).
        """
        return ThongBao.objects.create(
            tieu_de=sanitize_input_text(title),
            noi_dung=sanitize_input_text(content),
            loai=LoaiThongBao.HE_THONG,
            muc_do=muc_do,
            nguoi_gui=sender,
            nguoi_nhan=None,
            lien_ket=lien_ket
        )


class NotificationReadService:
    """
    Dịch vụ quản lý số đếm thông báo chưa đọc và đánh dấu đã xem (phục vụ polling 2 giây trên giao diện).
    """

    @classmethod
    def get_unread_count(cls, user: NguoiDung) -> int:
        """
        Tính số lượng thông báo mà người dùng chưa đọc (bao gồm thông báo cá nhân và thông báo chung toàn Sở).
        """
        # Các thông báo gửi riêng cho user hoặc gửi chung toàn cơ quan
        user_notifs = ThongBao.objects.filter(
            Q(nguoi_nhan=user) | Q(nguoi_nhan__isnull=True)
        )

        # Lấy danh sách ID thông báo đã được đánh dấu đọc
        read_ids = ThongBaoDaDoc.objects.filter(nguoi_dung=user).values_list('thong_bao_id', flat=True)

        unread_count = user_notifs.exclude(thong_bao_id__in=read_ids).count()
        return unread_count

    @classmethod
    def get_user_notifications(
        cls,
        user: NguoiDung,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Lấy danh sách thông báo mới nhất kèm trạng thái đã đọc của người dùng.
        """
        all_notifs = ThongBao.objects.filter(
            Q(nguoi_nhan=user) | Q(nguoi_nhan__isnull=True)
        ).order_by('-ngay_tao')[:limit]

        read_ids = set(
            ThongBaoDaDoc.objects.filter(
                nguoi_dung=user,
                thong_bao__in=all_notifs
            ).values_list('thong_bao_id', flat=True)
        )

        result = []
        for item in all_notifs:
            d = item.to_dict()
            d['da_doc'] = item.thong_bao_id in read_ids
            d['lien_ket'] = item.lien_ket or '#'
            d['nguoi_gui_ten'] = item.nguoi_gui.ho_va_ten if item.nguoi_gui else 'Hệ thống Quản lý Giáo dục'
            result.append(d)
        return result

    @classmethod
    def mark_as_read(cls, notification_id: int, user: NguoiDung) -> bool:
        """
        Đánh dấu một thông báo đã đọc.
        """
        try:
            notif = ThongBao.objects.get(pk=notification_id)
            ThongBaoDaDoc.objects.get_or_create(thong_bao=notif, nguoi_dung=user)
            return True
        except ThongBao.DoesNotExist:
            return False

    @classmethod
    @transaction.atomic
    def mark_all_as_read(cls, user: NguoiDung) -> int:
        """
        Đánh dấu toàn bộ thông báo của người dùng thành đã đọc.
        """
        unread_notifs = ThongBao.objects.filter(
            Q(nguoi_nhan=user) | Q(nguoi_nhan__isnull=True)
        ).exclude(
            thongbaodadoc__nguoi_dung=user
        )

        records_to_create = [
            ThongBaoDaDoc(thong_bao=n, nguoi_dung=user)
            for n in unread_notifs
        ]
        created = ThongBaoDaDoc.objects.bulk_create(records_to_create, ignore_conflicts=True)
        return len(created)
