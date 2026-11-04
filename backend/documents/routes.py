import os
from flask import Blueprint, request, jsonify, g, send_file
from backend.auth.decorators import login_required, role_required
from .services import (
    create_document,
    get_documents_list,
    get_document_detail,
    clerk_edit_document,
    clerk_reject_document,
    clerk_forward_to_leader,
    leader_reject_document,
    leader_sign_document,
    clerk_publish_document,
    get_file_for_download
)

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('', methods=['GET'])
@login_required
def list_documents():
    """Lấy danh sách văn bản đi theo phân quyền và bộ lọc."""
    filters = {
        'q': request.args.get('q', ''),
        'trang_thai': request.args.get('trang_thai', ''),
        'do_khan': request.args.get('do_khan', ''),
        'loai_van_ban': request.args.get('loai_van_ban', '')
    }
    docs = get_documents_list(g.current_user, filters)
    return jsonify({
        'thanh_cong': True,
        'du_lieu': docs,
        'tong_so': len(docs)
    }), 200

@documents_bp.route('/<int:doc_id>', methods=['GET'])
@login_required
def get_document(doc_id):
    """Lấy thông tin chi tiết một văn bản đi kèm lịch sử xử lý."""
    success, message, data, status_code = get_document_detail(g.current_user, doc_id)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': data
    }), status_code

@documents_bp.route('', methods=['POST'])
@login_required
@role_required('CHUYEN_VIEN', 'VAN_THU')
def create():
    """
    Bước 1: Chuyên viên (hoặc Văn thư) khởi tạo dự thảo văn bản đi mới.
    Nhận Multipart/Form-data kèm tệp đính kèm (.pdf, .doc, .docx).
    """
    uploaded_file = request.files.get('tep_dinh_kem')
    form_data = request.form.to_dict()

    success, message, data, status_code = create_document(g.current_user, form_data, uploaded_file)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': data
    }), status_code

@documents_bp.route('/<int:doc_id>', methods=['PUT'])
@login_required
@role_required('VAN_THU')
def edit_document(doc_id):
    """
    Bước 2a: Văn thư kiểm tra và chỉnh sửa thể thức văn bản.
    """
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    success, message, status_code = clerk_edit_document(g.current_user, doc_id, data)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@documents_bp.route('/<int:doc_id>/van-thu-tra-lai', methods=['POST'])
@documents_bp.route('/<int:doc_id>/tu-choi', methods=['POST'])
@login_required
def reject(doc_id):
    """
    Văn thư (hoặc Lãnh đạo) trả lại văn bản yêu cầu Chuyên viên chỉnh sửa.
    """
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ly_do = data.get('ly_do') or data.get('ly_do_chinh_sua') or data.get('reason') or ''
    role = g.current_user.get('vai_tro')

    if role == 'VAN_THU':
        success, message, status_code = clerk_reject_document(g.current_user, doc_id, ly_do)
    elif role == 'LANH_DAO':
        success, message, status_code = leader_reject_document(g.current_user, doc_id, ly_do)
    else:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Bạn không có quyền thực hiện thao tác trả lại văn bản.'
        }), 403

    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@documents_bp.route('/<int:doc_id>/trinh-lanh-dao', methods=['POST'])
@login_required
@role_required('VAN_THU')
def forward_to_leader(doc_id):
    """
    Bước 2b: Văn thư kiểm tra hợp lệ -> Cập nhật trạng thái gửi lên Lãnh đạo ký.
    """
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ghi_chu = data.get('ghi_chu', '')
    success, message, status_code = clerk_forward_to_leader(g.current_user, doc_id, ghi_chu)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message
    }), status_code

@documents_bp.route('/<int:doc_id>/ky-so', methods=['POST'])
@documents_bp.route('/<int:doc_id>/phe-duyet', methods=['POST'])
@login_required
@role_required('LANH_DAO')
def sign_document(doc_id):
    """
    Bước 3: Lãnh đạo gán chữ ký số bằng click chuột vào văn bản.
    Nhận tọa độ click: page, x, y (hoặc % tọa độ).
    """
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    success, message, result_data, status_code = leader_sign_document(g.current_user, doc_id, data)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': result_data
    }), status_code

@documents_bp.route('/<int:doc_id>/ban-hanh', methods=['POST'])
@login_required
@role_required('VAN_THU')
def publish_document(doc_id):
    """
    Bước 4: Văn thư kiểm tra file đã ký, cấp số hiệu chính thức và Ban hành.
    """
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    success, message, result_data, status_code = clerk_publish_document(g.current_user, doc_id, data)
    return jsonify({
        'thanh_cong': success,
        'thong_bao': message,
        'du_lieu': result_data
    }), status_code

@documents_bp.route('/<int:doc_id>/download', methods=['GET'])
@login_required
def download(doc_id):
    """
    Bước 5: Tải về file gốc hoặc file đã ký số của văn bản.
    """
    file_type = request.args.get('type', 'goc')
    success, message, file_path, file_name, status_code = get_file_for_download(doc_id, file_type)

    if not success:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': message
        }), status_code

    return send_file(
        file_path,
        as_attachment=True,
        download_name=file_name
    )

@documents_bp.route('/<int:doc_id>/preview', methods=['GET'])
@login_required
def preview_file(doc_id):
    """
    Xem trước tệp PDF trực tiếp trong trình duyệt để phục vụ thao tác click chuột ký số.
    """
    file_type = request.args.get('type', 'goc')
    success, message, file_path, file_name, status_code = get_file_for_download(doc_id, file_type)

    if not success:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': message
        }), status_code

    # Trả về dạng inline để viewer đọc
    ext = file_path.rsplit('.', 1)[-1].lower()
    mimetype = 'application/pdf' if ext == 'pdf' else 'application/octet-stream'

    return send_file(
        file_path,
        as_attachment=False,
        mimetype=mimetype,
        download_name=file_name
    )
