"""
DOSSIER MODEL - THỰC THỂ HỒ SƠ LƯU TRỮ CƠ QUAN (MVC ARCHITECTURE)
Bảng CSDL: ho_so_luu_tru
"""

from .base_model import BaseModel

class DossierModel(BaseModel):
    """Model quản lý hồ sơ lưu trữ cơ quan và liên kết văn bản."""

    @classmethod
    def get_by_id(cls, ho_so_id: int):
        cur = cls.db().execute('''
            SELECT hs.ho_so_id, hs.ma_ho_so, hs.tieu_de, hs.nguoi_lap_id, hs.nguoi_lap,
                   hs.don_vi, hs.nam_tai_lieu, hs.thoi_han_bao_quan,
                   (
                       (SELECT COUNT(*) FROM van_ban_di v WHERE v.ho_so_id = hs.ho_so_id AND v.trang_thai = 'DA_BAN_HANH') +
                       (SELECT COUNT(*) FROM van_ban_ban_hanh b WHERE b.ho_so_id = hs.ho_so_id)
                   ) AS so_luong_van_ban,
                   hs.tinh_trang, hs.mo_ta, hs.ngay_tao, hs.ngay_cap_nhat
            FROM ho_so_luu_tru hs
            WHERE hs.ho_so_id = ?
        ''', (ho_so_id,))
        return cls.dict_from_row(cur.fetchone())

    @classmethod
    def get_all(cls, filters: dict = None):
        filters = filters or {}
        query = '''
            SELECT hs.ho_so_id, hs.ma_ho_so, hs.tieu_de, hs.nguoi_lap_id, hs.nguoi_lap,
                   hs.don_vi, hs.nam_tai_lieu, hs.thoi_han_bao_quan,
                   (
                       (SELECT COUNT(*) FROM van_ban_di v WHERE v.ho_so_id = hs.ho_so_id AND v.trang_thai = 'DA_BAN_HANH') +
                       (SELECT COUNT(*) FROM van_ban_ban_hanh b WHERE b.ho_so_id = hs.ho_so_id)
                   ) AS so_luong_van_ban,
                   hs.tinh_trang, hs.mo_ta, hs.ngay_tao, hs.ngay_cap_nhat
            FROM ho_so_luu_tru hs
            WHERE 1=1
        '''
        params = []
        if filters.get('tinh_trang'):
            query += ' AND hs.tinh_trang = ?'
            params.append(filters['tinh_trang'])
        if filters.get('nam_tai_lieu'):
            query += ' AND hs.nam_tai_lieu = ?'
            params.append(int(filters['nam_tai_lieu']))
        query += ' ORDER BY hs.ho_so_id DESC'
        cur = cls.db().execute(query, params)
        return cls.list_from_rows(cur.fetchall())
