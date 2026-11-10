import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education_management.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import NguoiDung
from van_ban.models import VanBanDi, VanBanDen
from cong_viec.models import CongViec
from ho_so.models import HoSoLuuTru, VanBanBanHanh
from thong_bao.models import ThongBao
from chatbot.models import MauVanBan
from datetime import date

def seed():
    print("Bắt đầu nạp dữ liệu mẫu Django...")

    # 1. Superuser Django Admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@danang.edu.vn', 'Admin@123')
        print("[OK] Đã tạo superuser Django: admin / Admin@123")

    # 2. Người dùng hệ thống NguoiDung
    users_data = [
        {
            'ten_dang_nhap': 'admin_vanthu',
            'ho_va_ten': 'Văn thư Sở GD&ĐT Đà Nẵng',
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
            'chuc_vu': 'Giám đốc Sở',
            'vai_tro': 'LANH_DAO',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'GiamDoc@123'
        },
        {
            'ten_dang_nhap': 'minhcv',
            'ho_va_ten': 'Nguyễn Văn Nam',
            'email': 'namnv@danang.edu.vn',
            'sdt': '0914.567.890',
            'phong_ban': 'Phòng Giáo dục Trung học',
            'chuc_vu': 'Chuyên viên',
            'vai_tro': 'CHUYEN_VIEN',
            'trang_thai': 'HOAT_DONG',
            'mat_khau': 'ChuyenVien@123'
        }
    ]

    for item in users_data:
        pw = item.pop('mat_khau')
        user, created = NguoiDung.objects.get_or_create(ten_dang_nhap=item['ten_dang_nhap'], defaults=item)
        user.set_password(pw)
        user.save()
        print(f"[OK] Tài khoản {user.ten_dang_nhap} sẵn sàng.")

    admin_user = NguoiDung.objects.get(ten_dang_nhap='admin_vanthu')
    cv_user = NguoiDung.objects.get(ten_dang_nhap='minhcv')
    ld_user = NguoiDung.objects.get(ten_dang_nhap='giamdoc_so')

    # 3. Văn bản đi mẫu
    if not VanBanDi.objects.exists():
        VanBanDi.objects.create(
            so_ky_hieu='125/SGDĐT-GDTrH',
            trich_yeu='V/v hướng dẫn tổ chức kỳ thi chọn học sinh giỏi cấp thành phố năm học 2026-2027',
            loai_van_ban='Hướng dẫn',
            do_khan='Bình thường',
            don_vi_soan_thao='Phòng Giáo dục Trung học',
            noi_nhan='Các trường THPT trên địa bàn thành phố',
            noi_dung_tom_tat='Kế hoạch và quy chế thi học sinh giỏi các môn văn hóa.',
            nguoi_soan=cv_user,
            van_thu=admin_user,
            lanh_dao_ky=ld_user,
            lanh_dao_ky_ten=ld_user.ho_va_ten,
            trang_thai='DA_BAN_HANH'
        )
        print("[OK] Đã tạo văn bản đi mẫu.")

    # 4. Công việc mẫu
    if not CongViec.objects.exists():
        CongViec.objects.create(
            ten_cong_viec='Rà soát cơ sở vật chất phục vụ thi tốt nghiệp THPT',
            noi_dung='Kiểm tra hệ thống phòng thi, camera giám sát và máy phát điện dự phòng.',
            nguoi_giao=ld_user,
            nguoi_xu_ly=cv_user,
            phong_ban='Phòng Giáo dục Trung học',
            han_hoan_thanh=date(2026, 12, 31),
            do_uu_tien='CAO',
            tien_do=75,
            trang_thai='DANG_THUC_HIEN'
        )
        print("[OK] Đã tạo công việc mẫu.")

    # 5. Hồ sơ lưu trữ mẫu
    if not HoSoLuuTru.objects.exists():
        HoSoLuuTru.objects.create(
            ma_ho_so='HS-2026-GDTrH-001',
            tieu_de='Hồ sơ chỉ đạo chuyên môn năm học 2026 - Phòng GD Trung học',
            nguoi_lap=cv_user,
            don_vi='Phòng Giáo dục Trung học',
            nam_tai_lieu=2026,
            so_luong_van_ban=5,
            tinh_trang='DANG_THU_THAP',
            mo_ta='Tập hợp các công văn, hướng dẫn và kế hoạch chuyên môn.'
        )
        print("[OK] Đã tạo hồ sơ lưu trữ mẫu.")

    # 6. Thông báo mẫu
    if not ThongBao.objects.exists():
        ThongBao.objects.create(
            tieu_de='Lịch họp giao ban công tác tháng 11/2026',
            noi_dung='Kính mời Trưởng các phòng ban tham dự cuộc họp giao ban định kỳ vào 8h00 thứ Hai tại Hội trường A.',
            loai='Cuộc họp',
            muc_do='Quan trọng',
            nguoi_gui=admin_user
        )
        print("[OK] Đã tạo thông báo mẫu.")

    # 7. Mẫu văn bản Chatbot
    if not MauVanBan.objects.exists():
        MauVanBan.objects.create(
            ma_mau='MAU_TO_TRINH_01',
            ten_mau='Tờ trình về việc xin chủ trương tổ chức hội nghị/tập huấn',
            loai_van_ban='Tờ trình',
            linh_vuc='Hành chính tổng hợp',
            noi_dung_html='<h3>TỜ TRÌNH V/V XIN CHỦ TRƯƠNG TỔ CHỨC TẬP HUẤN</h3><p>Kính gửi: Ban Giám đốc Sở...</p>',
            noi_dung_text='TỜ TRÌNH V/V XIN CHỦ TRƯƠNG TỔ CHỨC TẬP HUẤN. Kính gửi: Ban Giám đốc Sở...'
        )
        print("[OK] Đã tạo mẫu văn bản chatbot.")

    print("Hoàn tất nạp dữ liệu mẫu Django thành công!")

if __name__ == '__main__':
    seed()
