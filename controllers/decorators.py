"""
DECORATORS - KIỂM SOÁT PHÂN QUYỀN VÀ TRẠNG THÁI NGƯỜI DÙNG (MVC ARCHITECTURE)
"""

from functools import wraps
from flask import session, jsonify, g
from database.db import get_db

def login_required(f):
    """Decorator kiểm tra người dùng đã đăng nhập và tài khoản còn đang HOAT_DONG."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'thanh_cong': False,
                'thong_bao': 'Vui lòng đăng nhập để tiếp tục.'
            }), 401

        db = get_db()
        user = db.execute('''
            SELECT nguoi_dung_id, ten_dang_nhap, ho_va_ten, email, sdt,
                   phong_ban, chuc_vu, vai_tro, trang_thai, bat_buoc_doi_mat_khau
            FROM nguoi_dung
            WHERE nguoi_dung_id = ?
        ''', (user_id,)).fetchone()

        if not user:
            session.clear()
            return jsonify({
                'thanh_cong': False,
                'thong_bao': 'Tài khoản không tồn tại hoặc đã bị xóa.'
            }), 401

        if user['trang_thai'] != 'HOAT_DONG':
            session.clear()
            thong_bao = 'Tài khoản của bạn hiện không thể sử dụng.'
            if user['trang_thai'] == 'CHO_DUYET':
                thong_bao = 'Tài khoản đang chờ Văn thư phê duyệt.'
            elif user['trang_thai'] == 'TU_CHOI':
                thong_bao = 'Tài khoản đã bị từ chối phê duyệt.'
            elif user['trang_thai'] == 'BI_KHOA':
                thong_bao = 'Tài khoản đã bị khóa bởi Quản trị viên.'
            return jsonify({
                'thanh_cong': False,
                'thong_bao': thong_bao
            }), 403

        # Gắn thông tin người dùng vào context g
        g.current_user = dict(user)
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator kiểm tra vai trò (VAN_THU, CHUYEN_VIEN, LANH_DAO)."""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            current_role = g.current_user.get('vai_tro')
            if current_role not in allowed_roles:
                return jsonify({
                    'thanh_cong': False,
                    'thong_bao': 'Bạn không có quyền thực hiện thao tác này.'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
