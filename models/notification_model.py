# ==============================================================================
# MODELS/NOTIFICATION_MODEL.PY - MVC ARCHITECTURE (MODEL LAYER)
# ==============================================================================

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
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    result = []
    for r in rows:
        hen_gio = r['ngay_hen_gio']
        da_den_han = False
        if hen_gio and hen_gio <= now_str and not r['da_doc']:
            da_den_han = True

        result.append({
            'id': r['thong_bao_id'],
            'tieu_de': r['tieu_de'],
            'noi_dung': r['noi_dung'],
            'loai': r['loai'],
            'muc_do': r['muc_do'],
            'nguoi_gui': r['nguoi_gui'],
            'thoi_gian': r['ngay_tao'],
            'da_doc': bool(r['da_doc']),
            'ngay_hen_gio': hen_gio,
            'da_den_han': da_den_han,
            'lien_ket': r['lien_ket'],
            'nguoi_nhan_id': r['nguoi_nhan_id']
        })

    return result

def get_due_reminders(user_id: int) -> list[dict]:
    """Lấy danh sách các thông báo / nhắc nhở có hẹn giờ đã đến hoặc quá hạn mà chưa đọc."""
    db = get_db()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
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
            COALESCE(nd_gui.ho_va_ten, 'Văn phòng Sở GD&ĐT') AS nguoi_gui
        FROM thong_bao tb
        LEFT JOIN nguoi_dung nd_gui ON tb.nguoi_gui_id = nd_gui.nguoi_dung_id
        LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
        WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
          AND tb.ngay_hen_gio IS NOT NULL
          AND tb.ngay_hen_gio <= ?
          AND tb_dd.ngay_doc IS NULL
        ORDER BY tb.ngay_hen_gio ASC
    '''
    rows = db.execute(query, (user_id, user_id, now_str)).fetchall()

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
            'ngay_hen_gio': r['ngay_hen_gio'],
            'lien_ket': r['lien_ket'],
            'da_doc': False,
            'da_den_han': True
        })
    return result

def get_unread_count(user_id: int) -> dict:
    """Đếm số lượng thông báo chưa đọc và số nhắc nhở đến hạn."""
    db = get_db()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Tổng số chưa đọc
    row = db.execute('''
        SELECT COUNT(*) AS chua_doc
        FROM thong_bao tb
        LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
        WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
          AND tb_dd.ngay_doc IS NULL
    ''', (user_id, user_id)).fetchone()
    total_unread = row['chua_doc'] if row else 0

    # Số lượng nhắc nhở có hẹn giờ đã đến hạn
    row_due = db.execute('''
        SELECT COUNT(*) AS den_han
        FROM thong_bao tb
        LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
        WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
          AND tb.ngay_hen_gio IS NOT NULL
          AND tb.ngay_hen_gio <= ?
          AND tb_dd.ngay_doc IS NULL
    ''', (user_id, user_id, now_str)).fetchone()
    due_count = row_due['den_han'] if row_due else 0

    return {
        'chua_doc': total_unread,
        'den_han': due_count
    }

def mark_as_read(thong_bao_id: int, user_id: int) -> tuple[bool, str, int]:
    """Đánh dấu thông báo cụ thể là đã đọc."""
    db = get_db()
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

def create_notification(data: dict, nguoi_gui_id: int, user_role: str = 'CHUYEN_VIEN') -> tuple[bool, str, dict | None, int]:
    """Tạo mới một thông báo điều hành (Văn thư/Lãnh đạo) hoặc lời nhắc nhở cá nhân (Mọi cán bộ)."""
    tieu_de = (data.get('tieu_de') or '').strip()
    noi_dung = (data.get('noi_dung') or '').strip()
    loai = (data.get('loai') or 'Hệ thống').strip()
    muc_do = (data.get('muc_do') or 'Bình thường').strip()
    nguoi_nhan_id = data.get('nguoi_nhan_id')
    ngay_hen_gio = (data.get('ngay_hen_gio') or '').strip() or None
    lien_ket = (data.get('lien_ket') or '').strip() or None

    if not tieu_de:
        return False, "Tiêu đề thông báo / nhắc nhở không được để trống.", None, 400

    if not noi_dung:
        return False, "Nội dung không được để trống.", None, 400

    if loai not in VALID_LOAI:
        loai = 'Hệ thống'

    if muc_do not in VALID_MUC_DO:
        muc_do = 'Bình thường'

    db = get_db()

    # Phân quyền:
    # - Nếu người tạo không phải Văn thư hoặc Lãnh đạo mà không chọn người nhận -> tự động gán cho chính mình làm lời nhắc cá nhân
    if not nguoi_nhan_id and user_role not in ('VAN_THU', 'LANH_DAO'):
        nguoi_nhan_id = nguoi_gui_id
        if loai != 'Nhắc nhở':
            loai = 'Nhắc nhở'
    elif nguoi_nhan_id:
        try:
            nguoi_nhan_id = int(nguoi_nhan_id)
            user_exists = db.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE nguoi_dung_id = ?', (nguoi_nhan_id,)).fetchone()
            if not user_exists:
                return False, "Người nhận không tồn tại trong hệ thống.", None, 404
        except (ValueError, TypeError):
            return False, "Định dạng người nhận không hợp lệ.", None, 400
    else:
        # nguoi_nhan_id = None: Phát hành thông báo chung toàn thể cán bộ cơ quan (chỉ Văn thư/Lãnh đạo)
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
    msg = "Phát hành thông báo thành công." if not nguoi_nhan_id else "Đã thiết lập nhắc nhở thành công."
    return True, msg, {'id': created_id, 'tieu_de': tieu_de, 'ngay_hen_gio': ngay_hen_gio}, 201

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


# ==============================================================================
# OBJECT MODEL HELPER
# ==============================================================================
from .base_model import BaseModel

class NotificationModel(BaseModel):
    """Model quản lý thông báo điều hành và nhắc nhở thời gian thực."""

    @classmethod
    def get_unread_count(cls, user_id: int):
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = cls.db().execute('''
            SELECT COUNT(*) AS chua_doc
            FROM thong_bao tb
            LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
            WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
              AND tb_dd.ngay_doc IS NULL
        ''', (user_id, user_id)).fetchone()
        
        row_due = cls.db().execute('''
            SELECT COUNT(*) AS den_han
            FROM thong_bao tb
            LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
            WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
              AND tb.ngay_hen_gio IS NOT NULL
              AND tb.ngay_hen_gio <= ?
              AND tb_dd.ngay_doc IS NULL
        ''', (user_id, user_id, now_str)).fetchone()

        return {
            'chua_doc': row['chua_doc'] if row else 0,
            'den_han': row_due['den_han'] if row_due else 0
        }

    @classmethod
    def get_by_user(cls, user_id: int):
        cur = cls.db().execute('''
            SELECT tb.*,
                   CASE WHEN tb_dd.ngay_doc IS NOT NULL THEN 1 ELSE 0 END AS da_doc
            FROM thong_bao tb
            LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
            WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
            ORDER BY tb.ngay_tao DESC
        ''', (user_id, user_id))
        return cls.list_from_rows(cur.fetchall())

