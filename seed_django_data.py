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
    print("=" * 60)
    print("🚀 BẮT ĐẦU NẠP DỮ LIỆU MẪU CHUẨN THỰC TẾ CHO HỆ THỐNG")
    print("   SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG")
    print("=" * 60)

    # 1. Superuser Django Admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@danang.edu.vn', 'Admin@123')
        print("[OK] Đã tạo tài khoản Django Superadmin: admin / Admin@123")

    # 2. Danh sách Cán bộ / Nhân sự (NguoiDung)
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
        print(f"  [User] {user.ten_dang_nhap.ljust(16)} | {user.ho_va_ten.ljust(22)} | {user.chuc_vu}")

    u_vanthu = NguoiDung.objects.get(ten_dang_nhap='admin_vanthu')
    u_giamdoc = NguoiDung.objects.get(ten_dang_nhap='giamdoc_so')
    u_phogd = NguoiDung.objects.get(ten_dang_nhap='phogiamdoc_so')
    u_nam = NguoiDung.objects.get(ten_dang_nhap='minhcv')
    u_thao = NguoiDung.objects.get(ten_dang_nhap='thaoltk')
    u_dung = NguoiDung.objects.get(ten_dang_nhap='dungpt')

    # 3. Văn bản đến (Incoming Documents)
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
        }
    ]

    for item in van_ban_den_samples:
        vb, created = VanBanDen.objects.get_or_create(
            so_ky_hieu=item['so_ky_hieu'],
            defaults=item
        )
        if not created:
            for k, v in item.items():
                setattr(vb, k, v)
            vb.save()
        print(f"  [VB Đến] #{vb.so_den} | {vb.so_ky_hieu.ljust(18)} | {vb.co_quan_ban_hanh}")

    # 4. Văn bản đi (Outgoing Documents)
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
        }
    ]

    for item in van_ban_di_samples:
        vb, created = VanBanDi.objects.get_or_create(
            so_ky_hieu=item['so_ky_hieu'],
            defaults=item
        )
        if not created:
            for k, v in item.items():
                setattr(vb, k, v)
            vb.save()
        print(f"  [VB Đi]   {vb.so_ky_hieu.ljust(18)} | {vb.loai_van_ban.ljust(12)} | {vb.trang_thai}")

    # 5. Phân công Công việc (CongViec)
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
        }
    ]

    for item in cong_viec_samples:
        cv, created = CongViec.objects.get_or_create(
            ten_cong_viec=item['ten_cong_viec'],
            defaults=item
        )
        if not created:
            for k, v in item.items():
                setattr(cv, k, v)
            cv.save()
        print(f"  [Công việc] {cv.ten_cong_viec[:35].ljust(38)} | Tiến độ: {str(cv.tien_do).rjust(3)}% | {cv.trang_thai}")

    # 6. Hồ sơ lưu trữ (HoSoLuuTru)
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
        }
    ]

    for item in ho_so_samples:
        hs, created = HoSoLuuTru.objects.get_or_create(
            ma_ho_so=item['ma_ho_so'],
            defaults=item
        )
        if not created:
            for k, v in item.items():
                setattr(hs, k, v)
            hs.save()
        print(f"  [Hồ sơ]    {hs.ma_ho_so.ljust(20)} | {hs.tieu_de[:35].ljust(38)} | {hs.tinh_trang}")

    # 7. Thông báo cơ quan (ThongBao)
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
        }
    ]

    for item in thong_bao_samples:
        tb, created = ThongBao.objects.get_or_create(
            tieu_de=item['tieu_de'],
            defaults=item
        )
        if not created:
            for k, v in item.items():
                setattr(tb, k, v)
            tb.save()
        print(f"  [Thông báo] {tb.tieu_de.ljust(50)} | {tb.loai} | Mức: {tb.muc_do}")

    # 8. Mẫu văn bản Chatbot AI (MauVanBan)
    mau_van_ban_samples = [
        {
            'ma_mau': 'MAU_TO_TRINH_01',
            'ten_mau': 'Tờ trình về việc xin chủ trương tổ chức hội nghị/tập huấn chuyên đề',
            'loai_van_ban': 'Tờ trình',
            'linh_vuc': 'Hành chính tổng hợp',
            'co_quan_ban_hanh': 'Sở Giáo dục và Đào tạo TP. Đà Nẵng',
            'noi_dung_html': '<div style="font-family: Times New Roman, serif; padding: 20px;">'
                             '<div style="text-align: center; margin-bottom: 20px;">'
                             '<strong>ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</strong><br/>'
                             '<strong>SỞ GIÁO DỤC VÀ ĐÀO TẠO</strong><br/>'
                             'Số: ... /TTr-SGDĐT'
                             '<div style="text-align: right; font-style: italic;">Đà Nẵng, ngày ... tháng ... năm 2026</div>'
                             '</div>'
                             '<h3 style="text-align: center;">TỜ TRÌNH<br/><span style="font-size: 15px; font-weight: normal;">V/v xin chủ trương tổ chức hội nghị tập huấn chuyên môn</span></h3>'
                             '<p><strong>Kính gửi:</strong> Ban Giám đốc Sở Giáo dục và Đào tạo TP. Đà Nẵng</p>'
                             '<p>- Căn cứ Kế hoạch nhiệm vụ năm học 2026-2027 của Sở Giáo dục và Đào tạo;<br/>'
                             '- Nhằm bồi dưỡng nâng cao năng lực ứng dụng công nghệ và chuyển đổi số cho đội ngũ cán bộ, giáo viên;<br/>'
                             'Phòng ... kính trình Ban Giám đốc Sở xem xét, phê duyệt chủ trương tổ chức Hội nghị tập huấn chuyên đề như sau:</p>'
                             '<p><strong>1. Mục đích, yêu cầu:</strong> Nâng cao năng lực chuyển đổi số.<br/>'
                             '<strong>2. Thành phần tham dự:</strong> Dự kiến 120 đại biểu.<br/>'
                             '<strong>3. Thời gian & địa điểm:</strong> 01 ngày, tại Hội trường tầng 3.<br/>'
                             '<strong>4. Kinh phí dự kiến:</strong> Từ nguồn chi thường xuyên năm 2026.</p>'
                             '<p>Kính trình Ban Giám đốc Sở xem xét, quyết định./.</p>'
                             '<table style="width: 100%; margin-top: 30px;"><tr><td style="width: 50%;"><em>Nơi nhận:</em><br/>- Như trên;<br/>- Lưu: VT, ...</td><td style="text-align: center;"><strong>TRƯỞNG PHÒNG</strong><br/><br/><br/><em>(Ký, ghi rõ họ tên)</em></td></tr></table>'
                             '</div>',
            'noi_dung_text': 'TỜ TRÌNH V/v xin chủ trương tổ chức hội nghị tập huấn chuyên môn. Kính gửi: Ban Giám đốc Sở GD&ĐT. Căn cứ kế hoạch năm học...'
        },
        {
            'ma_mau': 'MAU_CONG_VAN_02',
            'ten_mau': 'Công văn hướng dẫn triển khai nhiệm vụ chuyên môn gửi các đơn vị trực thuộc',
            'loai_van_ban': 'Công văn',
            'linh_vuc': 'Giáo dục chuyên môn',
            'co_quan_ban_hanh': 'Sở Giáo dục và Đào tạo TP. Đà Nẵng',
            'noi_dung_html': '<div style="font-family: Times New Roman, serif; padding: 20px;">'
                             '<div style="text-align: center; margin-bottom: 20px;">'
                             '<strong>SỞ GIÁO DỤC VÀ ĐÀO TẠO<br/>THÀNH PHỐ ĐÀ NẴNG</strong><br/>'
                             'Số: ... /SGDĐT-GDTrH'
                             '<div style="text-align: right; font-style: italic;">Đà Nẵng, ngày ... tháng ... năm 2026</div>'
                             '</div>'
                             '<h3 style="text-align: center;">CÔNG VĂN HƯỚNG DẪN<br/><span style="font-size: 15px; font-weight: normal;">V/v triển khai công tác chuẩn bị năm học mới 2026-2027</span></h3>'
                             '<p><strong>Kính gửi:</strong> Hiệu trưởng các trường THPT, trường phổ thông nhiều cấp học</p>'
                             '<p>Thực hiện chỉ đạo của Bộ GD&ĐT và UBND thành phố, Sở GD&ĐT hướng dẫn các đơn vị triển khai các nội dung sau:</p>'
                             '<p>1. Tổ chức rà soát cơ sở vật chất, phòng học bộ môn.<br/>2. Kiện toàn đội ngũ giáo viên đủ định mức theo quy định.<br/>3. Báo cáo tình hình chuẩn bị về Sở trước ngày 25/8.</p>'
                             '<table style="width: 100%; margin-top: 30px;"><tr><td style="width: 50%;"><em>Nơi nhận:</em><br/>- Như kính gửi;<br/>- Giám đốc (để b/c);<br/>- Lưu: VT, GDTrH.</td><td style="text-align: center;"><strong>KT. GIÁM ĐỐC<br/>PHÓ GIÁM ĐỐC</strong><br/><br/><br/><em>(Đã ký đóng dấu)</em></td></tr></table>'
                             '</div>',
            'noi_dung_text': 'CÔNG VĂN HƯỚNG DẪN V/v triển khai công tác chuẩn bị năm học mới. Kính gửi: Hiệu trưởng các trường THPT...'
        },
        {
            'ma_mau': 'MAU_QUYET_DINH_03',
            'ten_mau': 'Quyết định thành lập Hội đồng/Ban kiểm tra/Hội đồng chấm thi',
            'loai_van_ban': 'Quyết định',
            'linh_vuc': 'Tổ chức cán bộ',
            'co_quan_ban_hanh': 'Sở Giáo dục và Đào tạo TP. Đà Nẵng',
            'noi_dung_html': '<div style="font-family: Times New Roman, serif; padding: 20px;">'
                             '<div style="text-align: center; margin-bottom: 20px;">'
                             '<strong>ỦY BAN NHÂN DÂN THÀNH PHỐ ĐÀ NẴNG</strong><br/>'
                             '<strong>SỞ GIÁO DỤC VÀ ĐÀO TẠO</strong><br/>'
                             'Số: ... /QĐ-SGDĐT'
                             '<div style="text-align: right; font-style: italic;">Đà Nẵng, ngày ... tháng ... năm 2026</div>'
                             '</div>'
                             '<h3 style="text-align: center;">QUYẾT ĐỊNH<br/><span style="font-size: 15px; font-weight: normal;">Về việc thành lập Hội đồng thẩm định hồ sơ thi đua khen thưởng năm 2026</span></h3>'
                             '<p style="text-align: center;"><strong>GIÁM ĐỐC SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG</strong></p>'
                             '<p>- Căn cứ Quyết định quy định chức năng, nhiệm vụ, quyền hạn của Sở GD&ĐT;<br/>- Xét đề nghị của Trưởng phòng Tổ chức cán bộ;</p>'
                             '<p style="text-align: center;"><strong>QUYẾT ĐỊNH:</strong></p>'
                             '<p><strong>Điều 1.</strong> Thành lập Hội đồng gồm các ông (bà) có tên trong danh sách kèm theo.<br/>'
                             '<strong>Điều 2.</strong> Hội đồng có nhiệm vụ thẩm định hồ sơ theo đúng quy chế hiện hành.<br/>'
                             '<strong>Điều 3.</strong> Chánh Văn phòng, Trưởng phòng TCCB và các cá nhân có tên tại Điều 1 chịu trách nhiệm thi hành Quyết định này./.</p>'
                             '<table style="width: 100%; margin-top: 30px;"><tr><td style="width: 50%;"><em>Nơi nhận:</em><br/>- Như Điều 3;<br/>- Lưu: VT, TCCB.</td><td style="text-align: center;"><strong>GIÁM ĐỐC</strong><br/><br/><br/><em>(Ký tên và đóng dấu)</em></td></tr></table>'
                             '</div>',
            'noi_dung_text': 'QUYẾT ĐỊNH Về việc thành lập Hội đồng thẩm định. GIÁM ĐỐC SỞ GD&ĐT. Căn cứ chức năng nhiệm vụ... Điều 1: Thành lập hội đồng...'
        },
        {
            'ma_mau': 'MAU_BAO_CAO_04',
            'ten_mau': 'Báo cáo tổng kết công tác / tiến độ triển khai nhiệm vụ',
            'loai_van_ban': 'Báo cáo',
            'linh_vuc': 'Kế hoạch tổng hợp',
            'co_quan_ban_hanh': 'Sở Giáo dục và Đào tạo TP. Đà Nẵng',
            'noi_dung_html': '<div style="font-family: Times New Roman, serif; padding: 20px;">'
                             '<div style="text-align: center; margin-bottom: 20px;">'
                             '<strong>SỞ GIÁO DỤC VÀ ĐÀO TẠO<br/>THÀNH PHỐ ĐÀ NẴNG</strong><br/>'
                             'Số: ... /BC-SGDĐT'
                             '<div style="text-align: right; font-style: italic;">Đà Nẵng, ngày ... tháng ... năm 2026</div>'
                             '</div>'
                             '<h3 style="text-align: center;">BÁO CÁO<br/><span style="font-size: 15px; font-weight: normal;">Kết quả triển khai thực hiện nhiệm vụ Quý IV năm 2026</span></h3>'
                             '<p><strong>Kính gửi:</strong> Ủy ban nhân dân thành phố Đà Nẵng</p>'
                             '<p>Sở Giáo dục và Đào tạo trân trọng báo cáo tình hình triển khai công tác GD&ĐT như sau:</p>'
                             '<p><strong>I. KẾT QUẢ ĐẠT ĐƯỢC:</strong><br/>1. Công tác chỉ đạo điều hành: Đã ban hành 15 công văn hướng dẫn...<br/>2. Công tác chuyên môn: Tổ chức thành công hội thi GVG cấp thành phố...<br/><strong>II. NHIỆM VỤ TRỌNG TÂM THỜI GIAN TỚI:</strong> Tiếp tục triển khai...</p>'
                             '</div>',
            'noi_dung_text': 'BÁO CÁO Kết quả triển khai thực hiện nhiệm vụ. Kính gửi: UBND TP Đà Nẵng. Sở GD&ĐT trân trọng báo cáo...'
        },
        {
            'ma_mau': 'MAU_BIEN_BAN_05',
            'ten_mau': 'Biên bản cuộc họp giao ban nội bộ cơ quan',
            'loai_van_ban': 'Biên bản',
            'linh_vuc': 'Văn phòng',
            'co_quan_ban_hanh': 'Sở Giáo dục và Đào tạo TP. Đà Nẵng',
            'noi_dung_html': '<div style="font-family: Times New Roman, serif; padding: 20px;">'
                             '<h3 style="text-align: center;">BIÊN BẢN CUỘC HỌP GIAO BAN<br/><span style="font-size: 15px; font-weight: normal;">Định kỳ tháng 11 năm 2026</span></h3>'
                             '<p><strong>Thời gian:</strong> 08h00 ngày 15/11/2026.<br/>'
                             '<strong>Địa điểm:</strong> Phòng họp số 1, Sở GD&ĐT.<br/>'
                             '<strong>Chủ trì:</strong> Đ/c Lê Thị Bích Thuận - Giám đốc Sở.<br/>'
                             '<strong>Thư ký:</strong> Đ/c Nguyễn Thị Thu Hằng - Văn thư cơ quan.<br/>'
                             '<strong>Thành phần:</strong> Đại diện lãnh đạo các phòng thuộc Sở (có mặt 18/18).<br/>'
                             '<strong>Nội dung:</strong> Đánh giá công tác tháng 10 và triển khai nhiệm vụ tháng 11/2026.<br/>'
                             'Cuộc họp kết thúc vào lúc 11h30 cùng ngày./.</p>'
                             '</div>',
            'noi_dung_text': 'BIÊN BẢN CUỘC HỌP GIAO BAN định kỳ tháng 11/2026. Chủ trì: Giám đốc Sở Lê Thị Bích Thuận. Thư ký: Nguyễn Thị Thu Hằng...'
        }
    ]

    for item in mau_van_ban_samples:
        mvb, created = MauVanBan.objects.get_or_create(
            ma_mau=item['ma_mau'],
            defaults=item
        )
        if not created:
            for k, v in item.items():
                setattr(mvb, k, v)
            mvb.save()
        print(f"  [Mẫu VB]   {mvb.ma_mau.ljust(20)} | {mvb.ten_mau[:35].ljust(38)} | {mvb.loai_van_ban}")

    print("=" * 60)
    print("✅ ĐÃ NẠP THÀNH CÔNG TOÀN BỘ DỮ LIỆU THỰC TẾ CHO HỆ THỐNG!")
    print("=" * 60)

if __name__ == '__main__':
    seed()
