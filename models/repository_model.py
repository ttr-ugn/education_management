"""
REPOSITORY MODEL - THỰC THỂ KHO LƯU TRỮ VĂN BẢN SỐ HÓA (MVC ARCHITECTURE)
Bảng CSDL: van_ban_ban_hanh, van_ban_mau
"""

from .base_model import BaseModel

class RepositoryModel(BaseModel):
    """Model quản lý kho văn bản đã ban hành và biểu mẫu số hóa."""

    @classmethod
    def get_published_by_id(cls, van_ban_id: int):
        cur = cls.db().execute('SELECT * FROM van_ban_ban_hanh WHERE van_ban_id = ?', (van_ban_id,))
        return cls.dict_from_row(cur.fetchone())

    @classmethod
    def get_published_all(cls, filters: dict = None):
        filters = filters or {}
        query = 'SELECT * FROM van_ban_ban_hanh WHERE 1=1'
        params = []
        if filters.get('ho_so_id'):
            query += ' AND ho_so_id = ?'
            params.append(int(filters['ho_so_id']))
        if filters.get('nam'):
            query += ' AND nam_luu_tru = ?'
            params.append(int(filters['nam']))
        query += ' ORDER BY ngay_ban_hanh DESC'
        cur = cls.db().execute(query, params)
        return cls.list_from_rows(cur.fetchall())
