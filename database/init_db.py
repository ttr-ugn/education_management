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
from database.seed_mau_van_ban import seed_mau_van_ban

def init_database():
    """Khởi tạo file CSDL SQLite và nạp bảng nguoi_dung cùng kho mẫu văn bản."""
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

    conn.close()

    # Tự động nạp kho mẫu văn bản
    try:
        seed_mau_van_ban()
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể nạp kho mẫu văn bản: {e}")

    return True

if __name__ == '__main__':
    print("=" * 60)
    print("KHỞI TẠO CƠ SỞ DỮ LIỆU QLVB - SỞ GD&ĐT TP. ĐÀ NẴNG")
    print("=" * 60)
    init_database()
