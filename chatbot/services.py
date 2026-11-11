"""
Education Management - AI Chatbot & Template Assistant Service Layer (Chatbot)
Chịu trách nhiệm nhận diện ý định (Intent Classification), tìm kiếm kho lưu trữ văn bản & mẫu biểu,
và cung cấp nội dung xem trước trực quan (A4 Document Preview) theo chuẩn Nghị định 30/2020/NĐ-CP.
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from django.db.models import Q

from chatbot.models import MauVanBan, LichSuChat
from van_ban.models import VanBanDi, VanBanDen
from ho_so.models import HoSoLuuTru
from authentication.models import NguoiDung
from common.security import sanitize_input_text


class IntentType:
    """Các nhóm ý định của người dùng khi trò chuyện với trợ lý ảo"""
    TIM_MAU = 'TIM_MAU'
    TRA_CUU_KHO = 'TRA_CUU_KHO'
    HOI_THE_THUC = 'HOI_THE_THUC'
    HOI_QUY_TRINH = 'HOI_QUY_TRINH'
    HOI_KY_SO = 'HOI_KY_SO'
    SOAN_VAN_BAN = 'SOAN_VAN_BAN'
    CHAO_HOI = 'CHAO_HOI'
    MAC_DINH = 'MAC_DINH'


class ChatbotNLPService:
    """
    Bộ máy nhận diện ngôn ngữ tự nhiên, truy vấn kho lưu trữ văn bản và sinh bản xem trước.
    """

    INTENT_KEYWORDS = {
        IntentType.CHAO_HOI: [
            'xin chào', 'chào bạn', 'hello', 'hi bot', 'bạn là ai', 'giúp gì', 'chức năng', 'xin chao'
        ],
        IntentType.HOI_THE_THUC: [
            'thể thức', 'nghị định 30', 'căn lề', 'phông chữ', 'cỡ chữ', 'số ký hiệu', 'tiêu ngữ',
            'khoảng cách dòng', 'quy chuẩn'
        ],
        IntentType.HOI_QUY_TRINH: [
            'quy trình', 'trình ký', 'phê duyệt', 'vào sổ', 'ban hành', 'thu hồi', 'luân chuyển',
            'các bước'
        ],
        IntentType.HOI_KY_SO: [
            'chữ ký số', 'ký số', 'con dấu', 'chứng thư', 'văn thư đóng dấu', 'xác thực', 'sha-256'
        ],
        IntentType.SOAN_VAN_BAN: [
            'soạn thảo', 'viết giúp', 'tạo dự thảo', 'khởi tạo văn bản'
        ],
        IntentType.TIM_MAU: [
            'mẫu', 'biểu mẫu', 'tải mẫu', 'quyết định', 'kế hoạch', 'tờ trình', 'thông báo', 
            'hướng dẫn', 'khen thưởng', 'kinh phí', 'biên bản', 'báo cáo', 'phòng máy',
            'tuyển sinh', 'nghỉ lễ', 'giao ban', 'thi đua', 'đầu tư'
        ],
        IntentType.TRA_CUU_KHO: [
            'tìm văn bản', 'tra cứu', 'kho lưu trữ', 'tìm file', 'xem văn bản', 'văn bản số',
            'tìm kiếm', 'hồ sơ', 'dự thảo', 'văn bản đi', 'văn bản đến'
        ],
    }

    @classmethod
    def classify_intent(cls, message: str) -> str:
        """
        Phân loại ý định của câu hỏi dựa trên phân tích tập từ khóa hành chính.
        """
        lower_msg = message.lower().strip()

        for intent, keywords in cls.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in lower_msg:
                    return intent

        return IntentType.MAC_DINH

    @classmethod
    def search_templates(cls, query: str, limit: int = 4) -> List[MauVanBan]:
        """
        Tìm kiếm các mẫu văn bản liên quan trong kho mẫu văn bản hành chính của Sở GD&ĐT.
        """
        keywords = [k.strip() for k in query.lower().split() if len(k.strip()) >= 2]
        if not keywords:
            return list(MauVanBan.objects.all().order_by('-luot_xem')[:limit])

        q_obj = Q()
        for kw in keywords:
            q_obj |= Q(ten_mau__icontains=kw) | Q(loai_van_ban__icontains=kw) | Q(linh_vuc__icontains=kw)

        matches = list(MauVanBan.objects.filter(q_obj).order_by('-luot_xem'))
        matches.sort(
            key=lambda m: sum(1 for kw in keywords if kw in m.ten_mau.lower() or kw in m.loai_van_ban.lower()),
            reverse=True
        )
        if not matches:
            matches = list(MauVanBan.objects.all().order_by('-luot_xem')[:limit])
        return matches[:limit]

    @classmethod
    def generate_van_ban_di_html(cls, vb: VanBanDi) -> str:
        """Sinh mã HTML xem trước chuẩn A4 Nghị định 30 cho Văn bản đi."""
        so_hieu = vb.so_ky_hieu or f"Dự thảo số {vb.van_ban_id}"
        ngay_str = vb.ngay_ban_hanh.strftime("ngày %d tháng %m năm %Y") if vb.ngay_ban_hanh else (
            vb.ngay_tao.strftime("ngày %d tháng %m năm %Y") if vb.ngay_tao else "ngày ... tháng ... năm 2026"
        )
        noi_nhan_list = [f"- {n.strip()};" for n in (vb.noi_nhan or "Như trên").split(',') if n.strip()]
        noi_nhan_html = "<br>".join(noi_nhan_list) or "- Như trên;<br>- Lưu: VT."
        lanh_dao = vb.lanh_dao_ky_ten or (vb.lanh_dao_ky.ho_va_ten if vb.lanh_dao_ky else 'Lãnh đạo Sở')

        da_ky = vb.trang_thai in ('DA_KY_CHO_BAN_HANH', 'DA_BAN_HANH')
        sign_box = f"""
        <div style="margin: 10px 0; padding: 6px 14px; display: inline-block; border: 2px dashed #16a34a; border-radius: 6px; background: #f0fdf4; color: #166534; font-size: 11pt; font-weight: bold; text-align: left;">
          🔒 [ĐÃ KÝ SỐ ĐIỆN TỬ]<br>
          <span style="font-size: 9.5pt; font-weight: normal; color: #15803d;">Cơ quan: Sở Giáo dục và Đào tạo TP. Đà Nẵng</span><br>
          <span style="font-size: 9pt; font-weight: normal; color: #4b5563;">Người ký: {lanh_dao}</span>
        </div>
        """ if da_ky else """<div class="vb-sign-space" style="height: 50px;"></div>"""

        return f"""
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: {so_hieu}</div>
        <div class="vb-doc-excerpt">{vb.trich_yeu[:55]}...</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, {ngay_str}</div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">{vb.loai_van_ban.upper()}</div>
    <div class="vb-subject">{vb.trich_yeu}</div>
  </div>

  <div class="vb-content">
    <p>{vb.noi_dung_tom_tat or vb.trich_yeu}</p>
    <p>Sở Giáo dục và Đào tạo đề nghị Thủ trưởng các cơ quan, đơn vị, trường học trực thuộc nghiên cứu, chỉ đạo và triển khai nghiêm túc các nhiệm vụ theo đúng nội dung và tiến độ kế hoạch.</p>
    <p>Trong quá trình tổ chức triển khai, nếu có vướng mắc phát sinh, các đơn vị kịp thời phản ánh về Sở Giáo dục và Đào tạo (qua {vb.don_vi_soan_thao or 'Văn phòng Sở'}) để được hướng dẫn phối hợp giải quyết.</p>
  </div>

  <table class="vb-footer-table" style="margin-top: 36px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">{noi_nhan_html}</div>
        <div class="vb-recipient-item">- Lưu: VT, {vb.don_vi_soan_thao or 'VP'}.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">KT. GIÁM ĐỐC<br>PHÓ GIÁM ĐỐC</div>
        {sign_box}
        <div class="vb-sign-name">{lanh_dao}</div>
      </td>
    </tr>
  </table>
</div>
"""

    @classmethod
    def generate_van_ban_den_html(cls, vb: VanBanDen) -> str:
        """Sinh mã HTML xem trước chuẩn A4 cho Văn bản đến."""
        ngay_den_str = vb.ngay_den.strftime("ngày %d tháng %m năm %Y") if vb.ngay_den else "ngày ... tháng ... năm 2026"
        ngay_bh_str = vb.ngay_ban_hanh.strftime("ngày %d/%m/%Y") if vb.ngay_ban_hanh else "năm 2026"

        return f"""
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-agency-name">{vb.co_quan_ban_hanh.upper()}</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: {vb.so_ky_hieu or '...'}</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div style="border: 2px solid #0284c7; border-radius: 8px; padding: 8px; background: #f0f9ff; display: inline-block; text-align: center;">
          <b style="color: #0369a1; font-size: 11pt;">SỞ GIÁO DỤC VÀ ĐÀO TẠO ĐÀ NẴNG</b><br>
          <span style="font-size: 13pt; font-weight: bold; color: #dc2626;">VĂN BẢN ĐẾN</span><br>
          <span style="font-size: 11pt;">Số đến: <b>{vb.so_den}</b></span><br>
          <span style="font-size: 10pt; font-style: italic;">{ngay_den_str}</span>
        </div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">{vb.loai_van_ban.upper()}</div>
    <div class="vb-subject">{vb.trich_yeu}</div>
  </div>

  <div class="vb-content">
    <p><b>Cơ quan gửi:</b> {vb.co_quan_ban_hanh} | <b>Ngày ban hành:</b> {ngay_bh_str}</p>
    <p><b>Độ khẩn:</b> <span class="badge badge-danger">{vb.do_khan}</span> | <b>Độ mật:</b> {vb.do_mat}</p>
    <p><b>Nội dung trích yếu:</b> {vb.trich_yeu}</p>
    <div style="margin-top: 20px; padding: 14px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px;">
      <b style="color: #0f172a;">Ý KIẾN CHỈ ĐẠO CỦA LÃNH ĐẠO SỞ:</b>
      <p style="margin: 6px 0; color: #1e3a8a; font-style: italic;">"{vb.noi_dung_chi_dao or 'Giao phòng chuyên môn chủ trì nghiên cứu, tham mưu xử lý đúng hạn.'}"</p>
      <div style="font-size: 11pt; color: #475569; margin-top: 8px;">
        • Cán bộ chỉ đạo: <b>{vb.nguoi_chi_dao.ho_va_ten if vb.nguoi_chi_dao else 'Lãnh đạo Sở'}</b><br>
        • Cán bộ chủ trì: <b>{vb.nguoi_chu_tri.ho_va_ten if vb.nguoi_chu_tri else 'Chuyên viên phụ trách'}</b><br>
        • Hạn xử lý: <b style="color: #dc2626;">{vb.han_xu_ly.strftime('%d/%m/%Y') if vb.han_xu_ly else 'Đúng hạn quy định'}</b>
      </div>
    </div>
  </div>
</div>
"""

    @classmethod
    def search_repository(cls, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Tìm kiếm tổng hợp trên toàn bộ kho lưu trữ:
        1. Kho mẫu văn bản quy chuẩn (MauVanBan)
        2. Kho văn bản đi (VanBanDi)
        3. Kho văn bản đến (VanBanDen)
        4. Kho hồ sơ lưu trữ (HoSoLuuTru)
        """
        results: List[Dict[str, Any]] = []
        raw_words = [w.strip() for w in query.lower().split() if len(w.strip()) >= 2]
        stopwords = {'tôi', 'cần', 'muốn', 'xin', 'tìm', 'xem', 'cho', 'của', 'và', 'các', 'về', 'trong', 'với'}
        keywords = [w for w in raw_words if w not in stopwords]
        if not keywords:
            keywords = raw_words

        # 1. Tìm trong Kho mẫu văn bản (MauVanBan)
        q_mau = Q()
        for kw in keywords:
            q_mau |= Q(ten_mau__icontains=kw) | Q(loai_van_ban__icontains=kw) | Q(linh_vuc__icontains=kw) | Q(noi_dung_text__icontains=kw)

        for m in MauVanBan.objects.filter(q_mau):
            score = 0
            t_low = m.ten_mau.lower()
            c_low = f"{m.loai_van_ban} {m.linh_vuc}".lower()
            b_low = m.noi_dung_text.lower()
            phrase = query.lower().strip()
            if phrase and phrase in t_low:
                score += 100
            for kw in keywords:
                if kw in t_low:
                    score += 30
                elif kw in c_low:
                    score += 15
                elif kw in b_low:
                    score += 5

            results.append({
                'score': score,
                'mau_id': m.mau_id,
                'id': m.mau_id,
                'loai_tep': 'mau_van_ban',
                'ma_mau': m.ma_mau,
                'ten_mau': m.ten_mau,
                'loai_van_ban': m.loai_van_ban,
                'linh_vuc': m.linh_vuc,
                'tham_quyen_ky': 'Giám đốc Sở' if m.loai_van_ban in ('Quyết định', 'Kế hoạch') else ('Trưởng phòng' if m.loai_van_ban == 'Tờ trình' else 'Lãnh đạo Sở'),
                'mo_ta': f"Biểu mẫu chuẩn {m.loai_van_ban.lower()} theo Nghị định 30/2020/NĐ-CP lĩnh vực {m.linh_vuc}.",
                'dinh_dang': 'DOCX',
                'noi_dung_html': m.noi_dung_html,
                'noi_dung_text': m.noi_dung_text,
            })

        # 2. Tìm trong Kho văn bản đi (VanBanDi)
        if keywords:
            q_vb = Q()
            for kw in keywords:
                q_vb |= Q(so_ky_hieu__icontains=kw) | Q(trich_yeu__icontains=kw) | Q(loai_van_ban__icontains=kw) | Q(noi_dung_tom_tat__icontains=kw)

            for vb in VanBanDi.objects.filter(q_vb):
                score = 0
                t_low = (vb.trich_yeu or '').lower()
                c_low = f"{vb.loai_van_ban} {vb.so_ky_hieu or ''}".lower()
                b_low = (vb.noi_dung_tom_tat or '').lower()
                phrase = query.lower().strip()
                if phrase and phrase in t_low:
                    score += 100
                for kw in keywords:
                    if kw in t_low:
                        score += 30
                    elif kw in c_low:
                        score += 20
                    elif kw in b_low:
                        score += 5

                results.append({
                    'score': score,
                    'mau_id': vb.van_ban_id,
                    'id': vb.van_ban_id,
                    'loai_tep': 'van_ban_di',
                    'ma_mau': vb.so_ky_hieu or f"VB-DI-{vb.van_ban_id}",
                    'ten_mau': vb.trich_yeu,
                    'loai_van_ban': vb.loai_van_ban,
                    'linh_vuc': vb.don_vi_soan_thao or 'Văn phòng Sở',
                    'tham_quyen_ky': vb.lanh_dao_ky_ten or 'Lãnh đạo Sở',
                    'mo_ta': f"Văn bản đi - Trạng thái: {vb.get_trang_thai_display()} | Người ký: {vb.lanh_dao_ky_ten or 'Lãnh đạo Sở'}.",
                    'dinh_dang': 'PDF',
                    'noi_dung_html': cls.generate_van_ban_di_html(vb),
                })

        # 3. Tìm trong Kho văn bản đến (VanBanDen)
        if keywords:
            q_den = Q()
            for kw in keywords:
                q_den |= Q(so_den__icontains=kw) | Q(so_ky_hieu__icontains=kw) | Q(trich_yeu__icontains=kw) | Q(co_quan_ban_hanh__icontains=kw)

            for vd in VanBanDen.objects.filter(q_den):
                score = 0
                t_low = (vd.trich_yeu or '').lower()
                c_low = f"{vd.so_den} {vd.so_ky_hieu or ''} {vd.co_quan_ban_hanh or ''}".lower()
                phrase = query.lower().strip()
                if phrase and phrase in t_low:
                    score += 100
                for kw in keywords:
                    if kw in t_low:
                        score += 30
                    elif kw in c_low:
                        score += 20

                results.append({
                    'score': score,
                    'mau_id': vd.van_ban_id,
                    'id': vd.van_ban_id,
                    'loai_tep': 'van_ban_den',
                    'ma_mau': f"Số đến: {vd.so_den} ({vd.so_ky_hieu})",
                    'ten_mau': vd.trich_yeu,
                    'loai_van_ban': vd.loai_van_ban,
                    'linh_vuc': vd.co_quan_ban_hanh,
                    'tham_quyen_ky': vd.co_quan_ban_hanh,
                    'mo_ta': f"Văn bản đến từ {vd.co_quan_ban_hanh} | Hạn xử lý: {vd.han_xu_ly.strftime('%d/%m/%Y') if vd.han_xu_ly else 'Đúng hạn'}.",
                    'dinh_dang': 'PDF',
                    'noi_dung_html': cls.generate_van_ban_den_html(vd),
                })

        # Sắp xếp kết quả theo điểm tương đồng cao nhất
        results.sort(key=lambda x: x.get('score', 0), reverse=True)

        # 4. Fallback: Nếu không tìm thấy kết quả nào, trả về các mẫu văn bản phổ biến
        if not results:
            for m in MauVanBan.objects.all().order_by('-luot_xem')[:limit]:
                results.append({
                    'mau_id': m.mau_id,
                    'id': m.mau_id,
                    'loai_tep': 'mau_van_ban',
                    'ma_mau': m.ma_mau,
                    'ten_mau': m.ten_mau,
                    'loai_van_ban': m.loai_van_ban,
                    'linh_vuc': m.linh_vuc,
                    'tham_quyen_ky': 'Lãnh đạo Sở',
                    'mo_ta': f"Biểu mẫu chuẩn {m.loai_van_ban.lower()} theo Nghị định 30/2020/NĐ-CP lĩnh vực {m.linh_vuc}.",
                    'dinh_dang': 'DOCX',
                    'noi_dung_html': m.noi_dung_html,
                    'noi_dung_text': m.noi_dung_text,
                })

        return results[:limit]

    @classmethod
    def process_message(
        cls,
        user_message: str,
        user: Optional[NguoiDung] = None
    ) -> Dict[str, Any]:
        """
        Xử lý tin nhắn người dùng, tra cứu kho lưu trữ và đề xuất danh sách file kèm bản xem trước.
        """
        clean_msg = sanitize_input_text(user_message).strip()
        intent = cls.classify_intent(clean_msg)
        suggested_templates = []
        next_suggestions = []
        answer = ""

        if intent == IntentType.CHAO_HOI:
            user_name = user.ho_va_ten if user else "Đồng chí"
            answer = (
                f"Kính chào {user_name}! Tôi là Trợ lý ảo tra cứu văn bản và biểu mẫu điều hành của Sở GD&ĐT TP. Đà Nẵng.\n"
                "Đồng chí chỉ cần **nhập từ khóa hoặc nội dung văn bản cần tìm** (ví dụ: *tờ trình kinh phí*, *quyết định khen thưởng*, "
                "*kế hoạch tuyển sinh*, *hướng dẫn năm học*...), tôi sẽ tự động kiểm tra kho lưu trữ, đề xuất danh sách file "
                "và hỗ trợ mở chế độ xem trước trực tiếp ngay trên màn hình."
            )
            next_suggestions = [
                "Mẫu tờ trình xin phê duyệt kinh phí hoạt động chuyên môn",
                "Mẫu quyết định khen thưởng giáo viên và học sinh giỏi",
                "Mẫu kế hoạch tổ chức kỳ thi tuyển sinh vào lớp 10",
                "Xem toàn bộ kho mẫu văn bản"
            ]

        elif intent == IntentType.HOI_THE_THUC:
            answer = (
                "Về quy chuẩn thể thức văn bản hành chính theo Nghị định 30/2020/NĐ-CP của Chính phủ:\n"
                "1. **Phông chữ**: Chuẩn Unicode Times New Roman, cỡ chữ 13 - 14.\n"
                "2. **Căn lề khổ A4**: Trên 20-25mm, Dưới 20-25mm, Trái 30-35mm, Phải 15-20mm.\n"
                "3. **Số ký hiệu**: Phải theo quy tắc Số/LoạiVB-TênViếtTắt (Ví dụ: 125/QĐ-SGDĐT).\n"
                "4. **Dấu và chữ ký số**: Đặt ngay ngắn tại vị trí thẩm quyền ký, không đè lên chữ."
            )
            suggested_templates = cls.search_repository(clean_msg, limit=2)
            next_suggestions = [
                "Mẫu công văn hướng dẫn triển khai nhiệm vụ năm học",
                "Mẫu thông báo nghỉ lễ và phân công trực cơ quan",
                "Quy trình luân chuyển văn bản đi"
            ]

        elif intent == IntentType.HOI_QUY_TRINH:
            answer = (
                "Quy trình luân chuyển văn bản đi tại Sở GD&ĐT gồm 4 bước chính:\n"
                "1. **Chuyên viên**: Soạn thảo dự thảo và gửi đính kèm tệp văn bản.\n"
                "2. **Văn thư Sở**: Tiếp nhận và kiểm tra thể thức văn bản, trả lại nếu chưa đạt chuẩn.\n"
                "3. **Lãnh đạo Sở**: Xem xét nội dung và thực hiện ký số điện tử phê duyệt.\n"
                "4. **Văn thư**: Cấp số chính thức từ sổ đăng ký, đóng dấu số và ban hành tới các đơn vị nhận."
            )
            suggested_templates = cls.search_repository(clean_msg, limit=2)
            next_suggestions = [
                "Mẫu tờ trình xin kinh phí",
                "Hướng dẫn chữ ký số SHA-256",
                "Xem toàn bộ kho mẫu văn bản"
            ]

        elif intent == IntentType.HOI_KY_SO:
            answer = (
                "Hệ thống tích hợp ký số xác thực chuẩn mật mã SHA-256 theo chứng thư số chuyên dùng Chính phủ. "
                "Lãnh đạo Sở có thể trực tiếp ký số trên giao diện 'Phê duyệt văn bản đi', hệ thống sẽ tự động ghim chứng thư "
                "và con dấu điện tử vào đúng tọa độ trang cuối tài liệu."
            )
            suggested_templates = cls.search_repository(clean_msg, limit=2)

        elif intent == IntentType.TIM_MAU:
            suggested_templates = cls.search_repository(clean_msg, limit=4)
            templates_str = ", ".join([f"'{m.get('ten_mau', '')}'" for m in suggested_templates])
            answer = (
                f"Dưới đây là các văn bản/mẫu biểu phù hợp nhất với yêu cầu của đồng chí trong kho lưu trữ của Sở: "
                f"{templates_str}. Đồng chí có thể nhấn xem chi tiết hoặc tải xuống để sử dụng ngay."
            )
            next_suggestions = [
                "Mẫu quyết định khen thưởng giáo viên và học sinh giỏi",
                "Mẫu kế hoạch tổ chức kỳ thi tuyển sinh vào lớp 10",
                "Xem toàn bộ kho mẫu văn bản"
            ]

        else:
            # Tra cứu kho lưu trữ theo nội dung văn bản người dùng nhập
            suggested_templates = cls.search_repository(clean_msg, limit=4)
            count = len(suggested_templates)
            answer = (
                f"Tôi đã kiểm tra kho lưu trữ của Sở GD&ĐT và tìm thấy **{count} văn bản/tệp tài liệu** phù hợp nhất "
                f"với yêu cầu của đồng chí. Đồng chí có thể nhấn nút **'👁️ Xem trước (Preview)'** để mở chế độ xem trước "
                f"toàn văn chuẩn trang in A4, hoặc nhấn **'📥 Tải về'** để sử dụng."
            )
            next_suggestions = [
                "Mẫu quyết định khen thưởng giáo viên và học sinh giỏi",
                "Mẫu kế hoạch tổ chức kỳ thi tuyển sinh vào lớp 10",
                "Xem toàn bộ kho mẫu văn bản"
            ]

        # Lưu lịch sử hội thoại
        template_ids = ",".join([str(t.get('mau_id', '')) for t in suggested_templates]) if suggested_templates else ""
        try:
            LichSuChat.objects.create(
                nguoi_dung=user,
                cau_hoi=clean_msg,
                cau_tra_loi=answer,
                mau_de_xuat_ids=template_ids
            )
        except Exception:
            pass

        return {
            'answer': answer,
            'intent': intent,
            'suggested_templates': suggested_templates,
            'next_suggestions': next_suggestions
        }
