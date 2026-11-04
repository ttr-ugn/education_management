"""
DOCUMENT MODEL - THỰC THỂ QUẢN LÝ VĂN BẢN ĐI (MVC ARCHITECTURE)
Bảng CSDL: van_ban_di, lich_su_xu_ly_van_ban
"""

from .base_model import BaseModel

class DocumentModel(BaseModel):
    """Model quản lý văn bản đi và vòng đời xử lý 5 bước."""

    @classmethod
    def get_by_id(cls, doc_id: int):
        cur = cls.db().execute('''
            SELECT v.*, u.ho_va_ten AS nguoi_soan_thao, u.phong_ban AS phong_ban_soan
            FROM van_ban_di v
            JOIN nguoi_dung u ON v.nguoi_soan_id = u.nguoi_dung_id
            WHERE v.van_ban_id = ?
        ''', (doc_id,))
        return cls.dict_from_row(cur.fetchone())

    @classmethod
    def get_all(cls, filters: dict = None):
        filters = filters or {}
        query = '''
            SELECT v.*, u.ho_va_ten AS nguoi_soan_thao, u.phong_ban AS phong_ban_soan
            FROM van_ban_di v
            JOIN nguoi_dung u ON v.nguoi_soan_id = u.nguoi_dung_id
            WHERE 1=1
        '''
        params = []
        if filters.get('trang_thai'):
            query += ' AND v.trang_thai = ?'
            params.append(filters['trang_thai'])
        if filters.get('nguoi_soan_id'):
            query += ' AND v.nguoi_soan_id = ?'
            params.append(int(filters['nguoi_soan_id']))
        if filters.get('lanh_dao_ky_id'):
            query += ' AND v.lanh_dao_ky_id = ?'
            params.append(int(filters['lanh_dao_ky_id']))
        if filters.get('ho_so_id'):
            query += ' AND v.ho_so_id = ?'
            params.append(int(filters['ho_so_id']))
        query += ' ORDER BY v.van_ban_id DESC'
        cur = cls.db().execute(query, params)
        return cls.list_from_rows(cur.fetchall())

    @classmethod
    def get_history(cls, doc_id: int):
        cur = cls.db().execute('''
            SELECT h.*, u.ho_va_ten, u.chuc_vu
            FROM lich_su_xu_ly_van_ban h
            JOIN nguoi_dung u ON h.nguoi_thuc_hien_id = u.nguoi_dung_id
            WHERE h.van_ban_id = ?
            ORDER BY h.id ASC
        ''', (doc_id,))
        return cls.list_from_rows(cur.fetchall())
