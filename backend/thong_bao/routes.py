from flask import Blueprint, request, jsonify, g
from backend.auth.decorators import login_required, role_required
from .services import (
    get_user_notifications,
    get_unread_count,
    mark_as_read,
    mark_all_as_read,
    create_notification,
    delete_notification
)

thong_bao_bp = Blueprint('thong_bao', __name__)

@thong_bao_bp.route('', methods=['GET'])
@login_required
def danh_sach_thong_bao():
    """Lấy danh sách thông báo điều hành và nhắc nhở của người dùng."""
    user_id = g.current_user['nguoi_dung_id']
    loai = request.args.get('loai')
    muc_do = request.args.get('muc_do')
    chua_doc_only = request.args.get('chua_doc', '').lower() in ('1', 'true', 'yes')

    notifications = get_user_notifications(
        user_id=user_id,
        loai=loai,
        muc_do=muc_do,
        chua_doc_only=chua_doc_only
    )
    return jsonify({
        'thanh_cong': True,
        'du_lieu': notifications,
        'tong_so': len(notifications)
    }), 200

@thong_bao_bp.route('/dem-chua-doc', methods=['GET'])
@login_required
def dem_chua_doc():
    """Lấy số lượng thông báo chưa đọc của người dùng hiện tại."""
    user_id = g.current_user['nguoi_dung_id']
    count = get_unread_count(user_id)
    return jsonify({
        'thanh_cong': True,
        'chua_doc': count
    }), 200

@thong_bao_bp.route('/<int:thong_bao_id>/da-doc', methods=['POST'])
@login_required
def danh_dau_da_doc(thong_bao_id):
    """Đánh dấu một thông báo là đã đọc."""
    user_id = g.current_user['nguoi_dung_id']
    success, message, status_code = mark_as_read(thong_bao_id, user_id)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@thong_bao_bp.route('/doc-tat-ca', methods=['POST'])
@login_required
def danh_dau_tat_ca_da_doc():
    """Đánh dấu toàn bộ thông báo của người dùng là đã đọc."""
    user_id = g.current_user['nguoi_dung_id']
    success, message, status_code = mark_all_as_read(user_id)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@thong_bao_bp.route('', methods=['POST'])
@login_required
def tao_thong_bao():
    """Tạo thông báo mới hoặc lời nhắc nhở."""
    user_id = g.current_user['nguoi_dung_id']
    data = request.get_json(silent=True) or {}

    success, message, result, status_code = create_notification(data, nguoi_gui_id=user_id)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': result
    }), status_code

@thong_bao_bp.route('/<int:thong_bao_id>', methods=['DELETE'])
@login_required
def xoa_thong_bao(thong_bao_id):
    """Xóa thông báo."""
    user_id = g.current_user['nguoi_dung_id']
    user_role = g.current_user['vai_tro']
    success, message, status_code = delete_notification(thong_bao_id, user_id, user_role)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code
