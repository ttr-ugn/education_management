"""
TASK MODEL - THỰC THỂ GIAO VIỆC & THEO DÕI TIẾN ĐỘ (MVC ARCHITECTURE)
Bảng CSDL: cong_viec, nhat_ky_cong_viec
"""

from .base_model import BaseModel

class TaskModel(BaseModel):
    """Model quản lý nhiệm vụ điều hành và nhật ký tiến độ xử lý."""

    @classmethod
    def get_by_id(cls, task_id: int):
        cur = cls.db().execute('SELECT * FROM cong_viec WHERE cong_viec_id = ?', (task_id,))
        return cls.dict_from_row(cur.fetchone())

    @classmethod
    def get_all(cls, filters: dict = None):
        filters = filters or {}
        query = 'SELECT * FROM cong_viec WHERE 1=1'
        params = []
        if filters.get('trang_thai'):
            query += ' AND trang_thai = ?'
            params.append(filters['trang_thai'])
        if filters.get('nguoi_xu_ly_id'):
            query += ' AND nguoi_xu_ly_id = ?'
            params.append(int(filters['nguoi_xu_ly_id']))
        query += ' ORDER BY cong_viec_id DESC'
        cur = cls.db().execute(query, params)
        return cls.list_from_rows(cur.fetchall())

    @classmethod
    def get_logs(cls, task_id: int):
        cur = cls.db().execute('''
            SELECT * FROM nhat_ky_cong_viec
            WHERE cong_viec_id = ?
            ORDER BY thoi_gian ASC
        ''', (task_id,))
        return cls.list_from_rows(cur.fetchall())
