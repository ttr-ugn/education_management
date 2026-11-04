"""
USERS CONTROLLER - ĐIỀU KHIỂN QUẢN TRỊ NGƯỜI DÙNG & PHÂN QUYỀN (MVC ARCHITECTURE)
Route prefix: /api/users
"""

from flask import Blueprint, request, jsonify, g
from controllers.decorators import login_required, role_required
from models.user_model import (
    get_users_list,
    approve_user,
    reject_user,
    create_leader_user,
    lock_user,
    unlock_user,
    reset_user_password
)

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@role_required('VAN_THU')
def danh_sach_nguoi_dung():
    """Lấy danh sách người dùng có lọc và tìm kiếm (chỉ Văn thư)."""
    trang_thai = request.args.get('trang_thai')
    vai_tro = request.args.get('vai_tro')
    q = request.args.get('q')

    users = get_users_list(trang_thai=trang_thai, vai_tro=vai_tro, q=q)
    return jsonify({
        'thanh_cong': True,
        'du_lieu': users,
        'tong_so': len(users)
    }), 200

@users_bp.route('/<int:user_id>/duyet', methods=['POST'])
@role_required('VAN_THU')
def duyet(user_id):
    """Phê duyệt tài khoản Chuyên viên đang chờ duyệt (chỉ Văn thư)."""
    admin_id = g.current_user['nguoi_dung_id']
    success, message, status_code = approve_user(user_id, admin_id)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@users_bp.route('/<int:user_id>/tu-choi', methods=['POST'])
@role_required('VAN_THU')
def tu_choi(user_id):
    """Từ chối tài khoản Chuyên viên kèm theo lý do (chỉ Văn thư)."""
    admin_id = g.current_user['nguoi_dung_id']
    data = request.get_json(silent=True) or {}
    ly_do = data.get('ly_do')

    success, message, status_code = reject_user(user_id, admin_id, ly_do)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@users_bp.route('/lanh-dao', methods=['POST'])
@role_required('VAN_THU')
def tao_lanh_dao():
    """Văn thư tạo tài khoản Lãnh đạo, sinh mật khẩu tạm trả về 1 lần."""
    admin_id = g.current_user['nguoi_dung_id']
    data = request.get_json(silent=True) or {}

    success, message, result_data, status_code = create_leader_user(data, admin_id)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': result_data
    }), status_code

@users_bp.route('/<int:user_id>/khoa', methods=['POST'])
@role_required('VAN_THU')
def khoa(user_id):
    """Khóa tài khoản người dùng (chỉ Văn thư)."""
    current_admin_id = g.current_user['nguoi_dung_id']
    success, message, status_code = lock_user(user_id, current_admin_id)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@users_bp.route('/<int:user_id>/mo-khoa', methods=['POST'])
@role_required('VAN_THU')
def mo_khoa(user_id):
    """Mở khóa tài khoản người dùng (chỉ Văn thư)."""
    success, message, status_code = unlock_user(user_id)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@users_bp.route('/<int:user_id>/dat-lai-mat-khau', methods=['POST'])
@role_required('VAN_THU')
def dat_lai_mat_khau(user_id):
    """Đặt lại mật khẩu cho tài khoản người dùng (chỉ Văn thư)."""
    data = request.get_json(silent=True) or {}
    custom_password = data.get('mat_khau_moi')

    success, message, mat_khau_moi, status_code = reset_user_password(user_id, custom_password)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'mat_khau_moi': mat_khau_moi
    }), status_code
