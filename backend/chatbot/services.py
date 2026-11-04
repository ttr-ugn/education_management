import re
import json
import sqlite3
from flask import g
from database.db import get_db

def normalize_text(text):
    """Chuẩn hóa chuỗi văn bản phục vụ tìm kiếm từ khóa không dấu và có dấu."""
    if not text:
        return ""
    text = text.lower().strip()
    return re.sub(r'\s+', ' ', text)

def get_all_templates(keyword=None, loai=None, linh_vuc=None):
    """Lấy danh sách tất cả các mẫu văn bản trong kho lưu trữ (có bộ lọc)."""
    db = get_db()
    sql = """
        SELECT mau_id, ma_mau, ten_mau, loai_van_ban, linh_vuc,
               co_quan_ban_hanh, tham_quyen_ky, mo_ta, can_cu_phap_ly,
               tu_khoa, ten_tep, luot_xem, luot_tai, ngay_tao
        FROM mau_van_ban
        WHERE 1=1
    """
    params = []

    if loai:
        sql += " AND loai_van_ban = ?"
        params.append(loai)

    if linh_vuc:
        sql += " AND linh_vuc = ?"
        params.append(linh_vuc)

    if keyword:
        kw = f"%{keyword.strip()}%"
        sql += " AND (ten_mau LIKE ? OR tu_khoa LIKE ? OR ma_mau LIKE ? OR mo_ta LIKE ?)"
        params.extend([kw, kw, kw, kw])

    sql += " ORDER BY luot_xem DESC, mau_id ASC"
    rows = db.execute(sql, params).fetchall()
    return [dict(row) for row in rows]

def get_template_by_id(mau_id, increment_view=True):
    """Lấy chi tiết đầy đủ của một mẫu văn bản theo ID và tăng lượt xem."""
    db = get_db()
    row = db.execute("""
        SELECT mau_id, ma_mau, ten_mau, loai_van_ban, linh_vuc,
               co_quan_ban_hanh, tham_quyen_ky, mo_ta, can_cu_phap_ly,
               tu_khoa, noi_dung_html, noi_dung_text, ten_tep,
               luot_xem, luot_tai, ngay_tao
        FROM mau_van_ban
        WHERE mau_id = ?
    """, (mau_id,)).fetchone()

    if not row:
        return None

    if increment_view:
        db.execute("UPDATE mau_van_ban SET luot_xem = luot_xem + 1 WHERE mau_id = ?", (mau_id,))
        db.commit()

    return dict(row)

def increment_download_count(mau_id):
    """Tăng số lượt tải của mẫu văn bản."""
    db = get_db()
    db.execute("UPDATE mau_van_ban SET luot_tai = luot_tai + 1 WHERE mau_id = ?", (mau_id,))
    db.commit()

def generate_word_document(mau):
    """
    Tạo nội dung file Microsoft Word (.doc) chuẩn A4 và font Times New Roman
    theo thể thức Nghị định 30/2020/NĐ-CP.
    """
    html_content = mau.get('noi_dung_html', '')
    title = mau.get('ten_mau', 'Mẫu văn bản')

    # Định dạng Word HTML Mime tương thích 100% với Microsoft Word, WPS Office và LibreOffice
    word_doc = f"""<html xmlns:o='urn:schemas-microsoft-com:office:office'
xmlns:w='urn:schemas-microsoft-com:office:word'
xmlns='http://www.w3.org/TR/REC-html40'>
<head>
<meta charset='utf-8'>
<title>{title}</title>
<!--[if gte mso 9]>
<xml>
 <w:WordDocument>
  <w:View>Print</w:View>
  <w:Zoom>100</w:Zoom>
  <w:DoNotOptimizeForBrowser/>
 </w:WordDocument>
</xml>
<![endif]-->
<style>
@page Section1 {{
  size: 595.3pt 841.9pt; /* Kích thước chuẩn A4 */
  margin: 56.7pt 56.7pt 56.7pt 85.05pt; /* Lề: trên 2cm, dưới 2cm, phải 2cm, trái 3cm chuẩn Nghị định 30 */
  mso-header-margin: 35.4pt;
  mso-footer-margin: 35.4pt;
  mso-paper-source: 0;
}}
div.Section1 {{
  page: Section1;
}}
body {{
  font-family: 'Times New Roman', Times, serif;
  font-size: 13pt;
  line-height: 1.35;
  color: #000000;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12pt;
}}
table.vb-header-table td, table.vb-footer-table td {{
  border: none;
  padding: 2pt 4pt;
}}
.vb-agency-parent {{
  font-size: 12pt;
  text-transform: uppercase;
  color: #111;
}}
.vb-agency-name {{
  font-size: 13pt;
  font-weight: bold;
  text-transform: uppercase;
  color: #000;
}}
.vb-nation-title {{
  font-size: 12pt;
  font-weight: bold;
  text-transform: uppercase;
}}
.vb-motto {{
  font-size: 13pt;
  font-weight: bold;
}}
.vb-location-date {{
  font-size: 13pt;
  font-style: italic;
  margin-top: 4pt;
}}
.vb-line-short {{
  width: 100px;
  height: 1px;
  background-color: #000;
  margin: 4px auto 6px auto;
}}
.vb-line-medium {{
  width: 140px;
  height: 1px;
  background-color: #000;
  margin: 4px auto 6px auto;
}}
.vb-doc-number {{
  font-size: 12pt;
  margin-top: 4pt;
}}
.vb-doc-excerpt {{
  font-size: 11pt;
  font-style: italic;
  margin-top: 2pt;
}}
.vb-title-block {{
  text-align: center;
  margin: 18pt 0 14pt 0;
}}
.vb-title-type {{
  font-size: 15pt;
  font-weight: bold;
  text-transform: uppercase;
  margin-bottom: 4pt;
}}
.vb-subject {{
  font-size: 13pt;
  font-weight: bold;
}}
.vb-authority-title {{
  text-align: center;
  font-size: 14pt;
  font-weight: bold;
  text-transform: uppercase;
  margin: 12pt 0;
}}
.vb-recipient-block {{
  font-size: 13pt;
  margin-bottom: 14pt;
}}
.vb-content {{
  font-size: 13pt;
  text-align: justify;
  line-height: 1.4;
}}
.vb-content p {{
  margin: 4pt 0;
  text-indent: 28.35pt; /* Lùi đầu dòng 1cm */
}}
table.vb-table-bordered {{
  width: 100%;
  border-collapse: collapse;
  margin: 10pt 0;
}}
table.vb-table-bordered th, table.vb-table-bordered td {{
  border: 1px solid #000;
  padding: 6pt;
  font-size: 12pt;
}}
table.vb-table-bordered th {{
  background-color: #f2f2f2;
  text-align: center;
  font-weight: bold;
}}
.vb-recipients-title {{
  font-size: 12pt;
  font-weight: bold;
  font-style: italic;
}}
.vb-recipient-item {{
  font-size: 11pt;
  margin-left: 12pt;
}}
.vb-sign-role {{
  font-size: 13pt;
  font-weight: bold;
  text-transform: uppercase;
}}
.vb-sign-note {{
  font-size: 12pt;
  font-style: italic;
}}
.vb-sign-space {{
  height: 50pt;
}}
.vb-sign-name {{
  font-size: 13pt;
  font-weight: bold;
}}
</style>
</head>
<body>
<div class="Section1">
{html_content}
</div>
</body>
</html>"""
    return word_doc

def ask_chatbot(user_message, current_user=None):
    """
    Thuật toán phân tích ngữ nghĩa câu hỏi của chuyên viên,
    đối sánh các biểu mẫu liên quan trong kho lưu trữ và tạo phản hồi chuyên nghiệp.
    """
    if not user_message or not user_message.strip():
        return {
            'thanh_cong': False,
            'thong_bao': 'Vui lòng nhập câu hỏi hoặc yêu cầu cần trợ giúp.'
        }

    user_text = user_message.strip()
    norm = normalize_text(user_text)

    # Lấy toàn bộ mẫu trong kho lưu trữ
    db = get_db()
    templates = db.execute("""
        SELECT mau_id, ma_mau, ten_mau, loai_van_ban, linh_vuc,
               co_quan_ban_hanh, tham_quyen_ky, mo_ta, can_cu_phap_ly,
               tu_khoa, ten_tep, luot_xem, luot_tai
        FROM mau_van_ban
    """).fetchall()

    scored_templates = []

    # Danh mục từ khóa nhận diện loại văn bản
    loai_keywords = {
        'Tờ trình': ['tờ trình', 'to trinh', 'ttr', 'xin chủ trương', 'phê duyệt kinh phí', 'dự toán', 'xin tiền', 'mua sắm', 'sửa chữa', 'cơ sở vật chất', 'đề xuất kinh phí'],
        'Quyết định': ['quyết định', 'quyet dinh', 'qd', 'ban hành quy chế', 'khen thưởng', 'kỷ luật', 'thành lập', 'bổ nhiệm', 'tuyên dương', 'tiền thưởng'],
        'Công văn': ['công văn', 'cong van', 'cv', 'hướng dẫn', 'đôn đốc', 'nhắc nhở', 'phúc đáp', 'triển khai nhiệm vụ', 'nhiệm vụ năm học'],
        'Kế hoạch': ['kế hoạch', 'ke hoach', 'kh', 'tuyển sinh', 'lớp 10', 'tổ chức thi', 'kỳ thi', 'ôn tập', 'phương án'],
        'Thông báo': ['thông báo', 'thong bao', 'tb', 'nghỉ lễ', 'nghỉ tết', 'lịch trực', 'trực cơ quan', 'an toàn cơ quan', 'triệu tập'],
        'Biên bản': ['biên bản', 'bien ban', 'bb', 'cuộc họp', 'giao ban', 'thư ký', 'kết luận cuộc họp', 'họp sở'],
        'Báo cáo': ['báo cáo', 'bao cao', 'bc', 'chuyển đổi số', 'sơ kết', 'tổng kết', 'cntt', 'đánh giá', 'tổng hợp']
    }

    # Tính điểm đối sánh cho từng mẫu
    for t in templates:
        score = 0
        t_dict = dict(t)
        t_ten = normalize_text(t_dict['ten_mau'])
        t_tukhoa = normalize_text(t_dict.get('tu_khoa', ''))
        t_mota = normalize_text(t_dict.get('mo_ta', ''))
        t_loai = t_dict['loai_van_ban']

        # 1. Kiểm tra loại văn bản trực tiếp
        if t_loai.lower() in norm:
            score += 15

        # 2. Kiểm tra từ khóa đặc trưng của loại văn bản
        for kw in loai_keywords.get(t_loai, []):
            if kw in norm:
                score += 8

        # 3. Kiểm tra từ khóa riêng của mẫu văn bản
        keywords_list = [k.strip() for k in t_tukhoa.split(',') if k.strip()]
        for kw in keywords_list:
            norm_kw = normalize_text(kw)
            if norm_kw and norm_kw in norm:
                score += 10
            # Đối sánh từng từ đơn nếu câu hỏi dài
            elif len(norm_kw.split()) > 1 and any(word in norm for word in norm_kw.split() if len(word) > 2):
                score += 3

        # 4. Kiểm tra mã mẫu trực tiếp (BM-TT-01...)
        if t_dict['ma_mau'].lower() in norm:
            score += 30

        # 5. Đối sánh từ khóa trong tên mẫu
        for word in t_ten.split():
            if len(word) > 3 and word in norm:
                score += 2

        if score > 0:
            scored_templates.append((score, t_dict))

    # Sắp xếp các mẫu có điểm cao nhất lên đầu
    scored_templates.sort(key=lambda x: x[0], reverse=True)
    suggested = [item[1] for item in scored_templates[:4]]

    # Tạo câu trả lời thông minh của Trợ lý ảo
    user_name = current_user.get('ho_va_ten', 'đồng chí') if current_user else 'đồng chí'
    vai_tro = current_user.get('vai_tro', 'CHUYEN_VIEN') if current_user else 'CHUYEN_VIEN'

    # Xây dựng nội dung phản hồi văn bản
    greeting = f"Kính chào <b>{user_name}</b>! "
    body = ""
    suggested_chips = []

    if suggested:
        top_mau = suggested[0]
        loai_top = top_mau['loai_van_ban']

        body += f"Dựa trên yêu cầu của đồng chí, Trợ lý ảo đã đối soát trong <b>Kho lưu trữ biểu mẫu văn bản Sở GD&ĐT Đà Nẵng</b> và nhận thấy mẫu phù hợp nhất là: <b>{top_mau['ten_mau']}</b> (Mã số: <code>{top_mau['ma_mau']}</code>).<br><br>"
        
        # Hướng dẫn quy trình nghiệp vụ hành chính chuẩn Nghị định 30
        body += "<b>📋 Hướng dẫn nghiệp vụ và thẩm quyền ký duyệt:</b><br>"
        body += f"• <b>Loại văn bản:</b> {top_mau['loai_van_ban']} | <b>Lĩnh vực:</b> {top_mau['linh_vuc']}<br>"
        body += f"• <b>Thẩm quyền ký:</b> {top_mau['tham_quyen_ky']}<br>"
        body += f"• <b>Căn cứ pháp lý:</b> <i>{top_mau['can_cu_phap_ly']}</i><br>"
        body += f"• <b>Trường hợp áp dụng:</b> {top_mau['mo_ta']}<br><br>"
        body += "👉 Đồng chí có thể nhấn <b>\"👁️ Xem trước (Preview)\"</b> để kiểm tra thể thức trang A4 chuẩn hoặc nhấn <b>\"📥 Tải mẫu (.doc)\"</b> để tải file Word về soạn thảo trực tiếp."

        if len(suggested) > 1:
            body += f"<br><br><i>Ngoài ra, hệ thống gợi ý thêm <b>{len(suggested) - 1} mẫu liên quan</b> bên dưới để đồng chí tham khảo:</i>"

        suggested_chips = [
            f"Xem chi tiết {top_mau['ma_mau']}",
            "Quy trình trình ký lãnh đạo Sở",
            "Mẫu công văn gửi các trường",
            "Xem toàn bộ kho mẫu văn bản"
        ]
    else:
        # Nếu chưa khớp mẫu cụ thể, trả lời hướng dẫn tổng quan và gợi ý kho mẫu
        body += "Trợ lý ảo đã tiếp nhận yêu cầu của đồng chí. Để đảm bảo đúng quy định tại <b>Nghị định 30/2020/NĐ-CP</b> về công tác văn thư, đồng chí vui lòng cho biết rõ hơn loại văn bản cần soạn thảo (ví dụ: <i>Tờ trình xin kinh phí, Quyết định khen thưởng, Công văn chỉ đạo chuyên môn, Kế hoạch tuyển sinh, hay Thông báo trực cơ quan...</i>).<br><br>"
        body += "Đồng chí cũng có thể nhấn nút <b>\"Khám phá Kho mẫu văn bản\"</b> ở thanh công cụ phía trên để xem và tải về tất cả các biểu mẫu chuẩn hiện hành của Sở GD&ĐT."

        # Lấy 3 mẫu phổ biến nhất để chuyên viên tham khảo
        popular = db.execute("""
            SELECT mau_id, ma_mau, ten_mau, loai_van_ban, linh_vuc,
                   co_quan_ban_hanh, tham_quyen_ky, mo_ta, can_cu_phap_ly,
                   tu_khoa, ten_tep, luot_xem, luot_tai
            FROM mau_van_ban
            ORDER BY luot_xem DESC LIMIT 3
        """).fetchall()
        suggested = [dict(p) for p in popular]

        suggested_chips = [
            "Mẫu tờ trình xin kinh phí",
            "Mẫu quyết định khen thưởng thi đua",
            "Mẫu công văn hướng dẫn nhiệm vụ",
            "Mẫu kế hoạch tuyển sinh lớp 10"
        ]

    full_reply = greeting + body

    # Lưu lịch sử chat vào CSDL nếu người dùng đã đăng nhập
    user_id = current_user.get('nguoi_dung_id') if current_user else None
    try:
        mau_ids_json = json.dumps([m['mau_id'] for m in suggested])
        db.execute("""
            INSERT INTO lich_su_chat (nguoi_dung_id, cau_hoi, cau_tra_loi, mau_de_xuat_ids)
            VALUES (?, ?, ?, ?)
        """, (user_id, user_text, full_reply, mau_ids_json))
        db.commit()
    except Exception:
        pass

    return {
        'thanh_cong': True,
        'cau_tra_loi': full_reply,
        'mau_de_xuat': suggested,
        'tong_so_mau': len(suggested),
        'goi_y_tiep_theo': suggested_chips
    }
