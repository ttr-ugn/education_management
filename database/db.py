import sqlite3
from flask import g
from config import Config

def get_db():
    """Lấy hoặc khởi tạo kết nối SQLite cho request hiện tại."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            Config.DATABASE_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Cho phép truy cập cột như dictionary: row['ten_cot']
        g.db.row_factory = sqlite3.Row
        # Bắt buộc bật kiểm tra ràng buộc khóa ngoại
        g.db.execute('PRAGMA foreign_keys = ON;')
    return g.db

def close_db(e=None):
    """Đóng kết nối SQLite khi kết thúc request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Đăng ký hook đóng CSDL vào vòng đời của Flask app."""
    app.teardown_appcontext(close_db)
