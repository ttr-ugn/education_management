"""
CONTROLLERS/DOCUMENTS_CONTROLLER.PY - MVC ARCHITECTURE (CONTROLLER LAYER)
"""

import os
import mammoth
from flask import Blueprint, request, jsonify, g, send_file, Response
from controllers.decorators import login_required, role_required
from database.db import get_db
from models.document_model import (
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

def _render_a4_html_preview(doc, file_name, content_html):
    so_ky_hieu = doc['so_ky_hieu'] if (doc and doc['so_ky_hieu']) else 'Dự thảo'
    trich_yeu = doc['trich_yeu'] if (doc and doc['trich_yeu']) else 'Văn bản dự thảo'
    loai_van_ban = (doc['loai_van_ban'] if (doc and doc['loai_van_ban']) else 'CÔNG VĂN').upper()
    don_vi = (doc['don_vi_soan_thao'] if (doc and doc['don_vi_soan_thao']) else 'VĂN PHÒNG SỞ').upper()
    noi_nhan = (doc['noi_nhan'] if (doc and doc['noi_nhan']) else 'Như trên, Lưu VT')
    lanh_dao = (doc['lanh_dao_ky_ten'] if (doc and doc['lanh_dao_ky_ten']) else 'Lãnh đạo Sở')
    ngay_tao = doc['ngay_tao'] if (doc and doc['ngay_tao']) else ''

    ngay_str = "ngày ... tháng ... năm 2026"
    if ngay_tao:
        try:
            parts = str(ngay_tao).split(' ')[0].split('-')
            if len(parts) == 3:
                ngay_str = f"ngày {int(parts[2])} tháng {int(parts[1])} năm {parts[0]}"
        except Exception:
            pass

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Xem trước: {file_name}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 0;
      background: #525659;
      font-family: 'Times New Roman', Times, serif;
      color: #000;
      -webkit-print-color-adjust: exact;
    }}
    .toolbar {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: #1e293b;
      color: #fff;
      padding: 10px 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 13.5px;
    }}
    .toolbar-title {{
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 8px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .toolbar-actions {{
      display: flex;
      gap: 8px;
      flex-shrink: 0;
    }}
    .toolbar-btn {{
      background: #334155;
      color: #f8fafc;
      border: 1px solid #475569;
      border-radius: 4px;
      padding: 6px 14px;
      cursor: pointer;
      text-decoration: none;
      font-size: 12.5px;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: background 0.15s ease;
    }}
    .toolbar-btn:hover {{
      background: #475569;
      color: #ffffff;
    }}
    .toolbar-btn.btn-primary {{
      background: #0284c7;
      border-color: #0369a1;
    }}
    .toolbar-btn.btn-primary:hover {{
      background: #0369a1;
    }}
    .page-container {{
      padding: 24px 12px 60px 12px;
      display: flex;
      justify-content: center;
    }}
    .a4-page {{
      background: #ffffff;
      width: 210mm;
      min-height: 297mm;
      padding: 22mm 20mm 25mm 25mm;
      box-shadow: 0 6px 20px rgba(0,0,0,0.35);
      position: relative;
      font-size: 14pt;
      line-height: 1.5;
    }}
    .header-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 22px;
    }}
    .header-table td {{
      vertical-align: top;
      text-align: center;
      padding: 0 4px;
    }}
    .left-header {{
      width: 45%;
      font-size: 12.5pt;
    }}
    .right-header {{
      width: 55%;
      font-size: 12.5pt;
    }}
    .doc-unit {{
      font-size: 12pt;
      font-weight: bold;
      text-transform: uppercase;
    }}
    .doc-sub {{
      font-size: 12pt;
      font-weight: bold;
      text-transform: uppercase;
      border-bottom: 1px solid #000;
      display: inline-block;
      padding-bottom: 2px;
      margin-bottom: 4px;
    }}
    .doc-code {{
      font-size: 12pt;
      margin-top: 4px;
    }}
    .nation-name {{
      font-weight: bold;
      font-size: 12.5pt;
      text-transform: uppercase;
    }}
    .motto {{
      font-weight: bold;
      font-size: 13pt;
      border-bottom: 1.5px solid #000;
      display: inline-block;
      padding-bottom: 2px;
      margin-bottom: 4px;
    }}
    .doc-date {{
      font-style: italic;
      font-size: 13pt;
      margin-top: 4px;
    }}
    .doc-title-block {{
      text-align: center;
      margin: 18px 0 22px 0;
    }}
    .doc-title {{
      font-size: 15pt;
      font-weight: bold;
      text-transform: uppercase;
      margin: 0 0 6px 0;
    }}
    .doc-subject {{
      font-size: 13.5pt;
      font-weight: bold;
      font-style: italic;
    }}
    .doc-content {{
      text-align: justify;
      font-size: 14pt;
    }}
    .doc-content p {{
      margin: 0 0 10px 0;
      text-indent: 1.27cm;
    }}
    .doc-content h1, .doc-content h2, .doc-content h3 {{
      font-weight: bold;
      margin: 14px 0 6px 0;
    }}
    .doc-content table {{
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0;
    }}
    .doc-content table, .doc-content th, .doc-content td {{
      border: 1px solid #000;
      padding: 6px 10px;
    }}
    .footer-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 36px;
      page-break-inside: avoid;
    }}
    .footer-table td {{
      vertical-align: top;
    }}
    .recipients-block {{
      width: 50%;
      font-size: 11pt;
      line-height: 1.35;
    }}
    .recipients-block b {{
      font-style: italic;
    }}
    .signer-block {{
      width: 50%;
      text-align: center;
      font-size: 13pt;
    }}
    .signer-role {{
      font-weight: bold;
      text-transform: uppercase;
      margin-bottom: 50px;
    }}
    .signer-name {{
      font-weight: bold;
    }}
    @media print {{
      body {{ background: #fff; }}
      .toolbar {{ display: none; }}
      .page-container {{ padding: 0; }}
      .a4-page {{
        box-shadow: none;
        width: 100%;
        min-height: auto;
        padding: 0;
      }}
    }}
    @media (max-width: 800px) {{
      .a4-page {{
        width: 100%;
        padding: 15px;
        min-height: auto;
      }}
    }}
  </style>
</head>
<body>
  <div class="toolbar">
    <div class="toolbar-title">
      <span>📄 <b>{file_name}</b> &mdash; {trich_yeu}</span>
    </div>
    <div class="toolbar-actions">
      <button class="toolbar-btn" onclick="window.print()">🖨 In</button>
      <a class="toolbar-btn btn-primary" href="/api/van-ban-di/{doc['van_ban_id'] if doc else 0}/download?type=goc" download="{file_name}">📥 Tải về máy</a>
    </div>
  </div>
  <div class="page-container">
    <div class="a4-page">
      <table class="header-table">
        <tr>
          <td class="left-header">
            <div class="doc-unit">SỞ GIÁO DỤC VÀ ĐÀO TẠO</div>
            <div class="doc-sub">{don_vi}</div>
            <div class="doc-code">Số: <b>{so_ky_hieu}</b></div>
          </td>
          <td class="right-header">
            <div class="nation-name">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
            <div class="motto">Độc lập - Tự do - Hạnh phúc</div>
            <div class="doc-date">Đà Nẵng, {ngay_str}</div>
          </td>
        </tr>
      </table>

      <div class="doc-title-block">
        <h2 class="doc-title">{loai_van_ban}</h2>
        <div class="doc-subject">V/v: {trich_yeu}</div>
      </div>

      <div class="doc-content">
        {content_html}
      </div>

      <table class="footer-table">
        <tr>
          <td class="recipients-block">
            <b>Nơi nhận:</b><br>
            - {noi_nhan};<br>
            - Ban Giám đốc Sở;<br>
            - Lưu: VT, {don_vi}.
          </td>
          <td class="signer-block">
            <div class="signer-role">QUYỀN HẠN, CHỨC VỤ NGƯỜI KÝ</div>
            <div class="signer-name">{lanh_dao}</div>
          </td>
        </tr>
      </table>
    </div>
  </div>
</body>
</html>"""

@documents_bp.route('/<int:doc_id>/preview', methods=['GET'])
@login_required
def preview_file(doc_id):
    """
    Xem trước tệp văn bản đi (PDF dạng inline, DOCX/DOC chuyển sang A4 HTML) trực tiếp trong trình duyệt mà không cần tải về.
    """
    file_type = request.args.get('type', 'goc')
    success, message, file_path, file_name, status_code = get_file_for_download(doc_id, file_type)

    if not success:
        return jsonify({
            'thanh_cong': False,
            'thong_bao': message
        }), status_code

    if not file_path or not os.path.exists(file_path):
        return jsonify({
            'thanh_cong': False,
            'thong_bao': 'Tệp không tồn tại trên hệ thống máy chủ.'
        }), 404

    ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''

    # 1. Nếu là PDF: Trả về PDF dạng inline để trình duyệt render trực tiếp
    if ext == 'pdf':
        response = send_file(
            file_path,
            as_attachment=False,
            mimetype='application/pdf',
            download_name=file_name
        )
        response.headers['Content-Disposition'] = f'inline; filename="{file_name}"'
        return response

    # 2. Nếu là file hình ảnh:
    if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
        response = send_file(
            file_path,
            as_attachment=False,
            mimetype=f'image/{ext if ext != "jpg" else "jpeg"}',
            download_name=file_name
        )
        response.headers['Content-Disposition'] = f'inline; filename="{file_name}"'
        return response

    # 3. Lấy thông tin văn bản từ database
    db = get_db()
    doc = db.execute('''
        SELECT van_ban_id, so_ky_hieu, trich_yeu, loai_van_ban, do_khan,
               don_vi_soan_thao, noi_nhan, noi_dung_tom_tat,
               file_goc_path, file_goc_ten, file_da_ky_path, file_da_ky_ten,
               lanh_dao_ky_ten, trang_thai, ngay_tao
        FROM van_ban_di
        WHERE van_ban_id = ?
    ''', (doc_id,)).fetchone()

    # 4. Trích xuất DOCX hoặc text sang HTML
    content_html = ""
    if ext in ('docx', 'doc'):
        try:
            with open(file_path, 'rb') as docx_file:
                mammoth_res = mammoth.convert_to_html(docx_file)
                content_html = mammoth_res.value
        except Exception:
            # Fallback nếu tệp docx là file plain-text giả lập hoặc định dạng khác
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as txt_file:
                    raw_text = txt_file.read()
                    paras = [line.strip() for line in raw_text.splitlines() if line.strip()]
                    content_html = ''.join(f'<p>{p}</p>' for p in paras)
            except Exception as e:
                content_html = f'<p><em>Không thể phân tích nội dung tệp: {str(e)}</em></p>'
    elif ext in ('txt', 'log'):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as txt_file:
                raw_text = txt_file.read()
                paras = [line.strip() for line in raw_text.splitlines() if line.strip()]
                content_html = ''.join(f'<p>{p}</p>' for p in paras)
        except Exception as e:
            content_html = f'<p><em>Không thể đọc tệp văn bản: {str(e)}</em></p>'
    else:
        content_html = f'<p><em>Định dạng .{ext} không hỗ trợ hiển thị trực tiếp. Vui lòng tải về máy để xem.</em></p>'

    html_page = _render_a4_html_preview(doc, file_name, content_html)
    return Response(html_page, content_type='text/html; charset=utf-8', status=200)
