"""
CONTROLLERS/CONG_VIEC_CONTROLLER.PY - MVC ARCHITECTURE (CONTROLLER LAYER)
"""

from flask import Blueprint, request, jsonify, g

from controllers.decorators import login_required, role_required

from models.task_model import (

    get_tasks_list,

    get_task_by_id,

    create_task,

    update_task_progress,

    evaluate_task,

    delete_task,

    get_task_statistics

)



cong_viec_bp = Blueprint('cong_viec', __name__)



@cong_viec_bp.route('', methods=['GET'])

@login_required

def danh_sach_cong_viec():

    """Lấy danh sách công việc theo bộ lọc và phân quyền."""

    filters = {

        'q': request.args.get('q'),

        'trang_thai': request.args.get('trang_thai'),

        'do_uu_tien': request.args.get('do_uu_tien'),

        'phong_ban': request.args.get('phong_ban'),

        'chuyen_vien_id': request.args.get('chuyen_vien_id'),

        'scope': request.args.get('scope')

    }

    tasks = get_tasks_list(g.current_user, filters)

    return jsonify({

        'thanh_cong': True,

        'du_lieu': tasks,

        'tong_so': len(tasks)

    }), 200



@cong_viec_bp.route('/<int:task_id>', methods=['GET'])

@login_required

def chi_tiet_cong_viec(task_id):

    """Lấy chi tiết một nhiệm vụ kèm thông tin văn bản và nhật ký tiến độ."""

    task = get_task_by_id(task_id, g.current_user)

    if not task:

        return jsonify({

            'thanh_cong': False,

            'thong_bao': 'Không tìm thấy công việc yêu cầu.'

        }), 404

    return jsonify({

        'thanh_cong': True,

        'du_lieu': task

    }), 200



@cong_viec_bp.route('', methods=['POST'])

@role_required('VAN_THU')

def tao_cong_viec():

    """Giao việc mới (Chỉ dành cho Văn thư hoặc Lãnh đạo)."""

    data = request.get_json(silent=True) or {}

    success, message, task_id, status_code = create_task(data, g.current_user)

    return jsonify({

        'thanh_cong': success,

        'thong_bao': message,

        'cong_viec_id': task_id

    }), status_code



@cong_viec_bp.route('/<int:task_id>/tien-do', methods=['PUT', 'POST'])

@login_required

def cap_nhat_tien_do(task_id):

    """Cập nhật tiến độ và báo cáo kết quả thực hiện nhiệm vụ."""

    data = request.get_json(silent=True) or {}

    success, message, status_code = update_task_progress(task_id, data, g.current_user)

    return jsonify({

        'thanh_cong': success,

        'thong_bao': message

    }), status_code



@cong_viec_bp.route('/<int:task_id>/danh-gia', methods=['PUT', 'POST'])

@role_required('VAN_THU')

def danh_gia_nghiem_thu(task_id):

    """Nghiệm thu / Đánh giá kết quả (Chỉ dành cho Văn thư hoặc Lãnh đạo)."""

    data = request.get_json(silent=True) or {}

    success, message, status_code = evaluate_task(task_id, data, g.current_user)

    return jsonify({

        'thanh_cong': success,

        'thong_bao': message

    }), status_code



@cong_viec_bp.route('/<int:task_id>', methods=['DELETE'])

@role_required('VAN_THU')

def xoa_cong_viec(task_id):

    """Xóa công việc (Chỉ dành cho Văn thư hoặc Lãnh đạo)."""

    success, message, status_code = delete_task(task_id, g.current_user)

    return jsonify({

        'thanh_cong': success,

        'thong_bao': message

    }), status_code



@cong_viec_bp.route('/thong-ke', methods=['GET'])

@login_required

def thong_ke_cong_viec():

    """Lấy dữ liệu thống kê khối lượng công việc & cấu hình biểu đồ Chart.js."""

    filters = {

        'scope': request.args.get('scope'),

        'phong_ban': request.args.get('phong_ban')

    }

    stats = get_task_statistics(g.current_user, filters)

    return jsonify({

        'thanh_cong': True,

        'du_lieu': stats

    }), 200

