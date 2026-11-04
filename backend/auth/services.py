import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db
from config import Config

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9._]{4,30}$')

def validate_email(email: str) -> bool:
    """Kiểm tra định dạng email hợp lệ."""
    if not email or len(email) > 100:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_username(username: str) -> bool:
    """Tên đăng nhập 4-30 ký tự, gồm chữ cái, số, dấu chấm và gạch dưới."""
    if not username:
        return False
    return bool(USERNAME_REGEX.match(username.strip()))

def validate_password(password: str) -> tuple[bool, str]:
    """Mật khẩu ít nhất 8 ký tự, bao gồm cả chữ cái và số."""
    if not password or len(password) < 8:
        return False, "Mật khẩu phải có độ dài tối thiểu 8 ký tự."
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_letter and has_digit):
        return False, "Mật khẩu phải chứa ít nhất một chữ cái và một chữ số."
    return True, ""

def get_current_time_str() -> str:
    """Lấy thời gian hiện tại định dạng ISO chuẩn."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def parse_time_str(time_str: str) -> datetime | None:
    """Chuyển chuỗi thời gian thành đối tượng datetime."""
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.fromisoformat(time_str)
        except ValueError:
            return None

def register_user(data: dict) -> tuple[bool, str, int]:
    """Xử lý đăng ký tài khoản Chuyên viên hoặc Văn thư."""
    ten_dang_nhap = (data.get('ten_dang_nhap') or '').strip()
    mat_khau = data.get('mat_khau') or ''
    ho_va_ten = (data.get('ho_va_ten') or '').strip()
    email = (data.get('email') or '').strip().lower()
    sdt = (data.get('sdt') or '').strip()
    phong_ban = (data.get('phong_ban') or '').strip()
    chuc_vu = (data.get('chuc_vu') or '').strip()
    vai_tro = (data.get('vai_tro') or '').strip().upper()
    ma_noi_bo = (data.get('ma_noi_bo') or '').strip()

    # Kiểm tra dữ liệu bắt buộc
    if not all([ten_dang_nhap, mat_khau, ho_va_ten, email, vai_tro]):
        return False, "Vui lòng điền đầy đủ các thông tin bắt buộc.", 400

    if vai_tro not in ('CHUYEN_VIEN', 'VAN_THU'):
        return False, "Vai trò đăng ký không hợp lệ. Chỉ chấp nhận Chuyên viên hoặc Văn thư.", 400

    if not validate_username(ten_dang_nhap):
        return False, "Tên đăng nhập từ 4-30 ký tự, chỉ gồm chữ cái, số, dấu chấm (.) và gạch dưới (_).", 400

    if not validate_email(email):
        return False, "Định dạng email không hợp lệ.", 400

    valid_pw, pw_msg = validate_password(mat_khau)
    if not valid_pw:
        return False, pw_msg, 400

    # Kiểm tra mã nội bộ nếu đăng ký vai trò Văn thư
    if vai_tro == 'VAN_THU':
        if not ma_noi_bo or ma_noi_bo != Config.INTERNAL_CODE:
            return False, "Mã xác nhận nội bộ dành cho Văn thư không chính xác.", 400
        trang_thai = 'HOAT_DONG'
        bat_buoc_doi_mk = 0
    else:
        # Chuyên viên phải chờ duyệt
        trang_thai = 'CHO_DUYET'
        bat_buoc_doi_mk = 0

    db = get_db()

    # Kiểm tra trùng tên đăng nhập
    cursor = db.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE ten_dang_nhap = ?', (ten_dang_nhap,))
    if cursor.fetchone():
        return False, "Tên đăng nhập đã tồn tại trong hệ thống.", 409

    # Kiểm tra trùng email
    cursor = db.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE email = ?', (email,))
    if cursor.fetchone():
        return False, "Địa chỉ email đã được sử dụng.", 409

    mat_khau_hash = generate_password_hash(mat_khau)
    now_str = get_current_time_str()

    try:
        db.execute('''
            INSERT INTO nguoi_dung (
                ten_dang_nhap, mat_khau_hash, ho_va_ten, email, sdt,
                phong_ban, chuc_vu, vai_tro, trang_thai,
                bat_buoc_doi_mat_khau, so_lan_dang_nhap_sai, ngay_tao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ten_dang_nhap, mat_khau_hash, ho_va_ten, email, sdt,
            phong_ban, chuc_vu, vai_tro, trang_thai,
            bat_buoc_doi_mk, 0, now_str
        ))
        db.commit()
    except Exception as e:
        return False, f"Lỗi khi lưu dữ liệu người dùng: {str(e)}", 500

    if vai_tro == 'CHUYEN_VIEN':
        msg = "Đăng ký thành công! Tài khoản của bạn đang chờ Văn thư phê duyệt trước khi có thể đăng nhập."
    else:
        msg = "Đăng ký tài khoản Văn thư thành công! Bạn có thể đăng nhập ngay bây giờ."

    return True, msg, 201

def authenticate_user(ten_dang_nhap: str, mat_khau: str) -> tuple[bool, str, dict | None, int]:
    """Xác thực đăng nhập người dùng với đầy đủ kiểm tra trạng thái và khóa tạm."""
    if not ten_dang_nhap or not mat_khau:
        return False, "Vui lòng nhập tên đăng nhập và mật khẩu.", None, 400

    db = get_db()
    user = db.execute('''
        SELECT nguoi_dung_id, ten_dang_nhap, mat_khau_hash, ho_va_ten,
               email, sdt, phong_ban, chuc_vu, vai_tro, trang_thai,
               ly_do_tu_choi, bat_buoc_doi_mat_khau, so_lan_dang_nhap_sai,
               khoa_den
        FROM nguoi_dung
        WHERE ten_dang_nhap = ?
    ''', (ten_dang_nhap.strip(),)).fetchone()

    # Không tồn tại user: thông báo chung chung
    if not user:
        return False, "Tên đăng nhập hoặc mật khẩu không đúng.", None, 401

    user_dict = dict(user)
    now = datetime.now()

    # 1. Kiểm tra tài khoản có đang bị khóa tạm thời (brute-force) hay không
    if user_dict.get('khoa_den'):
        khoa_den_dt = parse_time_str(user_dict['khoa_den'])
        if khoa_den_dt and now < khoa_den_dt:
            con_lai_giay = int((khoa_den_dt - now).total_seconds())
            con_lai_phut = max(1, (con_lai_giay + 59) // 60)
            return False, f"Tài khoản đang bị tạm khóa do nhập sai mật khẩu quá 5 lần. Vui lòng thử lại sau {con_lai_phut} phút.", None, 423
        else:
            # Hết thời gian khóa tạm -> mở lại số lần sai
            db.execute('''
                UPDATE nguoi_dung
                SET so_lan_dang_nhap_sai = 0, khoa_den = NULL
                WHERE nguoi_dung_id = ?
            ''', (user_dict['nguoi_dung_id'],))
            db.commit()
            user_dict['so_lan_dang_nhap_sai'] = 0

    # 2. Kiểm tra mật khẩu
    if not check_password_hash(user_dict['mat_khau_hash'], mat_khau):
        so_lan_sai = user_dict['so_lan_dang_nhap_sai'] + 1
        if so_lan_sai >= 5:
            khoa_den_moi = (now + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
            db.execute('''
                UPDATE nguoi_dung
                SET so_lan_dang_nhap_sai = ?, khoa_den = ?
                WHERE nguoi_dung_id = ?
            ''', (so_lan_sai, khoa_den_moi, user_dict['nguoi_dung_id']))
            db.commit()
            return False, "Tài khoản tạm thời bị khóa 15 phút do nhập sai mật khẩu 5 lần liên tiếp.", None, 423
        else:
            db.execute('''
                UPDATE nguoi_dung
                SET so_lan_dang_nhap_sai = ?
                WHERE nguoi_dung_id = ?
            ''', (so_lan_sai, user_dict['nguoi_dung_id']))
            db.commit()
            return False, "Tên đăng nhập hoặc mật khẩu không đúng.", None, 401

    # 3. Mật khẩu đúng -> reset số lần đăng nhập sai và khóa tạm
    now_str = get_current_time_str()
    db.execute('''
        UPDATE nguoi_dung
        SET so_lan_dang_nhap_sai = 0, khoa_den = NULL, lan_dang_nhap_cuoi = ?
        WHERE nguoi_dung_id = ?
    ''', (now_str, user_dict['nguoi_dung_id']))
    db.commit()

    # 4. Kiểm tra trạng thái tài khoản
    trang_thai = user_dict['trang_thai']
    if trang_thai == 'CHO_DUYET':
        return False, "Tài khoản đang chờ Văn thư duyệt.", None, 403
    elif trang_thai == 'TU_CHOI':
        ly_do = user_dict.get('ly_do_tu_choi') or "Không có lý do chi tiết."
        return False, f"Tài khoản đã bị từ chối phê duyệt: {ly_do}", None, 403
    elif trang_thai == 'BI_KHOA':
        return False, "Tài khoản đã bị khóa bởi Quản trị viên.", None, 403
    elif trang_thai != 'HOAT_DONG':
        return False, "Trạng thái tài khoản không hợp lệ.", None, 403

    # Chuẩn bị dữ liệu trả về (TUYỆT ĐỐI không trả hash mật khẩu)
    user_payload = {
        'nguoi_dung_id': user_dict['nguoi_dung_id'],
        'ten_dang_nhap': user_dict['ten_dang_nhap'],
        'ho_va_ten': user_dict['ho_va_ten'],
        'email': user_dict['email'],
        'sdt': user_dict.get('sdt'),
        'phong_ban': user_dict.get('phong_ban'),
        'chuc_vu': user_dict.get('chuc_vu'),
        'vai_tro': user_dict['vai_tro'],
        'bat_buoc_doi_mat_khau': bool(user_dict['bat_buoc_doi_mat_khau'])
    }

    return True, "Đăng nhập thành công.", user_payload, 200

def change_user_password(user_id: int, mat_khau_cu: str, mat_khau_moi: str) -> tuple[bool, str, int]:
    """Đổi mật khẩu người dùng hiện tại."""
    if not mat_khau_cu or not mat_khau_moi:
        return False, "Vui lòng nhập đầy đủ mật khẩu cũ và mật khẩu mới.", 400

    valid_pw, pw_msg = validate_password(mat_khau_moi)
    if not valid_pw:
        return False, pw_msg, 400

    if mat_khau_cu == mat_khau_moi:
        return False, "Mật khẩu mới phải khác mật khẩu hiện tại.", 400

    db = get_db()
    user = db.execute('SELECT mat_khau_hash FROM nguoi_dung WHERE nguoi_dung_id = ?', (user_id,)).fetchone()
    if not user:
        return False, "Người dùng không tồn tại.", 404

    if not check_password_hash(user['mat_khau_hash'], mat_khau_cu):
        return False, "Mật khẩu hiện tại không chính xác.", 400

    mat_khau_moi_hash = generate_password_hash(mat_khau_moi)
    db.execute('''
        UPDATE nguoi_dung
        SET mat_khau_hash = ?, bat_buoc_doi_mat_khau = 0
        WHERE nguoi_dung_id = ?
    ''', (mat_khau_moi_hash, user_id))
    db.commit()

    return True, "Đổi mật khẩu thành công.", 200
