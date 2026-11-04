"""
BASE MODEL - LỚP CƠ SỞ CHO CÁC THỰC THỂ DỮ LIỆU (MVC ARCHITECTURE)
Cung cấp các tiện ích kết nối CSDL SQLite và chuyển đổi dữ liệu.
"""

from database.db import get_db

class BaseModel:
    """Lớp Model cơ sở chứa các phương thức dùng chung."""
    
    @staticmethod
    def db():
        """Lấy kết nối SQLite trong ngữ cảnh request hiện tại."""
        return get_db()
    
    @classmethod
    def dict_from_row(cls, row):
        """Chuyển đổi sqlite3.Row sang dictionary."""
        if row is None:
            return None
        return dict(row)
    
    @classmethod
    def list_from_rows(cls, rows):
        """Chuyển đổi danh sách sqlite3.Row sang danh sách dictionaries."""
        if not rows:
            return []
        return [dict(r) for r in rows]
