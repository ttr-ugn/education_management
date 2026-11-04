"""
CHATBOT MODEL - THỰC THỂ TRỢ LÝ ẢO & MẪU VĂN BẢN (MVC ARCHITECTURE)
Bảng CSDL: lich_su_chat, mau_van_ban
"""

from .base_model import BaseModel

class ChatbotModel(BaseModel):
    """Model quản lý mẫu văn bản hành chính và lịch sử hỏi đáp trợ lý ảo."""

    @classmethod
    def get_all_templates(cls):
        cur = cls.db().execute('SELECT * FROM mau_van_ban ORDER BY luot_tai DESC')
        return cls.list_from_rows(cur.fetchall())

    @classmethod
    def get_template_by_id(cls, mau_id: int):
        cur = cls.db().execute('SELECT * FROM mau_van_ban WHERE mau_id = ?', (mau_id,))
        return cls.dict_from_row(cur.fetchone())

    @classmethod
    def get_chat_history(cls, user_id: int):
        cur = cls.db().execute('''
            SELECT * FROM lich_su_chat
            WHERE nguoi_dung_id = ?
            ORDER BY thoi_gian ASC
        ''', (user_id,))
        return cls.list_from_rows(cur.fetchall())
