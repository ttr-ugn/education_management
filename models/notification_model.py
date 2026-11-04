"""
NOTIFICATION MODEL - THỰC THỂ THÔNG BÁO & NHẮC NHỞ (MVC ARCHITECTURE)
Bảng CSDL: thong_bao, thong_bao_da_doc
"""

from .base_model import BaseModel
from datetime import datetime

class NotificationModel(BaseModel):
    """Model quản lý thông báo điều hành và nhắc nhở thời gian thực."""

    @classmethod
    def get_unread_count(cls, user_id: int):
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = cls.db().execute('''
            SELECT COUNT(*) AS chua_doc
            FROM thong_bao tb
            LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
            WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
              AND tb_dd.ngay_doc IS NULL
        ''', (user_id, user_id)).fetchone()
        
        row_due = cls.db().execute('''
            SELECT COUNT(*) AS den_han
            FROM thong_bao tb
            LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
            WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
              AND tb.ngay_hen_gio IS NOT NULL
              AND tb.ngay_hen_gio <= ?
              AND tb_dd.ngay_doc IS NULL
        ''', (user_id, user_id, now_str)).fetchone()

        return {
            'chua_doc': row['chua_doc'] if row else 0,
            'den_han': row_due['den_han'] if row_due else 0
        }

    @classmethod
    def get_by_user(cls, user_id: int):
        cur = cls.db().execute('''
            SELECT tb.*,
                   CASE WHEN tb_dd.ngay_doc IS NOT NULL THEN 1 ELSE 0 END AS da_doc
            FROM thong_bao tb
            LEFT JOIN thong_bao_da_doc tb_dd ON tb.thong_bao_id = tb_dd.thong_bao_id AND tb_dd.nguoi_dung_id = ?
            WHERE (tb.nguoi_nhan_id IS NULL OR tb.nguoi_nhan_id = ?)
            ORDER BY tb.ngay_tao DESC
        ''', (user_id, user_id))
        return cls.list_from_rows(cur.fetchall())
