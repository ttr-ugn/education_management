import secrets
import string
from datetime import datetime
from werkzeug.security import generate_password_hash
from database.db import get_db
from backend.auth.services import validate_email, validate_username, validate_password, get_current_time_str

def generate_random_password(length: int = 10) -> str:
    """Sinh mật khẩu tạm thời ngẫu nhiên an toàn (chứa chữ hoa, chữ thường, số và ký tự đặc biệt)."""
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Đảm bảo có ít nhất 1 chữ thường, 1 chữ hoa, 1 chữ số, 1 ký tự đặc biệt
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%&*" for c in password)):
            return password

def get_users_list(trang_thai: str = None, vai_tro: str = None, q: str = None) -> list[dict]:
    """Lấy danh sách người dùng theo bộ lọc (không bao gồm mat_khau_hash)."""
    db = get_db()
    query = '''
        SELECT u.nguoi_dung_id, u.ten_dang_nhap, u.ho_va_ten, u.email, u.sdt,
               u.phong_ban, u.chuc_vu, u.vai_tro, u.trang_thai, u.ly_do_tu_choi,
               u.bat_buoc_doi_mat_khau, u.ngay_tao, u.ngay_duyet, u.lan_dang_nhap_cuoi,
               u.nguoi_tao_id, creator.ho_va_ten AS ten_nguoi_tao
        FROM nguoi_dung u
        LEFT JOIN nguoi_dung creator ON u.nguoi_tao_id = creator.nguoi_dung_id
        WHERE 1=1
    '''
    params = []

    if trang_thai:
        query += ' AND u.trang_thai = ?'
        params.append(trang_thai)

    if vai_tro:
        query += ' AND u.vai_tro = ?'
        params.append(vai_tro)

    if q:
        search = f"%{q.strip()}%"
        query += ''' AND (
            u.ho_va_ten LIKE ? OR
            u.ten_dang_nhap LIKE ? OR
            u.email LIKE ? OR
            u.phong_ban LIKE ? OR
            u.chuc_vu LIKE ?
        )'''
        params.extend([search, search, search, search, search])

    query += ' ORDER BY u.ngay_tao DESC'

    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]

def approve_user(user_id: int, admin_id: int) -> tuple[bool, str, int]:
    """Văn thư duyệt tài khoản Chuyên viên đang chờ duyệt."""
    db = get_db()
    user = db.execute('SELECT nguoi_dung_id, trang_thai, ho_va_ten FROM nguoi_dung WHERE nguoi_dung_id = ?', (user_id,)).fetchone()
    if not user:
        return False, "Không tìm thấy người dùng.", 404

    if user['trang_thai'] != 'CHO_DUYET':
        return False, f"Chỉ có thể phê duyệt tài khoản đang ở trạng thái 'Chờ duyệt' (Trạng thái hiện tại: {user['trang_thai']}).", 400

    now_str = get_current_time_str()
    db.execute('''
        UPDATE nguoi_dung
        SET trang_thai = 'HOAT_DONG',
            ngay_duyet = ?,
            nguoi_tao_id = ?,
            ly_do_tu_choi = NULL
        WHERE nguoi_dung_id = ?
    ''', (now_str, admin_id, user_id))
    db.commit()

    return True, f"Đã phê duyệt tài khoản của {user['ho_va_ten']} thành công.", 200

def reject_user(user_id: int, admin_id: int, ly_do: str) -> tuple[bool, str, int]:
    """Văn thư từ chối tài khoản Chuyên viên kèm theo lý do cụ thể."""
    if not ly_do or not ly_do.strip():
        return False, "Vui lòng nhập lý do từ chối tài khoản.", 400

    db = get_db()
    user = db.execute('SELECT nguoi_dung_id, trang_thai, ho_va_ten FROM nguoi_dung WHERE nguoi_dung_id = ?', (user_id,)).fetchone()
    if not user:
        return False, "Không tìm thấy người dùng.", 404

    if user['trang_thai'] != 'CHO_DUYET':
        return False, f"Chỉ có thể từ chối tài khoản đang ở trạng thái 'Chờ duyệt' (Trạng thái hiện tại: {user['trang_thai']}).", 400

    now_str = get_current_time_str()
    db.execute('''
        UPDATE nguoi_dung
        SET trang_thai = 'TU_CHOI',
            ly_do_tu_choi = ?,
            ngay_duyet = ?,
            nguoi_tao_id = ?
        WHERE nguoi_dung_id = ?
    ''', (ly_do.strip(), now_str, admin_id, user_id))
    db.commit()

    return True, f"Đã từ chối tài khoản của {user['ho_va_ten']}.", 200

def create_leader_user(data: dict, admin_id: int) -> tuple[bool, str, dict | None, int]:
    """Văn thư tạo tài khoản Lãnh đạo, sinh mật khẩu tạm trả về 1 lần."""
    ten_dang_nhap = (data.get('ten_dang_nhap') or '').strip()
    ho_va_ten = (data.get('ho_va_ten') or '').strip()
    email = (data.get('email') or '').strip().lower()
    sdt = (data.get('sdt') or '').strip()
    phong_ban = (data.get('phong_ban') or '').strip()
    chuc_vu = (data.get('chuc_vu') or '').strip()

    if not all([ten_dang_nhap, ho_va_ten, email, chuc_vu]):
        return False, "Vui lòng nhập đầy đủ: Tên đăng nhập, Họ và tên, Email, Chức vụ Lãnh đạo.", None, 400

    if not validate_username(ten_dang_nhap):
        return False, "Tên đăng nhập từ 4-30 ký tự, chỉ gồm chữ cái, số, dấu chấm (.) và gạch dưới (_).", None, 400

    if not validate_email(email):
        return False, "Định dạng email không hợp lệ.", None, 400

    db = get_db()

    # Kiểm tra trùng tên đăng nhập
    if db.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE ten_dang_nhap = ?', (ten_dang_nhap,)).fetchone():
        return False, "Tên đăng nhập đã tồn tại trong hệ thống.", None, 409

    # Kiểm tra trùng email
    if db.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE email = ?', (email,)).fetchone():
        return False, "Địa chỉ email đã được sử dụng.", None, 409

    mat_khau_tam = generate_random_password(10)
    mat_khau_hash = generate_password_hash(mat_khau_tam)
    now_str = get_current_time_str()

    try:
        cursor = db.execute('''
            INSERT INTO nguoi_dung (
                ten_dang_nhap, mat_khau_hash, ho_va_ten, email, sdt,
                phong_ban, chuc_vu, vai_tro, trang_thai,
                bat_buoc_doi_mat_khau, so_lan_dang_nhap_sai,
                nguoi_tao_id, ngay_tao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'LANH_DAO', 'HOAT_DONG', 1, 0, ?, ?)
        ''', (
            ten_dang_nhap, mat_khau_hash, ho_va_ten, email, sdt,
            phong_ban or 'Ban Giám đốc Sở', chuc_vu,
            admin_id, now_str
        ))
        db.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        return False, f"Lỗi khi tạo tài khoản Lãnh đạo: {str(e)}", None, 500

    result_data = {
        'nguoi_dung_id': new_id,
        'ten_dang_nhap': ten_dang_nhap,
        'ho_va_ten': ho_va_ten,
        'email': email,
        'chuc_vu': chuc_vu,
        'mat_khau_tam': mat_khau_tam,  # Chỉ hiển thị một lần duy nhất cho Văn thư
        'bat_buoc_doi_mat_khau': True
    }

    return True, "Tạo tài khoản Lãnh đạo thành công.", result_data, 201

def lock_user(user_id: int, current_admin_id: int) -> tuple[bool, str, int]:
    """Khóa tài khoản người dùng."""
    if user_id == current_admin_id:
        return False, "Không được tự khóa tài khoản của chính mình.", 400

    db = get_db()
    user = db.execute('SELECT nguoi_dung_id, vai_tro, trang_thai, ho_va_ten FROM nguoi_dung WHERE nguoi_dung_id = ?', (user_id,)).fetchone()
    if not user:
        return False, "Không tìm thấy người dùng.", 404

    if user['trang_thai'] == 'BI_KHOA':
        return False, "Tài khoản này hiện đang bị khóa rồi.", 400

    # Kiểm tra không được khóa Văn thư cuối cùng đang hoạt động
    if user['vai_tro'] == 'VAN_THU':
        active_vt_count = db.execute('''
            SELECT COUNT(*) AS cnt FROM nguoi_dung
            WHERE vai_tro = 'VAN_THU' AND trang_thai = 'HOAT_DONG'
        ''').fetchone()['cnt']
        if active_vt_count <= 1:
            return False, "Không thể khóa tài khoản Văn thư đang hoạt động duy nhất trong hệ thống.", 400

    db.execute("UPDATE nguoi_dung SET trang_thai = 'BI_KHOA' WHERE nguoi_dung_id = ?", (user_id,))
    db.commit()

    return True, f"Đã khóa tài khoản của {user['ho_va_ten']} thành công.", 200

def unlock_user(user_id: int) -> tuple[bool, str, int]:
    """Mở khóa tài khoản người dùng."""
    db = get_db()
    user = db.execute('SELECT nguoi_dung_id, trang_thai, ho_va_ten FROM nguoi_dung WHERE nguoi_dung_id = ?', (user_id,)).fetchone()
    if not user:
        return False, "Không tìm thấy người dùng.", 404

    if user['trang_thai'] == 'HOAT_DONG':
        return False, "Tài khoản này đang ở trạng thái Hoạt động.", 400

    db.execute('''
        UPDATE nguoi_dung
        SET trang_thai = 'HOAT_DONG',
            so_lan_dang_nhap_sai = 0,
            khoa_den = NULL
        WHERE nguoi_dung_id = ?
    ''', (user_id,))
    db.commit()

    return True, f"Đã mở khóa tài khoản của {user['ho_va_ten']} thành công.", 200

def reset_user_password(user_id: int, custom_password: str = None) -> tuple[bool, str, str | None, int]:
    """Đặt lại mật khẩu cho người dùng (Văn thư thực hiện)."""
    db = get_db()
    user = db.execute('SELECT nguoi_dung_id, ho_va_ten FROM nguoi_dung WHERE nguoi_dung_id = ?', (user_id,)).fetchone()
    if not user:
        return False, "Không tìm thấy người dùng.", None, 404

    if custom_password:
        valid_pw, pw_msg = validate_password(custom_password)
        if not valid_pw:
            return False, pw_msg, None, 400
        mat_khau_moi = custom_password
    else:
        mat_khau_moi = generate_random_password(10)

    mat_khau_hash = generate_password_hash(mat_khau_moi)

    db.execute('''
        UPDATE nguoi_dung
        SET mat_khau_hash = ?,
            bat_buoc_doi_mat_khau = 1,
            so_lan_dang_nhap_sai = 0,
            khoa_den = NULL
        WHERE nguoi_dung_id = ?
    ''', (mat_khau_hash, user_id))
    db.commit()

    return True, f"Đặt lại mật khẩu cho {user['ho_va_ten']} thành công.", mat_khau_moi, 200
