# ==============================================================================
# MODELS/REPOSITORY_MODEL.PY - MVC ARCHITECTURE (MODEL LAYER)
# ==============================================================================

import re
from datetime import datetime
from database.db import get_db

def get_current_time_str() -> str:
    """Lấy thời gian hiện tại định dạng ISO."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def parse_date_to_parts(date_str: str) -> tuple[int, int, int]:
    """Phân tích chuỗi YYYY-MM-DD thành (nam, thang, quy)."""
    try:
        dt = datetime.strptime(date_str.strip(), '%Y-%m-%d')
        nam = dt.year
        thang = dt.month
        quy = (thang - 1) // 3 + 1
        return nam, thang, quy
    except Exception:
        now = datetime.now()
        return now.year, now.month, (now.month - 1) // 3 + 1

def calculate_expiry_year(nam_luu_tru: int, thoi_han_bao_quan: str) -> int | None:
    """Tính toán năm hết hạn lưu trữ phục vụ cảnh báo tiêu hủy."""
    if not thoi_han_bao_quan or 'vĩnh viễn' in thoi_han_bao_quan.lower():
        return None
    match = re.search(r'\d+', thoi_han_bao_quan)
    if match:
        years = int(match.group())
        return nam_luu_tru + years
    return None

# ==============================================================================
# PHÂN HỆ 1: KHO VĂN BẢN ĐÃ KÝ BAN HÀNH (DATE-TIME CHRONOLOGICAL ARCHIVE)
# ==============================================================================

def get_cay_nien_dai() -> list[dict]:
    """
    Sinh cấu trúc cây niên đại lưu trữ (Timeline Tree):
    Năm lưu trữ -> Quý -> Tháng & số lượng văn bản lưu trong từng mốc.
    """
    db = get_db()
    cur = db.execute('''
        SELECT nam_luu_tru, quy_luu_tru, thang_luu_tru, COUNT(*) as so_luong
        FROM van_ban_ban_hanh
        GROUP BY nam_luu_tru, quy_luu_tru, thang_luu_tru
        ORDER BY nam_luu_tru DESC, quy_luu_tru DESC, thang_luu_tru DESC
    ''')
    rows = cur.fetchall()

    tree_dict = {}
    for r in rows:
        nam = r['nam_luu_tru']
        quy = r['quy_luu_tru']
        thang = r['thang_luu_tru']
        sl = r['so_luong']

        if nam not in tree_dict:
            tree_dict[nam] = {'nam': nam, 'tong_so': 0, 'cac_quy': {}}

        tree_dict[nam]['tong_so'] += sl

        if quy not in tree_dict[nam]['cac_quy']:
            tree_dict[nam]['cac_quy'][quy] = {'quy': quy, 'so_luong': 0, 'thang': []}

        tree_dict[nam]['cac_quy'][quy]['so_luong'] += sl
        tree_dict[nam]['cac_quy'][quy]['thang'].append({'thang': thang, 'so_luong': sl})

    result = []
    for nam, nam_data in sorted(tree_dict.items(), key=lambda x: x[0], reverse=True):
        quy_list = []
        for quy, quy_data in sorted(nam_data['cac_quy'].items(), key=lambda x: x[0], reverse=True):
            quy_list.append(quy_data)
        result.append({
            'nam': nam,
            'tong_so': nam_data['tong_so'],
            'danh_sach_quy': quy_list
        })
    return result

def get_van_ban_ban_hanh_list(filters: dict = None) -> list[dict]:
    """Tìm kiếm và lọc văn bản đã ký ban hành theo mốc thời gian và tiêu chí."""
    filters = filters or {}
    db = get_db()

    query = '''
        SELECT v.*, hs.ma_ho_so as ten_ho_so_lien_ket
        FROM van_ban_ban_hanh v
        LEFT JOIN ho_so_luu_tru hs ON v.ho_so_id = hs.ho_so_id
        WHERE 1=1
    '''
    params = []

    # 1. Tìm kiếm toàn văn / từ khóa
    q = (filters.get('q') or '').strip()
    if q:
        kw = f"%{q}%"
        query += '''
            AND (v.so_ky_hieu LIKE ? OR v.trich_yeu LIKE ? OR v.nguoi_ky LIKE ?
                 OR v.don_vi_soan_thao LIKE ? OR v.tu_khoa LIKE ?)
        '''
        params.extend([kw, kw, kw, kw, kw])

    # 2. Bộ lọc theo mốc thời gian Date-Time
    if filters.get('nam'):
        query += ' AND v.nam_luu_tru = ?'
        params.append(int(filters['nam']))

    if filters.get('thang'):
        query += ' AND v.thang_luu_tru = ?'
        params.append(int(filters['thang']))

    if filters.get('quy'):
        query += ' AND v.quy_luu_tru = ?'
        params.append(int(filters['quy']))

    if filters.get('tu_ngay'):
        query += ' AND v.ngay_ban_hanh >= ?'
        params.append(filters['tu_ngay'].strip())

    if filters.get('den_ngay'):
        query += ' AND v.ngay_ban_hanh <= ?'
        params.append(filters['den_ngay'].strip())

    # 3. Bộ lọc nghiệp vụ
    if filters.get('loai_van_ban'):
        query += ' AND v.loai_van_ban = ?'
        params.append(filters['loai_van_ban'].strip())

    if filters.get('nguoi_ky'):
        query += ' AND v.nguoi_ky LIKE ?'
        params.append(f"%{filters['nguoi_ky'].strip()}%")

    if filters.get('don_vi'):
        query += ' AND v.don_vi_soan_thao LIKE ?'
        params.append(f"%{filters['don_vi'].strip()}%")

    if filters.get('thoi_han_bao_quan'):
        query += ' AND v.thoi_han_bao_quan = ?'
        params.append(filters['thoi_han_bao_quan'].strip())

    if filters.get('ho_so_id'):
        query += ' AND v.ho_so_id = ?'
        params.append(int(filters['ho_so_id']))

    query += ' ORDER BY v.ngay_ban_hanh DESC, v.van_ban_id DESC'

    cur = db.execute(query, params)
    rows = cur.fetchall()

    return [dict(r) for r in rows]

def get_van_ban_ban_hanh_by_id(van_ban_id: int) -> dict | None:
    """Lấy thông tin chi tiết một văn bản đã ký ban hành."""
    db = get_db()
    cur = db.execute('''
        SELECT v.*, hs.ma_ho_so as ten_ho_so_lien_ket, hs.tieu_de as tieu_de_ho_so
        FROM van_ban_ban_hanh v
        LEFT JOIN ho_so_luu_tru hs ON v.ho_so_id = hs.ho_so_id
        WHERE v.van_ban_id = ?
    ''', (van_ban_id,))
    row = cur.fetchone()
    return dict(row) if row else None

def create_van_ban_ban_hanh(data: dict, current_user: dict) -> tuple[bool, str, dict | None, int]:
    """Lưu văn bản đã ký ban hành vào kho lưu trữ số hóa."""
    so_ky_hieu = (data.get('so_ky_hieu') or '').strip().upper()
    trich_yeu = (data.get('trich_yeu') or '').strip()
    loai_van_ban = (data.get('loai_van_ban') or '').strip()
    nguoi_ky = (data.get('nguoi_ky') or '').strip()
    chuc_vu_nguoi_ky = (data.get('chuc_vu_nguoi_ky') or 'Lãnh đạo Sở').strip()
    ngay_ky = (data.get('ngay_ky') or datetime.now().strftime('%Y-%m-%d')).strip()
    ngay_ban_hanh = (data.get('ngay_ban_hanh') or ngay_ky).strip()
    thoi_han_bao_quan = (data.get('thoi_han_bao_quan') or '10 năm').strip()

    if not all([so_ky_hieu, trich_yeu, loai_van_ban, nguoi_ky, ngay_ban_hanh]):
        return False, "Vui lòng nhập đầy đủ Số ký hiệu, Trích yếu, Loại văn bản, Người ký và Ngày ban hành.", None, 400

    db = get_db()
    # Kiểm tra số ký hiệu trùng lặp
    check_cur = db.execute('SELECT van_ban_id FROM van_ban_ban_hanh WHERE so_ky_hieu = ?', (so_ky_hieu,))
    if check_cur.fetchone():
        return False, f"Số ký hiệu '{so_ky_hieu}' đã tồn tại trong kho lưu trữ.", None, 409

    # Tự động tính toán các mốc thời gian Date-Time
    nam_luu_tru, thang_luu_tru, quy_luu_tru = parse_date_to_parts(ngay_ban_hanh)
    nam_het_han = calculate_expiry_year(nam_luu_tru, thoi_han_bao_quan)

    co_quan_ban_hanh = (data.get('co_quan_ban_hanh') or 'Sở Giáo dục và Đào tạo TP. Đà Nẵng').strip()
    don_vi_soan_thao = (data.get('don_vi_soan_thao') or current_user.get('phong_ban') or 'Văn phòng Sở').strip()
    muc_do_mat = data.get('muc_do_mat') or 'THUONG'
    do_khan = data.get('do_khan') or 'THUONG'
    so_to_so_trang = int(data.get('so_to_so_trang') or 1)
    ho_so_id = data.get('ho_so_id')
    tep_dinh_kem = (data.get('tep_dinh_kem') or '').strip()
    dinh_dang_tep = (data.get('dinh_dang_tep') or 'pdf').strip().lower()
    dung_luong_kb = int(data.get('dung_luong_kb') or 0)
    ma_xac_thuc_so = (data.get('ma_xac_thuc_so') or '').strip()
    tu_khoa = (data.get('tu_khoa') or '').strip()
    ghi_chu = (data.get('ghi_chu') or '').strip()

    now = get_current_time_str()
    cur = db.execute('''
        INSERT INTO van_ban_ban_hanh (
            so_ky_hieu, trich_yeu, loai_van_ban, co_quan_ban_hanh, don_vi_soan_thao,
            nguoi_ky, chuc_vu_nguoi_ky, ngay_ky, ngay_ban_hanh, nam_luu_tru,
            thang_luu_tru, quy_luu_tru, thoi_han_bao_quan, nam_het_han_bao_quan,
            muc_do_mat, do_khan, so_to_so_trang, ho_so_id, tep_dinh_kem,
            dinh_dang_tep, dung_luong_kb, ma_xac_thuc_so, tu_khoa, ghi_chu,
            nguoi_luu_id, ngay_tao, ngay_cap_nhat
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        so_ky_hieu, trich_yeu, loai_van_ban, co_quan_ban_hanh, don_vi_soan_thao,
        nguoi_ky, chuc_vu_nguoi_ky, ngay_ky, ngay_ban_hanh, nam_luu_tru,
        thang_luu_tru, quy_luu_tru, thoi_han_bao_quan, nam_het_han,
        muc_do_mat, do_khan, so_to_so_trang, ho_so_id, tep_dinh_kem,
        dinh_dang_tep, dung_luong_kb, ma_xac_thuc_so, tu_khoa, ghi_chu,
        current_user.get('nguoi_dung_id'), now, now
    ))
    db.commit()

    # Cập nhật số lượng văn bản trong hồ sơ nếu có liên kết
    if ho_so_id:
        db.execute('''
            UPDATE ho_so_luu_tru
            SET so_luong_van_ban = (SELECT COUNT(*) FROM van_ban_ban_hanh WHERE ho_so_id = ?)
            WHERE ho_so_id = ?
        ''', (ho_so_id, ho_so_id))
        db.commit()

    new_id = cur.lastrowid
    return True, "Đã lưu văn bản đã ký ban hành vào kho thành công.", get_van_ban_ban_hanh_by_id(new_id), 201

def update_van_ban_ban_hanh(van_ban_id: int, data: dict, current_user: dict) -> tuple[bool, str, dict | None, int]:
    """Cập nhật thông tin văn bản lưu trữ."""
    existing = get_van_ban_ban_hanh_by_id(van_ban_id)
    if not existing:
        return False, "Không tìm thấy văn bản lưu trữ yêu cầu.", None, 404

    so_ky_hieu = (data.get('so_ky_hieu') or existing['so_ky_hieu']).strip().upper()
    trich_yeu = (data.get('trich_yeu') or existing['trich_yeu']).strip()
    loai_van_ban = (data.get('loai_van_ban') or existing['loai_van_ban']).strip()
    nguoi_ky = (data.get('nguoi_ky') or existing['nguoi_ky']).strip()
    chuc_vu_nguoi_ky = (data.get('chuc_vu_nguoi_ky') or existing['chuc_vu_nguoi_ky']).strip()
    ngay_ky = (data.get('ngay_ky') or existing['ngay_ky']).strip()
    ngay_ban_hanh = (data.get('ngay_ban_hanh') or existing['ngay_ban_hanh']).strip()
    thoi_han_bao_quan = (data.get('thoi_han_bao_quan') or existing['thoi_han_bao_quan']).strip()
    don_vi_soan_thao = (data.get('don_vi_soan_thao') or existing['don_vi_soan_thao']).strip()
    ho_so_id = data.get('ho_so_id', existing['ho_so_id'])
    tu_khoa = data.get('tu_khoa', existing['tu_khoa'])
    ghi_chu = data.get('ghi_chu', existing['ghi_chu'])

    db = get_db()
    if so_ky_hieu != existing['so_ky_hieu']:
        check_cur = db.execute('SELECT van_ban_id FROM van_ban_ban_hanh WHERE so_ky_hieu = ? AND van_ban_id != ?', (so_ky_hieu, van_ban_id))
        if check_cur.fetchone():
            return False, f"Số ký hiệu '{so_ky_hieu}' đã được sử dụng.", None, 409

    nam_luu_tru, thang_luu_tru, quy_luu_tru = parse_date_to_parts(ngay_ban_hanh)
    nam_het_han = calculate_expiry_year(nam_luu_tru, thoi_han_bao_quan)
    now = get_current_time_str()

    db.execute('''
        UPDATE van_ban_ban_hanh
        SET so_ky_hieu = ?, trich_yeu = ?, loai_van_ban = ?, don_vi_soan_thao = ?,
            nguoi_ky = ?, chuc_vu_nguoi_ky = ?, ngay_ky = ?, ngay_ban_hanh = ?,
            nam_luu_tru = ?, thang_luu_tru = ?, quy_luu_tru = ?, thoi_han_bao_quan = ?,
            nam_het_han_bao_quan = ?, ho_so_id = ?, tu_khoa = ?, ghi_chu = ?, ngay_cap_nhat = ?
        WHERE van_ban_id = ?
    ''', (
        so_ky_hieu, trich_yeu, loai_van_ban, don_vi_soan_thao,
        nguoi_ky, chuc_vu_nguoi_ky, ngay_ky, ngay_ban_hanh,
        nam_luu_tru, thang_luu_tru, quy_luu_tru, thoi_han_bao_quan,
        nam_het_han, ho_so_id, tu_khoa, ghi_chu, now, van_ban_id
    ))
    db.commit()

    return True, "Cập nhật văn bản lưu trữ thành công.", get_van_ban_ban_hanh_by_id(van_ban_id), 200

def delete_van_ban_ban_hanh(van_ban_id: int, current_user: dict) -> tuple[bool, str, int]:
    """Xóa văn bản khỏi kho lưu trữ (chỉ Văn thư)."""
    if current_user.get('vai_tro') != 'VAN_THU':
        return False, "Chỉ Văn thư cơ quan mới có quyền xóa văn bản lưu trữ.", 403

    db = get_db()
    existing = get_van_ban_ban_hanh_by_id(van_ban_id)
    if not existing:
        return False, "Không tìm thấy văn bản lưu trữ.", 404

    ho_so_id = existing.get('ho_so_id')
    db.execute('DELETE FROM van_ban_ban_hanh WHERE van_ban_id = ?', (van_ban_id,))
    db.commit()

    if ho_so_id:
        db.execute('''
            UPDATE ho_so_luu_tru
            SET so_luong_van_ban = (SELECT COUNT(*) FROM van_ban_ban_hanh WHERE ho_so_id = ?)
            WHERE ho_so_id = ?
        ''', (ho_so_id, ho_so_id))
        db.commit()

    return True, "Đã xóa văn bản khỏi kho lưu trữ thành công.", 200

def get_canh_bao_tieu_huy(target_year: int = 2030) -> list[dict]:
    """
    IDEA ĐẶC BIỆT: Cảnh báo thời hạn lưu trữ & tiêu hủy tài liệu hết giá trị.
    Tìm các văn bản có thời hạn bảo quản xác định và năm hết hạn <= target_year.
    """
    db = get_db()
    cur = db.execute('''
        SELECT van_ban_id, so_ky_hieu, trich_yeu, loai_van_ban, ngay_ban_hanh,
               nam_luu_tru, thoi_han_bao_quan, nam_het_han_bao_quan, don_vi_soan_thao
        FROM van_ban_ban_hanh
        WHERE nam_het_han_bao_quan IS NOT NULL AND nam_het_han_bao_quan <= ?
        ORDER BY nam_het_han_bao_quan ASC
    ''', (target_year,))
    return [dict(r) for r in cur.fetchall()]


# ==============================================================================
# PHÂN HỆ 2: KHO VĂN BẢN MẪU (ADMINISTRATIVE TEMPLATES HUB)
# ==============================================================================

def get_van_ban_mau_list(filters: dict = None) -> list[dict]:
    """Lấy danh sách biểu mẫu hành chính chuẩn Sở GD&ĐT."""
    filters = filters or {}
    db = get_db()

    query = '''
        SELECT m.*, u.ho_va_ten as ten_nguoi_tao
        FROM van_ban_mau m
        LEFT JOIN nguoi_dung u ON m.nguoi_tao_id = u.nguoi_dung_id
        WHERE 1=1
    '''
    params = []

    q = (filters.get('q') or '').strip()
    if q:
        kw = f"%{q}%"
        query += ' AND (m.ma_bieu_mau LIKE ? OR m.ten_bieu_mau LIKE ? OR m.huong_dan_dien LIKE ?)'
        params.extend([kw, kw, kw])

    if filters.get('loai_van_ban'):
        query += ' AND m.loai_van_ban = ?'
        params.append(filters['loai_van_ban'].strip())

    if filters.get('linh_vuc'):
        query += ' AND m.linh_vuc = ?'
        params.append(filters['linh_vuc'].strip())

    if filters.get('trang_thai'):
        query += ' AND m.trang_thai = ?'
        params.append(filters['trang_thai'].strip())

    # Sắp xếp
    sort_by = filters.get('sort_by')
    if sort_by == 'luot_tai':
        query += ' ORDER BY m.luot_tai DESC, m.bieu_mau_id DESC'
    else:
        query += ' ORDER BY m.bieu_mau_id DESC'

    cur = db.execute(query, params)
    return [dict(r) for r in cur.fetchall()]

def get_van_ban_mau_by_id(bieu_mau_id: int) -> dict | None:
    """Lấy chi tiết văn bản mẫu kèm cẩm nang hướng dẫn điền."""
    db = get_db()
    cur = db.execute('''
        SELECT m.*, u.ho_va_ten as ten_nguoi_tao
        FROM van_ban_mau m
        LEFT JOIN nguoi_dung u ON m.nguoi_tao_id = u.nguoi_dung_id
        WHERE m.bieu_mau_id = ?
    ''', (bieu_mau_id,))
    row = cur.fetchone()
    return dict(row) if row else None

def create_van_ban_mau(data: dict, current_user: dict) -> tuple[bool, str, dict | None, int]:
    """Tải lên / Khởi tạo biểu mẫu hành chính mới."""
    ma_bieu_mau = (data.get('ma_bieu_mau') or '').strip().upper()
    ten_bieu_mau = (data.get('ten_bieu_mau') or '').strip()
    loai_van_ban = (data.get('loai_van_ban') or '').strip()
    linh_vuc = (data.get('linh_vuc') or 'Văn phòng Sở').strip()
    phien_ban = (data.get('phien_ban') or '1.0').strip()
    ngay_ap_dung = (data.get('ngay_ap_dung') or datetime.now().strftime('%Y-%m-%d')).strip()
    tep_mau = (data.get('tep_mau') or f"{ma_bieu_mau}.docx").strip()
    dinh_dang_tep = (data.get('dinh_dang_tep') or 'docx').strip().lower()
    dung_luong_kb = int(data.get('dung_luong_kb') or 50)
    huong_dan_dien = (data.get('huong_dan_dien') or '').strip()

    if not all([ma_bieu_mau, ten_bieu_mau, loai_van_ban]):
        return False, "Vui lòng nhập Mã biểu mẫu, Tên biểu mẫu và Loại văn bản.", None, 400

    db = get_db()
    check_cur = db.execute('SELECT bieu_mau_id FROM van_ban_mau WHERE ma_bieu_mau = ?', (ma_bieu_mau,))
    if check_cur.fetchone():
        return False, f"Mã biểu mẫu '{ma_bieu_mau}' đã tồn tại trong kho biểu mẫu.", None, 409

    now = get_current_time_str()
    cur = db.execute('''
        INSERT INTO van_ban_mau (
            ma_bieu_mau, ten_bieu_mau, loai_van_ban, linh_vuc, phien_ban,
            ngay_ap_dung, trang_thai, tep_mau, dinh_dang_tep, dung_luong_kb,
            luot_tai, huong_dan_dien, nguoi_tao_id, ngay_tao, ngay_cap_nhat
        ) VALUES (?, ?, ?, ?, ?, ?, 'DANG_AP_DUNG', ?, ?, ?, 0, ?, ?, ?, ?)
    ''', (
        ma_bieu_mau, ten_bieu_mau, loai_van_ban, linh_vuc, phien_ban,
        ngay_ap_dung, tep_mau, dinh_dang_tep, dung_luong_kb,
        huong_dan_dien, current_user.get('nguoi_dung_id'), now, now
    ))
    db.commit()

    new_id = cur.lastrowid
    return True, "Thêm văn bản mẫu mới vào kho thành công.", get_van_ban_mau_by_id(new_id), 201

def update_van_ban_mau(bieu_mau_id: int, data: dict, current_user: dict) -> tuple[bool, str, dict | None, int]:
    """Cập nhật văn bản mẫu hoặc nâng phiên bản."""
    existing = get_van_ban_mau_by_id(bieu_mau_id)
    if not existing:
        return False, "Không tìm thấy biểu mẫu yêu cầu.", None, 404

    ma_bieu_mau = (data.get('ma_bieu_mau') or existing['ma_bieu_mau']).strip().upper()
    ten_bieu_mau = (data.get('ten_bieu_mau') or existing['ten_bieu_mau']).strip()
    loai_van_ban = (data.get('loai_van_ban') or existing['loai_van_ban']).strip()
    linh_vuc = (data.get('linh_vuc') or existing['linh_vuc']).strip()
    phien_ban = (data.get('phien_ban') or existing['phien_ban']).strip()
    ngay_ap_dung = (data.get('ngay_ap_dung') or existing['ngay_ap_dung']).strip()
    trang_thai = (data.get('trang_thai') or existing['trang_thai']).strip()
    huong_dan_dien = data.get('huong_dan_dien', existing['huong_dan_dien'])

    db = get_db()
    if ma_bieu_mau != existing['ma_bieu_mau']:
        check_cur = db.execute('SELECT bieu_mau_id FROM van_ban_mau WHERE ma_bieu_mau = ? AND bieu_mau_id != ?', (ma_bieu_mau, bieu_mau_id))
        if check_cur.fetchone():
            return False, f"Mã biểu mẫu '{ma_bieu_mau}' đã được sử dụng.", None, 409

    now = get_current_time_str()
    db.execute('''
        UPDATE van_ban_mau
        SET ma_bieu_mau = ?, ten_bieu_mau = ?, loai_van_ban = ?, linh_vuc = ?,
            phien_ban = ?, ngay_ap_dung = ?, trang_thai = ?, huong_dan_dien = ?, ngay_cap_nhat = ?
        WHERE bieu_mau_id = ?
    ''', (ma_bieu_mau, ten_bieu_mau, loai_van_ban, linh_vuc, phien_ban, ngay_ap_dung, trang_thai, huong_dan_dien, now, bieu_mau_id))
    db.commit()

    return True, "Cập nhật biểu mẫu thành công.", get_van_ban_mau_by_id(bieu_mau_id), 200

def record_download_and_get_link(bieu_mau_id: int) -> tuple[bool, str, dict | None, int]:
    """IDEA: Tăng biến đếm lượt tải khi cán bộ/chuyên viên tải biểu mẫu về sử dụng."""
    existing = get_van_ban_mau_by_id(bieu_mau_id)
    if not existing:
        return False, "Không tìm thấy biểu mẫu.", None, 404

    db = get_db()
    db.execute('UPDATE van_ban_mau SET luot_tai = luot_tai + 1 WHERE bieu_mau_id = ?', (bieu_mau_id,))
    db.commit()

    download_info = {
        'bieu_mau_id': existing['bieu_mau_id'],
        'ma_bieu_mau': existing['ma_bieu_mau'],
        'ten_bieu_mau': existing['ten_bieu_mau'],
        'tep_mau': existing['tep_mau'],
        'dinh_dang_tep': existing['dinh_dang_tep'],
        'duong_dan_tai': f"/storage/templates/{existing['tep_mau']}",
        'luot_tai_moi': existing['luot_tai'] + 1
    }
    return True, "Tải biểu mẫu thành công.", download_info, 200

def delete_van_ban_mau(bieu_mau_id: int, current_user: dict) -> tuple[bool, str, int]:
    """Xóa biểu mẫu (chỉ Văn thư)."""
    if current_user.get('vai_tro') != 'VAN_THU':
        return False, "Chỉ Văn thư mới có quyền xóa biểu mẫu hệ thống.", 403

    db = get_db()
    db.execute('DELETE FROM van_ban_mau WHERE bieu_mau_id = ?', (bieu_mau_id,))
    db.commit()
    return True, "Đã xóa biểu mẫu thành công.", 200

# ==============================================================================
# TỔNG HỢP THỐNG KÊ KHO LƯU TRỮ SỐ HÓA
# ==============================================================================

def get_kho_van_ban_summary() -> dict:
    """Thống kê tổng quan kho lưu trữ văn bản số hóa."""
    db = get_db()

    # Tổng số văn bản đã ban hành
    cur = db.execute('SELECT COUNT(*), COALESCE(SUM(dung_luong_kb), 0) FROM van_ban_ban_hanh')
    row = cur.fetchone()
    tong_vbbh = row[0]
    tong_dung_luong_kb = row[1]

    # Tổng số biểu mẫu
    cur = db.execute('SELECT COUNT(*), COALESCE(SUM(luot_tai), 0) FROM van_ban_mau WHERE trang_thai = "DANG_AP_DUNG"')
    row = cur.fetchone()
    tong_bieu_mau = row[0]
    tong_luot_tai = row[1]

    # Phân bố văn bản ban hành theo loại
    cur = db.execute('''
        SELECT loai_van_ban, COUNT(*) as so_luong
        FROM van_ban_ban_hanh
        GROUP BY loai_van_ban
        ORDER BY so_luong DESC
    ''')
    loai_vb_list = [dict(r) for r in cur.fetchall()]

    # Phân bố theo thời hạn bảo quản
    cur = db.execute('''
        SELECT thoi_han_bao_quan, COUNT(*) as so_luong
        FROM van_ban_ban_hanh
        GROUP BY thoi_han_bao_quan
        ORDER BY so_luong DESC
    ''')
    thoi_han_list = [dict(r) for r in cur.fetchall()]

    # Top biểu mẫu được tải nhiều nhất
    cur = db.execute('''
        SELECT bieu_mau_id, ma_bieu_mau, ten_bieu_mau, luot_tai, dinh_dang_tep
        FROM van_ban_mau
        ORDER BY luot_tai DESC
        LIMIT 5
    ''')
    top_bieu_mau = [dict(r) for r in cur.fetchall()]

    return {
        'tong_so_van_ban_ban_hanh': tong_vbbh,
        'tong_so_bieu_mau': tong_bieu_mau,
        'tong_dung_luong_mb': round(tong_dung_luong_kb / 1024, 2),
        'tong_luot_tai_bieu_mau': tong_luot_tai,
        'phan_bo_loai_van_ban': loai_vb_list,
        'phan_bo_thoi_han': thoi_han_list,
        'top_bieu_mau_tai_nhieu': top_bieu_mau
    }

# ==============================================================================
# OBJECT MODEL HELPER
# ==============================================================================
from .base_model import BaseModel

class RepositoryModel(BaseModel):
    """Model quản lý kho văn bản đã ban hành và biểu mẫu số hóa."""

    @classmethod
    def get_published_by_id(cls, van_ban_id: int):
        cur = cls.db().execute('SELECT * FROM van_ban_ban_hanh WHERE van_ban_id = ?', (van_ban_id,))
        return cls.dict_from_row(cur.fetchone())

    @classmethod
    def get_published_all(cls, filters: dict = None):
        filters = filters or {}
        query = 'SELECT * FROM van_ban_ban_hanh WHERE 1=1'
        params = []
        if filters.get('ho_so_id'):
            query += ' AND ho_so_id = ?'
            params.append(int(filters['ho_so_id']))
        if filters.get('nam'):
            query += ' AND nam_luu_tru = ?'
            params.append(int(filters['nam']))
        query += ' ORDER BY ngay_ban_hanh DESC'
        cur = cls.db().execute(query, params)
        return cls.list_from_rows(cur.fetchall())

