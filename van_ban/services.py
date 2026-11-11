"""
Education Management - Document Processing Service Layer (Van Ban Di & Van Ban Den)
Chịu trách nhiệm quy trình luân chuyển văn bản, cấp số văn bản, ký số điện tử và lưu trữ lịch sử xử lý.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, Tuple, List
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Max

from van_ban.models import VanBanDi, LichSuXuLyVanBan, VanBanDen
from authentication.models import NguoiDung
from common.constants import (
    TrangThaiVanBanDi,
    TrangThaiVanBanDen,
    VaiTroNguoiDung,
    SystemErrorCodes,
)
from common.validators import validate_so_ky_hieu
from common.pdf_signer import PDFSignerService
from common.security import sanitize_input_text


class DocumentServiceException(Exception):
    """Ngoại lệ riêng cho các thao tác văn bản"""
    def __init__(self, message: str, code: int = SystemErrorCodes.INVALID_PARAMETERS):
        super().__init__(message)
        self.message = message
        self.code = code


class DocumentNumberingService:
    """
    Dịch vụ sinh số ký hiệu văn bản tự động tuân thủ Nghị định 30/2020/NĐ-CP.
    """

    LOAI_VAN_BAN_ABBR = {
        'Quyết định': 'QĐ',
        'Kế hoạch': 'KH',
        'Thông báo': 'TB',
        'Công văn': 'CV',
        'Tờ trình': 'TTr',
        'Báo cáo': 'BC',
        'Hướng dẫn': 'HD',
        'Biên bản': 'BB',
        'Chỉ thị': 'CT',
    }

    ORG_SUFFIX = 'SGDĐT'

    @classmethod
    def get_document_abbreviation(cls, loai_van_ban: str) -> str:
        return cls.LOAI_VAN_BAN_ABBR.get(loai_van_ban, 'CV')

    @classmethod
    def generate_next_outbound_number(cls, loai_van_ban: str, year: Optional[int] = None) -> str:
        """
        Sinh số ký hiệu văn bản kế tiếp theo năm và loại văn bản.
        Ví dụ: 25/QĐ-SGDĐT hoặc 104/KH-SGDĐT
        """
        target_year = year or datetime.now().year
        abbr = cls.get_document_abbreviation(loai_van_ban)

        # Đếm số văn bản cùng loại đã được ban hành hoặc cấp số trong năm
        existing_docs = VanBanDi.objects.filter(
            loai_van_ban=loai_van_ban,
            ngay_tao__year=target_year
        ).exclude(so_ky_hieu__isnull=True).exclude(so_ky_hieu='')

        current_count = existing_docs.count()
        next_seq = current_count + 1

        return f"{next_seq}/{abbr}-{cls.ORG_SUFFIX}"

    @classmethod
    def is_number_available(cls, so_ky_hieu: str, exclude_id: Optional[int] = None) -> bool:
        """
        Kiểm tra số ký hiệu có bị trùng trong hệ thống văn bản đi chưa.
        """
        query = VanBanDi.objects.filter(so_ky_hieu=so_ky_hieu.strip())
        if exclude_id:
            query = query.exclude(pk=exclude_id)
        return not query.exists()


class OutboundDocumentService:
    """
    Quản lý vòng đời Văn bản đi: Dự thảo -> Văn thư kiểm tra -> Lãnh đạo duyệt ký -> Ban hành.
    """

    @classmethod
    @transaction.atomic
    def create_draft(
        cls,
        author: NguoiDung,
        trich_yeu: str,
        loai_van_ban: str,
        do_khan: str = 'Bình thường',
        noi_nhan: str = '',
        noi_dung_tom_tat: str = '',
        don_vi_soan_thao: Optional[str] = None,
        lanh_dao_ky: Optional[NguoiDung] = None,
        file_goc_path: Optional[str] = None,
        file_goc_ten: Optional[str] = None
    ) -> VanBanDi:
        """
        Chuyên viên tạo mới dự thảo văn bản đi.
        """
        doc = VanBanDi.objects.create(
            trich_yeu=sanitize_input_text(trich_yeu),
            loai_van_ban=loai_van_ban,
            do_khan=do_khan,
            don_vi_soan_thao=don_vi_soan_thao or author.phong_ban or 'Phòng Giáo dục Trung học',
            noi_nhan=sanitize_input_text(noi_nhan),
            noi_dung_tom_tat=sanitize_input_text(noi_dung_tom_tat),
            nguoi_soan=author,
            lanh_dao_ky=lanh_dao_ky,
            trang_thai=TrangThaiVanBanDi.DU_THAO,
            file_goc_path=file_goc_path,
            file_goc_ten=file_goc_ten
        )

        # Ghi lịch sử tạo dự thảo
        LichSuXuLyVanBan.objects.create(
            van_ban=doc,
            nguoi_thuc_hien=author,
            hanh_dong="Tạo mới dự thảo văn bản",
            trang_thai_truoc=None,
            trang_thai_sau=TrangThaiVanBanDi.DU_THAO,
            noi_dung="Khởi tạo văn bản đi mới trên hệ thống"
        )
        return doc

    @classmethod
    @transaction.atomic
    def submit_to_clerk(
        cls,
        van_ban_id: int,
        submitter: NguoiDung,
        ghi_chu: str = ''
    ) -> Tuple[bool, str]:
        """
        Chuyên viên trình dự thảo sang Văn thư để kiểm tra thể thức văn bản.
        """
        try:
            doc = VanBanDi.objects.get(pk=van_ban_id)
        except VanBanDi.DoesNotExist:
            return False, "Không tìm thấy văn bản yêu cầu."

        if doc.trang_thai not in [TrangThaiVanBanDi.DU_THAO, TrangThaiVanBanDi.VAN_THU_TRA_LAI]:
            return False, f"Văn bản đang ở trạng thái '{doc.trang_thai}', không thể trình kiểm tra."

        prev_state = doc.trang_thai
        doc.trang_thai = TrangThaiVanBanDi.CHO_VAN_THU_KIEM_TRA
        doc.ngay_trinh_van_thu = timezone.now()
        doc.save(update_fields=['trang_thai', 'ngay_trinh_van_thu'])

        LichSuXuLyVanBan.objects.create(
            van_ban=doc,
            nguoi_thuc_hien=submitter,
            hanh_dong="Trình văn thư kiểm tra thể thức",
            trang_thai_truoc=prev_state,
            trang_thai_sau=doc.trang_thai,
            noi_dung=sanitize_input_text(ghi_chu) or "Chuyển văn thư xem xét thể thức"
        )
        return True, "Trình kiểm tra thể thức văn bản thành công."

    @classmethod
    @transaction.atomic
    def clerk_review(
        cls,
        van_ban_id: int,
        clerk: NguoiDung,
        approved: bool,
        y_kien: str = '',
        lanh_dao_ky: Optional[NguoiDung] = None
    ) -> Tuple[bool, str]:
        """
        Văn thư duyệt thể thức hoặc trả lại yêu cầu chỉnh sửa.
        """
        if clerk.vai_tro != VaiTroNguoiDung.VAN_THU:
            return False, "Chỉ cán bộ Văn thư mới có thẩm quyền kiểm tra thể thức."

        try:
            doc = VanBanDi.objects.get(pk=van_ban_id)
        except VanBanDi.DoesNotExist:
            return False, "Không tìm thấy văn bản."

        prev_state = doc.trang_thai
        if approved:
            doc.trang_thai = TrangThaiVanBanDi.CHO_LANH_DAO_DUYET
            doc.ngay_trinh_lanh_dao = timezone.now()
            doc.y_kien_van_thu = sanitize_input_text(y_kien)
            if lanh_dao_ky:
                doc.lanh_dao_ky = lanh_dao_ky
            action_text = "Văn thư thông qua thể thức - Trình lãnh đạo ký"
        else:
            doc.trang_thai = TrangThaiVanBanDi.VAN_THU_TRA_LAI
            doc.y_kien_van_thu = sanitize_input_text(y_kien)
            action_text = f"Văn thư trả lại hiệu chỉnh: {y_kien}"

        doc.save()

        LichSuXuLyVanBan.objects.create(
            van_ban=doc,
            nguoi_thuc_hien=clerk,
            hanh_dong=action_text,
            trang_thai_truoc=prev_state,
            trang_thai_sau=doc.trang_thai,
            noi_dung=sanitize_input_text(y_kien)
        )
        return True, "Cập nhật kết quả kiểm tra thể thức thành công."

    @classmethod
    @transaction.atomic
    def leader_sign_and_approve(
        cls,
        van_ban_id: int,
        leader: NguoiDung,
        approved: bool,
        y_kien: str = '',
        x: float = 400.0,
        y: float = 650.0
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Lãnh đạo ký số phê duyệt hoặc trả lại văn bản.
        """
        if leader.vai_tro != VaiTroNguoiDung.LANH_DAO:
            return False, "Chỉ Lãnh đạo mới có thẩm quyền ký duyệt văn bản.", None

        try:
            doc = VanBanDi.objects.get(pk=van_ban_id)
        except VanBanDi.DoesNotExist:
            return False, "Không tìm thấy văn bản.", None

        prev_state = doc.trang_thai
        sig_data = None

        if approved:
            doc.trang_thai = TrangThaiVanBanDi.CHO_CAP_SO
            doc.lanh_dao_ky_ten = leader.ho_va_ten
            doc.thoi_gian_ky = timezone.now()
            doc.ky_so_x = x
            doc.ky_so_y = y
            doc.y_kien_lanh_dao = sanitize_input_text(y_kien)

            # Thực hiện ký số bằng engine mật mã
            sig_result = PDFSignerService.apply_digital_signature(
                document_id=doc.van_ban_id,
                signer_name=leader.ho_va_ten,
                signer_title=leader.chuc_vu or "Phó Giám đốc Sở",
                x=x,
                y=y,
                file_path=doc.file_goc_path
            )
            doc.file_da_ky_ten = f"van_ban_da_ky_{doc.van_ban_id}.pdf"
            doc.file_da_ky_path = f"/uploads/signed/van_ban_da_ky_{doc.van_ban_id}.pdf"
            action_text = f"Lãnh đạo ({leader.ho_va_ten}) ký số phê duyệt"
            sig_data = sig_result
        else:
            doc.trang_thai = TrangThaiVanBanDi.LANH_DAO_TRA_LAI
            doc.y_kien_lanh_dao = sanitize_input_text(y_kien)
            action_text = f"Lãnh đạo trả lại văn bản: {y_kien}"

        doc.save()

        LichSuXuLyVanBan.objects.create(
            van_ban=doc,
            nguoi_thuc_hien=leader,
            hanh_dong=action_text,
            trang_thai_truoc=prev_state,
            trang_thai_sau=doc.trang_thai,
            noi_dung=sanitize_input_text(y_kien)
        )
        return True, "Xử lý phê duyệt văn bản thành công.", sig_data

    @classmethod
    @transaction.atomic
    def issue_document(
        cls,
        van_ban_id: int,
        clerk: NguoiDung,
        so_ky_hieu: Optional[str] = None,
        ngay_ban_hanh: Optional[date] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Văn thư cấp số chính thức và phát hành văn bản đi đến các cơ quan, đơn vị nhận.
        """
        if clerk.vai_tro != VaiTroNguoiDung.VAN_THU:
            return False, "Chỉ Văn thư mới có quyền cấp số và ban hành văn bản.", None

        try:
            doc = VanBanDi.objects.get(pk=van_ban_id)
        except VanBanDi.DoesNotExist:
            return False, "Không tìm thấy văn bản.", None

        prev_state = doc.trang_thai
        final_so_ky_hieu = so_ky_hieu or DocumentNumberingService.generate_next_outbound_number(doc.loai_van_ban)

        # Kiểm tra tính hợp lệ số ký hiệu
        is_valid, err = validate_so_ky_hieu(final_so_ky_hieu)
        if not is_valid:
            return False, err, None

        if not DocumentNumberingService.is_number_available(final_so_ky_hieu, exclude_id=doc.van_ban_id):
            return False, f"Số ký hiệu '{final_so_ky_hieu}' đã được sử dụng cho văn bản khác.", None

        doc.so_ky_hieu = final_so_ky_hieu
        doc.ngay_ban_hanh = ngay_ban_hanh or timezone.now()
        doc.trang_thai = TrangThaiVanBanDi.DA_BAN_HANH
        doc.save()

        LichSuXuLyVanBan.objects.create(
            van_ban=doc,
            nguoi_thuc_hien=clerk,
            hanh_dong=f"Cấp số {final_so_ky_hieu} & Ban hành chính thức",
            trang_thai_truoc=prev_state,
            trang_thai_sau=doc.trang_thai,
            noi_dung=f"Ban hành văn bản đến nơi nhận: {doc.noi_nhan}"
        )
        return True, f"Văn bản đã ban hành thành công với số {final_so_ky_hieu}", final_so_ky_hieu


class InboundDocumentService:
    """
    Quản lý luân chuyển Văn bản đến: Vào sổ -> Trình lãnh đạo cho ý kiến -> Giao chuyên viên xử lý -> Lưu trữ.
    """

    @classmethod
    @transaction.atomic
    def register_inbound_document(
        cls,
        clerk: NguoiDung,
        so_ky_hieu: str,
        co_quan_ban_hanh: str,
        trich_yeu: str,
        loai_van_ban: str,
        ngay_ban_hanh: Optional[date] = None,
        ngay_den: Optional[date] = None,
        do_khan: str = 'Bình thường',
        do_mat: str = 'Thường',
        han_xu_ly: Optional[date] = None
    ) -> VanBanDen:
        """
        Vào sổ văn bản đến mới. Tự động tính toán số đến kế tiếp trong năm.
        """
        current_year = (ngay_den or date.today()).year
        max_so_den = VanBanDen.objects.filter(ngay_den__year=current_year).aggregate(Max('so_den'))['so_den__max'] or 0
        next_so_den = max_so_den + 1

        doc = VanBanDen.objects.create(
            so_den=next_so_den,
            so_ky_hieu=so_ky_hieu.strip(),
            co_quan_ban_hanh=sanitize_input_text(co_quan_ban_hanh),
            trich_yeu=sanitize_input_text(trich_yeu),
            loai_van_ban=loai_van_ban,
            ngay_ban_hanh=ngay_ban_hanh or date.today(),
            ngay_den=ngay_den or date.today(),
            do_khan=do_khan,
            do_mat=do_mat,
            han_xu_ly=han_xu_ly,
            trang_thai=TrangThaiVanBanDen.CHO_TIEP_NHAN
        )
        return doc

    @classmethod
    def assign_directive(
        cls,
        van_ban_id: int,
        leader: NguoiDung,
        assignee: NguoiDung,
        directive_text: str,
        han_xu_ly: Optional[date] = None
    ) -> Tuple[bool, str]:
        """
        Lãnh đạo cho ý kiến chỉ đạo và phân công cán bộ chủ trì giải quyết.
        """
        try:
            doc = VanBanDen.objects.get(pk=van_ban_id)
        except VanBanDen.DoesNotExist:
            return False, "Không tìm thấy văn bản đến."

        doc.nguoi_chi_dao = leader
        doc.nguoi_chu_tri = assignee
        doc.noi_dung_chi_dao = sanitize_input_text(directive_text)
        if han_xu_ly:
            doc.han_xu_ly = han_xu_ly
        doc.trang_thai = TrangThaiVanBanDen.DANG_XU_LY
        doc.save()

        return True, f"Đã giao chỉ đạo xử lý văn bản cho đồng chí {assignee.ho_va_ten}."
