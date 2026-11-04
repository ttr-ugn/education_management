from flask import Blueprint, request, jsonify, g, Response
from backend.auth.decorators import login_required
from backend.chatbot.services import (
    ask_chatbot,
    get_all_templates,
    get_template_by_id,
    increment_download_count,
    generate_word_document
)
from database.db import get_db

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('', methods=['POST'])
@login_required
def chat():
    """Endpoint chính tiếp nhận câu hỏi của chuyên viên và gợi ý mẫu văn bản."""
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()

    if not message:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Nội dung tin nhắn không được để trống.'
        }), 400

    result = ask_chatbot(message, g.current_user)
    return jsonify(result), 200

@chatbot_bp.route('/kho-mau', methods=['GET'])
@login_required
def danh_sach_kho_mau():
    """Lấy danh sách tất cả mẫu văn bản trong kho lưu trữ (hỗ trợ tìm kiếm, lọc)."""
    keyword = request.args.get('keyword', '').strip()
    loai = request.args.get('loai', '').strip()
    linh_vuc = request.args.get('linh_vuc', '').strip()

    templates = get_all_templates(keyword=keyword, loai=loai, linh_vuc=linh_vuc)

    # Lấy thêm danh sách danh mục để phục vụ bộ lọc trên giao diện
    db = get_db()
    danh_muc_loai = [r['loai_van_ban'] for r in db.execute("SELECT DISTINCT loai_van_ban FROM mau_van_ban ORDER BY loai_van_ban").fetchall()]
    danh_muc_linh_vuc = [r['linh_vuc'] for r in db.execute("SELECT DISTINCT linh_vuc FROM mau_van_ban ORDER BY linh_vuc").fetchall()]

    return jsonify({
        'thanh_cong': True,
        'danh_sach_mau': templates,
        'tong_so': len(templates),
        'bo_loc': {
            'loai_van_ban': danh_muc_loai,
            'linh_vuc': danh_muc_linh_vuc
        }
    }), 200

@chatbot_bp.route('/mau-van-ban/<int:mau_id>', methods=['GET'])
@login_required
def chi_tiet_mau(mau_id):
    """Lấy chi tiết mẫu văn bản bao gồm nội dung HTML chuẩn để xem trước (Preview)."""
    mau = get_template_by_id(mau_id, increment_view=True)
    if not mau:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': f'Không tìm thấy mẫu văn bản có ID {mau_id}.'
        }), 404

    return jsonify({
        'thanh_cong': True,
        'mau': mau
    }), 200

@chatbot_bp.route('/mau-van-ban/<int:mau_id>/tai-ve', methods=['GET'])
@login_required
def tai_ve_mau(mau_id):
    """Xuất file Microsoft Word (.doc) chuẩn A4 để chuyên viên tải về soạn thảo."""
    mau = get_template_by_id(mau_id, increment_view=False)
    if not mau:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Mẫu văn bản không tồn tại.'
        }), 404

    increment_download_count(mau_id)
    word_content = generate_word_document(mau)
    filename = mau.get('ten_tep') or f"{mau.get('ma_mau', 'BM')}_Mau_van_ban.doc"

    # Trả về file định dạng Word HTML tương thích
    return Response(
        word_content,
        mimetype="application/msword; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Cache-Control": "no-cache"
        }
    )

@chatbot_bp.route('/lich-su', methods=['GET'])
@login_required
def lay_lich_su_chat():
    """Lấy 20 câu hỏi gần nhất của người dùng hiện tại."""
    user_id = g.current_user.get('nguoi_dung_id')
    db = get_db()
    rows = db.execute("""
        SELECT tin_nhan_id, cau_hoi, cau_tra_loi, mau_de_xuat_ids, thoi_gian
        FROM lich_su_chat
        WHERE nguoi_dung_id = ?
        ORDER BY tin_nhan_id DESC
        LIMIT 20
    """, (user_id,)).fetchall()

    return jsonify({
        'thanh_cong': True,
        'lich_su': [dict(r) for r in rows]
    }), 200
