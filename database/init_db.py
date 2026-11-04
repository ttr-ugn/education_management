import sys
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# Đảm bảo console trên Windows hỗ trợ utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config
from database.seed_mau_van_ban import seed_mau_van_ban

def init_database():
    """Khởi tạo toàn bộ CSDL và nạp dữ liệu mẫu cho cả 5 phân hệ."""
    db_path = Path(Config.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_path = Path(__file__).resolve().parent / 'schema.sql'
    if not schema_path.exists():
        print(f"[LỖI] Không tìm thấy file schema tại: {schema_path}")
        return False

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.execute('PRAGMA foreign_keys = ON;')
    cursor = conn.cursor()

    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"[OK] Đã khởi tạo schema CSDL thành công tại: {Config.DATABASE_PATH}")
    except Exception as e:
        print(f"[LỖI] Khởi tạo schema thất bại: {e}")
        conn.close()
        return False

    # 1. SEED TÀI KHOẢN NGƯỜI DÙNG CÁC VAI TRÒ
    default_users = [
        (
            Config.DEFAULT_ADMIN_USERNAME,
            generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD),
            Config.DEFAULT_ADMIN_NAME,
            Config.DEFAULT_ADMIN_EMAIL,
            '0236.3822.456',
            'Văn phòng Sở GD&ĐT',
            'Văn thư cơ quan',
            'VAN_THU',
            'HOAT_DONG',
            0,
            0
        ),
        (
            'giamdoc_so',
            generate_password_hash('GiamDoc@123'),
            'Lê Thị Bích Thuận',
            'giamdoc@danang.edu.vn',
            '0905.123.456',
            'Ban Giám đốc Sở',
            'Giám đốc Sở',
            'LANH_DAO',
            'HOAT_DONG',
            0,
            0
        ),
        (
            'minhcv',
            generate_password_hash('ChuyenVien@123'),
            'Nguyễn Văn Nam',
            'namnv@danang.edu.vn',
            '0914.567.890',
            'Phòng Giáo dục Trung học',
            'Chuyên viên',
            'CHUYEN_VIEN',
            'HOAT_DONG',
            0,
            0
        )
    ]

    for u in default_users:
        cursor.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE ten_dang_nhap = ?', (u[0],))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO nguoi_dung (
                    ten_dang_nhap, mat_khau_hash, ho_va_ten, email,
                    sdt, phong_ban, chuc_vu, vai_tro, trang_thai,
                    bat_buoc_doi_mat_khau, so_lan_dang_nhap_sai
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', u)
    conn.commit()
    print("[OK] Đã đồng bộ tài khoản mẫu (Văn thư, Lãnh đạo, Chuyên viên).")

    # Lấy ID của các user để seed quan hệ
    cursor.execute('SELECT ten_dang_nhap, nguoi_dung_id FROM nguoi_dung')
    user_ids = {row[0]: row[1] for row in cursor.fetchall()}
    admin_id = user_ids.get('admin_vanthu')
    lanh_dao_id = user_ids.get('giamdoc_so')
    chuyen_vien_id = user_ids.get('minhcv')

    # 2. SEED THÔNG BÁO ĐIỀU HÀNH
    cursor.execute('SELECT COUNT(*) FROM thong_bao')
    if cursor.fetchone()[0] == 0:
        sample_notifications = [
            (
                'Thông báo lịch họp giao ban công tác tháng 11/2026 của Ban Giám đốc Sở',
                'Kính mời Trưởng các Phòng chuyên môn dự buổi họp giao ban định kỳ vào lúc 08h00 ngày 06/11/2026 tại Hội trường A - Sở GD&ĐT Đà Nẵng. Các phòng chuẩn bị báo cáo tiến độ các đề án trọng điểm.',
                'Cuộc họp', 'Quan trọng', admin_id, None, '2026-11-06 08:00:00', None, '2026-11-03 08:30:00'
            ),
            (
                'Triển khai lịch bảo trì hệ thống máy chủ thư điện tử nội bộ cuối tuần',
                'Hệ thống mail @danang.edu.vn sẽ tạm dừng phục vụ trong khoảng thời gian từ 22h00 thứ Bảy đến 04h00 Chủ nhật tuần này để nâng cấp đường truyền cáp quang.',
                'Hệ thống', 'Bình thường', admin_id, None, None, None, '2026-11-02 14:15:00'
            ),
            (
                'Chúc mừng đồng chí đạt danh hiệu Chiến sĩ thi đua cấp Thành phố',
                'Sở GD&ĐT chúc mừng các đồng chí cán bộ, chuyên viên các phòng ban đã vinh dự được Chủ tịch UBND TP. Đà Nẵng trao tặng danh hiệu thi đua xuất sắc năm học 2025-2026.',
                'Khen thưởng', 'Bình thường', admin_id, None, None, None, '2026-10-30 09:00:00'
            )
        ]
        cursor.executemany('''
            INSERT INTO thong_bao (
                tieu_de, noi_dung, loai, muc_do, nguoi_gui_id,
                nguoi_nhan_id, ngay_hen_gio, lien_ket, ngay_tao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_notifications)
        conn.commit()
        print(f"[OK] Đã seed {len(sample_notifications)} thông báo điều hành mẫu.")

    # 3. SEED CÔNG VIỆC & NHIỆM VỤ
    cursor.execute('SELECT COUNT(*) FROM cong_viec')
    if cursor.fetchone()[0] == 0:
        tasks = [
            (
                'Xây dựng Kế hoạch tổ chức Hội thi Giáo viên dạy giỏi cấp THPT năm 2026-2027',
                'Dự thảo thể lệ, ban hành quyết định thành lập Ban giám khảo và phối hợp các trường đăng cai chuẩn bị cơ sở vật chất.',
                lanh_dao_id, chuyen_vien_id, 'Lê Thị Bích Thuận (Giám đốc Sở)', 'Nguyễn Văn Nam',
                'Phòng Giáo dục Trung học', '2026-10-25', '2026-11-15', 'CAO', 65, 'DANG_THUC_HIEN',
                'Đã hoàn thành dự thảo Thể lệ và gửi xin ý kiến các cụm chuyên môn.', '',
                '142/BGDĐT-GDTrH', 'V/v hướng dẫn tổ chức Kỳ thi tốt nghiệp THPT năm 2026', '2026-10-25'
            ),
            (
                'Khẩn trương kiểm tra cơ sở vật chất phòng chống bão lũ tại các trường ven sông',
                'Kiểm tra hệ thống thoát nước, chằng chống cây xanh và an toàn điện lưới tại các trường vùng trũng.',
                lanh_dao_id, chuyen_vien_id, 'Lê Thị Bích Thuận (Giám đốc Sở)', 'Nguyễn Văn Nam',
                'Phòng Giáo dục Tiểu học', '2026-10-20', '2026-11-01', 'KHAN_CAP', 100, 'HOAN_THANH',
                'Đã hoàn thành kiểm tra và có báo cáo tổng hợp.', 'Hoàn thành xuất sắc',
                '15/CĐ-PCTT', 'Công điện khẩn về ứng phó mưa lớn kéo dài', '2026-10-20'
            )
        ]
        for t in tasks:
            cursor.execute('''
                INSERT INTO cong_viec (
                    ten_cong_viec, noi_dung, nguoi_giao_id, nguoi_xu_ly_id,
                    nguoi_giao_ten, nguoi_xu_ly_ten, phong_ban, ngay_giao,
                    han_hoan_thanh, do_uu_tien, tien_do, trang_thai,
                    ket_qua_bao_cao, danh_gia_lanh_dao,
                    so_ky_hieu_vb, trich_yeu_vb, ngay_van_ban
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', t)
            tid = cursor.lastrowid
            cursor.execute('''
                INSERT INTO nhat_ky_cong_viec (
                    cong_viec_id, nguoi_cap_nhat_id, nguoi_cap_nhat_ten,
                    tien_do_cu, tien_do_moi, noi_dung_ghi_chu
                ) VALUES (?, ?, ?, 0, ?, ?)
            ''', (tid, chuyen_vien_id, 'Nguyễn Văn Nam', t[10], f"Khởi tạo và cập nhật tiến độ: {t[0]}"))
        conn.commit()
        print(f"[OK] Đã seed {len(tasks)} công việc nhiệm vụ mẫu.")

    # 4. SEED KHO LƯU TRỮ VÀ HỒ SƠ TÀI LIỆU
    cursor.execute('SELECT COUNT(*) FROM ho_so_luu_tru')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO ho_so_luu_tru (
                ma_ho_so, tieu_de, nguoi_lap_id, nguoi_lap,
                don_vi, nam_tai_lieu, thoi_han_bao_quan, so_luong_van_ban, tinh_trang, mo_ta
            ) VALUES 
            ('HS-2026-001', 'Hồ sơ chỉ đạo điều hành năm học 2025 - 2026', ?, 'Văn thư Sở GD&ĐT Đà Nẵng', 'Văn phòng Sở', 2026, 'Vĩnh viễn', 3, 'DANG_THU_THAP', 'Tập hợp các quyết định, chỉ thị, thông tư của Bộ và UBND TP.'),
            ('HS-2026-002', 'Hồ sơ tuyển sinh đầu cấp các lớp 1, 6, 10 năm học 2026 - 2027', ?, 'Nguyễn Văn Nam', 'Phòng GD Trung học', 2026, '10 năm', 2, 'DA_NOP_LUU_TRU', 'Kế hoạch phân tuyến tuyển sinh các quận huyện.')
        ''', (admin_id, chuyen_vien_id))

        cursor.execute('''
            INSERT INTO van_ban_ban_hanh (
                so_ky_hieu, trich_yeu, loai_van_ban, nguoi_ky, chuc_vu_nguoi_ky,
                ngay_ky, ngay_ban_hanh, nam_luu_tru, thang_luu_tru, quy_luu_tru,
                thoi_han_bao_quan, ho_so_id, tep_dinh_kem, dung_luong_kb, nguoi_luu_id
            ) VALUES 
            ('1205/SGDĐT-VP', 'Kế hoạch tổ chức Tuần lễ hưởng ứng học tập suốt đời năm 2026 trên địa bàn TP. Đà Nẵng', 'Kế hoạch', 'Lê Thị Bích Thuận', 'Giám đốc Sở', '2026-10-24', '2026-10-24', 2026, 10, 4, 'Vĩnh viễn', 1, 'KH_1205_SGDDT_HocTapSuotDoi.pdf', 1240, ?),
            ('88/UBND-VX', 'Về việc phân bổ kinh phí đầu tư cơ sở vật chất trường chuẩn quốc gia năm học 2026-2027', 'Quyết định', 'Chủ tịch UBND TP. Đà Nẵng', 'Chủ tịch UBND TP', '2026-10-28', '2026-10-29', 2026, 10, 4, '10 năm', 1, 'QD_88_PhanBoKinhPhi_UBND.pdf', 1840, ?)
        ''', (admin_id, admin_id))
        conn.commit()
        print("[OK] Đã seed kho hồ sơ lưu trữ và văn bản ban hành mẫu.")

    conn.close()

    # 5. SEED KHO MẪU VĂN BẢN CHO TRỢ LÝ CHATBOT
    try:
        seed_mau_van_ban()
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể nạp kho mẫu văn bản: {e}")

    return True

if __name__ == '__main__':
    print("=" * 65)
    print("KHỞI TẠO & ĐỒNG BỘ CSDL TOÀN HỆ THỐNG - SỞ GD&ĐT TP. ĐÀ NẴNG")
    print("=" * 65)
    init_database()
