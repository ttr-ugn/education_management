from flask import Blueprint, request, jsonify, g
from backend.auth.decorators import login_required, role_required
from .services import (
    get_ho_so_list,
    get_ho_so_by_id,
    create_ho_so,
    update_ho_so,
    delete_ho_so,
    submit_ho_so_to_archive,
    close_ho_so
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