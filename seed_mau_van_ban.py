import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education_management.settings')
django.setup()

from chatbot.models import MauVanBan

TEMPLATES = [
    {
        "ma_mau": "TTr-KHTC-01",
        "ten_mau": "Tờ trình xin phê duyệt kinh phí hoạt động chuyên môn",
        "loai_van_ban": "Tờ trình",
        "linh_vuc": "Kế hoạch - Tài chính",
        "noi_dung_text": """UBND THÀNH PHỐ ĐÀ NẴNG - SỞ GIÁO DỤC VÀ ĐÀO TẠO
Số: .../TTr-KHTC - Đà Nẵng, ngày ... tháng ... năm 2026
TỜ TRÌNH
Về việc xin phê duyệt dự toán kinh phí tổ chức tập huấn chuyên môn giáo viên năm 2026
Kính gửi: Giám đốc Sở Giáo dục và Đào tạo TP. Đà Nẵng.
Căn cứ chức năng, nhiệm vụ và nhu cầu thực tế bồi dưỡng giáo viên; Phòng Kế hoạch - Tài chính kính trình Giám đốc Sở xem xét phê duyệt dự toán kinh phí...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /TTr-KHTC</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</div>
      </td>
    </tr>
  </table>

  <div class="vb-title-block">
    <div class="vb-title-type">TỜ TRÌNH</div>
    <div class="vb-subject">Về việc xin phê duyệt dự toán kinh phí tổ chức tập huấn chuyên môn giáo viên THPT năm học 2026 - 2027</div>
  </div>

  <div class="vb-recipient-block" style="text-align: center; font-weight: bold;">
    Kính gửi: Giám đốc Sở Giáo dục và Đào tạo thành phố Đà Nẵng.
  </div>

  <div class="vb-content">
    <p>Căn cứ Nghị định số 30/2020/NĐ-CP ngày 05/3/2020 của Chính phủ về công tác văn thư;</p>
    <p>Căn cứ Kế hoạch năm học và nhu cầu nâng cao năng lực ứng dụng công nghệ thông tin và phương pháp dạy học mới cho đội ngũ cán bộ, giáo viên cốt cán trên địa bàn thành phố;</p>
    <p>Phòng Kế hoạch - Tài chính phối hợp với Phòng Giáo dục Trung học đã xây dựng dự toán chi tiết cho lớp bồi dưỡng 300 giáo viên với tổng dự toán: <b>150.000.000 VNĐ</b> <i>(Một trăm năm mươi triệu đồng chẵn)</i> từ nguồn kinh phí sự nghiệp giáo dục năm 2026.</p>
    <p>Kính trình Giám đốc Sở xem xét, phê duyệt để đơn vị triển khai các bước tiếp theo theo đúng quy định tài chính hiện hành.</p>
  </div>

  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Phó Giám đốc phụ trách khối;</div>
        <div class="vb-recipient-item">- Lưu: VT, KHTC.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">TRƯỞNG PHÒNG KẾ HOẠCH - TÀI CHÍNH</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Lê Thị Thảo</div>
      </td>
    </tr>
  </table>
</div>
"""
    },
    {
        "ma_mau": "TTr-CSVC-02",
        "ten_mau": "Tờ trình xin chủ trương đầu tư nâng cấp phòng máy tính",
        "loai_van_ban": "Tờ trình",
        "linh_vuc": "Kế hoạch - Tài chính",
        "noi_dung_text": """UBND TP. ĐÀ NẴNG - SỞ GD&ĐT\nSố: .../TTr-KHTC - TỜ TRÌNH về việc xin chủ trương đầu tư nâng cấp phòng máy vi tính phục vụ chuyển đổi số dạy học...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /TTr-SGDĐT</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</div>
      </td>
    </tr>
  </table>
  <div class="vb-title-block">
    <div class="vb-title-type">TỜ TRÌNH</div>
    <div class="vb-subject">Về việc xin chủ trương đầu tư dự án nâng cấp phòng máy vi tính và hạ tầng mạng các trường THPT trực thuộc</div>
  </div>
  <div class="vb-recipient-block" style="text-align: center; font-weight: bold;">
    Kính gửi: Ủy ban nhân dân thành phố Đà Nẵng.
  </div>
  <div class="vb-content">
    <p>Thực hiện Đề án Chuyển đổi số ngành giáo dục giai đoạn 2025 - 2030;</p>
    <p>Hiện nay hệ thống 12 phòng máy vi tính tại các trường THPT trên địa bàn đã xuống cấp, cấu hình cũ không đáp ứng được yêu cầu kiểm tra đánh giá trực tuyến theo Chương trình GDPT 2018;</p>
    <p>Sở Giáo dục và Đào tạo kính trình UBND thành phố xem xét chấp thuận chủ trương đầu tư gói mua sắm thiết bị với quy mô 480 bộ máy tính thế hệ mới.</p>
  </div>
  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Sở Tài chính;</div>
        <div class="vb-recipient-item">- Lưu: VT, KHTC.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">GIÁM ĐỐC SỞ</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Trần Văn Hưng</div>
      </td>
    </tr>
  </table>
</div>
"""
    },
    {
        "ma_mau": "QĐ-KT-03",
        "ten_mau": "Quyết định khen thưởng giáo viên và học sinh giỏi",
        "loai_van_ban": "Quyết định",
        "linh_vuc": "Tổ chức cán bộ",
        "noi_dung_text": """QUYẾT ĐỊNH về việc tặng Giấy khen cho giáo viên và học sinh đạt thành tích xuất sắc trong kỳ thi chọn học sinh giỏi cấp quốc gia năm 2026...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /QĐ-SGDĐT</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</div>
      </td>
    </tr>
  </table>
  <div class="vb-title-block">
    <div class="vb-title-type">QUYẾT ĐỊNH</div>
    <div class="vb-subject">Về việc tặng Giấy khen của Giám đốc Sở cho cán bộ, giáo viên và học sinh đạt giải cao trong Kỳ thi chọn Học sinh giỏi quốc gia năm học 2025 - 2026</div>
  </div>
  <div class="vb-authority-title">GIÁM ĐỐC SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG</div>
  <div class="vb-content">
    <p>Căn cứ Luật Thi đua, Khen thưởng số 06/2022/QH15;</p>
    <p>Căn cứ Quyết định số 18/2021/QĐ-UBND của UBND thành phố Đà Nẵng quy định chức năng, quyền hạn của Sở GD&ĐT;</p>
    <p>Theo đề nghị của Trưởng phòng Tổ chức cán bộ và Trưởng phòng Giáo dục Trung học;</p>
    <p style="text-align: center; font-weight: bold; margin: 12px 0;">QUYẾT ĐỊNH:</p>
    <p><b>Điều 1.</b> Tặng Giấy khen của Giám đốc Sở GD&ĐT kèm tiền thưởng cho 18 giáo viên và 42 học sinh đạt giải Nhất, Nhì, Ba trong Kỳ thi chọn HSG Quốc gia năm 2026.</p>
    <p><b>Điều 2.</b> Mức tiền thưởng thực hiện theo Nghị quyết số 32/2023/NQ-HĐND của HĐND thành phố.</p>
    <p><b>Điều 3.</b> Chánh Văn phòng, Trưởng các phòng chuyên môn và các cá nhân có tên chịu trách nhiệm thi hành Quyết định này.</p>
  </div>
  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- Như Điều 3;</div>
        <div class="vb-recipient-item">- Ban Thi đua Khen thưởng TP;</div>
        <div class="vb-recipient-item">- Lưu: VT, TCCB.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">GIÁM ĐỐC</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Trần Văn Hưng</div>
      </td>
    </tr>
  </table>
</div>
"""
    },
    {
        "ma_mau": "CV-HD-04",
        "ten_mau": "Công văn hướng dẫn triển khai nhiệm vụ năm học",
        "loai_van_ban": "Công văn",
        "linh_vuc": "Giáo dục Trung học",
        "noi_dung_text": """CÔNG VĂN về việc hướng dẫn thực hiện nhiệm vụ trọng tâm giáo dục trung học năm học 2026 - 2027...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /SGDĐT-GDTrH</div>
        <div class="vb-doc-excerpt">V/v triển khai nhiệm vụ trọng tâm năm học 2026 - 2027</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</div>
      </td>
    </tr>
  </table>
  <div class="vb-recipient-block" style="margin-top: 18px;">
    <b>Kính gửi:</b>
    <div style="margin-left: 20px;">- Phòng GD&ĐT các quận, huyện;<br>- Các trường THPT, trường phổ thông có nhiều cấp học.</div>
  </div>
  <div class="vb-content">
    <p>Thực hiện Chỉ thị số 01/CT-BGDĐT của Bộ Giáo dục và Đào tạo về nhiệm vụ trọng tâm năm học 2026 - 2027;</p>
    <p>Sở Giáo dục và Đào tạo thành phố Đà Nẵng hướng dẫn các đơn vị tập trung triển khai một số nội dung sau:</p>
    <p>1. Tăng cường đổi mới phương pháp giảng dạy, đa dạng hóa hình thức kiểm tra đánh giá theo định hướng phát triển phẩm chất, năng lực học sinh.</p>
    <p>2. Đẩy mạnh chuyển đổi số trong quản lý văn bản điều hành và dạy học kết hợp trực tuyến.</p>
    <p>3. Đảm bảo an toàn trường học, phòng chống bạo lực học đường và thực hiện nghiêm quy định phòng cháy chữa cháy.</p>
  </div>
  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Giám đốc Sở (để b/c);</div>
        <div class="vb-recipient-item">- Lưu: VT, GDTrH.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">KT. GIÁM ĐỐC<br>PHÓ GIÁM ĐỐC</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Nguyễn Văn Nam</div>
      </td>
    </tr>
  </table>
</div>
"""
    },
    {
        "ma_mau": "KH-TS-05",
        "ten_mau": "Kế hoạch tổ chức kỳ thi tuyển sinh vào lớp 10",
        "loai_van_ban": "Kế hoạch",
        "linh_vuc": "Khảo thí & ĐBCLGD",
        "noi_dung_text": """KẾ HOẠCH tổ chức Kỳ thi tuyển sinh vào lớp 10 trường THPT công lập năm học 2026 - 2027...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /KH-SGDĐT</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</div>
      </td>
    </tr>
  </table>
  <div class="vb-title-block">
    <div class="vb-title-type">KẾ HOẠCH</div>
    <div class="vb-subject">Tổ chức Kỳ thi tuyển sinh vào lớp 10 trung học phổ thông công lập năm học 2026 - 2027 trên địa bàn thành phố Đà Nẵng</div>
  </div>
  <div class="vb-content">
    <p><b>I. MỤC ĐÍCH, YÊU CẦU</b></p>
    <p>1. Đánh giá đúng năng lực, phẩm chất học sinh sau khi tốt nghiệp THCS, làm căn cứ tuyển sinh vào lớp 10 THPT công lập công bằng, khách quan, chính xác.</p>
    <p>2. Kỳ thi diễn ra an toàn, nghiêm túc, đúng quy chế của Bộ Giáo dục và Đào tạo.</p>
    <p><b>II. LỊCH THI VÀ MÔN THI</b></p>
    <p>- Môn thi: Toán (120 phút), Ngữ văn (120 phút), Ngoại ngữ (90 phút).</p>
    <p>- Thời gian thi dự kiến: Từ ngày 06/6/2026 đến ngày 08/6/2026.</p>
  </div>
  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- UBND TP (để b/c);</div>
        <div class="vb-recipient-item">- Các Phòng GD&ĐT;</div>
        <div class="vb-recipient-item">- Lưu: VT, QLCL.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">GIÁM ĐỐC</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Trần Văn Hưng</div>
      </td>
    </tr>
  </table>
</div>
"""
    },
    {
        "ma_mau": "TB-NL-06",
        "ten_mau": "Thông báo nghỉ lễ và phân công trực cơ quan",
        "loai_van_ban": "Thông báo",
        "linh_vuc": "Văn phòng Sở",
        "noi_dung_text": """THÔNG BÁO về việc nghỉ lễ và phân công lịch trực bảo đảm an ninh trật tự cơ quan...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /TB-SGDĐT</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</div>
      </td>
    </tr>
  </table>
  <div class="vb-title-block">
    <div class="vb-title-type">THÔNG BÁO</div>
    <div class="vb-subject">Về việc nghỉ Lễ Quốc khánh 02/9 và phân công trực cơ quan Sở Giáo dục và Đào tạo</div>
  </div>
  <div class="vb-content">
    <p>Thực hiện Thông báo của UBND thành phố Đà Nẵng về nghỉ các ngày lễ trong năm 2026;</p>
    <p>Sở Giáo dục và Đào tạo thông báo thời gian nghỉ lễ và trực cơ quan như sau:</p>
    <p>1. Cán bộ, công chức, viên chức và người lao động nghỉ lễ từ ngày 01/9/2026 đến hết ngày 03/9/2026.</p>
    <p>2. Phân công Lãnh đạo Sở và cán bộ trực 24/24 giờ để kịp thời xử lý các tình huống đột xuất, khẩn cấp phát sinh.</p>
  </div>
  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- Ban Giám đốc Sở;</div>
        <div class="vb-recipient-item">- Các phòng thuộc Sở;</div>
        <div class="vb-recipient-item">- Lưu: VT.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">CHÁNH VĂN PHÒNG</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Nguyễn Thị Thu Hằng</div>
      </td>
    </tr>
  </table>
</div>
"""
    },
    {
        "ma_mau": "BB-GB-07",
        "ten_mau": "Biên bản cuộc họp giao ban Lãnh đạo Sở",
        "loai_van_ban": "Biên bản",
        "linh_vuc": "Văn phòng Sở",
        "noi_dung_text": """BIÊN BẢN cuộc họp giao ban Lãnh đạo Sở tháng 11/2026...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO<br>TP. ĐÀ NẴNG</div>
        <div class="vb-line-short"></div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày 10 tháng 11 năm 2026</div>
      </td>
    </tr>
  </table>
  <div class="vb-title-block">
    <div class="vb-title-type">BIÊN BẢN</div>
    <div class="vb-subject">Cuộc họp giao ban công tác chỉ đạo điều hành tuần thứ 45 năm 2026</div>
  </div>
  <div class="vb-content">
    <p><b>Thời gian:</b> 08 giờ 30 phút, ngày 10/11/2026.</p>
    <p><b>Địa điểm:</b> Phòng họp số 1, trụ sở Sở Giáo dục và Đào tạo.</p>
    <p><b>Chủ trì:</b> Đồng chí Trần Văn Hưng - Giám đốc Sở.</p>
    <p><b>Nội dung chính:</b> Đánh giá tiến độ giải quyết hồ sơ một cửa, tiến độ chuẩn bị Hội thi Giáo viên dạy giỏi cấp thành phố và công tác giải ngân vốn đầu tư công năm 2026.</p>
  </div>
  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">THƯ KÝ CUỘC HỌP</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Nguyễn Thị Thu Hằng</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">CHỦ TRÌ CUỘC HỌP</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Trần Văn Hưng</div>
      </td>
    </tr>
  </table>
</div>
"""
    },
    {
        "ma_mau": "BC-CCHC-08",
        "ten_mau": "Báo cáo sơ kết công tác chuyển đổi số và CNTT",
        "loai_van_ban": "Báo cáo",
        "linh_vuc": "Chuyển đổi số & CNTT",
        "noi_dung_text": """BÁO CÁO tình hình ứng dụng công nghệ thông tin và chuyển đổi số trong quản trị hành chính ngành giáo dục năm 2026...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /BC-SGDĐT</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</div>
      </td>
    </tr>
  </table>
  <div class="vb-title-block">
    <div class="vb-title-type">BÁO CÁO</div>
    <div class="vb-subject">Kết quả công tác chuyển đổi số, an toàn thông tin và ứng dụng chữ ký số chuyên dùng năm 2026</div>
  </div>
  <div class="vb-content">
    <p>1. Tỷ lệ văn bản đi ký số điện tử đạt 98.4%, vượt chỉ tiêu UBND thành phố giao.</p>
    <p>2. 100% hồ sơ công việc được luân chuyển, xử lý hoàn toàn trên môi trường mạng thông qua Hệ thống Quản lý Văn bản và Điều hành.</p>
    <p>3. Tích hợp thành công Trợ lý ảo AI hỗ trợ tra cứu thể thức Nghị định 30/2020/NĐ-CP và kho mẫu văn bản điều hành.</p>
  </div>
  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- UBND TP Đà Nẵng;</div>
        <div class="vb-recipient-item">- Sở Thông tin và Truyền thông;</div>
        <div class="vb-recipient-item">- Lưu: VT, CNTT.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">GIÁM ĐỐC</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Trần Văn Hưng</div>
      </td>
    </tr>
  </table>
</div>
"""
    },
    {
        "ma_mau": "QĐ-HĐ-09",
        "ten_mau": "Quyết định thành lập Hội đồng coi thi tốt nghiệp THPT",
        "loai_van_ban": "Quyết định",
        "linh_vuc": "Khảo thí & ĐBCLGD",
        "noi_dung_text": """QUYẾT ĐỊNH về việc thành lập Hội đồng thi và các Ban của Hội đồng thi Kỳ thi tốt nghiệp THPT năm 2026 tại thành phố Đà Nẵng...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /QĐ-SGDĐT</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</div>
      </td>
    </tr>
  </table>
  <div class="vb-title-block">
    <div class="vb-title-type">QUYẾT ĐỊNH</div>
    <div class="vb-subject">Về việc thành lập Hội đồng coi thi Kỳ thi tốt nghiệp trung học phổ thông năm 2026</div>
  </div>
  <div class="vb-authority-title">GIÁM ĐỐC SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG</div>
  <div class="vb-content">
    <p>Căn cứ Quy chế thi tốt nghiệp THPT ban hành kèm theo Thông tư của Bộ GD&ĐT;</p>
    <p>Theo đề nghị của Trưởng phòng Khảo thí và Quản lý chất lượng giáo dục;</p>
    <p style="text-align: center; font-weight: bold; margin: 12px 0;">QUYẾT ĐỊNH:</p>
    <p><b>Điều 1.</b> Thành lập Hội đồng thi tốt nghiệp THPT năm 2026 tại Hội đồng thi số 04 - Sở GD&ĐT Đà Nẵng gồm các ông, bà có tên trong danh sách đính kèm.</p>
    <p><b>Điều 2.</b> Hội đồng thi có nhiệm vụ chỉ đạo, tổ chức thực hiện công tác coi thi, chấm thi theo đúng Quy chế thi hiện hành.</p>
  </div>
  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- Bộ GD&ĐT (để b/c);</div>
        <div class="vb-recipient-item">- UBND TP Đà Nẵng;</div>
        <div class="vb-recipient-item">- Lưu: VT, QLCL.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">GIÁM ĐỐC</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Trần Văn Hưng</div>
      </td>
    </tr>
  </table>
</div>
"""
    },
    {
        "ma_mau": "CV-CĐS-10",
        "ten_mau": "Công văn đôn đốc báo cáo chuyển đổi số và ứng dụng CNTT",
        "loai_van_ban": "Công văn",
        "linh_vuc": "Chuyển đổi số & CNTT",
        "noi_dung_text": """CÔNG VĂN về việc đôn đốc báo cáo dữ liệu định danh và tiến độ số hóa hồ sơ ngành giáo dục...""",
        "noi_dung_html": """
<div class="vb-container">
  <table class="vb-header-table">
    <tr>
      <td style="width: 45%; text-align: center; vertical-align: top;">
        <div class="vb-agency-parent">ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</div>
        <div class="vb-agency-name">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
        <div class="vb-line-short"></div>
        <div class="vb-doc-number">Số: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; /SGDĐT-VP</div>
        <div class="vb-doc-excerpt">V/v đôn đốc hoàn thành số hóa hồ sơ giáo dục</div>
      </td>
      <td style="width: 55%; text-align: center; vertical-align: top;">
        <div class="vb-nation-title">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
        <div class="vb-motto">Độc lập - Tự do - Hạnh phúc</div>
        <div class="vb-line-medium"></div>
        <div class="vb-location-date">Đà Nẵng, ngày &nbsp;&nbsp;&nbsp;&nbsp; tháng &nbsp;&nbsp;&nbsp;&nbsp; năm 2026</div>
      </td>
    </tr>
  </table>
  <div class="vb-recipient-block" style="margin-top: 18px;">
    <b>Kính gửi:</b>
    <div style="margin-left: 20px;">- Trưởng các phòng thuộc Sở;<br>- Hiệu trưởng các trường THPT và trực thuộc.</div>
  </div>
  <div class="vb-content">
    <p>Để phục vụ công tác tổng kết năm 2026 và tích hợp cơ sở dữ liệu quốc gia về giáo dục;</p>
    <p>Sở Giáo dục và Đào tạo yêu cầu Thủ trưởng các đơn vị khẩn trương rà soát, hoàn thành cập nhật hồ sơ dữ liệu trước ngày 25/11/2026.</p>
    <p>Các trường hợp chậm muộn sẽ được đưa vào tiêu chí đánh giá thi đua cuối năm của đơn vị.</p>
  </div>
  <table class="vb-footer-table" style="margin-top: 30px;">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <div class="vb-recipients-title">Nơi nhận:</div>
        <div class="vb-recipient-item">- Như trên;</div>
        <div class="vb-recipient-item">- Ban Giám đốc Sở;</div>
        <div class="vb-recipient-item">- Lưu: VT, CNTT.</div>
      </td>
      <td style="width: 50%; text-align: center; vertical-align: top;">
        <div class="vb-sign-role">KT. GIÁM ĐỐC<br>PHÓ GIÁM ĐỐC</div>
        <div class="vb-sign-space"></div>
        <div class="vb-sign-name">Nguyễn Văn Nam</div>
      </td>
    </tr>
  </table>
</div>
"""
    }
]

created = 0
for t in TEMPLATES:
    obj, is_new = MauVanBan.objects.update_or_create(
        ma_mau=t["ma_mau"],
        defaults=t
    )
    if is_new:
        created += 1

print(f"Hoàn thành khởi tạo {MauVanBan.objects.count()} mẫu văn bản (Tạo mới: {created})")
