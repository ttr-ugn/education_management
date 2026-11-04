import os
import uuid
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from database.db import get_db
from config import Config
from .pdf_sign import stamp_pdf_signature

def format_file_size(size_bytes: int) -> str:
    """Đổi kích thước byte sang định dạng thân thiện (KB, MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def record_history(db, van_ban_id: int, user_id: int, action: str, old_status: str, new_status: str, content: str = ""):
    """Ghi vết nhật ký xử lý tiến trình văn bản."""
    db.execute('''
        INSERT INTO lich_su_xu_ly_van_ban (
            van_ban_id, nguoi_thuc_hien_id, hanh_dong,
            trang_thai_truoc, trang_thai_sau, noi_dung, thoi_gian
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        van_ban_id, user_id, action,
        old_status, new_status, content,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))

def create_document(user: dict, form_data: dict, uploaded_file) -> tuple[bool, str, dict | None, int]:
    """
    Bước 1: Chuyên viên soạn thảo văn bản và gửi đến Văn thư.
    Trạng thái khởi tạo: CHO_VAN_THU_KIEM_TRA
    """
    trich_yeu = (form_data.get('trich_yeu') or '').strip()
    loai_van_ban = (form_data.get('loai_van_ban') or '').strip()
    don_vi_soan_thao = (form_data.get('don_vi_soan_thao') or user.get('phong_ban') or 'Phòng Chuyên môn').strip()
    noi_nhan = (form_data.get('noi_nhan') or '').strip()
    do_khan = (form_data.get('do_khan') or 'Bình thường').strip()
    noi_dung_tom_tat = (form_data.get('noi_dung_tom_tat') or '').strip()
    lanh_dao_ky = (form_data.get('lanh_dao_ky') or '').strip()

    if not trich_yeu or not loai_van_ban or not noi_nhan:
        return False, "Vui lòng nhập trích yếu, loại văn bản và nơi nhận văn bản.", None, 400

    if not uploaded_file or not uploaded_file.filename:
        return False, "Vui lòng đính kèm tệp văn bản dự thảo (.pdf, .doc, .docx).", None, 400

    original_name = uploaded_file.filename
    ext = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
    if ext not in Config.ALLOWED_EXTENSIONS:
        return False, f"Định dạng tệp không được hỗ trợ. Chỉ chấp nhận: {', '.join(Config.ALLOWED_EXTENSIONS)}", None, 400

    # Lưu tệp vào thư mục drafts
    drafts_dir = Path(Config.UPLOAD_FOLDER) / 'drafts'
    drafts_dir.mkdir(parents=True, exist_ok=True)

    safe_name = secure_filename(original_name) or f"draft_{int(datetime.now().timestamp())}.{ext}"
    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    file_path = drafts_dir / unique_filename

    try:
        uploaded_file.save(str(file_path))
        file_size = file_path.stat().st_size
        size_str = format_file_size(file_size)
    except Exception as e:
        return False, f"Không thể lưu tệp đính kèm: {str(e)}", None, 500

    db = get_db()
    
    # Tìm lãnh đạo nếu có
    lanh_dao_id = None
    if lanh_dao_ky:
        # Tìm theo ID hoặc tên
        ld_row = db.execute('''
            SELECT nguoi_dung_id, ho_va_ten FROM nguoi_dung 
            WHERE vai_tro = 'LANH_DAO' AND (ho_va_ten LIKE ? OR ? LIKE '%' || ho_va_ten || '%')
            LIMIT 1
        ''', (f"%{lanh_dao_ky}%", lanh_dao_ky)).fetchone()
        if ld_row:
            lanh_dao_id = ld_row['nguoi_dung_id']
            lanh_dao_ky = ld_row['ho_va_ten']

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        cursor = db.execute('''
            INSERT INTO van_ban_di (
                so_ky_hieu, trich_yeu, loai_van_ban, do_khan,
                don_vi_soan_thao, noi_nhan, noi_dung_tom_tat,
                file_goc_path, file_goc_ten, file_goc_dung_luong,
                nguoi_soan_id, lanh_dao_ky_id, lanh_dao_ky_ten,
                trang_thai, ngay_tao, ngay_trinh_van_thu
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CHO_VAN_THU_KIEM_TRA', ?, ?)
        ''', (
            "Dự thảo/SGDĐT", trich_yeu, loai_van_ban, do_khan,
            don_vi_soan_thao, noi_nhan, noi_dung_tom_tat,
            str(file_path), original_name, size_str,
            user['nguoi_dung_id'], lanh_dao_id, lanh_dao_ky,
            now_str, now_str
        ))
        new_id = cursor.lastrowid

        # Cập nhật mã ký hiệu dự thảo theo ID
        so_du_thao = f"Dự thảo-{new_id:03d}/SGDĐT"
        db.execute('UPDATE van_ban_di SET so_ky_hieu = ? WHERE van_ban_id = ?', (so_du_thao, new_id))

        # Ghi lịch sử
        record_history(
            db, new_id, user['nguoi_dung_id'],
            action='KHOI_TAO',
            old_status='',
            new_status='CHO_VAN_THU_KIEM_TRA',
            content=f"Chuyên viên {user['ho_va_ten']} khởi tạo dự thảo văn bản và gửi Văn thư kiểm tra."
        )

        db.commit()

        return True, "Khởi tạo và gửi dự thảo văn bản tới Văn thư thành công!", {
            'van_ban_id': new_id,
            'so_ky_hieu': so_du_thao,
            'trang_thai': 'CHO_VAN_THU_KIEM_TRA'
        }, 201

    except Exception as e:
        db.rollback()
        return False, f"Lỗi khi lưu văn bản vào CSDL: {str(e)}", None, 500

def get_documents_list(user: dict, filters: dict) -> list[dict]:
    """Lấy danh sách văn bản đi với bộ lọc và phân quyền theo vai trò."""
    db = get_db()
    role = user.get('vai_tro')
    user_id = user.get('nguoi_dung_id')

    query = '''
        SELECT v.*, 
               ns.ho_va_ten AS nguoi_soan_ten,
               vt.ho_va_ten AS van_thu_ten,
               ld.ho_va_ten AS lanh_dao_ten
        FROM van_ban_di v
        LEFT JOIN nguoi_dung ns ON v.nguoi_soan_id = ns.nguoi_dung_id
        LEFT JOIN nguoi_dung vt ON v.van_thu_id = vt.nguoi_dung_id
        LEFT JOIN nguoi_dung ld ON v.lanh_dao_ky_id = ld.nguoi_dung_id
        WHERE 1=1
    '''
    params = []

    # Phân quyền hiển thị theo vai trò
    if role == 'CHUYEN_VIEN':
        # Chuyên viên thấy văn bản do mình soạn hoặc đã ban hành công khai
        query += ' AND (v.nguoi_soan_id = ? OR v.trang_thai = "DA_BAN_HANH")'
        params.append(user_id)
    elif role == 'LANH_DAO':
        # Lãnh đạo thấy văn bản giao cho mình ký hoặc ở các bước phê duyệt / đã ban hành
        query += ''' AND (
            v.lanh_dao_ky_id = ? 
            OR v.trang_thai IN ('CHO_LANH_DAO_KY', 'DA_KY_CHO_BAN_HANH', 'DA_BAN_HANH')
        )'''
        params.append(user_id)
    # VAN_THU có thể xem toàn bộ văn bản để quản lý

    # Bộ lọc tìm kiếm text
    q = (filters.get('q') or '').strip()
    if q:
        query += ''' AND (
            v.so_ky_hieu LIKE ? 
            OR v.trich_yeu LIKE ? 
            OR v.don_vi_soan_thao LIKE ?
            OR ns.ho_va_ten LIKE ?
        )'''
        kw = f"%{q}%"
        params.extend([kw, kw, kw, kw])

    # Bộ lọc trạng thái
    trang_thai = filters.get('trang_thai')
    if trang_thai:
        # Hỗ trợ mapping nếu frontend gửi các mã cũ
        if trang_thai == 'CHO_LANH_DAO_DUYET':
            query += ' AND v.trang_thai = "CHO_LANH_DAO_KY"'
        elif trang_thai == 'DA_DUYET':
            query += ' AND v.trang_thai = "DA_KY_CHO_BAN_HANH"'
        elif trang_thai == 'YEU_CAU_CHINH_SUA':
            query += ' AND v.trang_thai IN ("VAN_THU_TRA_LAI", "LANH_DAO_TRA_LAI")'
        else:
            query += ' AND v.trang_thai = ?'
            params.append(trang_thai)

    if filters.get('do_khan'):
        query += ' AND v.do_khan = ?'
        params.append(filters.get('do_khan'))

    if filters.get('loai_van_ban'):
        query += ' AND v.loai_van_ban = ?'
        params.append(filters.get('loai_van_ban'))

    query += ' ORDER BY v.van_ban_id DESC'

    rows = db.execute(query, params).fetchall()
    result = []

    for r in rows:
        d = dict(r)
        # Chuẩn hóa để khớp hoàn hảo với cấu trúc FE đang dùng
        result.append({
            'id': d['van_ban_id'],
            'van_ban_id': d['van_ban_id'],
            'so_ky_hieu': d['so_ky_hieu'],
            'trich_yeu': d['trich_yeu'],
            'loai_van_ban': d['loai_van_ban'],
            'don_vi_soan_thao': d['don_vi_soan_thao'],
            'nguoi_soan_thao': d['nguoi_soan_ten'] or 'Chuyên viên',
            'lanh_dao_ky': d['lanh_dao_ten'] or d['lanh_dao_ky_ten'] or 'Lãnh đạo Sở',
            'ngay_soan': d['ngay_tao'].split(' ')[0] if d.get('ngay_tao') else '',
            'ngay_ban_hanh': d['ngay_ban_hanh'].split(' ')[0] if d.get('ngay_ban_hanh') else None,
            'do_khan': d['do_khan'],
            'trang_thai': d['trang_thai'],
            'noi_nhan': d['noi_nhan'],
            'ly_do_chinh_sua': d['y_kien_van_thu'] or d['y_kien_lanh_dao'] or '',
            'file_goc_ten': d['file_goc_ten'],
            'file_da_ky_ten': d['file_da_ky_ten'],
            'tep_dinh_kem': [
                {
                    'ten_tep': d['file_da_ky_ten'] if d.get('file_da_ky_path') else d['file_goc_ten'],
                    'dung_luong': d['file_goc_dung_luong'] or '1.0 MB',
                    'da_ky': bool(d.get('file_da_ky_path'))
                }
            ]
        })

    return result

def get_document_detail(user: dict, doc_id: int) -> tuple[bool, str, dict | None, int]:
    """Lấy thông tin chi tiết một văn bản kèm toàn bộ nhật ký xử lý."""
    db = get_db()
    row = db.execute('''
        SELECT v.*, 
               ns.ho_va_ten AS nguoi_soan_ten, ns.email AS nguoi_soan_email, ns.sdt AS nguoi_soan_sdt,
               vt.ho_va_ten AS van_thu_ten,
               ld.ho_va_ten AS lanh_dao_ten, ld.chuc_vu AS lanh_dao_chuc_vu
        FROM van_ban_di v
        LEFT JOIN nguoi_dung ns ON v.nguoi_soan_id = ns.nguoi_dung_id
        LEFT JOIN nguoi_dung vt ON v.van_thu_id = vt.nguoi_dung_id
        LEFT JOIN nguoi_dung ld ON v.lanh_dao_ky_id = ld.nguoi_dung_id
        WHERE v.van_ban_id = ?
    ''', (doc_id,)).fetchone()

    if not row:
        return False, "Không tìm thấy văn bản yêu cầu.", None, 404

    d = dict(row)

    # Lấy lịch sử xử lý
    history_rows = db.execute('''
        SELECT h.*, u.ho_va_ten AS nguoi_thuc_hien_ten, u.vai_tro
        FROM lich_su_xu_ly_van_ban h
        LEFT JOIN nguoi_dung u ON h.nguoi_thuc_hien_id = u.nguoi_dung_id
        WHERE h.van_ban_id = ?
        ORDER BY h.id ASC
    ''', (doc_id,)).fetchall()

    history = [dict(h) for h in history_rows]

    doc_data = {
        'id': d['van_ban_id'],
        'van_ban_id': d['van_ban_id'],
        'so_ky_hieu': d['so_ky_hieu'],
        'trich_yeu': d['trich_yeu'],
        'loai_van_ban': d['loai_van_ban'],
        'don_vi_soan_thao': d['don_vi_soan_thao'],
        'nguoi_soan_thao': d['nguoi_soan_ten'],
        'nguoi_soan_email': d['nguoi_soan_email'],
        'nguoi_soan_id': d['nguoi_soan_id'],
        'lanh_dao_ky': d['lanh_dao_ten'] or d['lanh_dao_ky_ten'],
        'lanh_dao_ky_id': d['lanh_dao_ky_id'],
        'van_thu_ten': d['van_thu_ten'],
        'ngay_soan': d['ngay_tao'].split(' ')[0] if d.get('ngay_tao') else '',
        'ngay_tao': d['ngay_tao'],
        'ngay_trinh_van_thu': d['ngay_trinh_van_thu'],
        'ngay_trinh_lanh_dao': d['ngay_trinh_lanh_dao'],
        'ngay_ban_hanh': d['ngay_ban_hanh'].split(' ')[0] if d.get('ngay_ban_hanh') else None,
        'do_khan': d['do_khan'],
        'trang_thai': d['trang_thai'],
        'noi_nhan': d['noi_nhan'],
        'noi_dung_tom_tat': d['noi_dung_tom_tat'],
        'y_kien_van_thu': d['y_kien_van_thu'],
        'y_kien_lanh_dao': d['y_kien_lanh_dao'],
        'ly_do_chinh_sua': d['y_kien_van_thu'] or d['y_kien_lanh_dao'] or '',
        'file_goc_ten': d['file_goc_ten'],
        'file_da_ky_ten': d['file_da_ky_ten'],
        'co_file_da_ky': bool(d.get('file_da_ky_path')),
        'ky_so_trang': d['ky_so_trang'],
        'ky_so_x': d['ky_so_x'],
        'ky_so_y': d['ky_so_y'],
        'thoi_gian_ky': d['thoi_gian_ky'],
        'tep_dinh_kem': [
            {
                'ten_tep': d['file_goc_ten'],
                'dung_luong': d['file_goc_dung_luong'] or '1.0 MB',
                'loai': 'goc',
                'download_url': f"/api/van-ban-di/{doc_id}/download?type=goc"
            }
        ],
        'lich_su': history
    }

    if d.get('file_da_ky_path'):
        doc_data['tep_dinh_kem'].append({
            'ten_tep': d['file_da_ky_ten'] or f"VB_{doc_id}_da_ky.pdf",
            'dung_luong': 'Chính thức',
            'loai': 'da_ky',
            'download_url': f"/api/van-ban-di/{doc_id}/download?type=da_ky"
        })

    return True, "Lấy thông tin thành công.", doc_data, 200

def clerk_edit_document(user: dict, doc_id: int, form_data: dict) -> tuple[bool, str, int]:
    """Bước 2a: Văn thư kiểm tra và chỉnh sửa thể thức/nội dung văn bản."""
    db = get_db()
    row = db.execute('SELECT * FROM van_ban_di WHERE van_ban_id = ?', (doc_id,)).fetchone()
    if not row:
        return False, "Không tìm thấy văn bản.", 404

    trich_yeu = (form_data.get('trich_yeu') or row['trich_yeu']).strip()
    loai_van_ban = (form_data.get('loai_van_ban') or row['loai_van_ban']).strip()
    noi_nhan = (form_data.get('noi_nhan') or row['noi_nhan']).strip()
    do_khan = (form_data.get('do_khan') or row['do_khan']).strip()
    don_vi = (form_data.get('don_vi_soan_thao') or row['don_vi_soan_thao']).strip()

    db.execute('''
        UPDATE van_ban_di 
        SET trich_yeu = ?, loai_van_ban = ?, noi_nhan = ?, do_khan = ?, don_vi_soan_thao = ?, van_thu_id = ?
        WHERE van_ban_id = ?
    ''', (trich_yeu, loai_van_ban, noi_nhan, do_khan, don_vi, user['nguoi_dung_id'], doc_id))

    record_history(
        db, doc_id, user['nguoi_dung_id'],
        action='VAN_THU_CHINH_SUA',
        old_status=row['trang_thai'],
        new_status=row['trang_thai'],
        content=f"Văn thư {user['ho_va_ten']} đã chỉnh sửa chuẩn hóa thông tin thể thức văn bản."
    )
    db.commit()
    return True, "Đã cập nhật thông tin văn bản thành công.", 200

def clerk_reject_document(user: dict, doc_id: int, ly_do: str) -> tuple[bool, str, int]:
    """Bước 2b: Văn thư trả lại cho Chuyên viên làm lại kèm ý kiến."""
    if not ly_do or not ly_do.strip():
        return False, "Vui lòng nhập lý do/ý kiến phản hồi yêu cầu Chuyên viên chỉnh sửa.", 400

    db = get_db()
    row = db.execute('SELECT trang_thai FROM van_ban_di WHERE van_ban_id = ?', (doc_id,)).fetchone()
    if not row:
        return False, "Không tìm thấy văn bản.", 404

    old_status = row['trang_thai']
    new_status = 'VAN_THU_TRA_LAI'

    db.execute('''
        UPDATE van_ban_di
        SET trang_thai = ?, y_kien_van_thu = ?, van_thu_id = ?
        WHERE van_ban_id = ?
    ''', (new_status, ly_do.strip(), user['nguoi_dung_id'], doc_id))

    record_history(
        db, doc_id, user['nguoi_dung_id'],
        action='VAN_THU_TRA_LAI',
        old_status=old_status,
        new_status=new_status,
        content=f"Văn thư {user['ho_va_ten']} yêu cầu Chuyên viên làm lại: {ly_do.strip()}"
    )
    db.commit()
    return True, "Đã trả lại văn bản cho Chuyên viên kèm ý kiến phản hồi.", 200

def clerk_forward_to_leader(user: dict, doc_id: int, ghi_chu: str = "") -> tuple[bool, str, int]:
    """Bước 2c: Văn thư kiểm tra đạt yêu cầu -> Cập nhật trạng thái gửi lên Lãnh đạo ký."""
    db = get_db()
    row = db.execute('SELECT trang_thai, lanh_dao_ky_id, lanh_dao_ky_ten FROM van_ban_di WHERE van_ban_id = ?', (doc_id,)).fetchone()
    if not row:
        return False, "Không tìm thấy văn bản.", 404

    old_status = row['trang_thai']
    new_status = 'CHO_LANH_DAO_KY'
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db.execute('''
        UPDATE van_ban_di
        SET trang_thai = ?, van_thu_id = ?, ngay_trinh_lanh_dao = ?
        WHERE van_ban_id = ?
    ''', (new_status, user['nguoi_dung_id'], now_str, doc_id))

    record_history(
        db, doc_id, user['nguoi_dung_id'],
        action='TRINH_LANH_DAO',
        old_status=old_status,
        new_status=new_status,
        content=ghi_chu.strip() or f"Văn thư {user['ho_va_ten']} đã kiểm tra hợp lệ và trình Lãnh đạo Sở ký duyệt."
    )
    db.commit()
    return True, "Đã duyệt và chuyển văn bản lên Lãnh đạo ký thành công!", 200

def leader_reject_document(user: dict, doc_id: int, ly_do: str) -> tuple[bool, str, int]:
    """Bước 3a: Lãnh đạo từ chối hoặc yêu cầu sửa đổi dự thảo."""
    if not ly_do or not ly_do.strip():
        return False, "Vui lòng nhập lý do yêu cầu chỉnh sửa dự thảo.", 400

    db = get_db()
    row = db.execute('SELECT trang_thai FROM van_ban_di WHERE van_ban_id = ?', (doc_id,)).fetchone()
    if not row:
        return False, "Không tìm thấy văn bản.", 404

    old_status = row['trang_thai']
    new_status = 'LANH_DAO_TRA_LAI'

    db.execute('''
        UPDATE van_ban_di
        SET trang_thai = ?, y_kien_lanh_dao = ?
        WHERE van_ban_id = ?
    ''', (new_status, ly_do.strip(), doc_id))

    record_history(
        db, doc_id, user['nguoi_dung_id'],
        action='LANH_DAO_TRA_LAI',
        old_status=old_status,
        new_status=new_status,
        content=f"Lãnh đạo {user['ho_va_ten']} không phê duyệt, yêu cầu sửa đổi: {ly_do.strip()}"
    )
    db.commit()
    return True, "Đã gửi ý kiến yêu cầu chỉnh sửa dự thảo thành công.", 200

def leader_sign_document(user: dict, doc_id: int, sign_data: dict) -> tuple[bool, str, dict | None, int]:
    """
    Bước 3b: Lãnh đạo gán chữ ký số bằng click chuột vào văn bản.
    Nhận tọa độ click chuột (x, y, page), thực hiện đóng dấu số lên PDF và cập nhật:
    Trạng thái: DA_KY_CHO_BAN_HANH (Đã ký, chuyển về Văn thư).
    """
    db = get_db()
    row = db.execute('SELECT * FROM van_ban_di WHERE van_ban_id = ?', (doc_id,)).fetchone()
    if not row:
        return False, "Không tìm thấy văn bản cần ký.", None, 404

    page_num = int(sign_data.get('page') or sign_data.get('ky_so_trang') or 1)
    x = float(sign_data.get('x') or sign_data.get('ky_so_x') or 60.0)
    y = float(sign_data.get('y') or sign_data.get('ky_so_y') or 70.0)
    is_percentage = bool(sign_data.get('is_percentage', True)) # Mặc định tọa độ chuột từ canvas web gửi theo %

    input_file = row['file_goc_path']
    signed_dir = Path(Config.UPLOAD_FOLDER) / 'signed'
    signed_dir.mkdir(parents=True, exist_ok=True)

    output_filename = f"VB_{doc_id:03d}_signed_{uuid.uuid4().hex[:6]}.pdf"
    output_path = signed_dir / output_filename
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    signer_name = user['ho_va_ten']
    signer_title = user.get('chuc_vu') or 'Lãnh đạo Sở'

    try:
        stamp_pdf_signature(
            input_pdf_path=input_file,
            output_pdf_path=str(output_path),
            page_num=page_num,
            x=x,
            y=y,
            signer_name=signer_name,
            signer_title=signer_title,
            sign_time=now_str,
            is_percentage=is_percentage,
            trich_yeu=row['trich_yeu']
        )
    except Exception as e:
        return False, f"Lỗi khi đóng dấu chữ ký số lên tài liệu: {str(e)}", None, 500

    old_status = row['trang_thai']
    new_status = 'DA_KY_CHO_BAN_HANH'

    db.execute('''
        UPDATE van_ban_di
        SET trang_thai = ?,
            file_da_ky_path = ?,
            file_da_ky_ten = ?,
            ky_so_trang = ?,
            ky_so_x = ?,
            ky_so_y = ?,
            thoi_gian_ky = ?,
            lanh_dao_ky_id = ?
        WHERE van_ban_id = ?
    ''', (
        new_status,
        str(output_path),
        output_filename,
        page_num,
        x,
        y,
        now_str,
        user['nguoi_dung_id'],
        doc_id
    ))

    record_history(
        db, doc_id, user['nguoi_dung_id'],
        action='KY_SO',
        old_status=old_status,
        new_status=new_status,
        content=f"Lãnh đạo {signer_name} ({signer_title}) đã gán chữ ký số điện tử tại trang {page_num} và chuyển về Văn thư kiểm tra."
    )
    db.commit()

    return True, "Đã ký số điện tử thành công! Văn bản đã được chuyển về Văn thư để kiểm tra và ban hành.", {
        'van_ban_id': doc_id,
        'trang_thai': new_status,
        'file_da_ky_ten': output_filename,
        'thoi_gian_ky': now_str
    }, 200

def clerk_publish_document(user: dict, doc_id: int, publish_data: dict) -> tuple[bool, str, dict | None, int]:
    """
    Bước 4: Văn thư kiểm tra lại file đã ký, cấp số hiệu chính thức và Ban hành.
    Trạng thái: DA_BAN_HANH
    """
    db = get_db()
    row = db.execute('SELECT * FROM van_ban_di WHERE van_ban_id = ?', (doc_id,)).fetchone()
    if not row:
        return False, "Không tìm thấy văn bản cần ban hành.", None, 404

    so_ky_hieu = (publish_data.get('so_ky_hieu') or '').strip()
    if not so_ky_hieu:
        loai = row['loai_van_ban']
        viet_tat = 'KH' if loai == 'Kế hoạch' else ('QD' if loai == 'Quyết định' else 'VP')
        so_ky_hieu = f"{doc_id + 1000}/SGDĐT-{viet_tat}"

    ngay_ban_hanh = publish_data.get('ngay_ban_hanh') or datetime.now().strftime('%Y-%m-%d')
    old_status = row['trang_thai']
    new_status = 'DA_BAN_HANH'

    db.execute('''
        UPDATE van_ban_di
        SET so_ky_hieu = ?, ngay_ban_hanh = ?, trang_thai = ?, van_thu_id = ?
        WHERE van_ban_id = ?
    ''', (so_ky_hieu, ngay_ban_hanh, new_status, user['nguoi_dung_id'], doc_id))

    record_history(
        db, doc_id, user['nguoi_dung_id'],
        action='BAN_HANH',
        old_status=old_status,
        new_status=new_status,
        content=f"Văn thư {user['ho_va_ten']} đã vào sổ cấp số hiệu chính thức: {so_ky_hieu} và chính thức ban hành văn bản."
    )
    db.commit()

    return True, f"Đã ban hành văn bản chính thức thành công với số hiệu: {so_ky_hieu}!", {
        'van_ban_id': doc_id,
        'so_ky_hieu': so_ky_hieu,
        'ngay_ban_hanh': ngay_ban_hanh,
        'trang_thai': new_status
    }, 200

def get_file_for_download(doc_id: int, file_type: str = 'goc') -> tuple[bool, str, str | None, str | None, int]:
    """
    Bước 5: Lấy đường dẫn file để tải về (file gốc hoặc file đã ký của Lãnh đạo).
    """
    db = get_db()
    row = db.execute('SELECT file_goc_path, file_goc_ten, file_da_ky_path, file_da_ky_ten FROM van_ban_di WHERE van_ban_id = ?', (doc_id,)).fetchone()
    if not row:
        return False, "Không tìm thấy văn bản.", None, None, 404

    if file_type == 'da_ky':
        if not row['file_da_ky_path'] or not os.path.exists(row['file_da_ky_path']):
            return False, "Văn bản này chưa có file ký số điện tử.", None, None, 404
        return True, "Thành công", row['file_da_ky_path'], row['file_da_ky_ten'] or f"VB_{doc_id}_da_ky.pdf", 200
    else:
        if not row['file_goc_path'] or not os.path.exists(row['file_goc_path']):
            return False, "Không tìm thấy tệp gốc trên máy chủ.", None, None, 404
        return True, "Thành công", row['file_goc_path'], row['file_goc_ten'], 200
