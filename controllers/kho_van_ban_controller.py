"""
CONTROLLERS/KHO_VAN_BAN_CONTROLLER.PY - MVC ARCHITECTURE (CONTROLLER LAYER)
"""

from flask import Blueprint, request, jsonify, g
from controllers.decorators import login_required, role_required
from models.repository_model import (
    get_cay_nien_dai,
    get_van_ban_ban_hanh_list,
    get_van_ban_ban_hanh_by_id,
    create_van_ban_ban_hanh,
    update_van_ban_ban_hanh,
    delete_van_ban_ban_hanh,
    get_canh_bao_tieu_huy,
    get_van_ban_mau_list,
    get_van_ban_mau_by_id,
    create_van_ban_mau,
    update_van_ban_mau,
    delete_van_ban_mau,
    record_download_and_get_link,
    get_kho_van_ban_summary
)

kho_van_ban_bp = Blueprint('kho_van_ban', __name__)

# ==============================================================================
# TRỤC THỜI GIAN (DATE-TIME) & THỐNG KÊ
# ==============================================================================

@kho_van_ban_bp.route('/thoi-gian/cay-nien-dai', methods=['GET'])
@login_required
def lay_cay_nien_dai():
    """Lấy cây niên đại lưu trữ (Năm -> Quý -> Tháng) phục vụ điều hướng."""
    tree = get_cay_nien_dai()
    return jsonify({
        'thanh_cong': True,
        'du_lieu': tree
    }), 200

@kho_van_ban_bp.route('/thoi-gian/thong-ke', methods=['GET'])
@login_required
def thong_ke_kho():
    """Lấy tổng hợp chỉ số thống kê kho lưu trữ số hóa."""
    stats = get_kho_van_ban_summary()
    return jsonify({
        'thanh_cong': True,
        'du_lieu': stats
    }), 200

@kho_van_ban_bp.route('/canh-bao-tieu-huy', methods=['GET'])
@login_required
def canh_bao_tieu_huy():
    """Lấy danh sách các văn bản sắp hoặc đã hết hạn bảo quản theo quy định."""
    target_year = request.args.get('nam_den_han', default=2030, type=int)
    list_warning = get_canh_bao_tieu_huy(target_year)
    return jsonify({
        'thanh_cong': True,
        'du_lieu': list_warning,
        'tong_so': len(list_warning)
    }), 200

# ==============================================================================
# KHO 1: VĂN BẢN ĐÃ KÝ BAN HÀNH (TRA CỨU & QUẢN LÝ)
# ==============================================================================

@kho_van_ban_bp.route('/ban-hanh', methods=['GET'])
@login_required
def danh_sach_ban_hanh():
    """
    Tra cứu văn bản đã ký ban hành theo mốc thời gian:
    Params: q, nam, thang, quy, tu_ngay, den_ngay, loai_van_ban, nguoi_ky, don_vi, thoi_han_bao_quan, ho_so_id
    """
    filters = {
        'q': request.args.get('q'),
        'nam': request.args.get('nam'),
        'thang': request.args.get('thang'),
        'quy': request.args.get('quy'),
        'tu_ngay': request.args.get('tu_ngay'),
        'den_ngay': request.args.get('den_ngay'),
        'loai_van_ban': request.args.get('loai_van_ban'),
        'nguoi_ky': request.args.get('nguoi_ky'),
        'don_vi': request.args.get('don_vi'),
        'thoi_han_bao_quan': request.args.get('thoi_han_bao_quan'),
        'ho_so_id': request.args.get('ho_so_id')
    }
    items = get_van_ban_ban_hanh_list(filters)
    return jsonify({
        'thanh_cong': True,
        'du_lieu': items,
        'tong_so': len(items)
    }), 200

@kho_van_ban_bp.route('/ban-hanh/<int:van_ban_id>', methods=['GET'])
@login_required
def chi_tiet_ban_hanh(van_ban_id):
    """Lấy chi tiết văn bản đã ký ban hành."""
    item = get_van_ban_ban_hanh_by_id(van_ban_id)
    if not item:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Không tìm thấy văn bản lưu trữ yêu cầu.'
        }), 404
    return jsonify({
        'thanh_cong': True,
        'du_lieu': item
    }), 200

@kho_van_ban_bp.route('/ban-hanh', methods=['POST'])
@login_required
def luu_ban_hanh():
    """Lưu trữ văn bản đã ký ban hành mới vào kho."""
    data = request.get_json(silent=True) or {}
    success, message, created_item, status_code = create_van_ban_ban_hanh(data, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': created_item
    }), status_code

@kho_van_ban_bp.route('/ban-hanh/<int:van_ban_id>', methods=['PUT'])
@login_required
def cap_nhat_ban_hanh(van_ban_id):
    """Cập nhật văn bản lưu trữ."""
    data = request.get_json(silent=True) or {}
    success, message, updated_item, status_code = update_van_ban_ban_hanh(van_ban_id, data, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': updated_item
    }), status_code

@kho_van_ban_bp.route('/ban-hanh/<int:van_ban_id>', methods=['DELETE'])
@login_required
def xoa_ban_hanh(van_ban_id):
    """Xóa văn bản lưu trữ (quyền Văn thư)."""
    success, message, status_code = delete_van_ban_ban_hanh(van_ban_id, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

# ==============================================================================
# KHO 2: VĂN BẢN MẪU (BIỂU MẪU HÀNH CHÍNH)
# ==============================================================================

@kho_van_ban_bp.route('/bieu-mau', methods=['GET'])
@login_required
def danh_sach_bieu_mau():
    """
    Lấy danh sách biểu mẫu hành chính:
    Params: q, loai_van_ban, linh_vuc, trang_thai, sort_by ('luot_tai' | 'id')
    """
    filters = {
        'q': request.args.get('q'),
        'loai_van_ban': request.args.get('loai_van_ban'),
        'linh_vuc': request.args.get('linh_vuc'),
        'trang_thai': request.args.get('trang_thai'),
        'sort_by': request.args.get('sort_by')
    }
    items = get_van_ban_mau_list(filters)
    return jsonify({
        'thanh_cong': True,
        'du_lieu': items,
        'tong_so': len(items)
    }), 200

@kho_van_ban_bp.route('/bieu-mau/<int:bieu_mau_id>', methods=['GET'])
@login_required
def chi_tiet_bieu_mau(bieu_mau_id):
    """Lấy chi tiết văn bản mẫu kèm cẩm nang hướng dẫn điền."""
    item = get_van_ban_mau_by_id(bieu_mau_id)
    if not item:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Không tìm thấy biểu mẫu yêu cầu.'
        }), 404
    return jsonify({
        'thanh_cong': True,
        'du_lieu': item
    }), 200

@kho_van_ban_bp.route('/bieu-mau', methods=['POST'])
@login_required
def them_bieu_mau():
    """Thêm biểu mẫu hành chính mới vào kho."""
    data = request.get_json(silent=True) or {}
    success, message, created_item, status_code = create_van_ban_mau(data, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': created_item
    }), status_code

@kho_van_ban_bp.route('/bieu-mau/<int:bieu_mau_id>', methods=['PUT'])
@login_required
def cap_nhat_bieu_mau(bieu_mau_id):
    """Cập nhật biểu mẫu hành chính / nâng phiên bản."""
    data = request.get_json(silent=True) or {}
    success, message, updated_item, status_code = update_van_ban_mau(bieu_mau_id, data, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': updated_item
    }), status_code

@kho_van_ban_bp.route('/bieu-mau/<int:bieu_mau_id>/tai-ve', methods=['POST'])
@login_required
def tai_bieu_mau(bieu_mau_id):
    """Cán bộ tải biểu mẫu -> tự động tăng lượt tải."""
    success, message, download_info, status_code = record_download_and_get_link(bieu_mau_id)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': download_info
    }), status_code

@kho_van_ban_bp.route('/bieu-mau/<int:bieu_mau_id>', methods=['DELETE'])
@login_required
def xoa_bieu_mau(bieu_mau_id):
    """Xóa biểu mẫu (quyền Văn thư)."""
    success, message, status_code = delete_van_ban_mau(bieu_mau_id, g.current_user)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code