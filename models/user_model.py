"""
USER MODEL - THỰC THỂ NGƯỜI DÙNG & TÀI KHOẢN (MVC ARCHITECTURE)
Bảng CSDL: nguoi_dung
"""

from .base_model import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class UserModel(BaseModel):
    """Model quản lý người dùng, tài khoản và phân quyền cán bộ."""

    @classmethod
    def get_by_id(cls, user_id: int):
        cur = cls.db().execute('SELECT * FROM nguoi_dung WHERE nguoi_dung_id = ?', (user_id,))
        return cls.dict_from_row(cur.fetchone())

    @classmethod
    def get_by_username(cls, username: str):
        cur = cls.db().execute('SELECT * FROM nguoi_dung WHERE ten_dang_nhap = ?', (username.strip(),))
        return cls.dict_from_row(cur.fetchone())

    @classmethod
    def get_all(cls, filters: dict = None):
        filters = filters or {}
        query = 'SELECT * FROM nguoi_dung WHERE 1=1'
        params = []
        if filters.get('vai_tro'):
            query += ' AND vai_tro = ?'
            params.append(filters['vai_tro'])
        if filters.get('trang_thai'):
            query += ' AND trang_thai = ?'
            params.append(filters['trang_thai'])
        query += ' ORDER BY nguoi_dung_id DESC'
        cur = cls.db().execute(query, params)
        return cls.list_from_rows(cur.fetchall())

    @classmethod
    def count_pending(cls):
        cur = cls.db().execute("SELECT COUNT(*) FROM nguoi_dung WHERE trang_thai = 'CHO_DUYET'")
        return cur.fetchone()[0]
