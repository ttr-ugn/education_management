import os
import django
from datetime import date, datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education_management.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import NguoiDung
from van_ban.models import VanBanDi, VanBanDen, LichSuXuLyVanBan
from cong_viec.models import CongViec, NhatKyCongViec
from ho_so.models import HoSoLuuTru, VanBanBanHanh
from thong_bao.models import ThongBao
from chatbot.models import MauVanBan

def seed():
    print("=" * 70)
    print("🚀 BẮT ĐẦU NẠP BỘ DỮ LIỆU ĐẦY ĐỦ (12-15 MỤC/PHÂN HỆ)")
    print("   HỆ THỐNG QUẢN LÝ ĐIỀU HÀNH - SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG")
    print("=" * 70)

    # 1. Superuser Django Admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@danang.edu.vn', 'Admin@123')
        print("[OK] Superuser Django: admin / Admin@123")

    # 2. Danh sách Cán bộ / Nhân sự cơ quan (NguoiDung)
    users_data = [
        {
            'ten_dang_nhap': 'admin_vanthu',
            'ho_va_ten': 'Nguyễn Thị Thu Hằng',
            'email': 'vanthu@danang.edu.vn',
            'sdt': '0236.3822.456',
            'phong_ban': 'Văn phòng Sở GD&ĐT',
            'chuc_vu': 'Văn thư cơ quan',
            'vai_tro': 'VAN_THU',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'Admin@123'
        },
        {
            'ten_dang_nhap': 'giamdoc_so',
            'ho_va_ten': 'Lê Thị Bích Thuận',
            'email': 'giamdoc@danang.edu.vn',
            'sdt': '0905.123.456',
            'phong_ban': 'Ban Giám đốc Sở',
            'chuc_vu': 'Giám đốc Sở GD&ĐT',
            'vai_tro': 'LANH_DAO',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'GiamDoc@123'
        },
        {
            'ten_dang_nhap': 'phogiamdoc_so',
            'ho_va_ten': 'Mai Tấn Linh',
            'email': 'linhmt@danang.edu.vn',
            'sdt': '0905.234.567',
            'phong_ban': 'Ban Giám đốc Sở',
            'chuc_vu': 'Phó Giám đốc Sở GD&ĐT',
            'vai_tro': 'LANH_DAO',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'LanhDao@123'
        },
        {
            'ten_dang_nhap': 'minhcv',
            'ho_va_ten': 'Nguyễn Văn Nam',
            'email': 'namnv@danang.edu.vn',
            'sdt': '0914.567.890',
            'phong_ban': 'Phòng Giáo dục Trung học',
            'chuc_vu': 'Chuyên viên chính',
            'vai_tro': 'CHUYEN_VIEN',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'ChuyenVien@123'
        },
        {
            'ten_dang_nhap': 'thaoltk',
            'ho_va_ten': 'Lê Thị Thảo',
            'email': 'thaolt@danang.edu.vn',
            'sdt': '0913.345.678',
            'phong_ban': 'Phòng Kế hoạch - Tài chính',
            'chuc_vu': 'Chuyên viên kế hoạch',
            'vai_tro': 'CHUYEN_VIEN',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'ChuyenVien@123'
        },
        {
            'ten_dang_nhap': 'dungpt',
            'ho_va_ten': 'Phạm Thị Thùy Dung',
            'email': 'dungpt@danang.edu.vn',
            'sdt': '0905.888.999',
            'phong_ban': 'Phòng Tổ chức cán bộ',
            'chuc_vu': 'Chuyên viên tổ chức',
            'vai_tro': 'CHUYEN_VIEN',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'ChuyenVien@123'
        },
        {
            'ten_dang_nhap': 'hoangnm',
            'ho_va_ten': 'Nguyễn Minh Hoàng',
            'email': 'hoangnm@danang.edu.vn',
            'sdt': '0905.777.666',
            'phong_ban': 'Phòng Khảo thí & Quản lý chất lượng',
            'chuc_vu': 'Chuyên viên khảo thí',
            'vai_tro': 'CHUYEN_VIEN',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'ChuyenVien@123'
        },
        {
            'ten_dang_nhap': 'lanpt',
            'ho_va_ten': 'Phan Thị Lan',
            'email': 'lanpt@danang.edu.vn',
            'sdt': '0918.222.333',
            'phong_ban': 'Phòng Giáo dục Mầm non - Tiểu học',
            'chuc_vu': 'Chuyên viên mầm non',
            'vai_tro': 'CHUYEN_VIEN',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'ChuyenVien@123'
        }
    ]

    for item in users_data:
        pw = item.pop('mat_khau')
        user, _ = NguoiDung.objects.get_or_create(ten_dang_nhap=item['ten_dang_nhap'], defaults=item)
        user.ho_va_ten = item['ho_va_ten']
        user.email = item['email']
        user.sdt = item['sdt']
        user.phong_ban = item['phong_ban']
        user.chuc_vu = item['chuc_vu']
        user.vai_tro = item['vai_tro']
        user.trang_thai = item['trang_thai']
        user.set_password(pw)
        user.save()

    u_vanthu = NguoiDung.objects.get(ten_dang_nhap='admin_vanthu')
    u_giamdoc = NguoiDung.objects.get(ten_dang_nhap='giamdoc_so')
    u_phogd = NguoiDung.objects.get(ten_dang_nhap='phogiamdoc_so')
    u_nam = NguoiDung.objects.get(ten_dang_nhap='minhcv')
    u_thao = NguoiDung.objects.get(ten_dang_nhap='thaoltk')
    u_dung = NguoiDung.objects.get(ten_dang_nhap='dungpt')
    u_hoang = NguoiDung.objects.get(ten_dang_nhap='hoangnm')
    u_lan = NguoiDung.objects.get(ten_dang_nhap='lanpt')
    print(f"[OK] Đã thiết lập {NguoiDung.objects.count()} tài khoản nhân sự Sở GD&ĐT.")

    # 3. VĂN BẢN ĐẾN (15 văn bản)
    van_ban_den_samples = [
        {
            'so_den': 1,
            'so_ky_hieu': '142/BGDĐT-GDTrH',
            'co_quan_ban_hanh': 'Bộ Giáo dục và Đào tạo',
            'ngay_ban_hanh': date(2026, 10, 25),
            'ngay_den': date(2026, 10, 27),
            'trich_yeu': 'V/v hướng dẫn tổ chức Kỳ thi tốt nghiệp Trung học phổ thông năm 2026 theo Chương trình GDPT 2018',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Khẩn',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_giamdoc,
            'nguoi_chu_tri': u_nam,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 20),
            'noi_dung_chi_dao': 'Giao Phòng GDTrH chủ trì nghiên cứu, lập kế hoạch chi tiết tập huấn cho các trường THPT toàn thành phố.'
        },
        {
            'so_den': 2,
            'so_ky_hieu': '88/UBND-VX',
            'co_quan_ban_hanh': 'Ủy ban nhân dân thành phố Đà Nẵng',
            'ngay_ban_hanh': date(2026, 10, 28),
            'ngay_den': date(2026, 10, 29),
            'trich_yeu': 'Về việc phân bổ kinh phí đầu tư cơ sở vật chất, thiết bị phòng học thông minh năm học 2026-2027',
            'loai_van_ban': 'Quyết định',
            'do_khan': 'Thượng khẩn',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_phogd,
            'nguoi_chu_tri': u_thao,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 15),
            'noi_dung_chi_dao': 'Phòng KHTC khẩn trương rà soát danh mục các trường THCS và THPT cần bổ sung thiết bị tương tác số.'
        },
        {
            'so_den': 3,
            'so_ky_hieu': '45/STTTT-CNTT',
            'co_quan_ban_hanh': 'Sở Thông tin và Truyền thông TP. Đà Nẵng',
            'ngay_ban_hanh': date(2026, 10, 30),
            'ngay_den': date(2026, 11, 1),
            'trich_yeu': 'Hướng dẫn bảo đảm an toàn thông tin mạng và chuyển đổi số trong cơ quan hành chính nhà nước dịp cuối năm 2026',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Bình thường',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_giamdoc,
            'nguoi_chu_tri': u_nam,
            'trang_thai': 'CHO_PHAN_CONG',
            'han_xu_ly': date(2026, 11, 30),
            'noi_dung_chi_dao': 'Văn phòng Sở phối hợp kiểm tra định kỳ hệ thống máy chủ và dữ liệu.'
        },
        {
            'so_den': 4,
            'so_ky_hieu': '512/SNV-TCBC',
            'co_quan_ban_hanh': 'Sở Nội vụ thành phố Đà Nẵng',
            'ngay_ban_hanh': date(2026, 11, 2),
            'ngay_den': date(2026, 11, 3),
            'trich_yeu': 'V/v thẩm định kế hoạch tuyển dụng bổ sung viên chức giáo dục năm học 2026-2027',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Bình thường',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_giamdoc,
            'nguoi_chu_tri': u_dung,
            'trang_thai': 'CHO_TIEP_NHAN',
            'han_xu_ly': date(2026, 12, 5),
            'noi_dung_chi_dao': 'Phòng TCCB chuẩn bị đầy đủ hồ sơ theo đề cương.'
        },
        {
            'so_den': 5,
            'so_ky_hieu': '203/BYT-DP',
            'co_quan_ban_hanh': 'Bộ Y tế',
            'ngay_ban_hanh': date(2026, 11, 5),
            'ngay_den': date(2026, 11, 6),
            'trich_yeu': 'Tăng cường công tác y tế trường học và phòng chống dịch bệnh mùa đông - xuân trong các cơ sở giáo dục',
            'loai_van_ban': 'Chỉ thị',
            'do_khan': 'Hỏa tốc',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_phogd,
            'nguoi_chu_tri': u_nam,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 12),
            'noi_dung_chi_dao': 'Ban hành văn bản khẩn gửi tất cả các trường học trên toàn địa bàn thành phố.'
        },
        {
            'so_den': 6,
            'so_ky_hieu': '105/BGDĐT-GDMN',
            'co_quan_ban_hanh': 'Bộ Giáo dục và Đào tạo',
            'ngay_ban_hanh': date(2026, 10, 15),
            'ngay_den': date(2026, 10, 17),
            'trich_yeu': 'V/v triển khai chương trình thí điểm cho trẻ mẫu giáo làm quen với tiếng Anh theo Thông tư mới',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Bình thường',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_phogd,
            'nguoi_chu_tri': u_lan,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 18),
            'noi_dung_chi_dao': 'Phòng GDMN-TH khảo sát các trường mầm non công lập đủ điều kiện tham gia thí điểm.'
        },
        {
            'so_den': 7,
            'so_ky_hieu': '215/UBND-TH',
            'co_quan_ban_hanh': 'Ủy ban nhân dân thành phố Đà Nẵng',
            'ngay_ban_hanh': date(2026, 10, 18),
            'ngay_den': date(2026, 10, 20),
            'trich_yeu': 'Chỉ đạo tăng cường bảo đảm trật tự an toàn giao thông trước cổng trường học năm học 2026-2027',
            'loai_van_ban': 'Chỉ thị',
            'do_khan': 'Khẩn',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_giamdoc,
            'nguoi_chu_tri': u_nam,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 15),
            'noi_dung_chi_dao': 'Phối hợp Công an thành phố và Thành Đoàn duy trì mô hình Cổng trường an toàn văn minh.'
        },
        {
            'so_den': 8,
            'so_ky_hieu': '789/STC-HCSN',
            'co_quan_ban_hanh': 'Sở Tài chính TP. Đà Nẵng',
            'ngay_ban_hanh': date(2026, 10, 22),
            'ngay_den': date(2026, 10, 24),
            'trich_yeu': 'Hướng dẫn xây dựng dự toán ngân sách nhà nước lĩnh vực giáo dục và đào tạo năm tài chính 2027',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Bình thường',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_phogd,
            'nguoi_chu_tri': u_thao,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 25),
            'noi_dung_chi_dao': 'Phòng KHTC hướng dẫn các đơn vị trực thuộc lập dự toán chi lương và chi chuyên môn.'
        },
        {
            'so_den': 9,
            'so_ky_hieu': '56/BGDĐT-QLCL',
            'co_quan_ban_hanh': 'Bộ Giáo dục và Đào tạo',
            'ngay_ban_hanh': date(2026, 10, 26),
            'ngay_den': date(2026, 10, 28),
            'trich_yeu': 'Kế hoạch kiểm tra công tác quản lý văn bằng, chứng chỉ và liên kết đào tạo ngoại ngữ, tin học năm 2026',
            'loai_van_ban': 'Kế hoạch',
            'do_khan': 'Khẩn',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_giamdoc,
            'nguoi_chu_tri': u_hoang,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 20),
            'noi_dung_chi_dao': 'Giao Phòng Quản lý chất lượng lập danh sách các trung tâm ngoại ngữ cần kiểm tra đột xuất.'
        },
        {
            'so_den': 10,
            'so_ky_hieu': '1024/CATP-PA03',
            'co_quan_ban_hanh': 'Công an thành phố Đà Nẵng',
            'ngay_ban_hanh': date(2026, 10, 29),
            'ngay_den': date(2026, 10, 31),
            'trich_yeu': 'Thông báo thủ đoạn lừa đảo công nghệ cao giả danh giáo viên, nhân viên y tế cấp cứu học sinh',
            'loai_van_ban': 'Thông báo',
            'do_khan': 'Thượng khẩn',
            'do_mat': 'Mật',
            'nguoi_chi_dao': u_giamdoc,
            'nguoi_chu_tri': u_nam,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 10),
            'noi_dung_chi_dao': 'Gửi công văn khẩn đến 100% trường học quán triệt phụ huynh nâng cao cảnh giác.'
        },
        {
            'so_den': 11,
            'so_ky_hieu': '312/BGDĐT-CTHSSV',
            'co_quan_ban_hanh': 'Bộ Giáo dục và Đào tạo',
            'ngay_ban_hanh': date(2026, 11, 1),
            'ngay_den': date(2026, 11, 2),
            'trich_yeu': 'Hướng dẫn tổ chức hoạt động tư vấn tâm lý học đường và công tác xã hội trong trường học năm 2026-2027',
            'loai_van_ban': 'Hướng dẫn',
            'do_khan': 'Bình thường',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_phogd,
            'nguoi_chu_tri': u_nam,
            'trang_thai': 'CHO_PHAN_CONG',
            'han_xu_ly': date(2026, 12, 1),
            'noi_dung_chi_dao': 'Nghiên cứu mô hình phòng tư vấn tâm lý học đường kiểu mẫu tại các trường THPT.'
        },
        {
            'so_den': 12,
            'so_ky_hieu': '65/LĐLĐ-CSPL',
            'co_quan_ban_hanh': 'Liên đoàn Lao động TP. Đà Nẵng',
            'ngay_ban_hanh': date(2026, 11, 3),
            'ngay_den': date(2026, 11, 4),
            'trich_yeu': 'V/v chăm lo đời sống, thăm hỏi cán bộ, nhà giáo và người lao động có hoàn cảnh khó khăn dịp Tết 2027',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Bình thường',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_giamdoc,
            'nguoi_chu_tri': u_dung,
            'trang_thai': 'CHO_TIEP_NHAN',
            'han_xu_ly': date(2026, 12, 10),
            'noi_dung_chi_dao': 'Phòng TCCB phối hợp Công đoàn ngành lập danh sách đối tượng hỗ trợ.'
        },
        {
            'so_den': 13,
            'so_ky_hieu': '430/SKHCN-QLKH',
            'co_quan_ban_hanh': 'Sở Khoa học và Công nghệ TP. Đà Nẵng',
            'ngay_ban_hanh': date(2026, 11, 4),
            'ngay_den': date(2026, 11, 5),
            'trich_yeu': 'Thông báo tiếp nhận hồ sơ đề tài nghiên cứu khoa học và sáng kiến kinh nghiệm cấp thành phố năm 2026',
            'loai_van_ban': 'Thông báo',
            'do_khan': 'Bình thường',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_phogd,
            'nguoi_chu_tri': u_hoang,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 30),
            'noi_dung_chi_dao': 'Phòng QLCL thông báo đến các nhà giáo có đề tài đăng ký đúng hạn.'
        },
        {
            'so_den': 14,
            'so_ky_hieu': '18/BGDĐT-TCCB',
            'co_quan_ban_hanh': 'Bộ Giáo dục và Đào tạo',
            'ngay_ban_hanh': date(2026, 11, 6),
            'ngay_den': date(2026, 11, 7),
            'trich_yeu': 'V/v rà soát quy hoạch phát triển mạng lưới cơ sở giáo dục đại học và sư phạm trên địa bàn miền Trung',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Bình thường',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_giamdoc,
            'nguoi_chu_tri': u_dung,
            'trang_thai': 'CHO_TIEP_NHAN',
            'han_xu_ly': date(2026, 12, 15),
            'noi_dung_chi_dao': 'Phòng TCCB chuẩn bị số liệu liên kết đào tạo cử nhân sư phạm.'
        },
        {
            'so_den': 15,
            'so_ky_hieu': '92/HĐND-VHXH',
            'co_quan_ban_hanh': 'Ban Văn hóa - Xã hội HĐND TP. Đà Nẵng',
            'ngay_ban_hanh': date(2026, 11, 7),
            'ngay_den': date(2026, 11, 8),
            'trich_yeu': 'Kế hoạch giám sát tình hình thực hiện chính sách miễn giảm học phí cho học sinh các cấp năm học 2026-2027',
            'loai_van_ban': 'Kế hoạch',
            'do_khan': 'Khẩn',
            'do_mat': 'Thường',
            'nguoi_chi_dao': u_giamdoc,
            'nguoi_chu_tri': u_thao,
            'trang_thai': 'DANG_XU_LY',
            'han_xu_ly': date(2026, 11, 22),
            'noi_dung_chi_dao': 'Phòng KHTC chuẩn bị báo cáo số liệu giải ngân kinh phí cấp bù học phí.'
        }
    ]

    for item in van_ban_den_samples:
        vb, _ = VanBanDen.objects.get_or_create(so_ky_hieu=item['so_ky_hieu'], defaults=item)
        for k, v in item.items():
            setattr(vb, k, v)
        vb.save()
    print(f"[OK] Đã nạp {VanBanDen.objects.count()} Văn bản đến.")

    # 4. VĂN BẢN ĐI (15 văn bản)
    van_ban_di_samples = [
        {
            'so_ky_hieu': '125/SGDĐT-GDTrH',
            'trich_yeu': 'V/v hướng dẫn tổ chức Kỳ thi chọn học sinh giỏi cấp thành phố năm học 2026-2027',
            'loai_van_ban': 'Hướng dẫn',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Phòng Giáo dục Trung học',
            'noi_nhan': 'Các trường THPT trên địa bàn thành phố',
            'noi_dung_tom_tat': 'Kế hoạch, lịch thi và quy chế thi học sinh giỏi các môn văn hóa lớp 9 và 12.',
            'nguoi_soan': u_nam,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_giamdoc,
            'lanh_dao_ky_ten': u_giamdoc.ho_va_ten,
            'trang_thai': 'DA_BAN_HANH'
        },
        {
            'so_ky_hieu': '1205/SGDĐT-VP',
            'trich_yeu': 'Kế hoạch tổ chức Tuần lễ hưởng ứng học tập suốt đời năm 2026 trên địa bàn TP. Đà Nẵng',
            'loai_van_ban': 'Kế hoạch',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Văn phòng Sở',
            'noi_nhan': 'UBND các quận/huyện, các trường học, TT GDTX',
            'noi_dung_tom_tat': 'Phát động phong trào tự học và chuyển đổi số phục vụ học tập suốt đời.',
            'nguoi_soan': u_nam,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_phogd,
            'lanh_dao_ky_ten': u_phogd.ho_va_ten,
            'trang_thai': 'DA_BAN_HANH'
        },
        {
            'so_ky_hieu': '342/QĐ-SGDĐT',
            'trich_yeu': 'Quyết định thành lập Đoàn kiểm tra công tác kiểm định chất lượng giáo dục tại các cơ sở giáo dục mầm non, phổ thông',
            'loai_van_ban': 'Quyết định',
            'do_khan': 'Khẩn',
            'don_vi_soan_thao': 'Phòng Quản lý chất lượng',
            'noi_nhan': 'Như Điều 3, Lưu VT, QLCL',
            'noi_dung_tom_tat': 'Thành lập đoàn đánh giá ngoài gồm 12 thành viên tiến hành khảo sát từ tháng 11/2026.',
            'nguoi_soan': u_thao,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_giamdoc,
            'lanh_dao_ky_ten': u_giamdoc.ho_va_ten,
            'trang_thai': 'DA_BAN_HANH'
        },
        {
            'so_ky_hieu': '89/TTr-SGDĐT',
            'trich_yeu': 'Tờ trình UBND thành phố về việc phê duyệt Đề án Chuyển đổi số ngành Giáo dục TP. Đà Nẵng giai đoạn 2026-2030',
            'loai_van_ban': 'Tờ trình',
            'do_khan': 'Khẩn',
            'don_vi_soan_thao': 'Phòng Kế hoạch - Tài chính',
            'noi_nhan': 'UBND TP. Đà Nẵng, Sở Tài chính, Sở Thông tin và Truyền thông',
            'noi_dung_tom_tat': 'Đề xuất bố trí kinh phí trang bị hệ thống quản lý dữ liệu số tập trung ngành GD&ĐT.',
            'nguoi_soan': u_thao,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_giamdoc,
            'lanh_dao_ky_ten': u_giamdoc.ho_va_ten,
            'trang_thai': 'CHO_LANH_DAO_KY'
        },
        {
            'so_ky_hieu': '76/CV-SGDĐT',
            'trich_yeu': 'V/v báo cáo thống kê tình hình đội ngũ nhà giáo và cán bộ quản lý giáo dục đầu năm học 2026-2027',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Phòng Tổ chức cán bộ',
            'noi_nhan': 'Bộ Giáo dục và Đào tạo (Cục Nhà giáo)',
            'noi_dung_tom_tat': 'Tổng hợp số liệu biên chế giáo viên các bậc mầm non, tiểu học, THCS và THPT.',
            'nguoi_soan': u_dung,
            'van_thu': u_vanthu,
            'lanh_dao_ky': None,
            'lanh_dao_ky_ten': None,
            'trang_thai': 'CHO_VAN_THU_KIEM_TRA'
        },
        {
            'so_ky_hieu': '1310/SGDĐT-GDMN',
            'trich_yeu': 'V/v tăng cường quản lý an toàn vệ sinh thực phẩm và tổ chức bữa ăn bán trú tại các cơ sở giáo dục mầm non',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Khẩn',
            'don_vi_soan_thao': 'Phòng Giáo dục Mầm non - Tiểu học',
            'noi_nhan': 'Phòng GD&ĐT các quận, huyện; các trường mầm non',
            'noi_dung_tom_tat': 'Yêu cầu 100% bếp ăn bán trú có hợp đồng thực phẩm rõ nguồn gốc, lưu mẫu 24h đúng quy định.',
            'nguoi_soan': u_lan,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_phogd,
            'lanh_dao_ky_ten': u_phogd.ho_va_ten,
            'trang_thai': 'DA_BAN_HANH'
        },
        {
            'so_ky_hieu': '450/QĐ-SGDĐT',
            'trich_yeu': 'Quyết định khen thưởng các tập thể, cá nhân có thành tích xuất sắc trong phong trào thi đua dạy tốt học tốt đợt 20/11',
            'loai_van_ban': 'Quyết định',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Phòng Tổ chức cán bộ',
            'noi_nhan': 'Các phòng thuộc Sở, các tập thể cá nhân có tên tại Điều 1',
            'noi_dung_tom_tat': 'Tặng giấy khen Giám đốc Sở cho 25 tập thể và 80 cá nhân xuất sắc tiêu biểu.',
            'nguoi_soan': u_dung,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_giamdoc,
            'lanh_dao_ky_ten': u_giamdoc.ho_va_ten,
            'trang_thai': 'DA_BAN_HANH'
        },
        {
            'so_ky_hieu': '1322/SGDĐT-VP',
            'trich_yeu': 'Thông báo kết luận của Giám đốc Sở GD&ĐT tại cuộc họp giao ban công tác chuyên môn tháng 10/2026',
            'loai_van_ban': 'Thông báo',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Văn phòng Sở',
            'noi_nhan': 'Ban Giám đốc Sở, các phòng chuyên môn',
            'noi_dung_tom_tat': 'Chỉ đạo trọng tâm: đẩy mạnh chuyển đổi số, tổ chức ôn tập cho học sinh khối 12 và đảm bảo an ninh trường học.',
            'nguoi_soan': u_vanthu,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_giamdoc,
            'lanh_dao_ky_ten': u_giamdoc.ho_va_ten,
            'trang_thai': 'DA_BAN_HANH'
        },
        {
            'so_ky_hieu': '95/TTr-SGDĐT',
            'trich_yeu': 'Tờ trình đề nghị UBND thành phố phê duyệt chủ trương mở rộng khuôn viên Trường THPT chuyên Lê Quý Đôn',
            'loai_van_ban': 'Tờ trình',
            'do_khan': 'Khẩn',
            'don_vi_soan_thao': 'Phòng Kế hoạch - Tài chính',
            'noi_nhan': 'UBND TP. Đà Nẵng, Sở Xây dựng, Sở Tài nguyên và Môi trường',
            'noi_dung_tom_tat': 'Quy hoạch bổ sung 1.5 ha xây dựng khu ký túc xá và nhà tập luyện thể thao đa năng.',
            'nguoi_soan': u_thao,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_giamdoc,
            'lanh_dao_ky_ten': u_giamdoc.ho_va_ten,
            'trang_thai': 'CHO_LANH_DAO_KY'
        },
        {
            'so_ky_hieu': '82/CV-SGDĐT',
            'trich_yeu': 'Hướng dẫn các cơ sở giáo dục thực hiện công khai tài chính và các khoản thu hộ, chi hộ đầu năm học 2026-2027',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Phòng Kế hoạch - Tài chính',
            'noi_nhan': 'Tất cả các trường mầm non, phổ thông trên địa bàn',
            'noi_dung_tom_tat': 'Nghiêm cấm lạm thu dưới mọi hình thức, yêu cầu thanh toán không dùng tiền mặt 100%.',
            'nguoi_soan': u_thao,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_phogd,
            'lanh_dao_ky_ten': u_phogd.ho_va_ten,
            'trang_thai': 'DA_KY_CHO_BAN_HANH'
        },
        {
            'so_ky_hieu': '1340/SGDĐT-QLCL',
            'trich_yeu': 'Hướng dẫn đăng ký dự thi và sử dụng phần mềm quản lý thi tốt nghiệp THPT năm 2026',
            'loai_van_ban': 'Hướng dẫn',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Phòng Khảo thí & Quản lý chất lượng',
            'noi_nhan': 'Các trường THPT, TT GDTX-GDHN',
            'noi_dung_tom_tat': 'Quy trình cấp tài khoản cho thí sinh, kiểm tra chéo dữ liệu CCCD và mã định danh VNeID.',
            'nguoi_soan': u_hoang,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_giamdoc,
            'lanh_dao_ky_ten': u_giamdoc.ho_va_ten,
            'trang_thai': 'CHO_LANH_DAO_KY'
        },
        {
            'so_ky_hieu': '85/CV-SGDĐT',
            'trich_yeu': 'Kế hoạch phối hợp tổ chức Cuộc thi Sáng tạo Khoa học kỹ thuật dành cho học sinh trung học năm 2026-2027',
            'loai_van_ban': 'Công văn',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Phòng Giáo dục Trung học',
            'noi_nhan': 'Đại học Đà Nẵng, Sở Khoa học & Công nghệ, các trường THPT',
            'noi_dung_tom_tat': 'Thể lệ cuộc thi, các lĩnh vực dự thi và thời hạn nộp báo cáo nghiên cứu trước ngày 20/12.',
            'nguoi_soan': u_nam,
            'van_thu': u_vanthu,
            'lanh_dao_ky': None,
            'lanh_dao_ky_ten': None,
            'trang_thai': 'CHO_VAN_THU_KIEM_TRA'
        },
        {
            'so_ky_hieu': '462/QĐ-SGDĐT',
            'trich_yeu': 'Quyết định điều động, bổ nhiệm viên chức quản lý các trường THPT công lập trực thuộc Sở GD&ĐT',
            'loai_van_ban': 'Quyết định',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Phòng Tổ chức cán bộ',
            'noi_nhan': 'Các trường THPT liên quan, cá nhân có tên tại Điều 1',
            'noi_dung_tom_tat': 'Bổ nhiệm 03 Hiệu trưởng và 05 Phó Hiệu trưởng các trường THPT Phan Châu Trinh, Hoàng Hoa Thám.',
            'nguoi_soan': u_dung,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_giamdoc,
            'lanh_dao_ky_ten': u_giamdoc.ho_va_ten,
            'trang_thai': 'CHO_LANH_DAO_KY'
        },
        {
            'so_ky_hieu': '1355/SGDĐT-GDTrH',
            'trich_yeu': 'Kế hoạch tổ chức Ngày hội Giáo dục STEM và Cuộc thi Robocon ngành Giáo dục Đà Nẵng năm học 2026-2027',
            'loai_van_ban': 'Kế hoạch',
            'do_khan': 'Bình thường',
            'don_vi_soan_thao': 'Phòng Giáo dục Trung học',
            'noi_nhan': 'Các trường THCS, THPT toàn thành phố',
            'noi_dung_tom_tat': 'Thời gian tổ chức dự kiến tháng 01/2027 tại Cung Thể thao Tiên Sơn.',
            'nguoi_soan': u_nam,
            'van_thu': u_vanthu,
            'lanh_dao_ky': None,
            'lanh_dao_ky_ten': None,
            'trang_thai': 'CHO_VAN_THU_KIEM_TRA'
        },
        {
            'so_ky_hieu': '91/TTr-SGDĐT',
            'trich_yeu': 'Tờ trình xin chủ trương đầu tư dự án Xây dựng hệ thống Học bạ số và Chứng chỉ số toàn diện ngành Giáo dục',
            'loai_van_ban': 'Tờ trình',
            'do_khan': 'Khẩn',
            'don_vi_soan_thao': 'Phòng Kế hoạch - Tài chính',
            'noi_nhan': 'UBND TP. Đà Nẵng, Sở Tài chính, Sở Thông tin và Truyền thông',
            'noi_dung_tom_tat': 'Triển khai công nghệ Blockchain lưu trữ học bạ số chống làm giả và liên thông cơ sở dữ liệu quốc gia.',
            'nguoi_soan': u_thao,
            'van_thu': u_vanthu,
            'lanh_dao_ky': u_giamdoc,
            'lanh_dao_ky_ten': u_giamdoc.ho_va_ten,
            'trang_thai': 'CHO_LANH_DAO_KY'
        }
    ]

    for item in van_ban_di_samples:
        vb, _ = VanBanDi.objects.get_or_create(so_ky_hieu=item['so_ky_hieu'], defaults=item)
        for k, v in item.items():
            setattr(vb, k, v)
        vb.save()
    print(f"[OK] Đã nạp {VanBanDi.objects.count()} Văn bản đi.")

    # 5. CÔNG VIỆC PHÂN CÔNG (15 công việc)
    cong_viec_samples = [
        {
            'ten_cong_viec': 'Rà soát cơ sở vật chất phục vụ thi tốt nghiệp THPT năm 2026',
            'noi_dung': 'Kiểm tra hệ thống phòng thi, camera giám sát, máy phát điện dự phòng tại 28 điểm thi.',
            'nguoi_giao': u_giamdoc,
            'nguoi_xu_ly': u_nam,
            'phong_ban': 'Phòng Giáo dục Trung học',
            'han_hoan_thanh': date(2026, 11, 25),
            'do_uu_tien': 'CAO',
            'tien_do': 80,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '142/BGDĐT-GDTrH',
            'trich_yeu_vb': 'V/v hướng dẫn tổ chức Kỳ thi tốt nghiệp THPT 2026'
        },
        {
            'ten_cong_viec': 'Xây dựng dự toán kinh phí trang bị phòng học thông minh năm học 2026-2027',
            'noi_dung': 'Khảo sát nhu cầu của 15 trường THPT, tổng hợp danh mục thiết bị và báo giá chi tiết.',
            'nguoi_giao': u_phogd,
            'nguoi_xu_ly': u_thao,
            'phong_ban': 'Phòng Kế hoạch - Tài chính',
            'han_hoan_thanh': date(2026, 11, 18),
            'do_uu_tien': 'CAO',
            'tien_do': 50,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '88/UBND-VX',
            'trich_yeu_vb': 'Phân bổ kinh phí thiết bị phòng học thông minh'
        },
        {
            'ten_cong_viec': 'Tổng hợp hồ sơ đề nghị công nhận trường đạt chuẩn quốc gia mức độ 2',
            'noi_dung': 'Thẩm định minh chứng 5 tiêu chuẩn của 04 trường THCS tại quận Hải Châu và Sơn Trà.',
            'nguoi_giao': u_giamdoc,
            'nguoi_xu_ly': u_nam,
            'phong_ban': 'Phòng Giáo dục Trung học',
            'han_hoan_thanh': date(2026, 11, 12),
            'do_uu_tien': 'TRUNG_BINH',
            'tien_do': 100,
            'trang_thai': 'CHO_PHE_DUYET',
            'ket_qua_bao_cao': 'Đã hoàn tất báo cáo thẩm định, đủ điều kiện trình Giám đốc Sở ký phê duyệt.',
            'so_ky_hieu_vb': '342/QĐ-SGDĐT',
            'trich_yeu_vb': 'Đoàn kiểm tra kiểm định chất lượng giáo dục'
        },
        {
            'ten_cong_viec': 'Tổ chức tập huấn an toàn thông tin và kỹ năng số cho cán bộ cơ quan',
            'noi_dung': 'Liên hệ chuyên gia Sở TT&TT, chuẩn bị hội trường và tài liệu phát tay cho 80 cán bộ.',
            'nguoi_giao': u_phogd,
            'nguoi_xu_ly': u_dung,
            'phong_ban': 'Phòng Tổ chức cán bộ',
            'han_hoan_thanh': date(2026, 11, 10),
            'do_uu_tien': 'THAP',
            'tien_do': 100,
            'trang_thai': 'DA_HOAN_THANH',
            'ket_qua_bao_cao': 'Lớp tập huấn diễn ra thành công vào ngày 08/11/2026 với 85/85 cán bộ tham gia.',
            'danh_gia_lanh_dao': 'Hoàn thành tốt, đúng tiến độ.'
        },
        {
            'ten_cong_viec': 'Báo cáo số liệu đội ngũ nhà giáo phục vụ kế hoạch tuyển dụng năm 2027',
            'noi_dung': 'Rà soát tỷ lệ giáo viên/lớp theo Thông tư 20/2023/TT-BGDĐT để xác định chỉ tiêu tuyển dụng.',
            'nguoi_giao': u_giamdoc,
            'nguoi_xu_ly': u_dung,
            'phong_ban': 'Phòng Tổ chức cán bộ',
            'han_hoan_thanh': date(2026, 12, 1),
            'do_uu_tien': 'TRUNG_BINH',
            'tien_do': 30,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '512/SNV-TCBC',
            'trich_yeu_vb': 'Thẩm định kế hoạch tuyển dụng viên chức GD'
        },
        {
            'ten_cong_viec': 'Thẩm định danh mục sách giáo khoa lớp 12 lựa chọn cho năm học 2026-2027',
            'noi_dung': 'Tổng hợp biên bản lựa chọn SGK từ 32 trường THPT, báo cáo Hội đồng lựa chọn SGK thành phố.',
            'nguoi_giao': u_giamdoc,
            'nguoi_xu_ly': u_nam,
            'phong_ban': 'Phòng Giáo dục Trung học',
            'han_hoan_thanh': date(2026, 11, 28),
            'do_uu_tien': 'CAO',
            'tien_do': 65,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '125/SGDĐT-GDTrH',
            'trich_yeu_vb': 'Hướng dẫn chuyên môn năm học mới'
        },
        {
            'ten_cong_viec': 'Kiểm tra công tác bán trú và an toàn vệ sinh thực phẩm tại 20 trường mầm non trọng điểm',
            'noi_dung': 'Kiểm tra đột xuất nguồn gốc thực phẩm, giấy khám sức khỏe nhân viên cấp dưỡng và quy trình lưu mẫu thức ăn.',
            'nguoi_giao': u_phogd,
            'nguoi_xu_ly': u_lan,
            'phong_ban': 'Phòng Giáo dục Mầm non - Tiểu học',
            'han_hoan_thanh': date(2026, 11, 19),
            'do_uu_tien': 'CAO',
            'tien_do': 40,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '1310/SGDĐT-GDMN',
            'trich_yeu_vb': 'An toàn vệ sinh thực phẩm bếp ăn bán trú'
        },
        {
            'ten_cong_viec': 'Quyết toán kinh phí tổ chức Hội thi giáo viên dạy giỏi cấp thành phố năm 2026',
            'noi_dung': 'Kiểm tra chứng từ bồi dưỡng ban giám khảo, thuê địa điểm thi thực hành và in ấn tài liệu.',
            'nguoi_giao': u_phogd,
            'nguoi_xu_ly': u_thao,
            'phong_ban': 'Phòng Kế hoạch - Tài chính',
            'han_hoan_thanh': date(2026, 11, 15),
            'do_uu_tien': 'TRUNG_BINH',
            'tien_do': 90,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '789/STC-HCSN',
            'trich_yeu_vb': 'Hướng dẫn dự toán ngân sách giáo dục'
        },
        {
            'ten_cong_viec': 'Lập danh sách cán bộ, giáo viên tiêu biểu nhận Kỷ niệm chương Vì sự nghiệp Giáo dục',
            'noi_dung': 'Thẩm định hồ sơ thâm niên 20 năm công tác đối với nữ và 25 năm đối với nam của 115 giáo viên.',
            'nguoi_giao': u_giamdoc,
            'nguoi_xu_ly': u_dung,
            'phong_ban': 'Phòng Tổ chức cán bộ',
            'han_hoan_thanh': date(2026, 11, 17),
            'do_uu_tien': 'TRUNG_BINH',
            'tien_do': 100,
            'trang_thai': 'CHO_PHE_DUYET',
            'ket_qua_bao_cao': 'Đã hoàn tất danh sách 115 hồ sơ đủ điều kiện gửi Bộ GD&ĐT đề nghị tặng Kỷ niệm chương.',
            'so_ky_hieu_vb': '450/QĐ-SGDĐT',
            'trich_yeu_vb': 'Khen thưởng phong trào thi đua 20/11'
        },
        {
            'ten_cong_viec': 'Rà soát chứng chỉ chức danh nghề nghiệp giáo viên các trường THPT trực thuộc',
            'noi_dung': 'Tổng hợp số lượng giáo viên hạng II, hạng III cần học bổ sung chứng chỉ theo chùm Thông tư 08/2023/TT-BGDĐT.',
            'nguoi_giao': u_phogd,
            'nguoi_xu_ly': u_dung,
            'phong_ban': 'Phòng Tổ chức cán bộ',
            'han_hoan_thanh': date(2026, 12, 5),
            'do_uu_tien': 'THAP',
            'tien_do': 20,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '18/BGDĐT-TCCB',
            'trich_yeu_vb': 'Quy hoạch phát triển đội ngũ sư phạm'
        },
        {
            'ten_cong_viec': 'Triển khai khảo sát mức độ hài lòng của phụ huynh đối với dịch vụ giáo dục công lập',
            'noi_dung': 'Phát phiếu khảo sát trực tuyến qua ứng dụng Danang Smart City cho 15.000 phụ huynh học sinh.',
            'nguoi_giao': u_giamdoc,
            'nguoi_xu_ly': u_hoang,
            'phong_ban': 'Phòng Khảo thí & Quản lý chất lượng',
            'han_hoan_thanh': date(2026, 12, 10),
            'do_uu_tien': 'TRUNG_BINH',
            'tien_do': 15,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '56/BGDĐT-QLCL',
            'trich_yeu_vb': 'Kiểm tra công tác quản lý chất lượng'
        },
        {
            'ten_cong_viec': 'Tổ chức cuộc thi Thiết kế bài giảng điện tử E-learning cấp thành phố',
            'noi_dung': 'Chấm thi 280 sản phẩm bài giảng số của giáo viên, tuyển chọn 30 bài xuất sắc vào kho học liệu số thành phố.',
            'nguoi_giao': u_phogd,
            'nguoi_xu_ly': u_nam,
            'phong_ban': 'Phòng Giáo dục Trung học',
            'han_hoan_thanh': date(2026, 11, 30),
            'do_uu_tien': 'CAO',
            'tien_do': 85,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '89/TTr-SGDĐT',
            'trich_yeu_vb': 'Đề án Chuyển đổi số ngành Giáo dục'
        },
        {
            'ten_cong_viec': 'Phối hợp Công an thành phố kiểm tra công tác phòng cháy chữa cháy tại các trường học',
            'noi_dung': 'Kiểm tra hệ thống vòi cứu hỏa, bình bọt, cầu thang thoát hiểm và tổ chức diễn tập tại 10 trường THPT.',
            'nguoi_giao': u_phogd,
            'nguoi_xu_ly': u_thao,
            'phong_ban': 'Phòng Kế hoạch - Tài chính',
            'han_hoan_thanh': date(2026, 11, 22),
            'do_uu_tien': 'KHAM_CAP',
            'tien_do': 70,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '215/UBND-TH',
            'trich_yeu_vb': 'Chỉ đạo an toàn trường học'
        },
        {
            'ten_cong_viec': 'Xây dựng kế hoạch tuyển sinh đầu cấp các lớp 1, 6, 10 năm học 2027-2028',
            'noi_dung': 'Khảo sát dự báo số lượng học sinh tốt nghiệp tiểu học và THCS trên từng địa bàn quận/huyện để phân luồng.',
            'nguoi_giao': u_giamdoc,
            'nguoi_xu_ly': u_nam,
            'phong_ban': 'Phòng Giáo dục Trung học',
            'han_hoan_thanh': date(2026, 12, 15),
            'do_uu_tien': 'CAO',
            'tien_do': 10,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '1355/SGDĐT-GDTrH',
            'trich_yeu_vb': 'Kế hoạch phát triển mạng lưới trường lớp'
        },
        {
            'ten_cong_viec': 'Báo cáo tổng kết công tác phòng chống tham nhũng, lãng phí ngành Giáo dục năm 2026',
            'noi_dung': 'Tổng hợp kết quả thanh tra, kiểm tra tài chính và quản lý tài sản công gửi Thanh tra thành phố.',
            'nguoi_giao': u_giamdoc,
            'nguoi_xu_ly': u_dung,
            'phong_ban': 'Phòng Tổ chức cán bộ',
            'han_hoan_thanh': date(2026, 12, 20),
            'do_uu_tien': 'TRUNG_BINH',
            'tien_do': 25,
            'trang_thai': 'DANG_THUC_HIEN',
            'so_ky_hieu_vb': '82/CV-SGDĐT',
            'trich_yeu_vb': 'Công khai tài chính và tài sản công'
        }
    ]

    for item in cong_viec_samples:
        cv, _ = CongViec.objects.get_or_create(ten_cong_viec=item['ten_cong_viec'], defaults=item)
        for k, v in item.items():
            setattr(cv, k, v)
        cv.save()
    print(f"[OK] Đã nạp {CongViec.objects.count()} Nhiệm vụ công việc.")

    # 6. HỒ SƠ LƯU TRỮ (12 hồ sơ)
    ho_so_samples = [
        {
            'ma_ho_so': 'HS-2026-GDTrH-001',
            'tieu_de': 'Hồ sơ chỉ đạo chuyên môn năm học 2026-2027 - Phòng Giáo dục Trung học',
            'nguoi_lap': u_nam,
            'don_vi': 'Phòng Giáo dục Trung học',
            'nam_tai_lieu': 2026,
            'thoi_han_bao_quan': '10 năm',
            'so_luong_van_ban': 15,
            'tinh_trang': 'DANG_THU_THAP',
            'mo_ta': 'Tập hợp các công văn, hướng dẫn và kế hoạch chuyên môn thi cử năm học 2026-2027.'
        },
        {
            'ma_ho_so': 'HS-2026-KHTC-002',
            'tieu_de': 'Hồ sơ đầu tư mua sắm trang thiết bị phòng tin học và thư viện số các trường THPT',
            'nguoi_lap': u_thao,
            'don_vi': 'Phòng Kế hoạch - Tài chính',
            'nam_tai_lieu': 2026,
            'thoi_han_bao_quan': '20 năm',
            'so_luong_van_ban': 8,
            'tinh_trang': 'DANG_THU_THAP',
            'mo_ta': 'Các quyết định phê duyệt chủ trương đầu tư, thẩm định giá và hồ sơ mời thầu.'
        },
        {
            'ma_ho_so': 'HS-2025-TCCB-005',
            'tieu_de': 'Hồ sơ thi tuyển chức danh lãnh đạo, quản lý các đơn vị sự nghiệp công lập năm 2025',
            'nguoi_lap': u_dung,
            'don_vi': 'Phòng Tổ chức cán bộ',
            'nam_tai_lieu': 2025,
            'thoi_han_bao_quan': 'Vĩnh viễn',
            'so_luong_van_ban': 28,
            'tinh_trang': 'DA_LUU_TRU',
            'mo_ta': 'Toàn bộ biên bản họp hội đồng, đề án vị trí việc làm và quyết định bổ nhiệm cán bộ.'
        },
        {
            'ma_ho_so': 'HS-2026-QLCL-003',
            'tieu_de': 'Hồ sơ tổ chức Kỳ thi tốt nghiệp THPT năm 2026 tại Hội đồng thi số 04 - TP. Đà Nẵng',
            'nguoi_lap': u_hoang,
            'don_vi': 'Phòng Khảo thí & Quản lý chất lượng',
            'nam_tai_lieu': 2026,
            'thoi_han_bao_quan': 'Vĩnh viễn',
            'so_luong_van_ban': 35,
            'tinh_trang': 'DANG_THU_THAP',
            'mo_ta': 'Danh sách điểm thi, ban in sao đề thi, ban coi thi, ban chấm thi và biên bản niêm phong bài thi.'
        },
        {
            'ma_ho_so': 'HS-2026-GDMN-004',
            'tieu_de': 'Hồ sơ công nhận các trường mầm non đạt chuẩn quốc gia mức độ 1 và 2 giai đoạn 2026-2031',
            'nguoi_lap': u_lan,
            'don_vi': 'Phòng Giáo dục Mầm non - Tiểu học',
            'nam_tai_lieu': 2026,
            'thoi_han_bao_quan': '20 năm',
            'so_luong_van_ban': 18,
            'tinh_trang': 'DANG_THU_THAP',
            'mo_ta': 'Hồ sơ tự đánh giá và báo cáo đánh giá ngoài của 12 trường mầm non trên địa bàn thành phố.'
        },
        {
            'ma_ho_so': 'HS-2025-VP-006',
            'tieu_de': 'Tập lưu văn bản đi của Giám đốc Sở Giáo dục và Đào tạo năm 2025',
            'nguoi_lap': u_vanthu,
            'don_vi': 'Văn phòng Sở GD&ĐT',
            'nam_tai_lieu': 2025,
            'thoi_han_bao_quan': 'Vĩnh viễn',
            'so_luong_van_ban': 450,
            'tinh_trang': 'DA_LUU_TRU',
            'mo_ta': 'Bản gốc có chữ ký tay và con dấu đỏ của toàn bộ văn bản đi phát hành trong năm 2025.'
        },
        {
            'ma_ho_so': 'HS-2025-KHTC-007',
            'tieu_de': 'Hồ sơ quyết toán ngân sách nhà nước và các nguồn tài trợ năm tài chính 2025',
            'nguoi_lap': u_thao,
            'don_vi': 'Phòng Kế hoạch - Tài chính',
            'nam_tai_lieu': 2025,
            'thoi_han_bao_quan': '20 năm',
            'so_luong_van_ban': 64,
            'tinh_trang': 'DA_LUU_TRU',
            'mo_ta': 'Báo cáo tài chính năm, thông báo phê duyệt quyết toán của Sở Tài chính và biên bản kiểm toán nhà nước.'
        },
        {
            'ma_ho_so': 'HS-2026-TCCB-008',
            'tieu_de': 'Hồ sơ nâng bậc lương trước thời hạn do lập thành tích xuất sắc năm 2026',
            'nguoi_lap': u_dung,
            'don_vi': 'Phòng Tổ chức cán bộ',
            'nam_tai_lieu': 2026,
            'thoi_han_bao_quan': '10 năm',
            'so_luong_van_ban': 22,
            'tinh_trang': 'DANG_THU_THAP',
            'mo_ta': 'Biên bản bình xét của các đơn vị và quyết định nâng lương của Giám đốc Sở cho 45 cá nhân.'
        },
        {
            'ma_ho_so': 'HS-2026-GDTrH-009',
            'tieu_de': 'Hồ sơ tham dự Cuộc thi Khoa học kỹ thuật cấp quốc gia học sinh trung học năm 2026',
            'nguoi_lap': u_nam,
            'don_vi': 'Phòng Giáo dục Trung học',
            'nam_tai_lieu': 2026,
            'thoi_han_bao_quan': '10 năm',
            'so_luong_van_ban': 14,
            'tinh_trang': 'DANG_THU_THAP',
            'mo_ta': 'Hồ sơ 06 dự án KHKT của học sinh Đà Nẵng đạt giải cấp thành phố tham gia vòng chung khảo quốc gia.'
        },
        {
            'ma_ho_so': 'HS-2024-TCCB-010',
            'tieu_de': 'Hồ sơ giải quyết đơn thư khiếu nại, tố cáo và kết luận thanh tra chuyên ngành năm 2024',
            'nguoi_lap': u_dung,
            'don_vi': 'Phòng Tổ chức cán bộ',
            'nam_tai_lieu': 2024,
            'thoi_han_bao_quan': '10 năm',
            'so_luong_van_ban': 19,
            'tinh_trang': 'DA_LUU_TRU',
            'mo_ta': 'Biên bản xác minh, kết luận thanh tra và quyết định xử lý kỷ luật (nếu có).'
        },
        {
            'ma_ho_so': 'HS-2026-VP-011',
            'tieu_de': 'Hồ sơ Hội nghị cán bộ, công chức, viên chức và người lao động cơ quan Sở GD&ĐT năm 2026',
            'nguoi_lap': u_vanthu,
            'don_vi': 'Văn phòng Sở GD&ĐT',
            'nam_tai_lieu': 2026,
            'thoi_han_bao_quan': '10 năm',
            'so_luong_van_ban': 12,
            'tinh_trang': 'DANG_THU_THAP',
            'mo_ta': 'Nghị quyết hội nghị, quy chế chi tiêu nội bộ năm 2026 và biên bản thỏa ước lao động.'
        },
        {
            'ma_ho_so': 'HS-2025-QLCL-012',
            'tieu_de': 'Hồ sơ lưu trữ bài thi và bảng điểm Kỳ thi tuyển sinh vào lớp 10 THPT công lập năm 2025',
            'nguoi_lap': u_hoang,
            'don_vi': 'Phòng Khảo thí & Quản lý chất lượng',
            'nam_tai_lieu': 2025,
            'thoi_han_bao_quan': '20 năm',
            'so_luong_van_ban': 120,
            'tinh_trang': 'DA_LUU_TRU',
            'mo_ta': 'Bảng ghi điểm gốc 3 môn Toán, Văn, Ngoại ngữ của 16.500 thí sinh toàn thành phố.'
        }
    ]

    for item in ho_so_samples:
        hs, _ = HoSoLuuTru.objects.get_or_create(ma_ho_so=item['ma_ho_so'], defaults=item)
        for k, v in item.items():
            setattr(hs, k, v)
        hs.save()
    print(f"[OK] Đã nạp {HoSoLuuTru.objects.count()} Hồ sơ lưu trữ.")

    # 7. THÔNG BÁO CƠ QUAN (12 thông báo)
    thong_bao_samples = [
        {
            'tieu_de': 'Lịch họp giao ban công tác tháng 11/2026',
            'noi_dung': 'Kính mời Trưởng, Phó các phòng ban thuộc Sở tham dự cuộc họp giao ban thường kỳ vào lúc 08h00 ngày 15/11/2026 tại Hội trường A. Chủ trì: Giám đốc Sở Lê Thị Bích Thuận.',
            'loai': 'Cuộc họp',
            'muc_do': 'Quan trọng',
            'nguoi_gui': u_vanthu,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Thông báo kế hoạch nghỉ Tết Dương lịch 2027 và phân công trực cơ quan',
            'noi_dung': 'Đề nghị các phòng ban lập danh sách cán bộ, chuyên viên trực Tết Dương lịch năm 2027 gửi về Văn phòng Sở trước ngày 15/12/2026 để tổng hợp ban hành lịch trực chung.',
            'loai': 'Chỉ đạo',
            'muc_do': 'Bình thường',
            'nguoi_gui': u_vanthu,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Cảnh báo nguy cơ an toàn an ninh mạng qua email công vụ giả mạo',
            'noi_dung': 'Thời gian gần đây xuất hiện hiện tượng email giả mạo thông báo của Sở yêu cầu cung cấp mật khẩu tài khoản. Đề nghị toàn thể cán bộ tuyệt đối không click vào các đường link lạ.',
            'loai': 'Khẩn',
            'muc_do': 'Khẩn',
            'nguoi_gui': u_vanthu,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Thông báo phát động ủng hộ phong trào "Tết vì người nghèo và nạn nhân da cam" năm 2027',
            'noi_dung': 'Công đoàn ngành Giáo dục phát động mỗi cán bộ, công chức, viên chức ủng hộ tối thiểu 01 ngày lương giúp đỡ các hoàn cảnh khó khăn trên địa bàn thành phố.',
            'loai': 'Phong trào',
            'muc_do': 'Bình thường',
            'nguoi_gui': u_dung,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Lịch kiểm tra tiến độ giải ngân vốn đầu tư công các dự án trường học Quý IV/2026',
            'noi_dung': 'Đoàn công tác do Phó Giám đốc Sở Mai Tấn Linh làm trưởng đoàn sẽ tiến hành kiểm tra thực tế tại công trình xây dựng Trường THPT Hòa Vang mới vào 08h30 ngày 21/11/2026.',
            'loai': 'Cuộc họp',
            'muc_do': 'Quan trọng',
            'nguoi_gui': u_thao,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Thông báo cử cán bộ tham gia bồi dưỡng nghiệp vụ quản lý nhà nước ngạch Chuyên viên chính năm 2026',
            'noi_dung': 'Phòng TCCB thông báo danh sách 06 cán bộ chuyên viên đủ tiêu chuẩn tham gia lớp bồi dưỡng tại Phân viện Học viện Hành chính Quốc gia khu vực miền Trung.',
            'loai': 'Chỉ đạo',
            'muc_do': 'Bình thường',
            'nguoi_gui': u_dung,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Nhắc nhở nộp báo cáo tổng kết thi đua học kỳ I năm học 2026-2027 trước ngày 15/12/2026',
            'noi_dung': 'Đề nghị thủ trưởng các đơn vị trực thuộc chỉ đạo tổng kết các chuyên đề chuyên môn và báo cáo kết quả thi đua đúng thời hạn quy định.',
            'loai': 'Nhắc nhở',
            'muc_do': 'Quan trọng',
            'nguoi_gui': u_nam,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Thông báo triển khai chữ ký số cá nhân SmartCA cho 100% cán bộ, chuyên viên cơ quan Sở',
            'noi_dung': 'Nhằm nâng cao hiệu quả giải quyết thủ tục hành chính không giấy tờ, đề nghị toàn thể chuyên viên liên hệ Văn phòng Sở để cài đặt chứng thư số trên thiết bị di động.',
            'loai': 'Chỉ đạo',
            'muc_do': 'Quan trọng',
            'nguoi_gui': u_vanthu,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Kế hoạch khám sức khỏe định kỳ năm 2026 cho cán bộ, công chức, viên chức cơ quan',
            'noi_dung': 'Ban Chấp hành Công đoàn cơ quan phối hợp với Bệnh viện Đa khoa Đà Nẵng tổ chức khám sức khỏe định kỳ vào 2 ngày 28-29/11/2026.',
            'loai': 'Phúc lợi',
            'muc_do': 'Bình thường',
            'nguoi_gui': u_vanthu,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Thông báo khẩn về việc chủ động ứng phó với mưa lớn, nguy cơ ngập lụt trên địa bàn',
            'noi_dung': 'Thực hiện công điện của Ban Chỉ huy PCTT&TKCN thành phố, yêu cầu các trường chủ động cho học sinh nghỉ học nếu đường đi ngập sâu nguy hiểm và kê cao tài sản phòng học.',
            'loai': 'Khẩn',
            'muc_do': 'Khẩn',
            'nguoi_gui': u_vanthu,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Lịch tiếp công dân định kỳ tháng 11/2026 của Giám đốc Sở Giáo dục và Đào tạo',
            'noi_dung': 'Giám đốc Sở Lê Thị Bích Thuận sẽ tiếp công dân định kỳ vào ngày 20/11/2026 từ 08h00 đến 11h30 tại Phòng Tiếp công dân cơ quan Sở.',
            'loai': 'Lịch công tác',
            'muc_do': 'Quan trọng',
            'nguoi_gui': u_vanthu,
            'lien_ket': '/pages/thong-bao.html'
        },
        {
            'tieu_de': 'Triệu tập đại biểu tham dự Hội thảo khoa học quốc tế về "Đổi mới phương pháp dạy học trong kỷ nguyên AI"',
            'noi_dung': 'Kính mời các đại biểu có tên trong danh sách tham dự Hội thảo do Sở GD&ĐT phối hợp với Đại học Đà Nẵng tổ chức vào ngày 05/12/2026 tại Khách sạn Mường Thanh Luxury.',
            'loai': 'Hội thảo',
            'muc_do': 'Bình thường',
            'nguoi_gui': u_nam,
            'lien_ket': '/pages/thong-bao.html'
        }
    ]

    for item in thong_bao_samples:
        tb, _ = ThongBao.objects.get_or_create(tieu_de=item['tieu_de'], defaults=item)
        for k, v in item.items():
            setattr(tb, k, v)
        tb.save()
    print(f"[OK] Đã nạp {ThongBao.objects.count()} Thông báo cơ quan.")

    # 8. MẪU VĂN BẢN CHATBOT (Giữ nguyên theo yêu cầu)
    print(f"[OK] Giữ nguyên {MauVanBan.objects.count()} Mẫu văn bản Chatbot theo yêu cầu.")

    print("=" * 70)
    print("✅ HOÀN TẤT NẠP TOÀN BỘ 100% DỮ LIỆU MẪU ĐỒNG BỘ!")
    print(f"   • Cán bộ nhân sự:   {NguoiDung.objects.count()} người")
    print(f"   • Văn bản đến:      {VanBanDen.objects.count()} văn bản")
    print(f"   • Văn bản đi:       {VanBanDi.objects.count()} văn bản")
    print(f"   • Công việc nhiệm vụ: {CongViec.objects.count()} công việc")
    print(f"   • Hồ sơ lưu trữ:    {HoSoLuuTru.objects.count()} hồ sơ")
    print(f"   • Thông báo nội bộ: {ThongBao.objects.count()} thông báo")
    print(f"   • Mẫu VB Chatbot:   {MauVanBan.objects.count()} mẫu")
    print("=" * 70)

if __name__ == '__main__':
    seed()
