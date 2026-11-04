from datetime import datetime
from database.db import get_db

VALID_LOAI = ('Cuộc họp', 'Hệ thống', 'Khen thưởng', 'Văn bản', 'Công việc', 'Nhắc nhở', 'Khác')
VALID_MUC_DO = ('Bình thường', 'Quan trọng', 'Khẩn cấp')

def get_user_notifications(user_id: int, loai: str = None, muc_do: str = None, chua_doc_only: bool = False) -> list[dict]:
    """Lấy danh sách thông báo điều hành và nhắc nhở của người dùng."""
    db = get_db()
    
    query = '''
        SELECT 
            tb.thong_bao_id,
            tb.tieu_de,
            tb.noi_dung,
            tb.loai,
            tb.muc_do,
            tb.nguoi_gui_id,
            tb.nguoi_nhan_id,
            tb.ngay_hen_gio,
            tb.lien_ket,
            tb.ngay_tao,
            COALESCE(nd_gui.ho_va_ten, 'Văn phòng Sở GD&ĐT') AS nguoi_gui,
            CASE WHEN tb_dd.ngay_doc IS NOT NULL THEN 1 ELSE 0 END AS da_doc
        FROM thong_bao tb
        LEFT JOIN nguoi_dung nd_gui ON tb.nguoi_gui_id = nd_gui.nguoi_dung_id
        LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
        WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
    '''
    params = [user_id, user_id]

    if loai and loai in VALID_LOAI:
        query += ' AND tb.loai = ?'
        params.append(loai)

    if muc_do and muc_do in VALID_MUC_DO:
        query += ' AND tb.muc_do = ?'
        params.append(muc_do)

    if chua_doc_only:
        query += ' AND tb_dd.ngay_doc IS NULL'

    query += ' ORDER BY tb.ngay_tao DESC'

    rows = db.execute(query, params).fetchall()

    result = []
    for r in rows:
        result.append({
            'id': r['thong_bao_id'],
            'tieu_de': r['tieu_de'],
            'noi_dung': r['noi_dung'],
            'loai': r['loai'],
            'muc_do': r['muc_do'],
            'nguoi_gui': r['nguoi_gui'],
            'thoi_gian': r['ngay_tao'],
            'da_doc': bool(r['da_doc']),
            'ngay_hen_gio': r['ngay_hen_gio'],
            'lien_ket': r['lien_ket'],
            'nguoi_nhan_id': r['nguoi_nhan_id']
        })

    return result

def get_unread_count(user_id: int) -> int:
    """Đếm số lượng thông báo chưa đọc của người dùng."""
    db = get_db()
    row = db.execute('''
        SELECT COUNT(*) AS chua_doc
        FROM thong_bao tb
        LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
        WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
          AND tb_dd.ngay_doc IS NULL
    ''', (user_id, user_id)).fetchone()

    return row['chua_doc'] if row else 0

def mark_as_read(thong_bao_id: int, user_id: int) -> tuple[bool, str, int]:
    """Đánh dấu thông báo cụ thể là đã đọc."""
    db = get_db()
    # Kiểm tra thông báo có tồn tại và người dùng có quyền đọc không
    tb = db.execute('''
        SELECT thong_bao_id FROM thong_bao 
        WHERE thong_bao_id = ? AND (nguoi_nhan_id IS NULL OR nguoi_nhan_id = ?)
    ''', (thong_bao_id, user_id)).fetchone()

    if not tb:
        return False, "Thông báo không tồn tại hoặc bạn không có quyền truy cập.", 404

    db.execute('''
        INSERT OR IGNORE INTO thong_bao_da_doc (thong_bao_id, nguoi_dung_id, ngay_doc)
        VALUES (?, ?, ?)
    ''', (thong_bao_id, user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    db.commit()

    return True, "Đã đánh dấu thông báo là đã đọc.", 200

def mark_all_as_read(user_id: int) -> tuple[bool, str, int]:
    """Đánh dấu tất cả thông báo thuộc về người dùng là đã đọc."""
    db = get_db()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute('''
        INSERT OR IGNORE INTO thong_bao_da_doc (thong_bao_id, nguoi_dung_id, ngay_doc)
        SELECT tb.thong_bao_id, ?, ?
        FROM thong_bao tb
        WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
    ''', (user_id, now_str, user_id))
    db.commit()

    return True, "Đã đánh dấu tất cả thông báo là đã đọc.", 200

def create_notification(data: dict, nguoi_gui_id: int) -> tuple[bool, str, dict | None, int]:
    """Tạo mới một thông báo hoặc nhắc nhở."""
    tieu_de = (data.get('tieu_de') or '').strip()
    noi_dung = (data.get('noi_dung') or '').strip()
    loai = (data.get('loai') or 'Hệ thống').strip()
    muc_do = (data.get('muc_do') or 'Bình thường').strip()
    nguoi_nhan_id = data.get('nguoi_nhan_id')
    ngay_hen_gio = (data.get('ngay_hen_gio') or '').strip() or None
    lien_ket = (data.get('lien_ket') or '').strip() or None

    if not tieu_de:
        return False, "Tiêu đề thông báo không được để trống.", None, 400

    if not noi_dung:
        return False, "Nội dung thông báo không được để trống.", None, 400

    if loai not in VALID_LOAI:
        loai = 'Hệ thống'

    if muc_do not in VALID_MUC_DO:
        muc_do = 'Bình thường'

    db = get_db()
    if nguoi_nhan_id:
        try:
            nguoi_nhan_id = int(nguoi_nhan_id)
            user_exists = db.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE nguoi_dung_id = ?', (nguoi_nhan_id,)).fetchone()
            if not user_exists:
                return False, "Người nhận không tồn tại trong hệ thống.", None, 404
        except (ValueError, TypeError):
            return False, "Định dạng người nhận không hợp lệ.", None, 400
    else:
        nguoi_nhan_id = None

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = db.execute('''
        INSERT INTO thong_bao (
            tieu_de, noi_dung, loai, muc_do, nguoi_gui_id,
            nguoi_nhan_id, ngay_hen_gio, lien_ket, ngay_tao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        tieu_de, noi_dung, loai, muc_do, nguoi_gui_id,
        nguoi_nhan_id, ngay_hen_gio, lien_ket, now_str
    ))
    db.commit()

    created_id = cursor.lastrowid
    return True, "Tạo thông báo thành công.", {'id': created_id, 'tieu_de': tieu_de}, 201

def delete_notification(thong_bao_id: int, user_id: int, user_role: str) -> tuple[bool, str, int]:
    """Xóa thông báo (chỉ Văn thư hoặc người tạo thông báo mới có quyền)."""
    db = get_db()
    tb = db.execute('SELECT thong_bao_id, nguoi_gui_id FROM thong_bao WHERE thong_bao_id = ?', (thong_bao_id,)).fetchone()
    if not tb:
        return False, "Thông báo không tồn tại.", 404

    if user_role != 'VAN_THU' and tb['nguoi_gui_id'] != user_id:
        return False, "Bạn không có quyền xóa thông báo này.", 403

    db.execute('DELETE FROM thong_bao WHERE thong_bao_id = ?', (thong_bao_id,))
    db.commit()
    return True, "Đã xóa thông báo thành công.", 200
