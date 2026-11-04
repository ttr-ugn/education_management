# ==============================================================================
# MODELS/TASK_MODEL.PY - MVC ARCHITECTURE (MODEL LAYER)
# ==============================================================================

import sqlite3
from datetime import datetime, date
from database.db import get_db

def _check_and_update_overdue():
    """Tự động kiểm tra và cập nhật trạng thái QUA_HAN nếu đã vượt quá deadline."""
    db = get_db()
    today_str = date.today().isoformat()
    db.execute('''
        UPDATE cong_viec
        SET trang_thai = 'QUA_HAN', ngay_cap_nhat = CURRENT_TIMESTAMP
        WHERE han_hoan_thanh < ?
          AND trang_thai IN ('CHUA_THUC_HIEN', 'DANG_THUC_HIEN')
    ''', (today_str,))
    db.commit()

def get_tasks_list(current_user, filters=None):
    """Lấy danh sách công việc theo phân quyền và bộ lọc."""
    if filters is None:
        filters = {}

    _check_and_update_overdue()
    db = get_db()

    query = '''
        SELECT 
            c.cong_viec_id,
            c.cong_viec_id AS id,
            c.ten_cong_viec,
            c.noi_dung,
            c.nguoi_giao_id,
            COALESCE(c.nguoi_giao_ten, u_giao.ho_va_ten, 'Lãnh đạo Sở') AS nguoi_giao,
            c.nguoi_xu_ly_id,
            COALESCE(c.nguoi_xu_ly_ten, u_nhan.ho_va_ten, 'Chuyên viên') AS nguoi_xu_ly,
            c.phong_ban,
            c.ngay_giao,
            c.han_hoan_thanh,
            c.do_uu_tien,
            c.tien_do,
            c.trang_thai,
            c.ket_qua_bao_cao,
            c.danh_gia_lanh_dao,
            c.tep_dinh_kem_ket_qua,
            c.so_ky_hieu_vb,
            c.trich_yeu_vb,
            c.ngay_van_ban,
            c.tep_dinh_kem_vb,
            c.ngay_tao,
            c.ngay_cap_nhat
        FROM cong_viec c
        LEFT JOIN nguoi_dung u_giao ON c.nguoi_giao_id = u_giao.nguoi_dung_id
        LEFT JOIN nguoi_dung u_nhan ON c.nguoi_xu_ly_id = u_nhan.nguoi_dung_id
        WHERE 1=1
    '''
    params = []

    role = current_user.get('vai_tro')
    user_id = current_user.get('nguoi_dung_id')

    # Phân quyền: Nếu là Chuyên viên và không bật scope=all thì chỉ xem việc của mình
    if role == 'CHUYEN_VIEN':
        if filters.get('scope') != 'all':
            query += ' AND (c.nguoi_xu_ly_id = ? OR c.nguoi_xu_ly_ten LIKE ?)'
            params.append(user_id)
            params.append(f"%{current_user.get('ho_va_ten', '')}%")

    # Lọc theo từ khóa tìm kiếm (tên, nội dung, văn bản, người xử lý)
    q = filters.get('q')
    if q:
        query += ''' AND (
            c.ten_cong_viec LIKE ? OR
            c.noi_dung LIKE ? OR
            c.so_ky_hieu_vb LIKE ? OR
            c.trich_yeu_vb LIKE ? OR
            c.nguoi_xu_ly_ten LIKE ?
        )'''
        pattern = f'%{q.strip()}%'
        params.extend([pattern, pattern, pattern, pattern, pattern])

    # Lọc theo trạng thái
    trang_thai = filters.get('trang_thai')
    if trang_thai:
        query += ' AND c.trang_thai = ?'
        params.append(trang_thai)

    # Lọc theo độ ưu tiên
    do_uu_tien = filters.get('do_uu_tien')
    if do_uu_tien:
        query += ' AND c.do_uu_tien = ?'
        params.append(do_uu_tien)

    # Lọc theo phòng ban
    phong_ban = filters.get('phong_ban')
    if phong_ban:
        query += ' AND c.phong_ban = ?'
        params.append(phong_ban)

    # Lọc theo chuyên viên xử lý
    chuyen_vien_id = filters.get('chuyen_vien_id')
    if chuyen_vien_id:
        query += ' AND c.nguoi_xu_ly_id = ?'
        params.append(chuyen_vien_id)

    # Sắp xếp: Ưu tiên việc khẩn cấp / quá hạn lên trước, sau đó theo hạn hoàn thành
    query += ''' ORDER BY 
        CASE c.trang_thai
            WHEN 'QUA_HAN' THEN 1
            WHEN 'CHO_DANH_GIA' THEN 2
            WHEN 'DANG_THUC_HIEN' THEN 3
            WHEN 'CHUA_THUC_HIEN' THEN 4
            WHEN 'HOAN_THANH' THEN 5
            ELSE 6
        END,
        c.han_hoan_thanh ASC,
        c.cong_viec_id DESC
    '''

    cursor = db.execute(query, params)
    rows = cursor.fetchall()

    tasks = [dict(row) for row in rows]
    return tasks

def get_task_by_id(task_id, current_user):
    """Lấy chi tiết 1 nhiệm vụ công việc kèm lịch sử tiến độ."""
    _check_and_update_overdue()
    db = get_db()

    query = '''
        SELECT 
            c.cong_viec_id,
            c.cong_viec_id AS id,
            c.ten_cong_viec,
            c.noi_dung,
            c.nguoi_giao_id,
            COALESCE(c.nguoi_giao_ten, u_giao.ho_va_ten, 'Lãnh đạo Sở') AS nguoi_giao,
            u_giao.email AS email_nguoi_giao,
            c.nguoi_xu_ly_id,
            COALESCE(c.nguoi_xu_ly_ten, u_nhan.ho_va_ten, 'Chuyên viên') AS nguoi_xu_ly,
            u_nhan.email AS email_nguoi_xu_ly,
            c.phong_ban,
            c.ngay_giao,
            c.han_hoan_thanh,
            c.do_uu_tien,
            c.tien_do,
            c.trang_thai,
            c.ket_qua_bao_cao,
            c.danh_gia_lanh_dao,
            c.tep_dinh_kem_ket_qua,
            c.so_ky_hieu_vb,
            c.trich_yeu_vb,
            c.ngay_van_ban,
            c.tep_dinh_kem_vb,
            c.ngay_tao,
            c.ngay_cap_nhat
        FROM cong_viec c
        LEFT JOIN nguoi_dung u_giao ON c.nguoi_giao_id = u_giao.nguoi_dung_id
        LEFT JOIN nguoi_dung u_nhan ON c.nguoi_xu_ly_id = u_nhan.nguoi_dung_id
        WHERE c.cong_viec_id = ?
    '''
    task = db.execute(query, (task_id,)).fetchone()
    if not task:
        return None

    task_dict = dict(task)

    # Lấy lịch sử cập nhật tiến độ
    logs_cursor = db.execute('''
        SELECT 
            nhat_ky_id,
            cong_viec_id,
            nguoi_cap_nhat_id,
            nguoi_cap_nhat_ten,
            tien_do_cu,
            tien_do_moi,
            noi_dung_ghi_chu,
            tep_dinh_kem,
            thoi_gian
        FROM nhat_ky_cong_viec
        WHERE cong_viec_id = ?
        ORDER BY nhat_ky_id DESC
    ''', (task_id,))
    task_dict['nhat_ky'] = [dict(log) for log in logs_cursor.fetchall()]

    return task_dict

def create_task(data, current_user):
    """Tạo mới một nhiệm vụ công việc điều hành (Văn thư hoặc Lãnh đạo)."""
    ten_cong_viec = (data.get('ten_cong_viec') or '').strip()
    if not ten_cong_viec:
        return False, 'Tên nhiệm vụ/công việc không được để trống.', None, 400

    han_hoan_thanh = (data.get('han_hoan_thanh') or '').strip()
    if not han_hoan_thanh:
        return False, 'Hạn hoàn thành không được để trống.', None, 400

    phong_ban = (data.get('phong_ban') or 'Phòng chuyên môn').strip()
    do_uu_tien = data.get('do_uu_tien') or 'TRUNG_BINH'
    if do_uu_tien not in ('THAP', 'TRUNG_BINH', 'CAO', 'KHAN_CAP'):
        do_uu_tien = 'TRUNG_BINH'

    noi_dung = (data.get('noi_dung') or '').strip()

    # Xử lý người xử lý (ID hoặc Tên)
    db = get_db()
    nguoi_xu_ly_id = data.get('nguoi_xu_ly_id')
    nguoi_xu_ly_ten = (data.get('nguoi_xu_ly') or data.get('nguoi_xu_ly_ten') or '').strip()

    if nguoi_xu_ly_id:
        user = db.execute('SELECT ho_va_ten, phong_ban FROM nguoi_dung WHERE nguoi_dung_id = ?', (nguoi_xu_ly_id,)).fetchone()
        if user:
            nguoi_xu_ly_ten = user['ho_va_ten']
            if not data.get('phong_ban') and user['phong_ban']:
                phong_ban = user['phong_ban']
    elif nguoi_xu_ly_ten:
        # Thử tìm theo tên
        clean_name = nguoi_xu_ly_ten.split('(')[0].strip()
        user = db.execute('SELECT nguoi_dung_id, ho_va_ten, phong_ban FROM nguoi_dung WHERE ho_va_ten LIKE ?', (f'%{clean_name}%',)).fetchone()
        if user:
            nguoi_xu_ly_id = user['nguoi_dung_id']
            if not data.get('phong_ban') and user['phong_ban']:
                phong_ban = user['phong_ban']

    nguoi_giao_id = current_user.get('nguoi_dung_id')
    nguoi_giao_ten = f"{current_user.get('ho_va_ten')} ({current_user.get('chuc_vu') or 'Cán bộ giao việc'})"

    # Thông tin văn bản liên kết
    so_ky_hieu_vb = (data.get('so_ky_hieu_vb') or '').strip()
    trich_yeu_vb = (data.get('trich_yeu_vb') or '').strip()
    ngay_van_ban = (data.get('ngay_van_ban') or '').strip()
    tep_dinh_kem_vb = (data.get('tep_dinh_kem_vb') or '').strip()

    try:
        cursor = db.execute('''
            INSERT INTO cong_viec (
                ten_cong_viec, noi_dung, nguoi_giao_id, nguoi_giao_ten,
                nguoi_xu_ly_id, nguoi_xu_ly_ten, phong_ban, ngay_giao,
                han_hoan_thanh, do_uu_tien, tien_do, trang_thai,
                so_ky_hieu_vb, trich_yeu_vb, ngay_van_ban, tep_dinh_kem_vb
            ) VALUES (?, ?, ?, ?, ?, ?, ?, DATE('now', 'localtime'), ?, ?, 0, 'CHUA_THUC_HIEN', ?, ?, ?, ?)
        ''', (
            ten_cong_viec, noi_dung, nguoi_giao_id, nguoi_giao_ten,
            nguoi_xu_ly_id, nguoi_xu_ly_ten or 'Chuyên viên phụ trách', phong_ban,
            han_hoan_thanh, do_uu_tien,
            so_ky_hieu_vb, trich_yeu_vb, ngay_van_ban, tep_dinh_kem_vb
        ))
        task_id = cursor.lastrowid

        # Ghi nhật ký khởi tạo
        db.execute('''
            INSERT INTO nhat_ky_cong_viec (
                cong_viec_id, nguoi_cap_nhat_id, nguoi_cap_nhat_ten,
                tien_do_cu, tien_do_moi, noi_dung_ghi_chu
            ) VALUES (?, ?, ?, 0, 0, ?)
        ''', (
            task_id, nguoi_giao_id, current_user.get('ho_va_ten'),
            f"Giao nhiệm vụ: {ten_cong_viec}. Hạn hoàn thành: {han_hoan_thanh}"
        ))

        db.commit()
        return True, 'Ban hành nhiệm vụ công việc thành công.', task_id, 201
    except Exception as e:
        db.rollback()
        return False, f'Lỗi khi tạo công việc: {str(e)}', None, 500

def update_task_progress(task_id, data, current_user):
    """Cập nhật tiến độ và gửi báo cáo kết quả (Chuyên viên hoặc Lãnh đạo/Văn thư)."""
    db = get_db()
    task = db.execute('SELECT * FROM cong_viec WHERE cong_viec_id = ?', (task_id,)).fetchone()
    if not task:
        return False, 'Không tìm thấy công việc yêu cầu.', 404

    # Kiểm tra quyền: Chỉ người được giao, Văn thư hoặc Lãnh đạo mới được cập nhật
    role = current_user.get('vai_tro')
    user_id = current_user.get('nguoi_dung_id')
    if role == 'CHUYEN_VIEN' and task['nguoi_xu_ly_id'] and task['nguoi_xu_ly_id'] != user_id:
        # Nếu chưa gán id, kiểm tra tên
        if current_user.get('ho_va_ten') not in (task['nguoi_xu_ly_ten'] or ''):
            return False, 'Bạn không được phân công thực hiện nhiệm vụ này.', 403

    tien_do_cu = task['tien_do']
    try:
        tien_do_moi = int(data.get('tien_do', tien_do_cu))
        tien_do_moi = max(0, min(100, tien_do_moi))
    except (ValueError, TypeError):
        return False, 'Tỷ lệ tiến độ phải là số nguyên từ 0 đến 100.', 400

    ket_qua_bao_cao = data.get('ket_qua_bao_cao') or data.get('bao_cao') or data.get('noi_dung_ghi_chu') or ''
    tep_dinh_kem = data.get('tep_dinh_kem') or data.get('tep_dinh_kem_ket_qua') or ''

    # Xác định trạng thái mới dựa trên tiến độ
    if tien_do_moi >= 100:
        trang_thai_moi = 'CHO_DANH_GIA'
    elif tien_do_moi > 0:
        # Kiểm tra quá hạn
        if task['han_hoan_thanh'] < date.today().isoformat():
            trang_thai_moi = 'QUA_HAN'
        else:
            trang_thai_moi = 'DANG_THUC_HIEN'
    else:
        trang_thai_moi = 'CHUA_THUC_HIEN'

    try:
        db.execute('''
            UPDATE cong_viec
            SET tien_do = ?,
                trang_thai = ?,
                ket_qua_bao_cao = CASE WHEN ? != '' THEN ? ELSE ket_qua_bao_cao END,
                tep_dinh_kem_ket_qua = CASE WHEN ? != '' THEN ? ELSE tep_dinh_kem_ket_qua END,
                ngay_cap_nhat = CURRENT_TIMESTAMP
            WHERE cong_viec_id = ?
        ''', (
            tien_do_moi, trang_thai_moi,
            ket_qua_bao_cao, ket_qua_bao_cao,
            tep_dinh_kem, tep_dinh_kem,
            task_id
        ))

        # Thêm nhật ký tiến độ
        ghi_chu = ket_qua_bao_cao if ket_qua_bao_cao else f"Cập nhật tiến độ từ {tien_do_cu}% lên {tien_do_moi}%."
        db.execute('''
            INSERT INTO nhat_ky_cong_viec (
                cong_viec_id, nguoi_cap_nhat_id, nguoi_cap_nhat_ten,
                tien_do_cu, tien_do_moi, noi_dung_ghi_chu, tep_dinh_kem
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id, user_id, current_user.get('ho_va_ten'),
            tien_do_cu, tien_do_moi, ghi_chu, tep_dinh_kem
        ))

        db.commit()
        return True, 'Cập nhật tiến độ công việc thành công.', 200
    except Exception as e:
        db.rollback()
        return False, f'Lỗi khi cập nhật tiến độ: {str(e)}', 500

def evaluate_task(task_id, data, current_user):
    """Nghiệm thu / Đánh giá kết quả công việc (Văn thư hoặc Lãnh đạo)."""
    db = get_db()
    task = db.execute('SELECT * FROM cong_viec WHERE cong_viec_id = ?', (task_id,)).fetchone()
    if not task:
        return False, 'Không tìm thấy công việc yêu cầu.', 404

    ket_luan = (data.get('ket_luan') or data.get('conclusion') or 'DAT').upper()
    nhan_xet = (data.get('nhan_xet') or data.get('comment') or data.get('danh_gia_lanh_dao') or '').strip()

    if ket_luan == 'DAT':
        trang_thai_moi = 'HOAN_THANH'
        tien_do_moi = 100
        thong_diep = 'Nghiệm thu ĐẠT kết quả thực hiện nhiệm vụ.'
    else:
        trang_thai_moi = 'DANG_THUC_HIEN'
        tien_do_moi = 75  # Yêu cầu bổ sung/làm lại
        thong_diep = 'Yêu cầu chuyên viên chỉnh sửa, bổ sung báo cáo.'

    nhan_xet_full = f"[{current_user.get('ho_va_ten')} - {current_user.get('chuc_vu') or 'Lãnh đạo'}]: {nhan_xet or thong_diep}"

    try:
        db.execute('''
            UPDATE cong_viec
            SET trang_thai = ?,
                tien_do = ?,
                danh_gia_lanh_dao = ?,
                ngay_cap_nhat = CURRENT_TIMESTAMP
            WHERE cong_viec_id = ?
        ''', (trang_thai_moi, tien_do_moi, nhan_xet_full, task_id))

        db.execute('''
            INSERT INTO nhat_ky_cong_viec (
                cong_viec_id, nguoi_cap_nhat_id, nguoi_cap_nhat_ten,
                tien_do_cu, tien_do_moi, noi_dung_ghi_chu
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            task_id, current_user.get('nguoi_dung_id'), current_user.get('ho_va_ten'),
            task['tien_do'], tien_do_moi, nhan_xet_full
        ))

        db.commit()
        return True, 'Đã lưu đánh giá & nghiệm thu công việc.', 200
    except Exception as e:
        db.rollback()
        return False, f'Lỗi khi đánh giá công việc: {str(e)}', 500

def delete_task(task_id, current_user):
    """Xóa nhiệm vụ công việc (Văn thư hoặc Lãnh đạo)."""
    db = get_db()
    task = db.execute('SELECT * FROM cong_viec WHERE cong_viec_id = ?', (task_id,)).fetchone()
    if not task:
        return False, 'Không tìm thấy công việc yêu cầu.', 404

    try:
        db.execute('DELETE FROM cong_viec WHERE cong_viec_id = ?', (task_id,))
        db.commit()
        return True, 'Đã xóa công việc thành công.', 200
    except Exception as e:
        db.rollback()
        return False, f'Lỗi khi xóa công việc: {str(e)}', 500

def get_task_statistics(current_user, filters=None):
    """Tổng hợp số liệu thống kê & biểu đồ Chart.js cho phân hệ Quản lý công việc."""
    if filters is None:
        filters = {}

    _check_and_update_overdue()
    db = get_db()

    role = current_user.get('vai_tro')
    user_id = current_user.get('nguoi_dung_id')

    where_clause = 'WHERE 1=1'
    params = []

    if role == 'CHUYEN_VIEN' and filters.get('scope') != 'all':
        where_clause += ' AND (nguoi_xu_ly_id = ? OR nguoi_xu_ly_ten LIKE ?)'
        params.append(user_id)
        params.append(f"%{current_user.get('ho_va_ten', '')}%")

    # 1. Thống kê theo trạng thái
    status_query = f'''
        SELECT trang_thai, COUNT(*) AS so_luong
        FROM cong_viec
        {where_clause}
        GROUP BY trang_thai
    '''
    rows = db.execute(status_query, params).fetchall()
    status_map = {
        'CHUA_THUC_HIEN': 0,
        'DANG_THUC_HIEN': 0,
        'CHO_DANH_GIA': 0,
        'HOAN_THANH': 0,
        'QUA_HAN': 0
    }
    for r in rows:
        status_map[r['trang_thai']] = r['so_luong']

    tong_so = sum(status_map.values())

    # 2. Thống kê theo phòng ban
    dept_query = f'''
        SELECT 
            phong_ban,
            COUNT(*) AS tong,
            SUM(CASE WHEN trang_thai = 'HOAN_THANH' THEN 1 ELSE 0 END) AS hoan_thanh,
            SUM(CASE WHEN trang_thai = 'QUA_HAN' THEN 1 ELSE 0 END) AS qua_han
        FROM cong_viec
        {where_clause}
        GROUP BY phong_ban
        ORDER BY tong DESC
    '''
    dept_rows = db.execute(dept_query, params).fetchall()

    dept_labels = [r['phong_ban'] for r in dept_rows]
    dept_tong = [r['tong'] for r in dept_rows]
    dept_hoan_thanh = [r['hoan_thanh'] for r in dept_rows]
    dept_qua_han = [r['qua_han'] for r in dept_rows]

    # 3. Tính tỷ lệ hoàn thành đúng hạn
    ty_le_dung_han = 0
    if tong_so > 0:
        ty_le_dung_han = round((status_map['HOAN_THANH'] / tong_so) * 100, 1)

    # 4. Chuẩn bị cấu trúc dữ liệu cho Chart.js
    chart_doughnut = {
        'labels': ['Đã hoàn thành', 'Đang thực hiện', 'Chờ nghiệm thu', 'Chưa thực hiện', 'Quá hạn'],
        'data': [
            status_map['HOAN_THANH'],
            status_map['DANG_THUC_HIEN'],
            status_map['CHO_DANH_GIA'],
            status_map['CHUA_THUC_HIEN'],
            status_map['QUA_HAN']
        ],
        'colors': ['#10b981', '#0d6efd', '#f59e0b', '#94a3b8', '#ef4444']
    }

    chart_bar = {
        'labels': dept_labels if dept_labels else ['Chưa có phòng ban'],
        'duoc_giao': dept_tong if dept_tong else [0],
        'da_xong': dept_hoan_thanh if dept_hoan_thanh else [0],
        'qua_han': dept_qua_han if dept_qua_han else [0]
    }

    return {
        'tong_so': tong_so,
        'theo_trang_thai': status_map,
        'ty_le_dung_han': ty_le_dung_han,
        'chart_doughnut': chart_doughnut,
        'chart_bar': chart_bar
    }


# ==============================================================================
# OBJECT MODEL HELPER
# ==============================================================================
from .base_model import BaseModel

class TaskModel(BaseModel):
    """Model quản lý nhiệm vụ điều hành và nhật ký tiến độ xử lý."""

    @classmethod
    def get_by_id(cls, task_id: int):
        cur = cls.db().execute('SELECT * FROM cong_viec WHERE cong_viec_id = ?', (task_id,))
        return cls.dict_from_row(cur.fetchone())

    @classmethod
    def get_all(cls, filters: dict = None):
        filters = filters or {}
        query = 'SELECT * FROM cong_viec WHERE 1=1'
        params = []
        if filters.get('trang_thai'):
            query += ' AND trang_thai = ?'
            params.append(filters['trang_thai'])
        if filters.get('nguoi_xu_ly_id'):
            query += ' AND nguoi_xu_ly_id = ?'
            params.append(int(filters['nguoi_xu_ly_id']))
        query += ' ORDER BY cong_viec_id DESC'
        cur = cls.db().execute(query, params)
        return cls.list_from_rows(cur.fetchall())

    @classmethod
    def get_logs(cls, task_id: int):
        cur = cls.db().execute('''
            SELECT * FROM nhat_ky_cong_viec
            WHERE cong_viec_id = ?
            ORDER BY thoi_gian ASC
        ''', (task_id,))
        return cls.list_from_rows(cur.fetchall())

