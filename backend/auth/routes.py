from flask import Blueprint, request, jsonify, session, g
from .services import register_user, authenticate_user, change_user_password
from .decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/dang-ky', methods=['POST'])
def dang_ky():
    """Đăng ký tài khoản người dùng mới (Chuyên viên hoặc Văn thư)."""
    data = request.get_json(silent=True) or {}
    success, message, status_code = register_user(data)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@auth_bp.route('/dang-nhap', methods=['POST'])
def dang_nhap():
    """Xác thực đăng nhập và thiết lập session."""
    data = request.get_json(silent=True) or {}
    ten_dang_nhap = data.get('ten_dang_nhap')
    mat_khau = data.get('mat_khau')

    success, message, user_info, status_code = authenticate_user(ten_dang_nhap, mat_khau)
    if not success:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': message
        }), status_code

    # Lưu session người dùng
    session.clear()
    session['user_id'] = user_info['nguoi_dung_id']
    session.permanent = True

    return jsonify({
        'thanh_cong': True,
        'thong_bao': message,
        'du_lieu': user_info
    }), 200

@auth_bp.route('/dang-xuat', methods=['POST'])
def dang_xuat():
    """Xóa session đăng nhập."""
    session.clear()
    return jsonify({
        'thanh_cong': True,
        'thong_bao': 'Đăng xuất thành công.'
    }), 200

@auth_bp.route('/toi', methods=['GET'])
@login_required
def toi():
    """Lấy thông tin người dùng hiện tại đang đăng nhập."""
    # g.current_user đã được nạp bởi decorator login_required
    return jsonify({
        'thanh_cong': True,
        'du_lieu': g.current_user
    }), 200

@auth_bp.route('/doi-mat-khau', methods=['POST'])
@login_required
def doi_mat_khau():
    """Đổi mật khẩu tài khoản hiện tại."""
    data = request.get_json(silent=True) or {}
    mat_khau_cu = data.get('mat_khau_cu')
    mat_khau_moi = data.get('mat_khau_moi')

    success, message, status_code = change_user_password(
        g.current_user['nguoi_dung_id'],
        mat_khau_cu,
        mat_khau_moi
    )
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code
