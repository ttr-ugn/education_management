"""
CONTROLLERS/HO_SO_CONTROLLER.PY - MVC ARCHITECTURE (CONTROLLER LAYER)
"""

from flask import Blueprint, request, jsonify, g
from controllers.decorators import login_required, role_required
from models.dossier_model import (
    get_ho_so_list,
    get_ho_so_by_id,
    create_ho_so,
    update_ho_so,
    delete_ho_so,
    submit_ho_so_to_archive,
    close_ho_so,
    get_van_ban_in_ho_so,
    get_available_van_ban,
    add_van_ban_to_ho_so,
    remove_van_ban_from_ho_so
)

ho_so_bp = Blueprint('ho_so', __name__)

@ho_so_bp.route('', methods=['GET'])
@login_required
def danh_sach():
    """Lấy danh sách hồ sơ lưu trữ theo bộ lọc."""
    q = request.args.get('q')
    tinh_trang = request.args.get('tinh_trang')
    nam_tai_lieu = request.args.get('nam_tai_lieu')
    don_vi = request.args.get('don_vi')

    items = get_ho_so_list(q=q, tinh_trang=tinh_trang, nam_tai_lieu=nam_tai_lieu, don_vi=don_vi)
    return jsonify({
        'thanh_cong': True,
        'du_lieu': items,
        'tong_so': len(items)
    }), 200

@ho_so_bp.route('/<int:ho_so_id>', methods=['GET'])
@login_required
def chi_tiet(ho_so_id):
    """Lấy chi tiết một hồ sơ lưu trữ."""
    hs = get_ho_so_by_id(ho_so_id)
    if not hs:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Không tìm thấy hồ sơ lưu trữ yêu cầu.'
        }), 404
    return jsonify({
        'thanh_cong': True,
        'du_lieu': hs
    }), 200

@ho_so_bp.route('/<int:ho_so_id>/van-ban', methods=['GET'])
@login_required
def danh_sach_van_ban(ho_so_id):
    """Lấy danh sách các văn bản thực tế trong hồ sơ lưu trữ."""
    hs = get_ho_so_by_id(ho_so_id)
    if not hs:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Không tìm thấy hồ sơ lưu trữ.'
        }), 404

    docs = get_van_ban_in_ho_so(ho_so_id)
    return jsonify({
        'thanh_cong': True,
        'du_lieu': docs,
        'tong_so': len(docs)
    }), 200

@ho_so_bp.route('/<int:ho_so_id>/van-ban-kha-dung', methods=['GET'])
@login_required
def van_ban_kha_dung(ho_so_id):
    """Lấy danh sách các văn bản đã ban hành có thể bổ sung vào hồ sơ này."""
    hs = get_ho_so_by_id(ho_so_id)
    if not hs:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Không tìm thấy hồ sơ lưu trữ.'
        }), 404

    available = get_available_van_ban(ho_so_id)
    return jsonify({
        'thanh_cong': True,
        'du_lieu': available,
        'tong_so': len(available)
    }), 200

@ho_so_bp.route('/<int:ho_so_id>/them-van-ban', methods=['POST'])
@login_required
def them_van_ban(ho_so_id):
    """Bổ sung một văn bản đã ban hành vào hồ sơ lưu trữ."""
    data = request.get_json(silent=True) or {}
    van_ban_id = data.get('van_ban_id')
    nguon = data.get('nguon', 'van_ban_di')

    if not van_ban_id:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Vui lòng cung cấp van_ban_id để bổ sung vào hồ sơ.'
        }), 400

    try:
        van_ban_id = int(van_ban_id)
    except (ValueError, TypeError):
        return jsonify({'thanh_cong': False, 'thong_bao': 'ID văn bản không hợp lệ.'}), 400

    success, message, status_code = add_van_ban_to_ho_so(ho_so_id, van_ban_id, nguon)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@ho_so_bp.route('/<int:ho_so_id>/xoa-van-ban', methods=['POST'])
@login_required
def xoa_van_ban(ho_so_id):
    """Gỡ một văn bản khỏi hồ sơ lưu trữ."""
    data = request.get_json(silent=True) or {}
    van_ban_id = data.get('van_ban_id')
    nguon = data.get('nguon', 'van_ban_di')

    if not van_ban_id:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Vui lòng cung cấp van_ban_id để gỡ khỏi hồ sơ.'
        }), 400

    try:
        van_ban_id = int(van_ban_id)
    except (ValueError, TypeError):
        return jsonify({'thanh_cong': False, 'thong_bao': 'ID văn bản không hợp lệ.'}), 400

    success, message, status_code = remove_van_ban_from_ho_so(ho_so_id, van_ban_id, nguon)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@ho_so_bp.route('', methods=['POST'])
@login_required
def tao_moi():
    """Lập mới một hồ sơ lưu trữ."""
    data = request.get_json(silent=True) or {}
    success, message, created_item, status_code = create_ho_so(data, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': created_item
    }), status_code

@ho_so_bp.route('/<int:ho_so_id>', methods=['PUT'])
@login_required
def cap_nhat(ho_so_id):
    """Cập nhật thông tin hồ sơ lưu trữ."""
    data = request.get_json(silent=True) or {}
    success, message, updated_item, status_code = update_ho_so(ho_so_id, data, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': updated_item
    }), status_code

@ho_so_bp.route('/<int:ho_so_id>', methods=['DELETE'])
@login_required
def xoa(ho_so_id):
    """Xóa hồ sơ lưu trữ."""
    success, message, status_code = delete_ho_so(ho_so_id, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@ho_so_bp.route('/<int:ho_so_id>/nop-luu-tru', methods=['POST'])
@login_required
def nop_luu_tru(ho_so_id):
    """Nộp hồ sơ vào kho lưu trữ cơ quan."""
    success, message, updated_item, status_code = submit_ho_so_to_archive(ho_so_id, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': updated_item
    }), status_code

@ho_so_bp.route('/<int:ho_so_id>/dong', methods=['POST'])
@login_required
def dong(ho_so_id):
    """Đóng hồ sơ lưu trữ."""
    success, message, updated_item, status_code = close_ho_so(ho_so_id, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': updated_item
    }), status_code
