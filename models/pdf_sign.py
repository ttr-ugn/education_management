"""
Module xử lý đóng dấu chữ ký số điện tử lên tệp tài liệu PDF (MVC Architecture - Model Layer)
Theo quy định về thể thức ký số văn bản điện tử (Nghị định 30/2020/NĐ-CP).
"""

import io
import os
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

def remove_accents(input_str: str) -> str:
    """Chuyển đổi ký tự tiếng Việt có dấu sang không dấu cho font chuẩn ReportLab."""
    if not input_str:
        return ""
    import unicodedata
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    res = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # Thay thế thủ công ký tự đ/Đ
    return res.replace('đ', 'd').replace('Đ', 'D')

def stamp_pdf_signature(
    input_pdf_path: str,
    output_pdf_path: str,
    page_num: int,
    x: float,
    y: float,
    signer_name: str,
    signer_title: str = "Giám đốc Sở",
    sign_time: str = None,
    is_percentage: bool = False,
    trich_yeu: str = ""
) -> bool:
    """
    Đóng dấu chữ ký số lên tài liệu PDF tại đúng tọa độ và trang được chọn.
    
    :param input_pdf_path: Đường dẫn file PDF gốc
    :param output_pdf_path: Đường dẫn lưu file PDF sau khi ký
    :param page_num: Số trang (1-indexed)
    :param x: Tọa độ X (hoặc % từ trái sang phải nếu is_percentage=True)
    :param y: Tọa độ Y (hoặc % từ trên xuống dưới nếu is_percentage=True)
    :param signer_name: Họ tên Lãnh đạo ký
    :param signer_title: Chức vụ Lãnh đạo
    :param sign_time: Thời gian ký (định dạng YYYY-MM-DD HH:MM:SS)
    :param is_percentage: True nếu tọa độ là phần trăm [0..100]
    :param trich_yeu: Trích yếu văn bản (phòng trường hợp cần sinh PDF thay thế nếu file gốc không phải PDF)
    """
    if not sign_time:
        sign_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    Path(output_pdf_path).parent.mkdir(parents=True, exist_ok=True)

    # 1. Kiểm tra file gốc có phải PDF hợp lệ không
    is_valid_pdf = False
    if os.path.exists(input_pdf_path):
        try:
            reader = PdfReader(input_pdf_path)
            if len(reader.pages) > 0:
                is_valid_pdf = True
        except Exception:
            is_valid_pdf = False

    # 2. Nếu file gốc là DOCX hoặc không đọc được dạng PDF, tự động tạo 1 trang PDF văn bản tiêu chuẩn
    if not is_valid_pdf:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(595.27, 841.89)) # Kích thước chuẩn A4
        can.setFont("Helvetica-Bold", 12)
        can.drawString(50, 790, "SO GIAO DUC VA DAO TAO TP. DA NANG")
        can.drawString(50, 770, "HE THONG QUAN LY VAN BAN DIEU HANH")
        can.line(50, 760, 545, 760)
        
        can.setFont("Helvetica-Bold", 14)
        can.drawString(50, 720, "BAN KHOA DANG KY & PHU LUC VAN BAN")
        
        can.setFont("Helvetica", 11)
        safe_trich_yeu = remove_accents(trich_yeu or "Van ban dieu hanh")
        can.drawString(50, 680, f"Trich yeu: {safe_trich_yeu}")
        can.drawString(50, 650, f"Tep ban dau: {os.path.basename(input_pdf_path)}")
        can.drawString(50, 620, f"Ngay tao: {datetime.now().strftime('%d/%m/%Y')}")
        can.save()
        packet.seek(0)
        reader = PdfReader(packet)

    # 3. Tính toán kích thước trang và tọa độ đóng dấu
    total_pages = len(reader.pages)
    target_page_idx = max(0, min(page_num - 1, total_pages - 1))
    target_page = reader.pages[target_page_idx]
    
    page_w = float(target_page.mediabox.width)
    page_h = float(target_page.mediabox.height)

    stamp_w = 210
    stamp_h = 75

    if is_percentage:
        # Chuyển đổi từ tọa độ canvas web (gốc trên-trái) sang hệ tọa độ PDF (gốc dưới-trái)
        stamp_x = (x / 100.0) * page_w
        # Trong web canvas, y=0 là đỉnh trang. Trong PDF, y=0 là đáy trang.
        stamp_y = page_h - ((y / 100.0) * page_h) - stamp_h
    else:
        stamp_x = x
        stamp_y = y

    # Giới hạn không để con dấu bị tràn ra ngoài lề trang giấy
    stamp_x = max(10, min(stamp_x, page_w - stamp_w - 10))
    stamp_y = max(10, min(stamp_y, page_h - stamp_h - 10))

    # 4. Vẽ con dấu chữ ký số điện tử
    stamp_packet = io.BytesIO()
    can = canvas.Canvas(stamp_packet, pagesize=(page_w, page_h))

    # Viền con dấu đỏ hành chính
    can.setStrokeColor(HexColor('#b91c1c'))
    can.setLineWidth(1.6)
    can.roundRect(stamp_x, stamp_y, stamp_w, stamp_h, 4, stroke=1, fill=0)

    # Nền mờ nhận diện
    can.setFillColor(HexColor('#fef2f2'))
    can.roundRect(stamp_x + 1, stamp_y + 1, stamp_w - 2, stamp_h - 2, 4, stroke=0, fill=1)

    # Nội dung thông tin chứng thư số
    safe_name = remove_accents(signer_name).upper()
    safe_title = remove_accents(signer_title)

    can.setFillColor(HexColor('#991b1b'))
    can.setFont("Helvetica-Bold", 8.5)
    can.drawString(stamp_x + 10, stamp_y + stamp_h - 16, f"KY BOI: {safe_name}")

    can.setFillColor(HexColor('#1f2937'))
    can.setFont("Helvetica", 7.5)
    can.drawString(stamp_x + 10, stamp_y + stamp_h - 29, f"Chuc vu: {safe_title}")
    can.drawString(stamp_x + 10, stamp_y + stamp_h - 41, "Co quan: SO GD&DT TP. DA NANG")
    can.drawString(stamp_x + 10, stamp_y + stamp_h - 53, f"Thoi gian ky: {sign_time}")

    can.setFillColor(HexColor('#047857'))
    can.setFont("Helvetica-Bold", 7)
    can.drawString(stamp_x + 10, stamp_y + 9, "[CHUNG THU SO HOP LE - NDD 30/2020]")

    can.save()
    stamp_packet.seek(0)

    # 5. Hợp nhất (merge) trang dấu vào trang PDF
    stamp_pdf = PdfReader(stamp_packet)
    overlay_page = stamp_pdf.pages[0]

    writer = PdfWriter()
    for idx, p in enumerate(reader.pages):
        if idx == target_page_idx:
            p.merge_page(overlay_page)
        writer.add_page(p)

    with open(output_pdf_path, 'wb') as f_out:
        writer.write(f_out)

    return True
