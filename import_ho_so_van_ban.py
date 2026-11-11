"""
Đồng bộ danh mục văn bản ban hành (VanBanBanHanh) và tệp PDF từ thư mục
'C:\\Users\\Lenovo\\Downloads\\Văn bản Điều hành' vào toàn bộ 12 hồ sơ lưu trữ (HoSoLuuTru).
Chạy độc lập: python import_ho_so_van_ban.py
"""

import os
import shutil
from datetime import date
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education_management.settings")
django.setup()

from ho_so.models import HoSoLuuTru, VanBanBanHanh  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
SOURCE_PDF_DIR = Path(r"C:\Users\Lenovo\Downloads\Văn bản Điều hành")
DEST_PDF_DIR = BASE_DIR / "media" / "van_ban_dieu_hanh"


ARCHIVAL_DOCS_DATA = [
    # 1. HS-2026-GDTrH-001 (Chuyên môn Giáo dục Trung học 2026-2027)
    {
        "ma_ho_so": "HS-2026-GDTrH-001",
        "so_ky_hieu": "1752/QĐ-SGDĐT",
        "trich_yeu": "Quyết định phê duyệt chỉ tiêu tuyển sinh lớp 10 trường THPT tư thục năm học 2026 - 2027 (đợt bổ sung)",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Sở Giáo dục và Đào tạo TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 8, 12),
        "ngay_ban_hanh": date(2026, 8, 12),
        "do_khan": "KHAN",
        "tep_dinh_kem": "van_ban_dieu_hanh/1752qdsgddt.pdf",
    },
    {
        "ma_ho_so": "HS-2026-GDTrH-001",
        "so_ky_hieu": "125/SGDĐT-GDTrH",
        "trich_yeu": "V/v hướng dẫn tổ chức Kỳ thi chọn học sinh giỏi cấp thành phố năm học 2026-2027",
        "loai_van_ban": "Hướng dẫn",
        "co_quan_ban_hanh": "Phòng Giáo dục Trung học - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 9, 8),
        "ngay_ban_hanh": date(2026, 9, 8),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2026-GDTrH-001",
        "so_ky_hieu": "412/SGDĐT-GDTrH",
        "trich_yeu": "Hướng dẫn thực hiện nhiệm vụ giáo dục trung học năm học 2026-2027 trên địa bàn thành phố Đà Nẵng",
        "loai_van_ban": "Công văn",
        "co_quan_ban_hanh": "Phòng Giáo dục Trung học - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 8, 25),
        "ngay_ban_hanh": date(2026, 8, 25),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 2. HS-2026-KHTC-002 (Đầu tư trang thiết bị phòng tin học & thư viện số THPT)
    {
        "ma_ho_so": "HS-2026-KHTC-002",
        "so_ky_hieu": "23/2024/TT-BGDĐT",
        "trich_yeu": "Thông tư sửa đổi, bổ sung một số điều của Quy định tiêu chuẩn cơ sở vật chất các trường mầm non, phổ thông",
        "loai_van_ban": "Thông tư",
        "co_quan_ban_hanh": "Bộ Giáo dục và Đào tạo",
        "nguoi_ky": "Nguyễn Kim Sơn",
        "chuc_vu_nguoi_ky": "Bộ trưởng Bộ GD&ĐT",
        "ngay_ky": date(2024, 12, 20),
        "ngay_ban_hanh": date(2024, 12, 20),
        "do_khan": "THUONG",
        "tep_dinh_kem": "van_ban_dieu_hanh/232024ttbgddtsigned.pdf",
    },
    {
        "ma_ho_so": "HS-2026-KHTC-002",
        "so_ky_hieu": "88/QĐ-UBND-KHTC",
        "trich_yeu": "Quyết định phân bổ kinh phí đầu tư mua sắm thiết bị phòng tin học và thư viện số các trường THPT công lập",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Kế hoạch - Tài chính - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 10, 28),
        "ngay_ban_hanh": date(2026, 10, 28),
        "do_khan": "KHAN",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2026-KHTC-002",
        "so_ky_hieu": "218/KH-SGDĐT-KHTC",
        "trich_yeu": "Kế hoạch đấu thầu mua sắm tập trung hệ thống máy tính và phần mềm quản lý thư viện số năm 2026",
        "loai_van_ban": "Kế hoạch",
        "co_quan_ban_hanh": "Phòng Kế hoạch - Tài chính - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 9, 18),
        "ngay_ban_hanh": date(2026, 9, 18),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 3. HS-2025-TCCB-005 (Thi tuyển chức danh lãnh đạo quản lý 2025)
    {
        "ma_ho_so": "HS-2025-TCCB-005",
        "so_ky_hieu": "315/KH-SGDĐT-TCCB",
        "trich_yeu": "Kế hoạch thi tuyển chức danh lãnh đạo, quản lý các đơn vị sự nghiệp công lập trực thuộc Sở GD&ĐT năm 2025",
        "loai_van_ban": "Kế hoạch",
        "co_quan_ban_hanh": "Phòng Tổ chức cán bộ - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2025, 4, 10),
        "ngay_ban_hanh": date(2025, 4, 10),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2025-TCCB-005",
        "so_ky_hieu": "628/QĐ-SGDĐT",
        "trich_yeu": "Quyết định thành lập Hội đồng thi tuyển chức danh Hiệu trưởng, Phó Hiệu trưởng các trường THPT năm 2025",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Tổ chức cán bộ - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2025, 5, 15),
        "ngay_ban_hanh": date(2025, 5, 15),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2025-TCCB-005",
        "so_ky_hieu": "945/QĐ-SGDĐT",
        "trich_yeu": "Quyết định công nhận kết quả thi tuyển và bổ nhiệm cán bộ quản lý đơn vị sự nghiệp giáo dục công lập năm 2025",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Tổ chức cán bộ - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2025, 7, 22),
        "ngay_ban_hanh": date(2025, 7, 22),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 4. HS-2026-QLCL-003 (Kỳ thi tốt nghiệp THPT năm 2026 - Hội đồng thi số 04)
    {
        "ma_ho_so": "HS-2026-QLCL-003",
        "so_ky_hieu": "342/QĐ-SGDĐT",
        "trich_yeu": "Quyết định thành lập Đoàn kiểm tra công tác chuẩn bị cơ sở vật chất và bảo đảm chất lượng coi thi tốt nghiệp THPT 2026",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Khảo thí & Quản lý chất lượng - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 5, 20),
        "ngay_ban_hanh": date(2026, 5, 20),
        "do_khan": "KHAN",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2026-QLCL-003",
        "so_ky_hieu": "1340/SGDĐT-QLCL",
        "trich_yeu": "Hướng dẫn đăng ký dự thi và vận hành phần mềm quản lý thi tốt nghiệp THPT năm 2026 tại Hội đồng thi số 04",
        "loai_van_ban": "Hướng dẫn",
        "co_quan_ban_hanh": "Phòng Khảo thí & Quản lý chất lượng - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 4, 12),
        "ngay_ban_hanh": date(2026, 4, 12),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2026-QLCL-003",
        "so_ky_hieu": "715/KH-SGDĐT-QLCL",
        "trich_yeu": "Kế hoạch phối hợp bảo đảm an ninh, bảo mật in sao đề thi và quy chế coi thi Kỳ thi tốt nghiệp THPT 2026",
        "loai_van_ban": "Kế hoạch",
        "co_quan_ban_hanh": "Phòng Khảo thí & Quản lý chất lượng - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 6, 5),
        "ngay_ban_hanh": date(2026, 6, 5),
        "do_khan": "KHAN",
        "tep_dinh_kem": None,
    },
    # 5. HS-2026-GDMN-004 (Trường mầm non đạt chuẩn quốc gia 2026-2031)
    {
        "ma_ho_so": "HS-2026-GDMN-004",
        "so_ky_hieu": "3666/SGDĐT-QLCL",
        "trich_yeu": "Công văn rà soát, cập nhật dữ liệu tuyển sinh đại học, cao đẳng ngành Giáo dục Mầm non trên địa bàn thành phố",
        "loai_van_ban": "Công văn",
        "co_quan_ban_hanh": "Sở Giáo dục và Đào tạo TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 7, 22),
        "ngay_ban_hanh": date(2026, 7, 22),
        "do_khan": "KHAN",
        "tep_dinh_kem": "van_ban_dieu_hanh/3666sgddtqlcl22072026signedsigned.pdf",
    },
    {
        "ma_ho_so": "HS-2026-GDMN-004",
        "so_ky_hieu": "1310/SGDĐT-GDMN",
        "trich_yeu": "V/v tăng cường quản lý an toàn vệ sinh thực phẩm và tổ chức bữa ăn bán trú tại các cơ sở giáo dục mầm non",
        "loai_van_ban": "Công văn",
        "co_quan_ban_hanh": "Phòng Giáo dục Mầm non - Tiểu học - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 9, 14),
        "ngay_ban_hanh": date(2026, 9, 14),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2026-GDMN-004",
        "so_ky_hieu": "504/KH-SGDĐT-GDMN",
        "trich_yeu": "Kế hoạch kiểm tra, đánh giá ngoài công nhận các trường mầm non đạt chuẩn quốc gia mức độ 1 và 2 năm 2026",
        "loai_van_ban": "Kế hoạch",
        "co_quan_ban_hanh": "Phòng Giáo dục Mầm non - Tiểu học - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 8, 29),
        "ngay_ban_hanh": date(2026, 8, 29),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 6. HS-2025-VP-006 (Tập lưu văn bản đi của Giám đốc Sở năm 2025)
    {
        "ma_ho_so": "HS-2025-VP-006",
        "so_ky_hieu": "1120/QĐ-SGDĐT",
        "trich_yeu": "Quyết định ban hành Chương trình công tác trọng tâm năm học 2025-2026 của ngành Giáo dục và Đào tạo TP. Đà Nẵng",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Văn phòng Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2025, 9, 2),
        "ngay_ban_hanh": date(2025, 9, 2),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2025-VP-006",
        "so_ky_hieu": "1485/SGDĐT-VP",
        "trich_yeu": "Thông báo kết luận của Giám đốc Sở tại Hội nghị giao ban công tác chỉ đạo điều hành quý IV năm 2025",
        "loai_van_ban": "Thông báo",
        "co_quan_ban_hanh": "Văn phòng Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2025, 11, 18),
        "ngay_ban_hanh": date(2025, 11, 18),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2025-VP-006",
        "so_ky_hieu": "1690/BC-SGDĐT",
        "trich_yeu": "Báo cáo tổng kết công tác văn thư lưu trữ, cải cách hành chính và điều hành văn bản điện tử năm 2025",
        "loai_van_ban": "Báo cáo",
        "co_quan_ban_hanh": "Văn phòng Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2025, 12, 26),
        "ngay_ban_hanh": date(2025, 12, 26),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 7. HS-2025-KHTC-007 (Quyết toán ngân sách nhà nước và nguồn tài trợ 2025)
    {
        "ma_ho_so": "HS-2025-KHTC-007",
        "so_ky_hieu": "410/QĐ-SGDĐT-KHTC",
        "trich_yeu": "Quyết định phê duyệt quyết toán ngân sách nhà nước chi thường xuyên và đầu tư công năm tài chính 2025",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Kế hoạch - Tài chính - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2025, 12, 30),
        "ngay_ban_hanh": date(2025, 12, 30),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2025-KHTC-007",
        "so_ky_hieu": "845/BC-SGDĐT-KHTC",
        "trich_yeu": "Báo cáo tổng hợp tình hình tiếp nhận, quản lý và sử dụng các nguồn tài trợ giáo dục năm tài chính 2025",
        "loai_van_ban": "Báo cáo",
        "co_quan_ban_hanh": "Phòng Kế hoạch - Tài chính - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 1, 20),
        "ngay_ban_hanh": date(2026, 1, 20),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 8. HS-2026-TCCB-008 (Nâng bậc lương trước thời hạn & thành tích xuất sắc 2026)
    {
        "ma_ho_so": "HS-2026-TCCB-008",
        "so_ky_hieu": "1656/QĐ-UBND",
        "trich_yeu": "Quyết định ban hành Quy chế xét tặng Giải thưởng 'Nhà giáo Đà Nẵng tiêu biểu' ngành Giáo dục và Đào tạo",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Ủy ban nhân dân thành phố Đà Nẵng",
        "nguoi_ky": "Lê Trung Chinh",
        "chuc_vu_nguoi_ky": "Chủ tịch UBND TP. Đà Nẵng",
        "ngay_ky": date(2023, 8, 8),
        "ngay_ban_hanh": date(2023, 8, 8),
        "do_khan": "THUONG",
        "tep_dinh_kem": "van_ban_dieu_hanh/qd-1656-ubndtp.pdf",
    },
    {
        "ma_ho_so": "HS-2026-TCCB-008",
        "so_ky_hieu": "450/QĐ-SGDĐT",
        "trich_yeu": "Quyết định khen thưởng các tập thể, cá nhân có thành tích xuất sắc trong phong trào thi đua dạy tốt học tốt đợt 20/11",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Tổ chức cán bộ - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 11, 5),
        "ngay_ban_hanh": date(2026, 11, 5),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2026-TCCB-008",
        "so_ky_hieu": "488/QĐ-SGDĐT-TCCB",
        "trich_yeu": "Quyết định nâng bậc lương trước thời hạn do lập thành tích xuất sắc trong thực hiện nhiệm vụ năm 2026",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Tổ chức cán bộ - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 10, 15),
        "ngay_ban_hanh": date(2026, 10, 15),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 9. HS-2026-GDTrH-009 (Cuộc thi Khoa học kỹ thuật cấp quốc gia học sinh trung học 2026)
    {
        "ma_ho_so": "HS-2026-GDTrH-009",
        "so_ky_hieu": "20/2024/TT-BGDĐT",
        "trich_yeu": "Thông tư sửa đổi, bổ sung Quy chế tuyển sinh công dân Việt Nam đi học nước ngoài (áp dụng xét tuyển học bổng quốc tế)",
        "loai_van_ban": "Thông tư",
        "co_quan_ban_hanh": "Bộ Giáo dục và Đào tạo",
        "nguoi_ky": "Nguyễn Kim Sơn",
        "chuc_vu_nguoi_ky": "Bộ trưởng Bộ GD&ĐT",
        "ngay_ky": date(2024, 11, 15),
        "ngay_ban_hanh": date(2024, 11, 15),
        "do_khan": "THUONG",
        "tep_dinh_kem": "van_ban_dieu_hanh/202024ttbgddtsigned.pdf",
    },
    {
        "ma_ho_so": "HS-2026-GDTrH-009",
        "so_ky_hieu": "85/CV-SGDĐT",
        "trich_yeu": "Kế hoạch phối hợp tổ chức Cuộc thi Sáng tạo Khoa học kỹ thuật dành cho học sinh trung học năm 2026-2027",
        "loai_van_ban": "Công văn",
        "co_quan_ban_hanh": "Phòng Giáo dục Trung học - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 9, 25),
        "ngay_ban_hanh": date(2026, 9, 25),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2026-GDTrH-009",
        "so_ky_hieu": "290/QĐ-SGDĐT-GDTrH",
        "trich_yeu": "Quyết định thành lập Đoàn dự thi và danh sách dự án học sinh Đà Nẵng tham dự Cuộc thi KHKT cấp quốc gia 2026",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Giáo dục Trung học - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 3, 4),
        "ngay_ban_hanh": date(2026, 3, 4),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 10. HS-2024-TCCB-010 (Giải quyết đơn thư, thanh tra chuyên ngành 2024)
    {
        "ma_ho_so": "HS-2024-TCCB-010",
        "so_ky_hieu": "19/2020/NĐ-CP",
        "trich_yeu": "Nghị định về kiểm tra, xử lý kỷ luật trong thi hành pháp luật về xử lý vi phạm hành chính",
        "loai_van_ban": "Nghị định",
        "co_quan_ban_hanh": "Chính phủ",
        "nguoi_ky": "Nguyễn Xuân Phúc",
        "chuc_vu_nguoi_ky": "Thủ tướng Chính phủ",
        "ngay_ky": date(2020, 2, 12),
        "ngay_ban_hanh": date(2020, 2, 12),
        "do_khan": "THUONG",
        "tep_dinh_kem": "van_ban_dieu_hanh/19signed.pdf",
    },
    {
        "ma_ho_so": "HS-2024-TCCB-010",
        "so_ky_hieu": "112/KL-TTr",
        "trich_yeu": "Kết luận thanh tra chuyên ngành công tác quản lý nhân sự, quy chế chuyên môn và giải quyết đơn thư năm 2024",
        "loai_van_ban": "Kết luận",
        "co_quan_ban_hanh": "Phòng Tổ chức cán bộ - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2024, 10, 14),
        "ngay_ban_hanh": date(2024, 10, 14),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2024-TCCB-010",
        "so_ky_hieu": "275/QĐ-SGDĐT-TCCB",
        "trich_yeu": "Quyết định giải quyết khiếu nại và chấn chỉnh kỷ luật, kỷ cương hành chính tại các đơn vị trực thuộc năm 2024",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Tổ chức cán bộ - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2024, 11, 22),
        "ngay_ban_hanh": date(2024, 11, 22),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 11. HS-2026-VP-011 (Hội nghị CBCCVC & hoạt động cơ quan Sở năm 2026)
    {
        "ma_ho_so": "HS-2026-VP-011",
        "so_ky_hieu": "128/KH-UBND",
        "trich_yeu": "Kế hoạch triển khai Dự án truyền thông “Xin chào Đà Nẵng - Global Greetings to Da Nang” trong cơ quan, trường học",
        "loai_van_ban": "Kế hoạch",
        "co_quan_ban_hanh": "Ủy ban nhân dân thành phố Đà Nẵng",
        "nguoi_ky": "Lê Trung Chinh",
        "chuc_vu_nguoi_ky": "Chủ tịch UBND TP. Đà Nẵng",
        "ngay_ky": date(2026, 5, 15),
        "ngay_ban_hanh": date(2026, 5, 15),
        "do_khan": "THUONG",
        "tep_dinh_kem": "van_ban_dieu_hanh/1.pdf",
    },
    {
        "ma_ho_so": "HS-2026-VP-011",
        "so_ky_hieu": "1205/SGDĐT-VP",
        "trich_yeu": "Kế hoạch tổ chức Tuần lễ hưởng ứng học tập suốt đời năm 2026 trên địa bàn thành phố Đà Nẵng",
        "loai_van_ban": "Kế hoạch",
        "co_quan_ban_hanh": "Văn phòng Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 9, 28),
        "ngay_ban_hanh": date(2026, 9, 28),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2026-VP-011",
        "so_ky_hieu": "1322/SGDĐT-VP",
        "trich_yeu": "Thông báo kết luận của Giám đốc Sở GD&ĐT tại cuộc họp giao ban công tác chuyên môn và quy chế cơ quan tháng 10/2026",
        "loai_van_ban": "Thông báo",
        "co_quan_ban_hanh": "Văn phòng Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 10, 30),
        "ngay_ban_hanh": date(2026, 10, 30),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # 12. HS-2025-QLCL-012 (Lưu trữ bài thi & bảng điểm tuyển sinh lớp 10 năm 2025)
    {
        "ma_ho_so": "HS-2025-QLCL-012",
        "so_ky_hieu": "518/QĐ-SGDĐT-QLCL",
        "trich_yeu": "Quyết định phê duyệt điểm chuẩn và danh sách trúng tuyển Kỳ thi tuyển sinh vào lớp 10 THPT công lập năm học 2025-2026",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Khảo thí & Quản lý chất lượng - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2025, 6, 18),
        "ngay_ban_hanh": date(2025, 6, 18),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": "HS-2025-QLCL-012",
        "so_ky_hieu": "602/BC-SGDĐT-QLCL",
        "trich_yeu": "Báo cáo tổng kết công tác chấm thi, phúc khảo và niêm phong lưu trữ bài thi lớp 10 THPT công lập năm 2025",
        "loai_van_ban": "Báo cáo",
        "co_quan_ban_hanh": "Phòng Khảo thí & Quản lý chất lượng - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2025, 7, 2),
        "ngay_ban_hanh": date(2025, 7, 2),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    # Văn bản khả dụng chưa gắn vào hồ sơ (cho tính năng '+ Thêm văn bản vào hồ sơ')
    {
        "ma_ho_so": None,
        "so_ky_hieu": "82/CV-SGDĐT",
        "trich_yeu": "Hướng dẫn các cơ sở giáo dục thực hiện công khai tài chính và các khoản thu hộ, chi hộ đầu năm học 2026-2027",
        "loai_van_ban": "Công văn",
        "co_quan_ban_hanh": "Phòng Kế hoạch - Tài chính - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Mai Tấn Linh",
        "chuc_vu_nguoi_ky": "Phó Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 9, 5),
        "ngay_ban_hanh": date(2026, 9, 5),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": None,
        "so_ky_hieu": "1355/SGDĐT-GDTrH",
        "trich_yeu": "Kế hoạch tổ chức Ngày hội Giáo dục STEM và Cuộc thi Robocon ngành Giáo dục Đà Nẵng năm học 2026-2027",
        "loai_van_ban": "Kế hoạch",
        "co_quan_ban_hanh": "Phòng Giáo dục Trung học - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 10, 12),
        "ngay_ban_hanh": date(2026, 10, 12),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": None,
        "so_ky_hieu": "89/TTr-SGDĐT",
        "trich_yeu": "Tờ trình UBND thành phố về việc phê duyệt Đề án Chuyển đổi số ngành Giáo dục TP. Đà Nẵng giai đoạn 2026-2030",
        "loai_van_ban": "Tờ trình",
        "co_quan_ban_hanh": "Phòng Kế hoạch - Tài chính - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 10, 20),
        "ngay_ban_hanh": date(2026, 10, 20),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": None,
        "so_ky_hieu": "462/QĐ-SGDĐT",
        "trich_yeu": "Quyết định điều động, bổ nhiệm viên chức quản lý các trường THPT công lập trực thuộc Sở GD&ĐT",
        "loai_van_ban": "Quyết định",
        "co_quan_ban_hanh": "Phòng Tổ chức cán bộ - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 10, 25),
        "ngay_ban_hanh": date(2026, 10, 25),
        "do_khan": "THUONG",
        "tep_dinh_kem": None,
    },
    {
        "ma_ho_so": None,
        "so_ky_hieu": "91/TTr-SGDĐT",
        "trich_yeu": "Tờ trình xin chủ trương đầu tư dự án Xây dựng hệ thống Học bạ số và Chứng chỉ số toàn diện ngành Giáo dục",
        "loai_van_ban": "Tờ trình",
        "co_quan_ban_hanh": "Phòng Kế hoạch - Tài chính - Sở GD&ĐT TP. Đà Nẵng",
        "nguoi_ky": "Lê Thị Bích Thuận",
        "chuc_vu_nguoi_ky": "Giám đốc Sở GD&ĐT",
        "ngay_ky": date(2026, 11, 1),
        "ngay_ban_hanh": date(2026, 11, 1),
        "do_khan": "KHAN",
        "tep_dinh_kem": None,
    },
]


def copy_source_pdfs() -> int:
    """Đảm bảo 7 file PDF từ thư mục Downloads\\Văn bản Điều hành nằm sẵn trong media/van_ban_dieu_hanh."""
    DEST_PDF_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    if SOURCE_PDF_DIR.is_dir():
        for pdf_file in SOURCE_PDF_DIR.glob("*.pdf"):
            dest_file = DEST_PDF_DIR / pdf_file.name
            if not dest_file.exists():
                shutil.copy2(pdf_file, dest_file)
                copied += 1
    return copied


def sync_ho_so_van_ban(verbose: bool = True) -> dict:
    """Nạp đồng bộ VanBanBanHanh cho toàn bộ 12 HoSoLuuTru và đồng bộ lại so_luong_van_ban."""
    copied_pdfs = copy_source_pdfs()
    dossiers_by_code = {hs.ma_ho_so: hs for hs in HoSoLuuTru.objects.all()}

    created_count = 0
    updated_count = 0
    for item in ARCHIVAL_DOCS_DATA:
        ma_ho_so = item["ma_ho_so"]
        ho_so = dossiers_by_code.get(ma_ho_so) if ma_ho_so else None
        ngay_bh = item["ngay_ban_hanh"]

        defaults = {
            "trich_yeu": item["trich_yeu"],
            "loai_van_ban": item["loai_van_ban"],
            "co_quan_ban_hanh": item["co_quan_ban_hanh"],
            "nguoi_ky": item["nguoi_ky"],
            "chuc_vu_nguoi_ky": item["chuc_vu_nguoi_ky"],
            "ngay_ky": item["ngay_ky"],
            "ngay_ban_hanh": ngay_bh,
            "nam_luu_tru": ho_so.nam_tai_lieu if ho_so else ngay_bh.year,
            "thang_luu_tru": ngay_bh.month,
            "quy_luu_tru": (ngay_bh.month - 1) // 3 + 1,
            "thoi_han_bao_quan": ho_so.thoi_han_bao_quan if ho_so else "10 năm",
            "muc_do_mat": "THUONG",
            "do_khan": item["do_khan"],
            "ho_so": ho_so,
            "tep_dinh_kem": item["tep_dinh_kem"],
        }

        doc, created = VanBanBanHanh.objects.update_or_create(
            so_ky_hieu=item["so_ky_hieu"],
            defaults=defaults,
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    # Đồng bộ lại chính xác số lượng văn bản của từng hồ sơ theo database thực tế
    synced_dossiers = 0
    for hs in HoSoLuuTru.objects.all():
        actual_count = VanBanBanHanh.objects.filter(ho_so=hs).count()
        if hs.so_luong_van_ban != actual_count:
            hs.so_luong_van_ban = actual_count
            hs.save(update_fields=["so_luong_van_ban", "ngay_cap_nhat"])
        synced_dossiers += 1

    summary = {
        "copied_pdfs": copied_pdfs,
        "created": created_count,
        "updated": updated_count,
        "total_docs": VanBanBanHanh.objects.count(),
        "unlinked_docs": VanBanBanHanh.objects.filter(ho_so__isnull=True).count(),
        "dossiers": synced_dossiers,
    }
    if verbose:
        print(
            f"[OK] Đồng bộ văn bản hồ sơ: +{created_count} mới, {updated_count} cập nhật, "
            f"tổng {summary['total_docs']} văn bản (khả dụng chưa gắn: {summary['unlinked_docs']}), "
            f"{synced_dossiers} hồ sơ đã đồng bộ số lượng."
        )
    return summary


if __name__ == "__main__":
    sync_ho_so_van_ban(verbose=True)
