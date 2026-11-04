from datetime import datetime
from database.db import get_db

def get_current_time_str() -> str:
    """Lấy thời gian hiện tại định dạng ISO."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_ho_so_list(q: str = None, tinh_trang: str = None, nam_tai_lieu: int = None, don_vi: str = None) -> list[dict]:
    """Lấy danh sách hồ sơ lưu trữ có lọc và tìm kiếm."""
    db = get_db()
    query = '''
        SELECT ho_so_id, ma_ho_so, tieu_de, nguoi_lap_id, nguoi_lap,
               don_vi, nam_tai_lieu, thoi_han_bao_quan, so_luong_van_ban,
               tinh_trang, mo_ta, ngay_tao, ngay_cap_nhat
        FROM ho_so_luu_tru
        WHERE 1=1
    '''
    params = []

    if q:
        kw = f"%{q.strip()}%"
        query += '''
            AND (ma_ho_so LIKE ? OR tieu_de LIKE ? OR don_vi LIKE ? OR nguoi_lap LIKE ?)
        '''
        params.extend([kw, kw, kw, kw])

    if tinh_trang:
        query += ' AND tinh_trang = ?'
        params.append(tinh_trang.strip())

    if nam_tai_lieu:
        query += ' AND nam_tai_lieu = ?'
        params.append(int(nam_tai_lieu))

    if don_vi:
        query += ' AND don_vi LIKE ?'
        params.append(f"%{don_vi.strip()}%")

    query += ' ORDER BY ho_so_id DESC'

    cur = db.execute(query, params)
    rows = cur.fetchall()

    result = []
    for r in rows:
        result.append({
            'id': r['ho_so_id'],
            'ho_so_id': r['ho_so_id'],
            'ma_ho_so': r['ma_ho_so'],
            'tieu_de': r['tieu_de'],
            'nguoi_lap_id': r['nguoi_lap_id'],
            'nguoi_lap': r['nguoi_lap'],
            'don_vi': r['don_vi'],
            'nam_tai_lieu': r['nam_tai_lieu'],
            'thoi_han_bao_quan': r['thoi_han_bao_quan'],
            'so_luong_van_ban': r['so_luong_van_ban'],
            'tinh_trang': r['tinh_trang'],
            'mo_ta': r['mo_ta'] or '',
            'ngay_tao': r['ngay_tao'],
            'ngay_cap_nhat': r['ngay_cap_nhat']
        })
    return result

def get_ho_so_by_id(ho_so_id: int) -> dict | None:
    """Lấy thông tin chi tiết của 1 hồ sơ lưu trữ theo ID."""
    db = get_db()
    cur = db.execute('''
        SELECT ho_so_id, ma_ho_so, tieu_de, nguoi_lap_id, nguoi_lap,
               don_vi, nam_tai_lieu, thoi_han_bao_quan, so_luong_van_ban,
               tinh_trang, mo_ta, ngay_tao, ngay_cap_nhat
        FROM ho_so_luu_tru
        WHERE ho_so_id = ?
    ''', (ho_so_id,))
    r = cur.fetchone()
    if not r:
        return None

    return {
        'id': r['ho_so_id'],
        'ho_so_id': r['ho_so_id'],
        'ma_ho_so': r['ma_ho_so'],
        'tieu_de': r['tieu_de'],
        'nguoi_lap_id': r['nguoi_lap_id'],
        'nguoi_lap': r['nguoi_lap'],
        'don_vi': r['don_vi'],
        'nam_tai_lieu': r['nam_tai_lieu'],
        'thoi_han_bao_quan': r['thoi_han_bao_quan'],
        'so_luong_van_ban': r['so_luong_van_ban'],
        'tinh_trang': r['tinh_trang'],
        'mo_ta': r['mo_ta'] or '',
        'ngay_tao': r['ngay_tao'],
        'ngay_cap_nhat': r['ngay_cap_nhat']
    }

def create_ho_so(data: dict, current_user: dict) -> tuple[bool, str, dict | None, int]:
    """Tạo mới hồ sơ lưu trữ tài liệu."""
    tieu_de = (data.get('tieu_de') or '').strip()
    ma_ho_so = (data.get('ma_ho_so') or '').strip().upper()
    nam_tai_lieu = data.get('nam_tai_lieu') or 2026
    thoi_han_bao_quan = (data.get('thoi_han_bao_quan') or '10 năm').strip()
    don_vi = (data.get('don_vi') or current_user.get('phong_ban') or 'Văn phòng Sở GD&ĐT').strip()
    nguoi_lap = (data.get('nguoi_lap') or current_user.get('ho_va_ten') or 'Cán bộ lập hồ sơ').strip()
    mo_ta = (data.get('mo_ta') or '').strip()

    if not tieu_de or not ma_ho_so:
        return False, "Tiêu đề và mã hồ sơ là các trường bắt buộc.", None, 400

    try:
        nam_tai_lieu = int(nam_tai_lieu)
    except (ValueError, TypeError):
        nam_tai_lieu = 2026

    db = get_db()
    # Kiểm tra mã hồ sơ trùng lặp
    check_cur = db.execute('SELECT ho_so_id FROM ho_so_luu_tru WHERE ma_ho_so = ?', (ma_ho_so,))
    if check_cur.fetchone():
        return False, f"Mã hồ sơ '{ma_ho_so}' đã tồn tại trong hệ thống.", None, 409

    now = get_current_time_str()
    cur = db.execute('''
        INSERT INTO ho_so_luu_tru (
            ma_ho_so, tieu_de, nguoi_lap_id, nguoi_lap, don_vi,
            nam_tai_lieu, thoi_han_bao_quan, so_luong_van_ban, tinh_trang,
            mo_ta, ngay_tao, ngay_cap_nhat
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'DANG_THU_THAP', ?, ?, ?)
    ''', (
        ma_ho_so,
        tieu_de,
        current_user.get('nguoi_dung_id'),
        nguoi_lap,
        don_vi,
        nam_tai_lieu,
        thoi_han_bao_quan,
        mo_ta,
        now,
        now
    ))
    db.commit()
    new_id = cur.lastrowid
    created_hs = get_ho_so_by_id(new_id)

    return True, "Khởi tạo hồ sơ lưu trữ thành công.", created_hs, 201

def update_ho_so(ho_so_id: int, data: dict, current_user: dict) -> tuple[bool, str, dict | None, int]:
    """Cập nhật thông tin hồ sơ lưu trữ."""
    existing = get_ho_so_by_id(ho_so_id)
    if not existing:
        return False, "Không tìm thấy hồ sơ lưu trữ yêu cầu.", None, 404

    if existing['tinh_trang'] == 'DA_DONG' and current_user.get('vai_tro') != 'VAN_THU':
        return False, "Hồ sơ đã đóng, chỉ Văn thư mới có quyền chỉnh sửa.", None, 403

    tieu_de = (data.get('tieu_de') or existing['tieu_de']).strip()
    ma_ho_so = (data.get('ma_ho_so') or existing['ma_ho_so']).strip().upper()
    nam_tai_lieu = data.get('nam_tai_lieu') or existing['nam_tai_lieu']
    thoi_han_bao_quan = (data.get('thoi_han_bao_quan') or existing['thoi_han_bao_quan']).strip()
    don_vi = (data.get('don_vi') or existing['don_vi']).strip()
    mo_ta = data.get('mo_ta', existing['mo_ta'])

    try:
        nam_tai_lieu = int(nam_tai_lieu)
    except (ValueError, TypeError):
        nam_tai_lieu = existing['nam_tai_lieu']

    db = get_db()
    # Kiểm tra mã hồ sơ trùng lặp với hồ sơ khác
    if ma_ho_so != existing['ma_ho_so']:
        check_cur = db.execute('SELECT ho_so_id FROM ho_so_luu_tru WHERE ma_ho_so = ? AND ho_so_id != ?', (ma_ho_so, ho_so_id))
        if check_cur.fetchone():
            return False, f"Mã hồ sơ '{ma_ho_so}' đã được sử dụng bởi hồ sơ khác.", None, 409

    now = get_current_time_str()
    db.execute('''
        UPDATE ho_so_luu_tru
        SET ma_ho_so = ?, tieu_de = ?, don_vi = ?, nam_tai_lieu = ?,
            thoi_han_bao_quan = ?, mo_ta = ?, ngay_cap_nhat = ?
        WHERE ho_so_id = ?
    ''', (ma_ho_so, tieu_de, don_vi, nam_tai_lieu, thoi_han_bao_quan, mo_ta, now, ho_so_id))
    db.commit()

    updated_hs = get_ho_so_by_id(ho_so_id)
    return True, "Cập nhật hồ sơ thành công.", updated_hs, 200

def submit_ho_so_to_archive(ho_so_id: int, current_user: dict) -> tuple[bool, str, dict | None, int]:
    """Nộp hồ sơ vào kho lưu trữ cơ quan Sở GD&ĐT."""
    existing = get_ho_so_by_id(ho_so_id)
    if not existing:
        return False, "Không tìm thấy hồ sơ lưu trữ.", None, 404

    db = get_db()
    now = get_current_time_str()
    db.execute('''
        UPDATE ho_so_luu_tru
        SET tinh_trang = 'DA_NOP_LUU_TRU', ngay_cap_nhat = ?
        WHERE ho_so_id = ?
    ''', (now, ho_so_id))
    db.commit()

    updated_hs = get_ho_so_by_id(ho_so_id)
    return True, "Đã nộp hồ sơ vào Kho lưu trữ cơ quan thành công.", updated_hs, 200

def close_ho_so(ho_so_id: int, current_user: dict) -> tuple[bool, str, dict | None, int]:
    """Đóng hồ sơ lưu trữ."""
    existing = get_ho_so_by_id(ho_so_id)
    if not existing:
        return False, "Không tìm thấy hồ sơ lưu trữ.", None, 404

    db = get_db()
    now = get_current_time_str()
    db.execute('''
        UPDATE ho_so_luu_tru
        SET tinh_trang = 'DA_DONG', ngay_cap_nhat = ?
        WHERE ho_so_id = ?
    ''', (now, ho_so_id))
    db.commit()

    updated_hs = get_ho_so_by_id(ho_so_id)
    return True, "Đã đóng hồ sơ lưu trữ thành công.", updated_hs, 200

def delete_ho_so(ho_so_id: int, current_user: dict) -> tuple[bool, str, int]:
    """Xóa hồ sơ lưu trữ (chỉ khi đang thu thập hoặc là Văn thư)."""
    existing = get_ho_so_by_id(ho_so_id)
    if not existing:
        return False, "Không tìm thấy hồ sơ lưu trữ.", 404

    if existing['tinh_trang'] != 'DANG_THU_THAP' and current_user.get('vai_tro') != 'VAN_THU':
        return False, "Hồ sơ đã nộp lưu trữ hoặc đã đóng, chỉ Văn thư mới có quyền xóa.", 403

    db = get_db()
    db.execute('DELETE FROM ho_so_luu_tru WHERE ho_so_id = ?', (ho_so_id,))
    db.commit()
    return True, "Đã xóa hồ sơ lưu trữ thành công.", 200