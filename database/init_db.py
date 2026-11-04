import sys
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# Đảm bảo mã hóa console trên Windows không bị lỗi ký tự tiếng Việt
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Đảm bảo import được config từ thư mục gốc
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config

def init_database():
    """Khởi tạo file CSDL SQLite và nạp bảng nguoi_dung, thong_bao."""
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

    # Seed tài khoản Văn thư (Admin) mặc định
    admin_username = Config.DEFAULT_ADMIN_USERNAME
    cursor.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE ten_dang_nhap = ?', (admin_username,))
    existing = cursor.fetchone()

    if not existing:
        admin_pass_hash = generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD)
        try:
            cursor.execute('''
                INSERT INTO nguoi_dung (
                    ten_dang_nhap, mat_khau_hash, ho_va_ten, email,
                    sdt, phong_ban, chuc_vu, vai_tro, trang_thai,
                    bat_buoc_doi_mat_khau, so_lan_dang_nhap_sai
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                admin_username,
                admin_pass_hash,
                Config.DEFAULT_ADMIN_NAME,
                Config.DEFAULT_ADMIN_EMAIL,
                '0236.3822.456',
                'Văn phòng Sở GD&ĐT',
                'Văn thư cơ quan',
                'VAN_THU',
                'HOAT_DONG',
                1,  # Bắt buộc đổi mật khẩu ở lần đăng nhập đầu
                0
            ))
            conn.commit()
            print(f"[OK] Đã tạo tài khoản Văn thư mặc định thành công:")
            print(f"     - Tên đăng nhập: {admin_username}")
            print(f"     - Mật khẩu: {Config.DEFAULT_ADMIN_PASSWORD}")
            print(f"     - Vai trò: VAN_THU (Trạng thái: HOAT_DONG, Bắt buộc đổi MK: Có)")
        except Exception as e:
            print(f"[LỖI] Không thể seed tài khoản Văn thư: {e}")
            conn.close()
            return False
    else:
        print(f"[INFO] Tài khoản Văn thư '{admin_username}' đã tồn tại sẵn trong CSDL.")

    # Seed dữ liệu mẫu thông báo điều hành nếu bảng còn trống
    cursor.execute('SELECT COUNT(*) FROM thong_bao')
    tb_count = cursor.fetchone()[0]
    if tb_count == 0:
        cursor.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE ten_dang_nhap = ?', (admin_username,))
        admin_row = cursor.fetchone()
        admin_id = admin_row[0] if admin_row else None

        sample_notifications = [
            (
                'Thông báo lịch họp giao ban công tác tháng 11/2026 của Ban Giám đốc Sở',
                'Kính mời Trưởng các Phòng chuyên môn dự buổi họp giao ban định kỳ vào lúc 08h00 ngày 06/11/2026 tại Hội trường A - Sở GD&ĐT Đà Nẵng. Các phòng chuẩn bị báo cáo tiến độ các đề án trọng điểm.',
                'Cuộc họp',
                'Quan trọng',
                admin_id,
                None,
                '2026-11-06 08:00:00',
                None,
                '2026-11-03 08:30:00'
            ),
            (
                'Triển khai lịch bảo trì hệ thống máy chủ thư điện tử nội bộ cuối tuần',
                'Hệ thống mail @danang.edu.vn sẽ tạm dừng phục vụ trong khoảng thời gian từ 22h00 thứ Bảy đến 04h00 Chủ nhật tuần này để nâng cấp đường truyền cáp quang.',
                'Hệ thống',
                'Bình thường',
                admin_id,
                None,
                None,
                None,
                '2026-11-02 14:15:00'
            ),
            (
                'Chúc mừng đồng chí đạt danh hiệu Chiến sĩ thi đua cấp Thành phố',
                'Sở GD&ĐT chúc mừng 05 đồng chí cán bộ, chuyên viên các phòng ban đã vinh dự được Chủ tịch UBND TP. Đà Nẵng trao tặng danh hiệu thi đua xuất sắc năm học 2025-2026.',
                'Khen thưởng',
                'Bình thường',
                admin_id,
                None,
                None,
                None,
                '2026-10-30 09:00:00'
            )
        ]

        cursor.executemany('''
            INSERT INTO thong_bao (
                tieu_de, noi_dung, loai, muc_do, nguoi_gui_id,
                nguoi_nhan_id, ngay_hen_gio, lien_ket, ngay_tao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_notifications)
        conn.commit()
        print(f"[OK] Đã nạp thành công {len(sample_notifications)} thông báo điều hành mẫu.")

    conn.close()
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("KHỞI TẠO CƠ SỞ DỮ LIỆU QLVB - SỞ GD&ĐT TP. ĐÀ NẴNG")
    print("=" * 60)
    init_database()
