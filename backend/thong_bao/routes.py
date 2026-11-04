from flask import Blueprint, request, jsonify, g
from backend.auth.decorators import login_required, role_required
from .services import (
    get_user_notifications,
    get_unread_count,
    get_due_reminders,
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
    """Lấy số lượng thông báo chưa đọc và số nhắc nhở đến hạn."""
    user_id = g.current_user['nguoi_dung_id']
    stats = get_unread_count(user_id)
    return jsonify({
        'thanh_cong': True,
        'chua_doc': stats['chua_doc'],
        'den_han': stats['den_han']
    }), 200

@thong_bao_bp.route('/kiem-tra-den-han', methods=['GET'])
@login_required
def kiem_tra_den_han():
    """Kiểm tra và lấy danh sách các nhắc nhở đã đến hoặc quá hạn."""
    user_id = g.current_user['nguoi_dung_id']
    due_items = get_due_reminders(user_id)
    return jsonify({
        'thanh_cong': True,
        'nhac_nho_den_han': due_items,
        'so_luong': len(due_items)
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
    """Tạo thông báo điều hành (Văn thư/Lãnh đạo) hoặc lời nhắc nhở cá nhân (Mọi cán bộ)."""
    user_id = g.current_user['nguoi_dung_id']
    user_role = g.current_user['vai_tro']
    data = request.get_json(silent=True) or {}

    success, message, result, status_code = create_notification(
        data=data,
        nguoi_gui_id=user_id,
        user_role=user_role
    )
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
