from datetime import datetime
from database.db import get_db

def get_current_time_str() -> str:
    """Lấy thời gian hiện tại định dạng ISO."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_ho_so_list(q: str = None, tinh_trang: str = None, nam_tai_lieu: int = None, don_vi: str = None) -> list[dict]:
    """Lấy danh sách hồ sơ lưu trữ có lọc và tìm kiếm, đồng bộ số lượng văn bản thực tế."""
    db = get_db()
    query = '''
        SELECT hs.ho_so_id, hs.ma_ho_so, hs.tieu_de, hs.nguoi_lap_id, hs.nguoi_lap,
               hs.don_vi, hs.nam_tai_lieu, hs.thoi_han_bao_quan,
               (
                   (SELECT COUNT(*) FROM van_ban_di v WHERE v.ho_so_id = hs.ho_so_id AND v.trang_thai = 'DA_BAN_HANH') +
                   (SELECT COUNT(*) FROM van_ban_ban_hanh b WHERE b.ho_so_id = hs.ho_so_id)
               ) AS so_luong_van_ban,
               hs.tinh_trang, hs.mo_ta, hs.ngay_tao, hs.ngay_cap_nhat
        FROM ho_so_luu_tru hs
        WHERE 1=1
    '''
    params = []

    if q:
        kw = f"%{q.strip()}%"
        query += '''
            AND (hs.ma_ho_so LIKE ? OR hs.tieu_de LIKE ? OR hs.don_vi LIKE ? OR hs.nguoi_lap LIKE ?)
        '''
        params.extend([kw, kw, kw, kw])

    if tinh_trang:
        query += ' AND hs.tinh_trang = ?'
        params.append(tinh_trang.strip())

    if nam_tai_lieu:
        query += ' AND hs.nam_tai_lieu = ?'
        params.append(int(nam_tai_lieu))

    if don_vi:
        query += ' AND hs.don_vi LIKE ?'
        params.append(f"%{don_vi.strip()}%")

    query += ' ORDER BY hs.ho_so_id DESC'

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
    """Lấy thông tin chi tiết của 1 hồ sơ lưu trữ theo ID, đồng bộ số lượng văn bản thực tế."""
    db = get_db()
    cur = db.execute('''
        SELECT hs.ho_so_id, hs.ma_ho_so, hs.tieu_de, hs.nguoi_lap_id, hs.nguoi_lap,
               hs.don_vi, hs.nam_tai_lieu, hs.thoi_han_bao_quan,
               (
                   (SELECT COUNT(*) FROM van_ban_di v WHERE v.ho_so_id = hs.ho_so_id AND v.trang_thai = 'DA_BAN_HANH') +
                   (SELECT COUNT(*) FROM van_ban_ban_hanh b WHERE b.ho_so_id = hs.ho_so_id)
               ) AS so_luong_van_ban,
               hs.tinh_trang, hs.mo_ta, hs.ngay_tao, hs.ngay_cap_nhat
        FROM ho_so_luu_tru hs
        WHERE hs.ho_so_id = ?
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
    # Gỡ liên kết hồ sơ ở các văn bản
    db.execute('UPDATE van_ban_di SET ho_so_id = NULL WHERE ho_so_id = ?', (ho_so_id,))
    db.execute('UPDATE van_ban_ban_hanh SET ho_so_id = NULL WHERE ho_so_id = ?', (ho_so_id,))
    db.execute('DELETE FROM ho_so_luu_tru WHERE ho_so_id = ?', (ho_so_id,))
    db.commit()
    return True, "Đã xóa hồ sơ lưu trữ thành công.", 200

def get_van_ban_in_ho_so(ho_so_id: int) -> list[dict]:
    """Lấy danh sách toàn bộ văn bản thực tế đang lưu trữ trong hồ sơ này."""
    db = get_db()
    result = []

    # 1. Từ bảng van_ban_di (văn bản đi đã ban hành trong quy trình nội bộ)
    cur_di = db.execute('''
        SELECT van_ban_id, so_ky_hieu, trich_yeu, loai_van_ban, don_vi_soan_thao,
               lanh_dao_ky_ten, ngay_ban_hanh, file_goc_ten, file_da_ky_ten,
               file_da_ky_path, file_goc_path, ngay_tao
        FROM van_ban_di
        WHERE ho_so_id = ? AND trang_thai = 'DA_BAN_HANH'
        ORDER BY van_ban_id DESC
    ''', (ho_so_id,))
    for r in cur_di.fetchall():
        ten_file = r['file_da_ky_ten'] or r['file_goc_ten'] or 'Tài liệu số hóa'
        has_signed = bool(r['file_da_ky_path'])
        result.append({
            'van_ban_id': r['van_ban_id'],
            'nguon': 'van_ban_di',
            'so_ky_hieu': r['so_ky_hieu'] or f"Dự thảo #{r['van_ban_id']}",
            'trich_yeu': r['trich_yeu'],
            'loai_van_ban': r['loai_van_ban'] or 'Văn bản',
            'don_vi_soan_thao': r['don_vi_soan_thao'] or 'Sở GD&ĐT',
            'nguoi_ky': r['lanh_dao_ky_ten'] or 'Lãnh đạo Sở',
            'ngay_ban_hanh': r['ngay_ban_hanh'] or (r['ngay_tao'][:10] if r['ngay_tao'] else '2026-11-04'),
            'tep_dinh_kem': ten_file,
            'preview_url': f"/api/van-ban-di/{r['van_ban_id']}/preview?type={'da_ky' if has_signed else 'goc'}",
            'download_url': f"/api/van-ban-di/{r['van_ban_id']}/download?type={'da_ky' if has_signed else 'goc'}"
        })

    # 2. Từ bảng van_ban_ban_hanh (văn bản đã lưu kho số hóa)
    cur_bh = db.execute('''
        SELECT van_ban_id, so_ky_hieu, trich_yeu, loai_van_ban, don_vi_soan_thao,
               nguoi_ky, ngay_ban_hanh, tep_dinh_kem
        FROM van_ban_ban_hanh
        WHERE ho_so_id = ?
        ORDER BY van_ban_id DESC
    ''', (ho_so_id,))
    for r in cur_bh.fetchall():
        result.append({
            'van_ban_id': r['van_ban_id'],
            'nguon': 'van_ban_ban_hanh',
            'so_ky_hieu': r['so_ky_hieu'],
            'trich_yeu': r['trich_yeu'],
            'loai_van_ban': r['loai_van_ban'] or 'Văn bản',
            'don_vi_soan_thao': r['don_vi_soan_thao'] or 'Sở GD&ĐT',
            'nguoi_ky': r['nguoi_ky'] or 'Lãnh đạo cơ quan',
            'ngay_ban_hanh': r['ngay_ban_hanh'] or '2026-10-25',
            'tep_dinh_kem': r['tep_dinh_kem'] or 'Tài liệu số hóa.pdf',
            'preview_url': f"/api/kho-van-ban/ban-hanh/{r['van_ban_id']}/tai-ve",
            'download_url': f"/api/kho-van-ban/ban-hanh/{r['van_ban_id']}/tai-ve"
        })

    return result

def get_available_van_ban(ho_so_id: int) -> list[dict]:
    """Lấy danh sách các văn bản đã ban hành có thể bổ sung vào hồ sơ lưu trữ này."""
    db = get_db()
    result = []

    # Văn bản đi đã ban hành chưa thuộc hồ sơ này
    cur_di = db.execute('''
        SELECT van_ban_id, so_ky_hieu, trich_yeu, loai_van_ban, don_vi_soan_thao,
               lanh_dao_ky_ten, ngay_ban_hanh, file_da_ky_ten, file_goc_ten
        FROM van_ban_di
        WHERE trang_thai = 'DA_BAN_HANH' AND (ho_so_id IS NULL OR ho_so_id != ?)
        ORDER BY van_ban_id DESC
    ''', (ho_so_id,))
    for r in cur_di.fetchall():
        result.append({
            'van_ban_id': r['van_ban_id'],
            'nguon': 'van_ban_di',
            'so_ky_hieu': r['so_ky_hieu'],
            'trich_yeu': r['trich_yeu'],
            'loai_van_ban': r['loai_van_ban'],
            'don_vi_soan_thao': r['don_vi_soan_thao'],
            'nguoi_ky': r['lanh_dao_ky_ten'] or 'Lãnh đạo Sở',
            'ngay_ban_hanh': r['ngay_ban_hanh'],
            'tep_dinh_kem': r['file_da_ky_ten'] or r['file_goc_ten'] or 'Tài liệu'
        })

    # Văn bản đã ban hành từ kho lưu trữ chưa thuộc hồ sơ này
    cur_bh = db.execute('''
        SELECT van_ban_id, so_ky_hieu, trich_yeu, loai_van_ban, don_vi_soan_thao,
               nguoi_ky, ngay_ban_hanh, tep_dinh_kem
        FROM van_ban_ban_hanh
        WHERE (ho_so_id IS NULL OR ho_so_id != ?)
        ORDER BY van_ban_id DESC
    ''', (ho_so_id,))
    for r in cur_bh.fetchall():
        result.append({
            'van_ban_id': r['van_ban_id'],
            'nguon': 'van_ban_ban_hanh',
            'so_ky_hieu': r['so_ky_hieu'],
            'trich_yeu': r['trich_yeu'],
            'loai_van_ban': r['loai_van_ban'],
            'don_vi_soan_thao': r['don_vi_soan_thao'] or 'Sở GD&ĐT',
            'nguoi_ky': r['nguoi_ky'],
            'ngay_ban_hanh': r['ngay_ban_hanh'],
            'tep_dinh_kem': r['tep_dinh_kem'] or 'Tài liệu'
        })

    return result

def add_van_ban_to_ho_so(ho_so_id: int, van_ban_id: int, nguon: str = 'van_ban_di') -> tuple[bool, str, int]:
    """Bổ sung một văn bản đã ban hành vào hồ sơ lưu trữ."""
    hs = get_ho_so_by_id(ho_so_id)
    if not hs:
        return False, "Không tìm thấy hồ sơ lưu trữ.", 404

    if hs['tinh_trang'] == 'DA_DONG':
        return False, "Hồ sơ đã đóng, không thể bổ sung thêm văn bản.", 400

    db = get_db()
    if nguon == 'van_ban_ban_hanh':
        db.execute('UPDATE van_ban_ban_hanh SET ho_so_id = ? WHERE van_ban_id = ?', (ho_so_id, van_ban_id))
    else:
        db.execute('UPDATE van_ban_di SET ho_so_id = ? WHERE van_ban_id = ?', (ho_so_id, van_ban_id))

    # Cập nhật số lượng văn bản trong hồ sơ
    count_cur = db.execute('''
        SELECT 
            (SELECT COUNT(*) FROM van_ban_di WHERE ho_so_id = ? AND trang_thai = 'DA_BAN_HANH') +
            (SELECT COUNT(*) FROM van_ban_ban_hanh WHERE ho_so_id = ?)
    ''', (ho_so_id, ho_so_id))
    total_vb = count_cur.fetchone()[0]
    db.execute('UPDATE ho_so_luu_tru SET so_luong_van_ban = ?, ngay_cap_nhat = CURRENT_TIMESTAMP WHERE ho_so_id = ?', (total_vb, ho_so_id))
    db.commit()

    return True, "Đã thêm văn bản vào hồ sơ lưu trữ thành công.", 200

def remove_van_ban_from_ho_so(ho_so_id: int, van_ban_id: int, nguon: str = 'van_ban_di') -> tuple[bool, str, int]:
    """Gỡ một văn bản ra khỏi hồ sơ lưu trữ."""
    hs = get_ho_so_by_id(ho_so_id)
    if not hs:
        return False, "Không tìm thấy hồ sơ lưu trữ.", 404

    if hs['tinh_trang'] == 'DA_DONG':
        return False, "Hồ sơ đã đóng, không thể thay đổi danh mục văn bản.", 400

    db = get_db()
    if nguon == 'van_ban_ban_hanh':
        db.execute('UPDATE van_ban_ban_hanh SET ho_so_id = NULL WHERE van_ban_id = ? AND ho_so_id = ?', (van_ban_id, ho_so_id))
    else:
        db.execute('UPDATE van_ban_di SET ho_so_id = NULL WHERE van_ban_id = ? AND ho_so_id = ?', (van_ban_id, ho_so_id))

    # Cập nhật số lượng văn bản trong hồ sơ
    count_cur = db.execute('''
        SELECT 
            (SELECT COUNT(*) FROM van_ban_di WHERE ho_so_id = ? AND trang_thai = 'DA_BAN_HANH') +
            (SELECT COUNT(*) FROM van_ban_ban_hanh WHERE ho_so_id = ?)
    ''', (ho_so_id, ho_so_id))
    total_vb = count_cur.fetchone()[0]
    db.execute('UPDATE ho_so_luu_tru SET so_luong_van_ban = ?, ngay_cap_nhat = CURRENT_TIMESTAMP WHERE ho_so_id = ?', (total_vb, ho_so_id))
    db.commit()

    return True, "Đã gỡ văn bản khỏi hồ sơ lưu trữ thành công.", 200
