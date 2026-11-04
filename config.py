import os
from pathlib import Path
from dotenv import load_dotenv

# Nạp file .env từ thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    """Cấu hình ứng dụng Flask quản lý văn bản điều hành."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key-sgd-danang-2026')
    
    # Đường dẫn file SQLite DB
    DB_REL_PATH = os.getenv('DATABASE_PATH', 'database/qlvb.db')
    DATABASE_PATH = str((BASE_DIR / DB_REL_PATH).resolve())
    
    # Mã xác nhận nội bộ dùng để đăng ký tài khoản Văn thư
    INTERNAL_CODE = os.getenv('INTERNAL_CODE', 'DANANG_SGD_VT2026')
    
    # Thông tin tài khoản Văn thư mặc định (dùng khi chạy init_db.py)
    DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin_vanthu')
    DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'Admin@123')
    DEFAULT_ADMIN_NAME = os.getenv('DEFAULT_ADMIN_NAME', 'Văn thư Sở GD&ĐT Đà Nẵng')
    DEFAULT_ADMIN_EMAIL = os.getenv('DEFAULT_ADMIN_EMAIL', 'vanthu@danang.edu.vn')
    
    # Cấu hình bảo mật Session Cookie
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Đổi True nếu chạy trên HTTPS production
    PERMANENT_SESSION_LIFETIME = 86400  # 24 giờ

    # Cấu hình lưu trữ tài liệu tải lên
    UPLOAD_FOLDER = str((BASE_DIR / 'uploads' / 'documents').resolve())
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
