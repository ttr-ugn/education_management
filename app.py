import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request, redirect

# Đảm bảo mã hóa console trên Windows không bị lỗi ký tự tiếng Việt
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config
from database import db

# ==============================================================================
# IMPORT 8 CONTROLLER BLUEPRINTS THEO MÔ HÌNH MVC (MODEL - VIEW - CONTROLLER)
# ==============================================================================
from controllers.auth_controller import auth_bp
from controllers.users_controller import users_bp
from controllers.documents_controller import documents_bp
from controllers.ho_so_controller import ho_so_bp
from controllers.kho_van_ban_controller import kho_van_ban_bp
from controllers.thong_bao_controller import thong_bao_bp
from controllers.cong_viec_controller import cong_viec_bp
from controllers.chatbot_controller import chatbot_bp

def create_app():
    """Khởi tạo và cấu hình ứng dụng Flask (MVC Architecture)."""
    base_dir = Path(__file__).resolve().parent
    frontend_dir = str(base_dir / 'frontend')

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path=''
    )
    app.config.from_object(Config)

    # Đăng ký đóng kết nối CSDL theo chu kỳ request
    db.init_app(app)

    # Đăng ký các Controller Blueprints (API Endpoints)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(documents_bp, url_prefix='/api/van-ban-di')
    app.register_blueprint(ho_so_bp, url_prefix='/api/ho-so')
    app.register_blueprint(kho_van_ban_bp, url_prefix='/api/kho-van-ban')
    app.register_blueprint(thong_bao_bp, url_prefix='/api/thong-bao')
    app.register_blueprint(cong_viec_bp, url_prefix='/api/cong-viec')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')

    # Định tuyến trang chủ -> phục vụ frontend/index.html (Views)
    @app.route('/')
    def index():
        return send_from_directory(frontend_dir, 'index.html')

    # Xử lý các đường dẫn tĩnh nếu truy cập trực tiếp
    @app.route('/<path:filename>')
    def serve_frontend_files(filename):
        file_path = Path(frontend_dir) / filename
        if file_path.is_file():
            return send_from_directory(frontend_dir, filename)
        # Nếu là request API mà không khớp route -> trả JSON 404
        if filename.startswith('api/'):
            return jsonify({
                'thanh_cong': False,
                'thong_bao': f"API endpoint '/{filename}' không tồn tại."
            }), 404
        # Mặc định trả về trang chủ index.html để FE tự điều hướng
        return send_from_directory(frontend_dir, 'index.html')

    # Bắt lỗi toàn cục cho API
    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith('/api/'):
            return jsonify({
                'thanh_cong': False,
                'thong_bao': 'Tài nguyên API yêu cầu không tồn tại.'
            }), 404
        return send_from_directory(frontend_dir, 'index.html'), 404

    @app.errorhandler(500)
    def handle_500(e):
        if request.path.startswith('/api/'):
            return jsonify({
                'thanh_cong': False,
                'thong_bao': 'Lỗi máy chủ nội bộ. Vui lòng kiểm tra log hệ thống.'
            }), 500
        return "Lỗi máy chủ nội bộ", 500

    return app

app = create_app()

if __name__ == '__main__':
    print("=" * 70)
    print("HỆ THỐNG QUẢN LÝ VĂN BẢN ĐIỀU HÀNH - SỞ GD&ĐT TP. ĐÀ NẴNG (MVC)")
    print("Server đang khởi động tại: http://localhost:5000")
    print("Tài khoản Văn thư mặc định: admin_vanthu / Admin@123")
    print("Tài khoản Lãnh đạo mẫu:     giamdoc_so   / GiamDoc@123")
    print("Tài khoản Chuyên viên mẫu:  minhcv       / ChuyenVien@123")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=True)
