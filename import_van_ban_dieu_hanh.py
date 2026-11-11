import os
import html
import shutil
import pypdf
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education_management.settings")
django.setup()

from chatbot.models import MauVanBan

SOURCE_DIR = r"C:\Users\Lenovo\Downloads\Văn bản Điều hành"
DEST_DIR = os.path.join(os.path.dirname(__file__), "media", "van_ban_dieu_hanh")
os.makedirs(DEST_DIR, exist_ok=True)

DOC_METADATA = [
    {
        "file_name": "1.pdf",
        "ma_mau": "128/KH-UBND",
        "ten_mau": "Kế hoạch thực hiện Dự án truyền thông “Xin chào Đà Nẵng - Global Greetings to Da Nang”",
        "loai_van_ban": "Kế hoạch",
        "linh_vuc": "Hành chính - Đối ngoại",
        "co_quan_ban_hanh": "ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG",
        "ngay_ban_hanh_str": "ngày 15 tháng 5 năm 2026",
        "is_scanned": False,
        "summary_paragraphs": [],
        "extra_keywords": "Xin chào Đà Nẵng Global Greetings to Da Nang dự án truyền thông hội nhập quốc tế đối ngoại",
    },
    {
        "file_name": "1752qdsgddt.pdf",
        "ma_mau": "1752/QĐ-SGDĐT",
        "ten_mau": "Quyết định phê duyệt chỉ tiêu tuyển sinh lớp 10 trường THPT tư thục năm học 2026 - 2027",
        "loai_van_ban": "Quyết định",
        "linh_vuc": "Giáo dục Trung học",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG",
        "ngay_ban_hanh_str": "ngày 12 tháng 8 năm 2026",
        "is_scanned": False,
        "summary_paragraphs": [],
        "extra_keywords": "chỉ tiêu tuyển sinh lớp 10 THPT tư thục năm học 2026 2027 đợt 3",
    },
    {
        "file_name": "19signed.pdf",
        "ma_mau": "19/2020/NĐ-CP",
        "ten_mau": "Nghị định kiểm tra, xử lý kỷ luật trong thi hành pháp luật về xử lý vi phạm hành chính",
        "loai_van_ban": "Nghị định",
        "linh_vuc": "Thanh tra - Pháp chế",
        "co_quan_ban_hanh": "CHÍNH PHỦ",
        "ngay_ban_hanh_str": "ngày 12 tháng 02 năm 2020",
        "is_scanned": True,
        "summary_paragraphs": [
            "Nghị định số 19/2020/NĐ-CP ngày 12/02/2020 của Chính phủ quy định về kiểm tra, xử lý kỷ luật trong thi hành pháp luật về xử lý vi phạm hành chính.",
            "Phạm vi điều chỉnh: Quy định thẩm quyền, trình tự, thủ tục kiểm tra tình hình thi hành pháp luật về xử lý vi phạm hành chính; xem xét, xử lý kỷ luật đối với người có thẩm quyền, cán bộ, công chức, viên chức có hành vi vi phạm trong thi hành pháp luật về xử lý vi phạm hành chính.",
            "Tài liệu gốc là bản quét (scan) có dấu đỏ chính thức gồm 24 trang, được hiển thị trực tiếp ngay bên dưới để đồng chí tra cứu toàn văn."
        ],
        "extra_keywords": "kiểm tra xử lý kỷ luật thi hành pháp luật xử lý vi phạm hành chính thanh tra công vụ cán bộ công chức viên chức",
    },
    {
        "file_name": "202024ttbgddtsigned.pdf",
        "ma_mau": "20/2024/TT-BGDĐT",
        "ten_mau": "Thông tư sửa đổi, bổ sung Quy chế tuyển sinh công dân Việt Nam đi học nước ngoài",
        "loai_van_ban": "Thông tư",
        "linh_vuc": "Hợp tác quốc tế",
        "co_quan_ban_hanh": "BỘ GIÁO DỤC VÀ ĐÀO TẠO",
        "ngay_ban_hanh_str": "ngày 15 tháng 11 năm 2024",
        "is_scanned": True,
        "summary_paragraphs": [
            "Thông tư số 20/2024/TT-BGDĐT của Bộ trưởng Bộ Giáo dục và Đào tạo sửa đổi, bổ sung một số điều của Quy chế tuyển sinh đi học nước ngoài ban hành kèm theo Thông tư số 06/2016/TT-BGDĐT (được sửa đổi, bổ sung bởi Thông tư số 18/2022/TT-BGDĐT).",
            "Nội dung trọng tâm: Quy định điều kiện dự tuyển, hồ sơ đăng ký, quy trình xét tuyển, cử công dân Việt Nam đi học tập ở nước ngoài theo học bổng ngân sách nhà nước và học bổng hiệp định.",
            "Bản PDF chính thức (bản scan có dấu) được tích hợp trực tiếp ở khung bên dưới để đồng chí xem chi tiết từng điều khoản."
        ],
        "extra_keywords": "quy chế tuyển sinh đi học nước ngoài du học học bổng hiệp định ngân sách nhà nước công dân Việt Nam",
    },
    {
        "file_name": "232024ttbgddtsigned.pdf",
        "ma_mau": "23/2024/TT-BGDĐT",
        "ten_mau": "Thông tư sửa đổi, bổ sung Quy định tiêu chuẩn cơ sở vật chất các trường mầm non, phổ thông",
        "loai_van_ban": "Thông tư",
        "linh_vuc": "Cơ sở vật chất",
        "co_quan_ban_hanh": "BỘ GIÁO DỤC VÀ ĐÀO TẠO",
        "ngay_ban_hanh_str": "ngày 20 tháng 12 năm 2024",
        "is_scanned": True,
        "summary_paragraphs": [
            "Thông tư số 23/2024/TT-BGDĐT của Bộ trưởng Bộ Giáo dục và Đào tạo sửa đổi, bổ sung một số điều của Quy định tiêu chuẩn cơ sở vật chất các trường mầm non, tiểu học, trung học cơ sở, trung học phổ thông và trường phổ thông có nhiều cấp học (ban hành kèm Thông tư 13/2020/TT-BGDĐT).",
            "Nội dung quy định: Tiêu chuẩn diện tích đất, quy mô nhóm lớp, khối phòng học tập, phòng chức năng, thư viện, hạ tầng kỹ thuật và thiết bị dạy học đáp ứng chuẩn quốc gia.",
            "Tài liệu PDF gốc có chữ ký và dấu ban hành của Bộ GD&ĐT được nhúng trực tiếp ngay bên dưới."
        ],
        "extra_keywords": "tiêu chuẩn cơ sở vật chất trường mầm non tiểu học trung học cơ sở trung học phổ thông nhiều cấp học phòng học thư viện diện tích đất chuẩn quốc gia",
    },
    {
        "file_name": "3666sgddtqlcl22072026signedsigned.pdf",
        "ma_mau": "3666/SGDĐT-QLCL",
        "ten_mau": "Công văn rà soát, cập nhật dữ liệu tuyển sinh đại học, cao đẳng ngành Giáo dục Mầm non",
        "loai_van_ban": "Công văn",
        "linh_vuc": "Khảo thí & ĐBCLGD",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG",
        "ngay_ban_hanh_str": "ngày 22 tháng 7 năm 2026",
        "is_scanned": False,
        "summary_paragraphs": [],
        "extra_keywords": "rà soát cập nhật dữ liệu tuyển sinh đại học cao đẳng Giáo dục Mầm non Công văn 4619 QLCL",
    },
    {
        "file_name": "qd-1656-ubndtp.pdf",
        "ma_mau": "1656/QĐ-UBND",
        "ten_mau": "Quyết định ban hành Quy chế xét tặng Giải thưởng 'Nhà giáo Đà Nẵng tiêu biểu'",
        "loai_van_ban": "Quyết định",
        "linh_vuc": "Tổ chức cán bộ",
        "co_quan_ban_hanh": "ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG",
        "ngay_ban_hanh_str": "ngày 08 tháng 8 năm 2023",
        "is_scanned": True,
        "summary_paragraphs": [
            "Quyết định số 1656/QĐ-UBND ngày 08/8/2023 của Chủ tịch UBND thành phố Đà Nẵng về việc ban hành Quy chế xét tặng Giải thưởng “Nhà giáo Đà Nẵng tiêu biểu” ngành Giáo dục và Đào tạo thành phố Đà Nẵng.",
            "Nội dung Quy chế: Quy định đối tượng, tiêu chuẩn, điều kiện, quy trình xét chọn, Hội đồng xét tặng, mức thưởng và tổ chức trao Giải thưởng tôn vinh các nhà giáo có nhiều đóng góp xuất sắc cho sự nghiệp giáo dục thành phố.",
            "Tệp PDF gốc đầy đủ 16 trang được hiển thị trực tiếp bên dưới."
        ],
        "extra_keywords": "Quy chế xét tặng Giải thưởng Nhà giáo Đà Nẵng tiêu biểu giáo viên xuất sắc thi đua khen thưởng",
    },
]

imported_count = 0

for item in DOC_METADATA:
    src_file = os.path.join(SOURCE_DIR, item["file_name"])
    dest_file = os.path.join(DEST_DIR, item["file_name"])

    if os.path.exists(src_file):
        shutil.copy2(src_file, dest_file)
        print(f"Copied {item['file_name']} -> {dest_file}")

    extracted_text = ""
    num_pages = 0
    if os.path.exists(dest_file):
        try:
            reader = pypdf.PdfReader(dest_file)
            num_pages = len(reader.pages)
            for page in reader.pages:
                txt = page.extract_text() or ""
                extracted_text += txt + "\n"
        except Exception as e:
            print(f"Lỗi extract text {item['file_name']}: {e}")

    extracted_text = extracted_text.strip()
    media_url = f"/media/van_ban_dieu_hanh/{item['file_name']}"

    if item["is_scanned"]:
        body_paragraphs = item["summary_paragraphs"]
        searchable_text = "\n".join([
            f"{item['co_quan_ban_hanh']} - {item['ma_mau']}",
            item["ten_mau"],
            item["extra_keywords"],
            *item["summary_paragraphs"],
        ])
    else:
        paragraphs = [p.strip() for p in extracted_text.split("\n\n") if p.strip()]
        if len(paragraphs) < 3:
            paragraphs = [p.strip() for p in extracted_text.split("\n") if len(p.strip()) > 30]
        filtered = [
            p for p in paragraphs
            if not p.upper().startswith((
                "CỘNG HÒA XÃ HỘI", "CỘNG HOÀ XÃ HỘI", "ĐỘC LẬP - TỰ DO",
                "ỦY BAN NHÂN DÂN", "SỞ GIÁO DỤC", "ĐÀ NẴNG, NGÀY", "SỐ:"
            ))
        ]
        body_paragraphs = (filtered or paragraphs)[:15] or [item["ten_mau"]]
        searchable_text = f"{item['ten_mau']}\n{item['extra_keywords']}\n{extracted_text}"

    content_html_paragraphs = "".join(
        f"<p>{html.escape(p)}</p>\n" for p in body_paragraphs
    )

    noi_dung_html = f"""
<div class="vb-container">
  <!-- Thanh công cụ tệp đính kèm -->
  <div style="margin-bottom: 20px; padding: 12px 16px; background: #e0f2fe; border: 1px solid #7dd3fc; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
    <div style="display: flex; align-items: center; gap: 8px; font-size: 13px; color: #0369a1;">
      <span style="font-size: 18px;">📄</span>
      <span>Tệp tài liệu gốc: <b>{html.escape(item['file_name'])}</b> ({num_pages} trang)</span>
    </div>
    <div style="display: flex; gap: 8px;">
      <a href="{media_url}" target="_blank" class="btn btn-sm btn-primary" style="display: inline-flex; align-items: center; gap: 4px; padding: 5px 12px; background: #0284c7; color: #fff; text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: 600;">
        <span>👁️ Xem PDF gốc</span> ↗
      </a>
      <a href="{media_url}" download class="btn btn-sm" style="display: inline-flex; align-items: center; gap: 4px; padding: 5px 12px; background: #f1f5f9; color: #334155; text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: 600; border: 1px solid #cbd5e1;">
        <span>📥 Tải PDF</span>
      </a>
    </div>
  </div>

  <!-- Bố cục trang in A4 chuẩn Nghị định 30/2020/NĐ-CP -->
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-name">{html.escape(item['co_quan_ban_hanh'])}</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: {html.escape(item['ma_mau'])}</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">{html.escape(item['ngay_ban_hanh_str'])}</div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">{html.escape(item['loai_van_ban'].upper())}</div>
    <div class="vb-subject">{html.escape(item['ten_mau'])}</div>
  </div>

  <div class="vb-content" style="margin-top: 18px;">
    {content_html_paragraphs}
  </div>

  <div class="pdf-preview-embed" style="margin-top: 22px; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; background: #f8fafc;">
    <div style="padding: 8px 14px; background: #1e293b; color: #f8fafc; font-size: 12px; font-weight: 600; display: flex; justify-content: space-between; align-items: center;">
      <span>📑 XEM TRỰC TIẾP BẢN PDF ĐÍNH KÈM ({num_pages} trang)</span>
      <a href="{media_url}" target="_blank" style="color: #38bdf8; text-decoration: none;">Mở toàn màn hình ↗</a>
    </div>
    <iframe src="{media_url}" style="width: 100%; height: 760px; border: none; display: block;" title="Xem trước PDF"></iframe>
  </div>

  <table class="vb-footer-table" style="margin-top: 28px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- Các cơ quan, đơn vị trực thuộc;</div>
        <div class="vb-recipient-item">- Ban Giám đốc Sở;</div>
        <div class="vb-recipient-item">- Lưu: VT, {html.escape(item['linh_vuc'])}.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">THẨM QUYỀN BAN HÀNH</div>
        <div style="margin: 12px 0; padding: 6px 14px; display: inline-block; border: 2px dashed #16a34a; border-radius: 6px; background: #f0fdf4; color: #166534; font-size: 11pt; font-weight: bold; text-align: left;">
          🔒 [ĐÃ KÝ SỐ ĐIỆN TỬ]<br>
          <span style="font-size: 9.5pt; font-weight: normal; color: #15803d;">Cơ quan: {html.escape(item['co_quan_ban_hanh'])}</span>
        </div>
      </td>
    </tr>
  </table>
</div>
"""

    obj, created = MauVanBan.objects.update_or_create(
        ma_mau=item["ma_mau"],
        defaults={
            "ten_mau": item["ten_mau"],
            "loai_van_ban": item["loai_van_ban"],
            "linh_vuc": item["linh_vuc"],
            "co_quan_ban_hanh": item["co_quan_ban_hanh"],
            "noi_dung_html": noi_dung_html,
            "noi_dung_text": searchable_text[:10000],
        }
    )
    imported_count += 1
    print(f"[OK] Đã nạp vào kho: [{obj.ma_mau}] {obj.ten_mau[:50]}... (Tạo mới: {created})")

print(f"\n✅ Hoàn tất nạp {imported_count} văn bản điều hành vào kho lưu trữ! Tổng số văn bản trong kho: {MauVanBan.objects.count()}")
