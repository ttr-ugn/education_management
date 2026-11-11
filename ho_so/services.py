"""
Education Management - Archival & Dossier Management Service Layer (Ho So Luu Tru)
Chịu trách nhiệm quản lý hồ sơ cơ quan, lập danh mục văn bản lưu trữ, tính hạn bảo quản và bàn giao lưu trữ.
"""

import html
import re
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Dict, Any, Tuple, List
from django.conf import settings
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


class ArchivalDocumentService:
    """
    Dịch vụ chuẩn hóa dữ liệu xem trước và tải về cho văn bản ban hành trong hồ sơ lưu trữ.
    """

    @staticmethod
    def resolve_attachment(tep_dinh_kem: Optional[str]) -> Tuple[Optional[str], Optional[Path], bool]:
        """
        Chuẩn hóa đường dẫn tệp đính kèm trong MEDIA_ROOT và kiểm tra định dạng PDF.
        Trả về: (media_url, disk_path, is_pdf).
        """
        raw = (tep_dinh_kem or '').strip().replace('\\', '/')
        if not raw:
            return None, None, False

        rel = raw[len('/media/'):] if raw.startswith('/media/') else raw.lstrip('/')
        media_root = Path(settings.MEDIA_ROOT).resolve()
        candidate = (media_root / rel).resolve()
        if not candidate.is_relative_to(media_root) or not candidate.is_file():
            return None, None, False

        media_prefix = settings.MEDIA_URL.rstrip('/')
        media_url = f"{media_prefix}/{rel}"
        is_pdf = candidate.suffix.lower() == '.pdf'
        return media_url, candidate, is_pdf

    @classmethod
    def serialize_document(cls, doc: VanBanBanHanh) -> Dict[str, Any]:
        """Chuyển đổi bản ghi VanBanBanHanh sang JSON đầy đủ cho giao diện chi tiết hồ sơ."""
        media_url, _, is_pdf = cls.resolve_attachment(doc.tep_dinh_kem)
        don_vi = doc.co_quan_ban_hanh or (
            doc.ho_so.don_vi if doc.ho_so else 'Sở Giáo dục và Đào tạo TP. Đà Nẵng'
        )
        return {
            'van_ban_id': doc.van_ban_id,
            'so_ky_hieu': doc.so_ky_hieu,
            'trich_yeu': doc.trich_yeu,
            'loai_van_ban': doc.loai_van_ban,
            'co_quan_ban_hanh': doc.co_quan_ban_hanh,
            'don_vi_soan_thao': don_vi,
            'nguoi_ky': doc.nguoi_ky,
            'chuc_vu_nguoi_ky': doc.chuc_vu_nguoi_ky,
            'ngay_ky': doc.ngay_ky.strftime('%Y-%m-%d') if doc.ngay_ky else '',
            'ngay_ban_hanh': doc.ngay_ban_hanh.strftime('%Y-%m-%d') if doc.ngay_ban_hanh else '',
            'do_khan': doc.do_khan,
            'muc_do_mat': doc.muc_do_mat,
            'thoi_han_bao_quan': doc.thoi_han_bao_quan,
            'tep_dinh_kem': media_url or (doc.tep_dinh_kem or ''),
            'nguon': 'PDF gốc lưu trữ' if is_pdf else 'Văn bản ban hành điện tử',
            'preview_url': media_url if is_pdf else f'/api/ho-so/van-ban/{doc.van_ban_id}/xem-truoc',
            'download_url': f'/api/ho-so/van-ban/{doc.van_ban_id}/tai-ve',
        }

    @staticmethod
    def safe_download_filename(so_ky_hieu: str, ext: str) -> str:
        """Tạo tên tệp tải về an toàn từ số ký hiệu văn bản."""
        slug = re.sub(r'[^A-Za-z0-9._-]+', '_', (so_ky_hieu or 'van_ban')).strip('_')
        return f"{slug or 'van_ban'}.{ext.lstrip('.')}"

    @staticmethod
    def build_document_html(doc: VanBanBanHanh, for_word: bool = False) -> str:
        """
        Sinh HTML chuẩn A4 Nghị định 30/2020/NĐ-CP cho xem trước trình duyệt hoặc tải file .doc.
        """
        so_ky_hieu = html.escape(doc.so_ky_hieu or '')
        trich_yeu = html.escape(doc.trich_yeu or '')
        loai_vb = html.escape((doc.loai_van_ban or 'Văn bản').upper())
        co_quan_raw = (doc.co_quan_ban_hanh or 'Sở Giáo dục và Đào tạo TP. Đà Nẵng').strip()
        co_quan = html.escape(co_quan_raw.upper())
        nguoi_ky = html.escape(doc.nguoi_ky or '')
        chuc_vu = html.escape((doc.chuc_vu_nguoi_ky or 'THỦ TRƯỞNG ĐƠN VỊ').upper())

        ngay_bh = doc.ngay_ban_hanh
        ngay_str = (
            f"Đà Nẵng, ngày {ngay_bh.day:02d} tháng {ngay_bh.month:02d} năm {ngay_bh.year}"
            if ngay_bh else "Đà Nẵng, ngày ... tháng ... năm 2026"
        )
        ngay_ky_str = doc.ngay_ky.strftime('%d/%m/%Y') if doc.ngay_ky else (ngay_bh.strftime('%d/%m/%Y') if ngay_bh else '')

        parent_html = (
            '<div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>'
            if 'SỞ GIÁO DỤC' in co_quan_raw.upper() else ''
        )

        ho_so_info = (
            f"Thuộc hồ sơ lưu trữ: <b>{html.escape(doc.ho_so.ma_ho_so)}</b> — {html.escape(doc.ho_so.tieu_de)} "
            f"(Đơn vị lập: {html.escape(doc.ho_so.don_vi)}; Thời hạn bảo quản: {html.escape(doc.thoi_han_bao_quan)})."
            if doc.ho_so else
            f"Trạng thái lưu trữ: Văn bản đã ban hành sẵn sàng đưa vào hồ sơ công việc (Thời hạn bảo quản dự kiến: {html.escape(doc.thoi_han_bao_quan)})."
        )

        body_html = f"""
<div class="vb-page">
  <table class="vb-header-table">
    <tr>
      <td style="width: 46%; text-align: center; vertical-align: top;">
        {parent_html}
        <div class="vb-agency-name">{co_quan}</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: {so_ky_hieu}</div>
      </td>
      <td style="width: 54%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">{html.escape(ngay_str)}</div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">{loai_vb}</div>
    <div class="vb-subject">{trich_yeu}</div>
  </div>

  <div class="vb-content">
    <p><b>Nội dung trích yếu:</b> {trich_yeu}.</p>
    <p>Căn cứ chức năng, nhiệm vụ và quyền hạn hiện hành; theo đề nghị của các phòng chuyên môn, nghiệp vụ thuộc Sở Giáo dục và Đào tạo thành phố Đà Nẵng, lãnh đạo cơ quan ban hành chính thức {html.escape((doc.loai_van_ban or 'văn bản').lower())} số <b>{so_ky_hieu}</b> để làm cơ sở tổ chức triển khai thực hiện thống nhất trong toàn ngành.</p>
    <p>Thủ trưởng các phòng thuộc Sở, Hiệu trưởng các trường THPT, trường phổ thông nhiều cấp học, Giám đốc các trung tâm giáo dục nghề nghiệp - giáo dục thường xuyên và các đơn vị trực thuộc căn cứ nội dung văn bản chủ động xây dựng kế hoạch triển khai đúng tiến độ, bảo đảm chất lượng và báo cáo kết quả thực hiện theo quy định.</p>
    <div class="vb-archive-meta">
      <div><b>Thông tin hồ sơ lưu trữ điện tử:</b></div>
      <div>• {ho_so_info}</div>
      <div>• Độ khẩn: <b>{html.escape(doc.do_khan)}</b> &nbsp;|&nbsp; Mức độ mật: <b>{html.escape(doc.muc_do_mat)}</b> &nbsp;|&nbsp; Kỳ lưu trữ: Tháng {doc.thang_luu_tru}/{doc.nam_luu_tru} (Quý {doc.quy_luu_tru})</div>
    </div>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 48%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Giám đốc, các Phó Giám đốc Sở;</div>
        <div class="vb-recipient-item">- Các phòng chuyên môn, nghiệp vụ;</div>
        <div class="vb-recipient-item">- Lưu: VT, Lưu trữ điện tử ({html.escape(doc.ho_so.ma_ho_so if doc.ho_so else 'Sở GD&ĐT')}).</div>
      </td>
      <td style="width: 52%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">{chuc_vu}</div>
        <div class="vb-sign-stamp">
          ĐÃ KÝ SỐ ĐIỆN TỬ<br>
          <span>Cơ quan: {co_quan}</span><br>
          <span>Ngày ký: {html.escape(ngay_ky_str)}</span>
        </div>
        <div class="vb-sign-name">{nguoi_ky}</div>
      </td>
    </tr>
  </table>
</div>
"""

        common_css = """
@page { size: 210mm 297mm; margin: 20mm 20mm 20mm 30mm; }
body { font-family: 'Times New Roman', Times, serif; font-size: 13pt; line-height: 1.45; color: #111827; margin: 0; }
table { width: 100%; border-collapse: collapse; }
td { border: none; padding: 2px 4px; }
.vb-agency-parent { font-size: 12pt; text-transform: uppercase; }
.vb-agency-name { font-size: 12.5pt; font-weight: bold; text-transform: uppercase; }
.vb-line-short { width: 90px; border-top: 1px solid #111827; margin: 4px auto 6px auto; }
.vb-line-medium { width: 150px; border-top: 1px solid #111827; margin: 4px auto 6px auto; }
.vb-doc-number { font-size: 12.5pt; margin-top: 4px; }
.vb-nation-title { font-size: 12pt; font-weight: bold; text-transform: uppercase; }
.vb-motto { font-size: 12.5pt; font-weight: bold; }
.vb-location-date { font-size: 12.5pt; font-style: italic; margin-top: 4px; }
.vb-title-block { text-align: center; margin: 20px 0 14px 0; }
.vb-title-type { font-size: 14.5pt; font-weight: bold; text-transform: uppercase; }
.vb-subject { font-size: 13pt; font-weight: bold; max-width: 90%; margin: 6px auto 0 auto; }
.vb-content p { text-indent: 1.27cm; text-align: justify; margin: 8px 0; }
.vb-archive-meta { margin-top: 16px; padding: 10px 14px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 11.5pt; line-height: 1.5; }
.vb-footer-table { margin-top: 28px; }
.vb-recipients-title { font-size: 11.5pt; font-weight: bold; font-style: italic; margin-bottom: 4px; }
.vb-recipient-item { font-size: 11pt; line-height: 1.35; }
.vb-sign-role { font-size: 12.5pt; font-weight: bold; text-transform: uppercase; }
.vb-sign-stamp { margin: 10px auto; padding: 6px 12px; display: inline-block; border: 2px dashed #16a34a; border-radius: 6px; background: #f0fdf4; color: #166534; font-size: 10.5pt; font-weight: bold; text-align: left; }
.vb-sign-stamp span { font-size: 9.5pt; font-weight: normal; color: #15803d; }
.vb-sign-name { font-size: 13pt; font-weight: bold; margin-top: 4px; }
"""

        if for_word:
            return f"""<!DOCTYPE html>
<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
<head>
<meta charset='utf-8'>
<title>{so_ky_hieu}</title>
<style>{common_css}</style>
</head>
<body>{body_html}</body>
</html>"""

        return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>{so_ky_hieu} - Xem trước văn bản</title>
<style>
{common_css}
body {{ background: #525659; padding: 20px; }}
.vb-page {{ background: #ffffff; max-width: 210mm; min-height: 297mm; margin: 0 auto; padding: 20mm 20mm 20mm 30mm; box-sizing: border-box; box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35); }}
@media print {{
  body {{ background: #ffffff; padding: 0; }}
  .vb-page {{ box-shadow: none; margin: 0; padding: 0; min-height: auto; }}
}}
</style>
</head>
<body>{body_html}</body>
</html>"""
