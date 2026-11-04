import sys
import sqlite3
from pathlib import Path

# Đảm bảo mã hóa console trên Windows không bị lỗi ký tự tiếng Việt
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config

DANH_SACH_MAU = [
    {
        "ma_mau": "BM-TT-01",
        "ten_mau": "Tờ trình về việc đề nghị phê duyệt dự toán kinh phí tổ chức hoạt động chuyên môn",
        "loai_van_ban": "Tờ trình",
        "linh_vuc": "Kế hoạch - Tài chính",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "Trưởng phòng chuyên môn trình Giám đốc Sở",
        "mo_ta": "Sử dụng khi chuyên viên các phòng chuyên môn cần xin chủ trương và phê duyệt dự toán kinh phí tổ chức tập huấn, bồi dưỡng giáo viên, hội thi học sinh giỏi, hội thảo khoa học.",
        "can_cu_phap_ly": "Nghị định số 30/2020/NĐ-CP; Thông tư số 22/2019/TT-BGDĐT; Quyết định phân bổ ngân sách hàng năm của UBND TP. Đà Nẵng.",
        "tu_khoa": "tờ trình, kinh phí, dự toán, xin tiền, giáo viên dạy giỏi, hội thi, chuyên môn, phê duyệt kinh phí, tài chính, bồi dưỡng, tập huấn",
        "ten_tep": "BM-TT-01_To_trinh_du_toan_kinh_phi.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: ... /TTr-[VIẾT TẮT PHÒNG BAN]

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

TỜ TRÌNH
Về việc đề nghị phê duyệt dự toán kinh phí tổ chức hoạt động chuyên môn ngành Giáo dục và Đào tạo năm 2026

Kính gửi: Giám đốc Sở Giáo dục và Đào tạo thành phố Đà Nẵng.

Căn cứ Quyết định số .../QĐ-UBND ngày ... tháng ... năm 2025 của Ủy ban nhân dân thành phố Đà Nẵng về việc giao dự toán thu, chi ngân sách nhà nước năm 2026;
Căn cứ Kế hoạch số .../KH-SGDĐT ngày ... tháng ... năm 2026 của Sở Giáo dục và Đào tạo về nhiệm vụ trọng tâm năm học 2025 - 2026;
Căn cứ nhu cầu thực tế và kế hoạch triển khai hoạt động chuyên môn của Phòng [Tên phòng chuyên môn],

Phòng [Tên phòng chuyên môn] kính trình Giám đốc Sở xem xét, phê duyệt dự toán kinh phí tổ chức [Tên hoạt động/hội thảo/hội thi] với các nội dung cụ thể như sau:

I. MỤC ĐÍCH, YÊU CẦU
1. Mục đích: [Nêu rõ mục tiêu cần đạt được của hoạt động].
2. Yêu cầu: Tổ chức nghiêm túc, thiết thực, hiệu quả, tiết kiệm, đúng quy định tài chính hiện hành.

II. THỜI GIAN, ĐỊA ĐIỂM VÀ ĐỐI TƯỢNG THAM GIA
1. Thời gian: Từ ngày .../.../2026 đến ngày .../.../2026.
2. Địa điểm: [Hội trường Sở / Trường THPT ...].
3. Thành phần tham dự: Dự kiến khoảng [...] đại biểu, cán bộ quản lý và giáo viên.

III. DỰ TOÁN KINH PHÍ VÀ NGUỒN KINH PHÍ
1. Tổng kinh phí đề nghị: ... VNĐ (Bằng chữ: ... đồng chẵn).
Trong đó chi tiết:
- Chi thuê hội trường, thiết bị âm thanh, máy chiếu: ... VNĐ
- Chi in ấn tài liệu, văn phòng phẩm: ... VNĐ
- Chi bồi dưỡng báo cáo viên, ban tổ chức: ... VNĐ
- Chi nước uống, giải khát giữa giờ: ... VNĐ
2. Nguồn kinh phí: Nguồn kinh phí chi thường xuyên sự nghiệp giáo dục năm 2026 được Sở giao.

Kính trình Giám đốc Sở xem xét, phê duyệt để đơn vị triển khai thực hiện./.

Nơi nhận:
- Như trên;
- Phòng Kế hoạch - Tài chính (để phối hợp);
- Lưu: VT, [Tên phòng chuyên môn].

TRƯỞNG PHÒNG
(Ký, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/TTr-[PHÒNG CHUYÊN MÔN]</div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">TỜ TRÌNH</div>
    <div class="vb-subject">Về việc đề nghị phê duyệt dự toán kinh phí tổ chức [Tên hoạt động chuyên môn] năm 2026</div>
  </div>

  <div class="vb-recipient-block">
    <b>Kính gửi:</b> Giám đốc Sở Giáo dục và Đào tạo thành phố Đà Nẵng.
  </div>

  <div class="vb-content">
    <p><i>Căn cứ Quyết định số .../QĐ-UBND ngày ... tháng ... năm 2025 của Ủy ban nhân dân thành phố Đà Nẵng về việc giao dự toán ngân sách nhà nước năm 2026;</i></p>
    <p><i>Căn cứ Kế hoạch năm học 2025 - 2026 của Sở Giáo dục và Đào tạo thành phố Đà Nẵng;</i></p>
    <p><i>Xét đề nghị của Phòng [Tên phòng chuyên môn trình] về việc triển khai công tác chuyên môn;</i></p>
    <p>Phòng [Tên phòng chuyên môn] kính trình Giám đốc Sở Giáo dục và Đào tạo xem xét, phê duyệt kế hoạch và dự toán kinh phí tổ chức hoạt động với các nội dung chi tiết sau:</p>

    <p><b>I. MỤC ĐÍCH VÀ YÊU CẦU</b></p>
    <p>1. Mục đích: [Nêu rõ mục tiêu nâng cao năng lực chuyên môn, đổi mới phương pháp giảng dạy, bồi dưỡng học sinh...]</p>
    <p>2. Yêu cầu: Đảm bảo thiết thực, tiết kiệm, hiệu quả, tuân thủ đúng chế độ chi tiêu tài chính công hiện hành.</p>

    <p><b>II. QUY MÔ, THỜI GIAN VÀ ĐỊA ĐIỂM</b></p>
    <p>1. Thời gian: Dự kiến diễn ra từ ngày .../.../2026 đến ngày .../.../2026.</p>
    <p>2. Địa điểm: [Hội trường tầng 3 Sở GD&ĐT / Trường THPT chuyên Lê Quý Đôn].</p>
    <p>3. Thành phần: Cán bộ quản lý, giáo viên cốt cán các trường trực thuộc (dự kiến: ... đại biểu).</p>

    <p><b>III. DỰ TOÁN KINH PHÍ THỰC HIỆN</b></p>
    <p>Tổng dự toán kinh phí đề nghị cấp: <b>... VNĐ</b> <i>(Bằng chữ: ... đồng chẵn).</i></p>
    <table class="vb-table-bordered">
      <thead>
        <tr>
          <th>STT</th>
          <th>Nội dung chi</th>
          <th>Đơn vị tính</th>
          <th>Số lượng</th>
          <th>Đơn giá (VNĐ)</th>
          <th>Thành tiền (VNĐ)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align: center;">1</td>
          <td>Chi in ấn tài liệu bồi dưỡng, văn phòng phẩm</td>
          <td style="text-align: center;">Bộ</td>
          <td style="text-align: center;">...</td>
          <td style="text-align: right;">...</td>
          <td style="text-align: right;">...</td>
        </tr>
        <tr>
          <td style="text-align: center;">2</td>
          <td>Thù lao báo cáo viên / Chuyên gia</td>
          <td style="text-align: center;">Buổi</td>
          <td style="text-align: center;">...</td>
          <td style="text-align: right;">...</td>
          <td style="text-align: right;">...</td>
        </tr>
        <tr>
          <td style="text-align: center;">3</td>
          <td>Nước uống, phục vụ hội nghị</td>
          <td style="text-align: center;">Đại biểu</td>
          <td style="text-align: center;">...</td>
          <td style="text-align: right;">...</td>
          <td style="text-align: right;">...</td>
        </tr>
        <tr>
          <td colspan="5" style="text-align: right; font-weight: bold;">TỔNG CỘNG:</td>
          <td style="text-align: right; font-weight: bold;">...</td>
        </tr>
      </tbody>
    </table>
    <p>Nguồn kinh phí: Trích từ nguồn kinh phí sự nghiệp giáo dục năm 2026 được UBND thành phố giao.</p>

    <p>Kính trình Giám đốc Sở xem xét, ký duyệt để phòng có căn cứ phối hợp với Phòng Kế hoạch - Tài chính triển khai thực hiện./.</p>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title"><b><i>Nơi nhận:</i></b></div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Phòng KHTC (phối hợp);</div>
        <div class="vb-recipient-item">- Lưu: VT, [Tên phòng].</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>TRƯỞNG PHÒNG [TÊN PHÒNG]</b></div>
        <div class="vb-sign-note"><i>(Ký, ghi rõ họ tên)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Trưởng phòng]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    },
    {
        "ma_mau": "BM-TT-02",
        "ten_mau": "Tờ trình xin chủ trương đầu tư nâng cấp, cải tạo cơ sở vật chất và phòng máy tính",
        "loai_van_ban": "Tờ trình",
        "linh_vuc": "Kế hoạch - Tài chính",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "Trưởng phòng Kế hoạch - Tài chính",
        "mo_ta": "Sử dụng khi cần xin chủ trương từ Ban Giám đốc Sở hoặc UBND thành phố để sửa chữa, cải tạo phòng máy vi tính, hệ thống mạng internet, thư viện hoặc cơ sở vật chất trường học.",
        "can_cu_phap_ly": "Luật Đầu tư công 2019; Luật Ngân sách nhà nước 2015; Đề án chuyển đổi số ngành Giáo dục và Đào tạo TP. Đà Nẵng.",
        "tu_khoa": "tờ trình, cơ sở vật chất, phòng máy, sửa chữa, nâng cấp, đầu tư, mua sắm thiết bị, phòng học, hạ tầng mạng, máy vi tính, phòng tin học",
        "ten_tep": "BM-TT-02_To_trinh_sua_chua_co_so_vat_chat.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: ... /TTr-KHTC

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

TỜ TRÌNH
Về việc xin chủ trương đầu tư, nâng cấp hệ thống phòng máy vi tính phục vụ giảng dạy tin học năm học 2026 - 2027

Kính gửi: Giám đốc Sở Giáo dục và Đào tạo thành phố Đà Nẵng.

Căn cứ hiện trạng cơ sở vật chất và báo cáo đề xuất của các trường THPT trực thuộc Sở về nhu cầu phòng máy vi tính phục vụ Chương trình GDPT 2018;
Phòng Kế hoạch - Tài chính kính trình Giám đốc Sở xem xét, phê duyệt chủ trương đầu tư nâng cấp phòng máy vi tính với các nội dung trọng tâm sau:
1. Đơn vị thụ hưởng: Các trường THPT có hệ thống phòng máy xuống cấp (danh sách đính kèm).
2. Quy mô đầu tư: Mua mới ... bộ máy tính cấu hình chuẩn giáo dục, nâng cấp đường truyền internet cáp quang.
3. Tổng mức đầu tư dự kiến: ... VNĐ.
4. Thời gian hoàn thành: Trước ngày 30/8/2026 sẵn sàng cho năm học mới.
Kính trình Giám đốc Sở phê duyệt chủ trương./.

TRƯỞNG PHÒNG KẾ HOẠCH - TÀI CHÍNH
(Ký, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/TTr-KHTC</div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">TỜ TRÌNH</div>
    <div class="vb-subject">Về việc xin chủ trương đầu tư, nâng cấp hệ thống phòng máy tính và hạ tầng mạng giáo dục năm 2026</div>
  </div>

  <div class="vb-recipient-block">
    <b>Kính gửi:</b> Giám đốc Sở Giáo dục và Đào tạo thành phố Đà Nẵng.
  </div>

  <div class="vb-content">
    <p><i>Căn cứ Luật Quản lý, sử dụng tài sản công số 15/2017/QH14;</i></p>
    <p><i>Căn cứ Quyết định về chuyển đổi số ngành Giáo dục và Đào tạo thành phố Đà Nẵng giai đoạn 2025 - 2030;</i></p>
    <p><i>Căn cứ kết quả kiểm tra thực tế cơ sở vật chất tại các đơn vị trực thuộc Sở tháng .../2026;</i></p>
    <p>Phòng Kế hoạch - Tài chính kính báo cáo và xin ý kiến chỉ đạo của Giám đốc Sở về việc nâng cấp phòng học bộ môn Tin học phục vụ dạy và học theo chương trình mới:</p>
    <p><b>1. Sự cần thiết đầu tư:</b> Hiện tại các phòng máy tính tại ... trường THPT đã sử dụng trên 8 năm, linh kiện thường xuyên hư hỏng, không đáp ứng được yêu cầu thực hành lập trình và ứng dụng trí tuệ nhân tạo (AI).</p>
    <p><b>2. Quy mô dự kiến:</b> Trang bị bổ sung ... phòng máy (mỗi phòng 25 máy tính cấu hình tiêu chuẩn), 01 máy chủ quản trị mạng và thiết bị lưu điện UPS.</p>
    <p><b>3. Tổng kinh phí dự toán:</b> Khoảng ... VNĐ (Bằng chữ: ...).</p>
    <p>Kính trình Giám đốc Sở xem xét, phê duyệt chủ trương để phòng phối hợp tiến hành các thủ tục đấu thầu theo luật định./.</p>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title"><b><i>Nơi nhận:</i></b></div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Phòng GDTrH (để phối hợp);</div>
        <div class="vb-recipient-item">- Lưu: VT, KHTC.</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>TRƯỞNG PHÒNG KẾ HOẠCH - TÀI CHÍNH</b></div>
        <div class="vb-sign-note"><i>(Ký, ghi rõ họ tên)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Trưởng phòng]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    },
    {
        "ma_mau": "BM-QD-01",
        "ten_mau": "Quyết định về việc khen thưởng tập thể và cá nhân có thành tích xuất sắc trong công tác bồi dưỡng học sinh giỏi",
        "loai_van_ban": "Quyết định",
        "linh_vuc": "Tổ chức cán bộ",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "Giám đốc Sở Giáo dục và Đào tạo",
        "mo_ta": "Sử dụng khi ban hành Quyết định tặng Giấy khen kèm theo mức tiền thưởng cho các giáo viên bồi dưỡng và học sinh đạt giải cao trong các kỳ thi học sinh giỏi các cấp.",
        "can_cu_phap_ly": "Luật Thi đua, Khen thưởng số 06/2022/QH15; Nghị định số 98/2023/NĐ-CP; Quy chế khen thưởng ngành GD&ĐT TP. Đà Nẵng.",
        "tu_khoa": "quyết định, khen thưởng, học sinh giỏi, giấy khen, tiền thưởng, thi đua, tuyên dương, thành tích, giáo viên giỏi, hsg quốc gia",
        "ten_tep": "BM-QD-01_Quyet_dinh_khen_thuong_HSG.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: ... /QĐ-SGDĐT

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

QUYẾT ĐỊNH
Về việc khen thưởng giáo viên và học sinh đạt thành tích xuất sắc trong Kỳ thi chọn học sinh giỏi năm học 2025 - 2026

GIÁM ĐỐC SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG

Căn cứ Luật Thi đua, khen thưởng ngày 15 tháng 6 năm 2022;
Căn cứ Quyết định số .../QĐ-UBND của UBND thành phố Đà Nẵng quy định chức năng, nhiệm vụ, quyền hạn và cơ cấu tổ chức của Sở Giáo dục và Đào tạo;
Căn cứ kết quả Kỳ thi chọn học sinh giỏi cấp quốc gia năm học 2025 - 2026;
Theo đề nghị của Trưởng phòng Tổ chức cán bộ và Trưởng phòng Giáo dục Trung học.

QUYẾT ĐỊNH:

Điều 1. Tặng Giấy khen của Giám đốc Sở Giáo dục và Đào tạo kèm theo tiền thưởng cho ... tập thể và ... cá nhân (danh sách đính kèm) đã đạt thành tích xuất sắc trong công tác bồi dưỡng và tham gia Kỳ thi chọn học sinh giỏi.
Điều 2. Tiền thưởng được trích từ Quỹ thi đua khen thưởng của Sở GD&ĐT theo quy định hiện hành. Mức chi thưởng cụ thể:
- Giải Nhất: ... VNĐ / giải.
- Giải Nhì: ... VNĐ / giải.
- Giải Ba: ... VNĐ / giải.
Điều 3. Chánh Văn phòng Sở, Trưởng các phòng: Tổ chức cán bộ, Kế hoạch - Tài chính, Giáo dục Trung học, Thủ trưởng các đơn vị có liên quan và các tập thể, cá nhân có tên tại Điều 1 chịu trách nhiệm thi hành Quyết định này./.

Nơi nhận:
- Như Điều 3;
- Ban Giám đốc Sở;
- Lưu: VT, TCCB.

GIÁM ĐỐC
(Ký, đóng dấu, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/QĐ-SGDĐT</div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">QUYẾT ĐỊNH</div>
    <div class="vb-subject">Về việc khen thưởng các tập thể và cá nhân có thành tích xuất sắc trong công tác bồi dưỡng học sinh giỏi năm học 2025 - 2026</div>
  </div>

  <div class="vb-authority-title"><b>GIÁM ĐỐC SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG</b></div>

  <div class="vb-content">
    <p><i>Căn cứ Luật Thi đua, khen thưởng số 06/2022/QH15 ngày 15 tháng 6 năm 2022;</i></p>
    <p><i>Căn cứ Quyết định số .../2021/QĐ-UBND của Ủy ban nhân dân thành phố Đà Nẵng quy định chức năng, nhiệm vụ, quyền hạn và cơ cấu tổ chức của Sở Giáo dục và Đào tạo thành phố Đà Nẵng;</i></p>
    <p><i>Căn cứ Quyết định số .../QĐ-BGDĐT của Bộ Giáo dục và Đào tạo về việc công nhận kết quả Kỳ thi chọn học sinh giỏi quốc gia năm học 2025 - 2026;</i></p>
    <p><i>Theo đề nghị của Trưởng phòng Tổ chức cán bộ và Trưởng phòng Giáo dục Trung học,</i></p>

    <div style="text-align: center; font-weight: bold; margin: 15px 0;">QUYẾT ĐỊNH:</div>

    <p><b>Điều 1.</b> Tặng Giấy khen của Giám đốc Sở Giáo dục và Đào tạo thành phố Đà Nẵng kèm theo tiền thưởng cho <b>... tập thể</b> và <b>... giáo viên, học sinh</b> đạt thành tích xuất sắc (Có danh sách chi tiết đính kèm theo Quyết định này).</p>

    <p><b>Điều 2.</b> Mức tiền thưởng thực hiện theo Nghị định số 98/2023/NĐ-CP của Chính phủ. Tiền thưởng được trích từ nguồn Quỹ khen thưởng sự nghiệp giáo dục năm 2026 của Sở GD&ĐT.</p>

    <p><b>Điều 3.</b> Chánh Văn phòng Sở, Trưởng phòng Kế hoạch - Tài chính, Trưởng phòng Tổ chức cán bộ, Trưởng phòng Giáo dục Trung học, Hiệu trưởng các trường có liên quan và các cá nhân có tên tại Điều 1 chịu trách nhiệm thi hành Quyết định này kể từ ngày ký./.</p>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title"><b><i>Nơi nhận:</i></b></div>
        <div class="vb-recipient-item">- Như Điều 3;</div>
        <div class="vb-recipient-item">- UBND thành phố (để b/c);</div>
        <div class="vb-recipient-item">- Ban Giám đốc Sở;</div>
        <div class="vb-recipient-item">- Lưu: VT, TCCB.</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>GIÁM ĐỐC</b></div>
        <div class="vb-sign-note"><i>(Ký tên, đóng dấu)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Giám đốc Sở]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    },
    {
        "ma_mau": "BM-QD-02",
        "ten_mau": "Quyết định ban hành Quy chế làm việc của cơ quan Sở Giáo dục và Đào tạo",
        "loai_van_ban": "Quyết định",
        "linh_vuc": "Hành chính - Tổng hợp",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "Giám đốc Sở Giáo dục và Đào tạo",
        "mo_ta": "Mẫu quyết định quy phạm nội bộ ban hành các quy chế, quy trình phối hợp công tác, phân công nhiệm vụ và chế độ thông tin báo cáo giữa các phòng chuyên môn.",
        "can_cu_phap_ly": "Nghị định số 30/2020/NĐ-CP; Luật Cán bộ, công chức; Quyết định phân cấp quản lý của UBND TP. Đà Nẵng.",
        "tu_khoa": "quyết định, quy chế làm việc, nội bộ, nguyên tắc làm việc, văn phòng sở, điều hành, phân công nhiệm vụ, chế độ báo cáo",
        "ten_tep": "BM-QD-02_Quyet_dinh_ban_hanh_quy_che.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: ... /QĐ-SGDĐT

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

QUYẾT ĐỊNH
Ban hành Quy chế làm việc của cơ quan Sở Giáo dục và Đào tạo thành phố Đà Nẵng

GIÁM ĐỐC SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG

Căn cứ Luật Tổ chức chính quyền địa phương ngày 19/6/2015;
Căn cứ Nghị định số 30/2020/NĐ-CP của Chính phủ về công tác văn thư;
Theo đề nghị của Chánh Văn phòng Sở Giáo dục và Đào tạo.

QUYẾT ĐỊNH:
Điều 1. Ban hành kèm theo Quyết định này "Quy chế làm việc của cơ quan Sở Giáo dục và Đào tạo thành phố Đà Nẵng".
Điều 2. Quyết định này có hiệu lực kể từ ngày ký và thay thế Quyết định số ... trước đây.
Điều 3. Toàn thể công chức, người lao động thuộc cơ quan Sở GD&ĐT chịu trách nhiệm thi hành Quyết định này./.

GIÁM ĐỐC
(Ký, đóng dấu, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/QĐ-SGDĐT</div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">QUYẾT ĐỊNH</div>
    <div class="vb-subject">Ban hành Quy chế làm việc của cơ quan Sở Giáo dục và Đào tạo thành phố Đà Nẵng</div>
  </div>

  <div class="vb-authority-title"><b>GIÁM ĐỐC SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG</b></div>

  <div class="vb-content">
    <p><i>Căn cứ Quyết định của UBND thành phố Đà Nẵng quy định chức năng, nhiệm vụ, quyền hạn của Sở Giáo dục và Đào tạo;</i></p>
    <p><i>Xét đề nghị của Chánh Văn phòng Sở Giáo dục và Đào tạo,</i></p>

    <div style="text-align: center; font-weight: bold; margin: 15px 0;">QUYẾT ĐỊNH:</div>

    <p><b>Điều 1.</b> Ban hành kèm theo Quyết định này Quy chế làm việc nội bộ của cơ quan Sở Giáo dục và Đào tạo thành phố Đà Nẵng.</p>
    <p><b>Điều 2.</b> Quy chế bao gồm 07 Chương, 32 Điều quy định nguyên tắc làm việc, trách nhiệm của Ban Giám đốc, Trưởng phòng, Chuyên viên và quy trình xử lý văn bản điện tử trên môi trường số.</p>
    <p><b>Điều 3.</b> Quyết định này có hiệu lực kể từ ngày ký. Các phòng, ban chuyên môn và toàn thể công chức, viên chức cơ quan chịu trách nhiệm thi hành./.</p>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title"><b><i>Nơi nhận:</i></b></div>
        <div class="vb-recipient-item">- Ban Giám đốc Sở;</div>
        <div class="vb-recipient-item">- Các phòng chuyên môn thuộc Sở;</div>
        <div class="vb-recipient-item">- Lưu: VT, VP.</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>GIÁM ĐỐC</b></div>
        <div class="vb-sign-note"><i>(Ký tên, đóng dấu)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Giám đốc Sở]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    },
    {
        "ma_mau": "BM-CV-01",
        "ten_mau": "Công văn hướng dẫn triển khai nhiệm vụ năm học đối với các đơn vị trực thuộc",
        "loai_van_ban": "Công văn",
        "linh_vuc": "Giáo dục Trung học",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "KT. GIÁM ĐỐC - PHÓ GIÁM ĐỐC",
        "mo_ta": "Mẫu công văn hành chính phổ biến nhất dùng để chỉ đạo chuyên môn, hướng dẫn thực hiện chương trình giảng dạy, tổ chức thi kiểm tra và hoạt động giáo dục toàn diện.",
        "can_cu_phap_ly": "Chỉ thị số 08/CT-BGDĐT; Khung kế hoạch thời gian năm học của UBND TP. Đà Nẵng.",
        "tu_khoa": "công văn, hướng dẫn, nhiệm vụ năm học, giáo dục trung học, trường thpt, phòng gd&đt, chỉ đạo chuyên môn, dạy học",
        "ten_tep": "BM-CV-01_Cong_van_huong_dan_nhiem_vu.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: ... /SGDĐT-GDTrH
V/v hướng dẫn thực hiện nhiệm vụ giáo dục trung học năm học 2025 - 2026

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

Kính gửi:
- Phòng Giáo dục và Đào tạo các quận, huyện;
- Các trường Trung học phổ thông, trường phổ thông có nhiều cấp học.

Thực hiện Hướng dẫn của Bộ Giáo dục và Đào tạo và Kế hoạch thời gian năm học của UBND thành phố Đà Nẵng, Sở Giáo dục và Đào tạo hướng dẫn các đơn vị triển khai thực hiện các nhiệm vụ trọng tâm sau:

1. Thực hiện hiệu quả Chương trình Giáo dục phổ thông 2018
- Chủ động xây dựng kế hoạch giáo dục nhà trường linh hoạt, sáng tạo.
- Đổi mới mạnh mẽ phương pháp dạy học và kiểm tra, đánh giá theo hướng phát triển năng lực, phẩm chất học sinh.

2. Nâng cao chất lượng đội ngũ giáo viên
- Đẩy mạnh sinh hoạt chuyên môn theo nghiên cứu bài học, ứng dụng công nghệ thông tin và chuyển đổi số trong bài giảng.

3. Tổ chức thực hiện
Thủ trưởng các đơn vị quán triệt nội dung hướng dẫn này đến toàn thể cán bộ, giáo viên và gửi báo cáo kết quả triển khai về Sở GD&ĐT (qua Phòng GDTrH) trước ngày 15 hàng tháng./.

Nơi nhận:
- Như trên;
- Giám đốc Sở (để b/c);
- Lưu: VT, GDTrH.

KT. GIÁM ĐỐC
PHÓ GIÁM ĐỐC
(Ký, đóng dấu, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/SGDĐT-GDTrH</div>
        <div class="vb-doc-excerpt"><i>V/v hướng dẫn triển khai nhiệm vụ chuyên môn năm học mới</i></div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-recipient-block" style="margin-top: 25px;">
    <b>Kính gửi:</b><br>
    &nbsp;&nbsp;&nbsp;&nbsp;- Phòng Giáo dục và Đào tạo các quận, huyện;<br>
    &nbsp;&nbsp;&nbsp;&nbsp;- Các trường Trung học phổ thông trực thuộc Sở.
  </div>

  <div class="vb-content">
    <p>Căn cứ Chỉ thị của Bộ Giáo dục và Đào tạo về thực hiện nhiệm vụ trọng tâm năm học;</p>
    <p>Thực hiện Quyết định ban hành khung kế hoạch thời gian năm học của Ủy ban nhân dân thành phố Đà Nẵng;</p>
    <p>Sở Giáo dục và Đào tạo hướng dẫn các đơn vị, trường học tập trung thực hiện các nhiệm vụ chuyên môn như sau:</p>

    <p><b>1. Công tác dạy học và kiểm tra đánh giá:</b></p>
    <p>- Thực hiện nghiêm túc kế hoạch thời gian năm học; xây dựng ma trận và bản đặc tả đề kiểm tra định kỳ theo định hướng phát triển năng lực học sinh.</p>
    <p>- Đẩy mạnh ứng dụng học liệu số và kiểm tra trực tuyến trên nền tảng giáo dục của thành phố.</p>

    <p><b>2. Công tác bồi dưỡng giáo viên:</b></p>
    <p>- Tiếp tục triển khai bồi dưỡng thường xuyên mô-đun đổi mới phương pháp giảng dạy và tích hợp giáo dục STEM/STEAM.</p>

    <p><b>3. Chế độ thông tin, báo cáo:</b></p>
    <p>Yêu cầu các đơn vị gửi báo cáo tình hình đầu năm học về Sở GD&ĐT trước ngày .../.../2026 qua hệ thống Quản lý văn bản điện tử./.</p>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title"><b><i>Nơi nhận:</i></b></div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Giám đốc Sở (để báo cáo);</div>
        <div class="vb-recipient-item">- Các Phó Giám đốc Sở;</div>
        <div class="vb-recipient-item">- Lưu: VT, GDTrH.</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>KT. GIÁM ĐỐC<br>PHÓ GIÁM ĐỐC</b></div>
        <div class="vb-sign-note"><i>(Ký tên, đóng dấu)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Phó Giám đốc]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    },
    {
        "ma_mau": "BM-CV-02",
        "ten_mau": "Công văn đôn đốc tiến độ nộp báo cáo số liệu và thống kê đầu năm",
        "loai_van_ban": "Công văn",
        "linh_vuc": "Hành chính - Tổng hợp",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "CHÁNH VĂN PHÒNG",
        "mo_ta": "Sử dụng khi cần nhắc nhở, đôn đốc các trường, đơn vị trực thuộc nộp báo cáo thống kê định kỳ, hồ sơ phổ cập hoặc số liệu tổng hợp đúng thời hạn.",
        "can_cu_phap_ly": "Quy chế làm việc của Sở GD&ĐT; Kế hoạch cải cách hành chính và kỷ luật kỷ cương công vụ.",
        "tu_khoa": "công văn, đôn đốc, nhắc nhở, nộp báo cáo, số liệu thống kê, chậm hạn, trễ hạn, phổ cập, văn phòng sở",
        "ten_tep": "BM-CV-02_Cong_van_don_doc_bao_cao.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: ... /SGDĐT-VP
V/v đôn đốc nộp báo cáo thống kê đầu năm học 2025 - 2026

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

Kính gửi: Thủ trưởng các đơn vị, trường học trực thuộc Sở.

Theo Công văn số .../SGDĐT-VP ngày .../.../2026 của Sở GD&ĐT, thời hạn hoàn thành cập nhật và gửi báo cáo số liệu thống kê đầu năm là ngày .../.../2026.
Tuy nhiên, đến nay vẫn còn một số đơn vị chưa gửi báo cáo hoặc số liệu chưa đầy đủ, ảnh hưởng đến tiến độ tổng hợp chung báo cáo UBND thành phố và Bộ GD&ĐT.
Sở Giáo dục và Đào tạo yêu cầu Thủ trưởng các đơn vị khẩn trương hoàn thiện và gửi báo cáo về Sở trước 17h00 ngày .../.../2026. Quá thời hạn trên, Thủ trưởng đơn vị chịu trách nhiệm trước Giám đốc Sở về việc chậm trễ này./.

CHÁNH VĂN PHÒNG
(Ký, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/SGDĐT-VP</div>
        <div class="vb-doc-excerpt"><i>V/v đôn đốc tiến độ nộp báo cáo số liệu và số hóa hồ sơ</i></div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-recipient-block" style="margin-top: 25px;">
    <b>Kính gửi:</b> Thủ trưởng các phòng thuộc Sở và các đơn vị trường học trực thuộc.
  </div>

  <div class="vb-content">
    <p>Thực hiện chỉ đạo của Giám đốc Sở GD&ĐT về việc chuẩn hóa dữ liệu báo cáo ngành giáo dục phục vụ công tác điều hành năm 2026;</p>
    <p>Qua theo dõi trên Hệ thống Quản lý văn bản điều hành, tính đến ngày .../.../2026 vẫn còn một số phòng ban, trường học chưa nộp báo cáo theo đúng thời hạn quy định.</p>
    <p>Để đảm bảo tiến độ tổng hợp báo cáo phục vụ cuộc họp giao ban tháng của UBND thành phố, Văn phòng Sở đề nghị Thủ trưởng các đơn vị:</p>
    <p>1. Khẩn trương rà soát, hoàn thành việc số hóa số liệu và nộp văn bản báo cáo qua phần mềm QLVB trước <b>11h30 ngày .../.../2026</b>.</p>
    <p>2. Phân công cán bộ đầu mối liên hệ trực tiếp Văn phòng Sở để đối soát dữ liệu (SĐT: 0236.3822.456).</p>
    <p>Sau thời hạn nêu trên, Văn phòng Sở sẽ tổng hợp danh sách đơn vị chậm trễ để báo cáo Giám đốc Sở xem xét thi đua cuối năm./.</p>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title"><b><i>Nơi nhận:</i></b></div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Giám đốc Sở (để báo cáo);</div>
        <div class="vb-recipient-item">- Lưu: VT, VP.</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>TL. GIÁM ĐỐC<br>CHÁNH VĂN PHÒNG</b></div>
        <div class="vb-sign-note"><i>(Ký tên, đóng dấu)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Chánh Văn phòng]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    },
    {
        "ma_mau": "BM-KH-01",
        "ten_mau": "Kế hoạch tổ chức Kỳ thi tuyển sinh vào lớp 10 THPT công lập",
        "loai_van_ban": "Kế hoạch",
        "linh_vuc": "Khảo thí & ĐBCLGD",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "GIÁM ĐỐC SỞ",
        "mo_ta": "Mẫu kế hoạch tổ chức kỳ thi tuyển sinh chi tiết: mục đích yêu cầu, chỉ tiêu tuyển sinh, lịch thi các môn, quy chế coi thi - chấm thi, phối hợp an ninh trật tự và phân công nhiệm vụ.",
        "can_cu_phap_ly": "Thông tư số 11/2014/TT-BGDĐT; Quyết định phê duyệt Kế hoạch tuyển sinh của UBND TP. Đà Nẵng.",
        "tu_khoa": "kế hoạch, tuyển sinh, lớp 10, kỳ thi, thi tuyển, khảo thí, tổ chức thi, coi thi, chấm thi, lê quý đôn, thi vào 10",
        "ten_tep": "BM-KH-01_Ke_hoach_tuyen_sinh_lop_10.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: ... /KH-SGDĐT

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

KẾ HOẠCH
Tổ chức Kỳ thi tuyển sinh vào lớp 10 trung học phổ thông năm học 2026 - 2027 trên địa bàn thành phố Đà Nẵng

Nhằm tổ chức Kỳ thi tuyển sinh vào lớp 10 THPT nghiêm túc, an toàn, khách quan, công bằng và đúng quy chế, Sở Giáo dục và Đào tạo ban hành Kế hoạch tổ chức cụ thể như sau:
I. MỤC ĐÍCH, YÊU CẦU
1. Mục đích: Đánh giá đúng năng lực học sinh, phân luồng sau THCS và tuyển sinh đúng chỉ tiêu.
2. Yêu cầu: Đảm bảo an toàn tuyệt đối về đề thi, phòng thi, an ninh trường thi và phòng chống gian lận.
II. PHƯƠNG THỨC VÀ LỊCH THI
1. Môn thi: Toán, Ngữ văn, Ngoại ngữ (và môn chuyên đối với Trường THPT Chuyên Lê Quý Đôn).
2. Lịch thi: Diễn ra trong các ngày .../.../2026.
III. TỔ CHỨC THỰC HIỆN
- Phòng Khảo thí chủ trì công tác ra đề, in sao đề thi và quản lý kết quả thi.
- Phòng KHTC đảm bảo kinh phí, máy scan bài thi trắc nghiệm.
- Công an thành phố phối hợp bảo vệ bí mật đề thi, bài thi./.

GIÁM ĐỐC
(Ký, đóng dấu, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/KH-SGDĐT</div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">KẾ HOẠCH</div>
    <div class="vb-subject">Tổ chức Kỳ thi tuyển sinh vào lớp 10 Trung học phổ thông năm học 2026 - 2027 trên địa bàn thành phố Đà Nẵng</div>
  </div>

  <div class="vb-content">
    <p>Thực hiện Quyết định của UBND thành phố Đà Nẵng phê duyệt Kế hoạch phát triển giáo dục và tuyển sinh các lớp đầu cấp;</p>
    <p>Sở Giáo dục và Đào tạo ban hành Kế hoạch tổ chức Kỳ thi tuyển sinh vào lớp 10 THPT công lập năm học 2026 - 2027 với các nội dung trọng tâm như sau:</p>

    <p><b>I. MỤC ĐÍCH - YÊU CẦU</b></p>
    <p>1. Thực hiện tốt công tác phân luồng học sinh sau tốt nghiệp THCS; tuyển chọn học sinh vào học các trường THPT công lập phù hợp với năng lực và nguyện vọng.</p>
    <p>2. Kỳ thi phải diễn ra nghiêm túc, an toàn, công bằng, khách quan, tạo điều kiện thuận lợi nhất cho thí sinh và phụ huynh.</p>

    <p><b>II. MÔN THI, HÌNH THỨC VÀ THỜI GIAN THI</b></p>
    <p>- Môn thi: <b>Toán</b> (120 phút), <b>Ngữ văn</b> (120 phút) và <b>Ngoại ngữ</b> (90 phút). Thí sinh thi vào THPT chuyên Lê Quý Đôn dự thi thêm môn chuyên tương ứng.</p>
    <p>- Thời gian tổ chức thi: Dự kiến từ ngày 05/6/2026 đến ngày 08/6/2026 tại ... điểm thi trên toàn địa bàn thành phố.</p>

    <p><b>III. PHÂN CÔNG NHIỆM VỤ</b></p>
    <p>- <i>Phòng Khảo thí & ĐBCLGD:</i> Tham mưu thành lập các Hội đồng ra đề, coi thi, chấm thi; tập huấn nghiệp vụ cho cán bộ coi thi.</p>
    <p>- <i>Văn phòng Sở & Phòng KHTC:</i> Bố trí phương tiện, kinh phí, văn phòng phẩm và phối hợp với Công an thành phố đảm bảo an ninh trật tự.</p>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title"><b><i>Nơi nhận:</i></b></div>
        <div class="vb-recipient-item">- Bộ GD&ĐT (để b/c);</div>
        <div class="vb-recipient-item">- UBND thành phố (để b/c);</div>
        <div class="vb-recipient-item">- Các Phòng GD&ĐT, trường THPT;</div>
        <div class="vb-recipient-item">- Lưu: VT, KTQLCL.</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>GIÁM ĐỐC</b></div>
        <div class="vb-sign-note"><i>(Ký tên, đóng dấu)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Giám đốc Sở]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    },
    {
        "ma_mau": "BM-TB-01",
        "ten_mau": "Thông báo về việc nghỉ Lễ và phân công trực cơ quan Sở GD&ĐT",
        "loai_van_ban": "Thông báo",
        "linh_vuc": "Văn phòng Sở",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "TL. GIÁM ĐỐC - CHÁNH VĂN PHÒNG",
        "mo_ta": "Mẫu thông báo nghỉ Lễ, Tết chính thức của ngành Giáo dục thành phố: thời gian nghỉ, quy định trực chỉ huy cơ quan, phòng chống cháy nổ và báo cáo tình hình khẩn cấp.",
        "can_cu_phap_ly": "Bộ luật Lao động năm 2019; Thông báo lịch nghỉ của UBND thành phố Đà Nẵng.",
        "tu_khoa": "thông báo, nghỉ lễ, trực cơ quan, quốc khánh, tết, 2/9, 30/4, lịch trực, an toàn cơ quan, nghỉ tết, văn phòng sở",
        "ten_tep": "BM-TB-01_Thong_bao_nghi_le_truc_co_quan.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: ... /TB-SGDĐT

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

THÔNG BÁO
Về việc nghỉ Lễ và tổ chức trực cơ quan Sở Giáo dục và Đào tạo

Thực hiện Thông báo của Ủy ban nhân dân thành phố Đà Nẵng về việc nghỉ Lễ; Sở Giáo dục và Đào tạo thông báo đến toàn thể các phòng thuộc Sở và các đơn vị, trường học lịch nghỉ và công tác trực như sau:
1. Thời gian nghỉ Lễ: Từ ngày .../.../2026 đến hết ngày .../.../2026.
2. Công tác phân công trực:
- Văn phòng Sở phân công lịch trực lãnh đạo, trực cán bộ chuyên viên 24/24h (danh sách đính kèm).
- Các đơn vị, trường học niêm phong các phòng làm việc, ngắt các nguồn điện không cần thiết, kiểm tra thiết bị phòng cháy chữa cháy.
3. Chế độ thông tin báo cáo:
Trường hợp có tình huống phát sinh khẩn cấp, báo cáo ngay về Lãnh đạo Sở qua số điện thoại trực chỉ huy: 0236.3822.456./.

TL. GIÁM ĐỐC
CHÁNH VĂN PHÒNG
(Ký, đóng dấu, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/TB-SGDĐT</div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">THÔNG BÁO</div>
    <div class="vb-subject">Về việc nghỉ Lễ và tổ chức trực bảo vệ an toàn cơ quan Sở Giáo dục và Đào tạo</div>
  </div>

  <div class="vb-content">
    <p>Thực hiện Thông báo số .../TB-UBND của Ủy ban nhân dân thành phố Đà Nẵng về việc nghỉ các ngày Lễ trong năm 2026;</p>
    <p>Sở Giáo dục và Đào tạo thông báo đến các phòng chuyên môn thuộc Sở, các Phòng GD&ĐT quận, huyện và các trường học trực thuộc các nội dung sau:</p>

    <p><b>1. Thời gian nghỉ:</b></p>
    <p>- Cán bộ, công chức, viên chức, người lao động và học sinh toàn ngành được nghỉ từ ngày <b>.../.../2026</b> đến hết ngày <b>.../.../2026</b>. Bắt đầu làm việc lại bình thường từ ngày .../.../2026.</p>

    <p><b>2. Đảm bảo an ninh, an toàn trường học:</b></p>
    <p>- Thực hiện nghiêm chế độ trực lãnh đạo và trực cơ quan 24/24 giờ để kịp thời xử lý các tình huống đột xuất.</p>
    <p>- Kiểm tra kỹ hệ thống điện, trang thiết bị phòng cháy chữa cháy, khóa cổng và niêm phong các phòng hồ sơ lưu trữ.</p>

    <p><b>3. Báo cáo tình hình:</b></p>
    <p>Thủ trưởng các đơn vị báo cáo tình hình an ninh trật tự trước và sau kỳ nghỉ lễ về Văn phòng Sở trước 16h00 ngày làm việc đầu tiên./.</p>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title"><b><i>Nơi nhận:</i></b></div>
        <div class="vb-recipient-item">- Ban Giám đốc Sở;</div>
        <div class="vb-recipient-item">- Các đơn vị, trường học trực thuộc;</div>
        <div class="vb-recipient-item">- Website Sở GD&ĐT;</div>
        <div class="vb-recipient-item">- Lưu: VT, VP.</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>TL. GIÁM ĐỐC<br>CHÁNH VĂN PHÒNG</b></div>
        <div class="vb-sign-note"><i>(Ký tên, đóng dấu)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Chánh Văn phòng]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    },
    {
        "ma_mau": "BM-BB-01",
        "ten_mau": "Biên bản cuộc họp giao ban Lãnh đạo Sở và Trưởng các Phòng chuyên môn",
        "loai_van_ban": "Biên bản",
        "linh_vuc": "Hành chính - Tổng hợp",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "Chủ trì cuộc họp & Thư ký cuộc họp",
        "mo_ta": "Mẫu biên bản cuộc họp giao ban định kỳ: ghi nhận tiến độ công việc, các khó khăn vướng mắc của từng phòng và kết luận chỉ đạo của Giám đốc Sở.",
        "can_cu_phap_ly": "Nghị định số 30/2020/NĐ-CP; Quy chế làm việc cơ quan Sở GD&ĐT.",
        "tu_khoa": "biên bản, cuộc họp, giao ban, thư ký, kết luận lãnh đạo, ghi biên bản, họp sở, phòng ban",
        "ten_tep": "BM-BB-01_Bien_ban_hop_giao_ban.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

BIÊN BẢN
Cuộc họp giao ban công tác tháng ... năm 2026 của Lãnh đạo Sở Giáo dục và Đào tạo

Thời gian bắt đầu: Vào hồi 08h00, ngày ... tháng ... năm 2026.
Địa điểm: Phòng họp số 1, Cơ quan Sở GD&ĐT thành phố Đà Nẵng.
Chủ trì: Đồng chí [Họ và tên] - Giám đốc Sở Giáo dục và Đào tạo.
Thư ký: Đồng chí [Họ và tên] - Chuyên viên Văn phòng Sở.
Thành phần tham dự:
- Các đồng chí Phó Giám đốc Sở;
- Trưởng các phòng chuyên môn, nghiệp vụ thuộc Sở.

NỘI DUNG CUỘC HỌP:
1. Đánh giá kết quả công tác tháng qua:
- Văn phòng Sở báo cáo tiến độ xử lý văn bản đến/đi và kết quả thực hiện các kết luận giao việc.
- Các phòng báo cáo khó khăn vướng mắc về tuyển sinh, cơ sở vật chất và thi học sinh giỏi.
2. Ý kiến phát biểu của các thành viên dự họp:
[Tóm tắt ý kiến phát biểu của từng đồng chí]
3. Kết luận chỉ đạo của Giám đốc Sở:
- Giao Phòng GDTrH rà soát ngay kế hoạch ôn tập lớp 12.
- Giao Phòng KHTC đôn đốc giải ngân vốn đầu tư công thiết bị trường học.
- Văn phòng Sở ban hành Thông báo kết luận giao ban trước ngày mai.

Cuộc họp kết thúc vào hồi 11h30 cùng ngày. Biên bản đã được thông qua các thành viên tham dự./.

THƯ KÝ CUỘC HỌP
(Ký, ghi rõ họ tên)

CHỦ TRÌ CUỘC HỌP
(Ký, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">BIÊN BẢN</div>
    <div class="vb-subject">Cuộc họp giao ban định kỳ Lãnh đạo Sở và Trưởng các Phòng chuyên môn tháng .../2026</div>
  </div>

  <div class="vb-content">
    <p><b>I. THỜI GIAN, ĐỊA ĐIỂM, THÀNH PHẦN:</b></p>
    <p>- Thời gian: Vào hồi 08 giờ 00 phút, ngày ... tháng ... năm 2026.</p>
    <p>- Địa điểm: Phòng họp số 1, Cơ quan Sở Giáo dục và Đào tạo (tầng 4).</p>
    <p>- Chủ trì: Đồng chí [Họ tên] - Giám đốc Sở GD&ĐT.</p>
    <p>- Thư ký: Đồng chí [Họ tên] - Chuyên viên Văn phòng Sở.</p>
    <p>- Thành phần: Các đồng chí Phó Giám đốc Sở, Trưởng/Phó trưởng các phòng ban chuyên môn.</p>

    <p><b>II. TIẾN TRÌNH VÀ NỘI DUNG CUỘC HỌP:</b></p>
    <p>1. Văn phòng Sở trình bày tóm tắt kết quả theo dõi thực hiện nhiệm vụ được Lãnh đạo Sở giao trong tháng.</p>
    <p>2. Ý kiến báo cáo của Trưởng các phòng chuyên môn về công tác chuẩn bị kỳ thi, kiểm tra điều kiện an toàn trường học và giải ngân nguồn vốn tài chính.</p>
    <p>3. Các đồng chí Phó Giám đốc Sở cho ý kiến chỉ đạo theo các lĩnh vực phụ trách.</p>

    <p><b>III. KẾT LUẬN CỦA GIÁM ĐỐC SỞ:</b></p>
    <p>- Đánh giá cao tinh thần trách nhiệm của các phòng ban trong việc giải quyết hồ sơ đúng hạn trên môi trường số.</p>
    <p>- Yêu cầu tập trung cao độ cho công tác tuyển sinh các lớp đầu cấp và tổ chức kỳ thi nghiêm túc, an toàn.</p>
    <p>Biên bản cuộc họp được đọc lại cho toàn thể thành viên nghe và thống nhất ký tên./.</p>
  </div>

  <table class="vb-footer-table" style="margin-top: 40px;">
    <tr>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>THƯ KÝ CUỘC HỌP</b></div>
        <div class="vb-sign-note"><i>(Ký, ghi rõ họ tên)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Thư ký]</b></div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>CHỦ TRÌ CUỘC HỌP</b></div>
        <div class="vb-sign-note"><i>(Ký, ghi rõ họ tên)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Giám đốc Sở]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    },
    {
        "ma_mau": "BM-BC-01",
        "ten_mau": "Báo cáo sơ kết công tác chuyển đổi số và ứng dụng CNTT ngành giáo dục",
        "loai_van_ban": "Báo cáo",
        "linh_vuc": "Chuyển đổi số & CNTT",
        "co_quan_ban_hanh": "SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG",
        "tham_quyen_ky": "GIÁM ĐỐC SỞ",
        "mo_ta": "Mẫu báo cáo tổng hợp: kết quả triển khai hạ tầng số, phần mềm quản lý văn bản điều hành, dạy học trực tuyến, số hóa hồ sơ sổ sách, khó khăn và nhiệm vụ trọng tâm.",
        "can_cu_phap_ly": "Nghị quyết của Thành ủy Đà Nẵng về chuyển đổi số; Quyết định số 131/QĐ-TTg của Thủ tướng Chính phủ.",
        "tu_khoa": "báo cáo, chuyển đổi số, cntt, sơ kết, đánh giá, phương hướng, ứng dụng công nghệ, hồ sơ số, quản lý văn bản",
        "ten_tep": "BM-BC-01_Bao_cao_chuyen_doi_so.doc",
        "noi_dung_text": """ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG
SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: ... /BC-SGDĐT

CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
Đà Nẵng, ngày ... tháng ... năm 2026

BÁO CÁO
Sơ kết công tác chuyển đổi số và ứng dụng công nghệ thông tin ngành Giáo dục và Đào tạo thành phố Đà Nẵng năm học 2025 - 2026

Kính gửi:
- Bộ Giáo dục và Đào tạo;
- Ủy ban nhân dân thành phố Đà Nẵng.

Sở Giáo dục và Đào tạo thành phố Đà Nẵng báo cáo kết quả thực hiện công tác chuyển đổi số ngành giáo dục với các nội dung chính sau:
I. KẾT QUẢ ĐẠT ĐƯỢC
1. Hạ tầng số: 100% các đơn vị trường học kết nối cáp quang internet băng thông rộng.
2. Quản lý điều hành số: Hệ thống Quản lý văn bản điều hành nội bộ đã liên thông gửi/nhận văn bản đạt tỷ lệ 98.5% văn bản điện tử ký số.
3. Chuyển đổi số trong dạy và học: 100% học sinh THPT được tạo tài khoản định danh giáo dục.
II. KHÓ KHĂN, VƯỚNG MẮC
- Kinh phí bảo trì hệ thống và an toàn thông tin mạng tại một số trường học còn hạn hẹp.
III. NHIỆM VỤ TRỌNG TÂM THỜI GIAN TỚI
- Tiếp tục nâng cấp hệ thống phần mềm, tích hợp trí tuệ nhân tạo (Chatbot) trợ giúp tra cứu văn bản điều hành.
Sở GD&ĐT kính báo cáo Bộ GD&ĐT và UBND thành phố theo dõi, chỉ đạo./.

GIÁM ĐỐC
(Ký, đóng dấu, ghi rõ họ tên)""",
        "noi_dung_html": """<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; vertical-align: top; text-align: center;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/BC-SGDĐT</div>
      </td>
      <td style="width: 55%; vertical-align: top; text-align: center;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date"><i>Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</i></div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">BÁO CÁO</div>
    <div class="vb-subject">Sơ kết công tác chuyển đổi số và hiện đại hóa quản trị giáo dục năm học 2025 - 2026</div>
  </div>

  <div class="vb-recipient-block">
    <b>Kính gửi:</b><br>
    &nbsp;&nbsp;&nbsp;&nbsp;- Bộ Giáo dục và Đào tạo (Cục CNTT);<br>
    &nbsp;&nbsp;&nbsp;&nbsp;- Ủy ban nhân dân thành phố Đà Nẵng.
  </div>

  <div class="vb-content">
    <p>Thực hiện Kế hoạch số .../KH-UBND của UBND thành phố Đà Nẵng về chuyển đổi số;</p>
    <p>Sở Giáo dục và Đào tạo báo cáo kết quả triển khai ứng dụng công nghệ thông tin và chuyển đổi số trong ngành giáo dục như sau:</p>

    <p><b>1. Công tác quản lý văn bản điều hành và cải cách hành chính:</b></p>
    <p>- Triển khai 100% trao đổi văn bản điện tử có chữ ký số công vụ giữa cơ quan Sở với các trường học và cơ quan hành chính thành phố.</p>
    <p>- Đưa vào vận hành Trợ lý ảo AI (Chatbot) hỗ trợ chuyên viên tìm kiếm biểu mẫu văn bản hành chính và giải đáp quy trình tự động 24/7.</p>

    <p><b>2. Số hóa cơ sở dữ liệu ngành:</b></p>
    <p>- Hoàn thành 100% số hóa hồ sơ học bạ, văn bằng chứng chỉ và kết quả thi tốt nghiệp.</p>

    <p><b>3. Kiến nghị, đề xuất:</b></p>
    <p>Kính đề nghị UBND thành phố tiếp tục bố trí ngân sách duy trì bản quyền phần mềm và nâng cấp bảo mật an toàn thông tin mạng cho các trường học./.</p>
  </div>

  <table class="vb-footer-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title"><b><i>Nơi nhận:</i></b></div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Ban Giám đốc Sở;</div>
        <div class="vb-recipient-item">- Lưu: VT, CNTT.</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: center;">
        <div class="vb-sign-role"><b>GIÁM ĐỐC</b></div>
        <div class="vb-sign-note"><i>(Ký tên, đóng dấu)</i></div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name"><b>[Họ và tên Giám đốc Sở]</b></div>
      </td>
    </tr>
  </table>
</div>"""
    }
]

def seed_mau_van_ban():
    db_path = Path(Config.DATABASE_PATH)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Đảm bảo bảng tồn tại
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mau_van_ban (
            mau_id            INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_mau            TEXT NOT NULL UNIQUE COLLATE NOCASE,
            ten_mau           TEXT NOT NULL,
            loai_van_ban      TEXT NOT NULL,
            linh_vuc          TEXT NOT NULL,
            co_quan_ban_hanh  TEXT NOT NULL DEFAULT 'SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG',
            tham_quyen_ky     TEXT,
            mo_ta             TEXT,
            can_cu_phap_ly    TEXT,
            tu_khoa           TEXT,
            noi_dung_html     TEXT NOT NULL,
            noi_dung_text     TEXT NOT NULL,
            ten_tep           TEXT,
            luot_xem          INTEGER NOT NULL DEFAULT 0,
            luot_tai          INTEGER NOT NULL DEFAULT 0,
            ngay_tao          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lich_su_chat (
            tin_nhan_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nguoi_dung_id     INTEGER,
            cau_hoi           TEXT NOT NULL,
            cau_tra_loi       TEXT NOT NULL,
            mau_de_xuat_ids   TEXT,
            thoi_gian         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE
        );
    """)

    conn.commit()

    count_inserted = 0
    count_updated = 0

    for m in DANH_SACH_MAU:
        cursor.execute("SELECT mau_id FROM mau_van_ban WHERE ma_mau = ?", (m["ma_mau"],))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE mau_van_ban SET
                    ten_mau = ?, loai_van_ban = ?, linh_vuc = ?,
                    co_quan_ban_hanh = ?, tham_quyen_ky = ?, mo_ta = ?,
                    can_cu_phap_ly = ?, tu_khoa = ?, noi_dung_html = ?,
                    noi_dung_text = ?, ten_tep = ?
                WHERE ma_mau = ?
            """, (
                m["ten_mau"], m["loai_van_ban"], m["linh_vuc"],
                m["co_quan_ban_hanh"], m["tham_quyen_ky"], m["mo_ta"],
                m["can_cu_phap_ly"], m["tu_khoa"], m["noi_dung_html"],
                m["noi_dung_text"], m["ten_tep"], m["ma_mau"]
            ))
            count_updated += 1
        else:
            cursor.execute("""
                INSERT INTO mau_van_ban (
                    ma_mau, ten_mau, loai_van_ban, linh_vuc,
                    co_quan_ban_hanh, tham_quyen_ky, mo_ta,
                    can_cu_phap_ly, tu_khoa, noi_dung_html,
                    noi_dung_text, ten_tep, luot_xem, luot_tai
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                m["ma_mau"], m["ten_mau"], m["loai_van_ban"], m["linh_vuc"],
                m["co_quan_ban_hanh"], m["tham_quyen_ky"], m["mo_ta"],
                m["can_cu_phap_ly"], m["tu_khoa"], m["noi_dung_html"],
                m["noi_dung_text"], m["ten_tep"], 0, 0
            ))
            count_inserted += 1

    conn.commit()
    conn.close()

    print(f"[OK] Đã nạp thành công kho mẫu văn bản vào {Config.DATABASE_PATH}:")
    print(f"     - Thêm mới: {count_inserted} mẫu")
    print(f"     - Cập nhật: {count_updated} mẫu")
    print(f"     - Tổng số mẫu hiện có: {len(DANH_SACH_MAU)} mẫu")
    return True

if __name__ == '__main__':
    seed_mau_van_ban()
