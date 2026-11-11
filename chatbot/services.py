"""
Education Management - AI Chatbot & Template Assistant Service Layer (Chatbot)
Chịu trách nhiệm nhận diện ý định (Intent Classification), tìm kiếm mẫu văn bản quy chuẩn, và giải đáp thể thức hành chính.
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from django.db.models import Q

from chatbot.models import MauVanBan, LichSuChat
from authentication.models import NguoiDung
from common.security import sanitize_input_text


class IntentType:
    """Các nhóm ý định của người dùng khi trò chuyện với trợ lý ảo"""
    TIM_MAU = 'TIM_MAU'
    HOI_THE_THUC = 'HOI_THE_THUC'
    HOI_QUY_TRINH = 'HOI_QUY_TRINH'
    HOI_KY_SO = 'HOI_KY_SO'
    SOAN_VAN_BAN = 'SOAN_VAN_BAN'
    CHAO_HOI = 'CHAO_HOI'
    MAC_DINH = 'MAC_DINH'


class ChatbotNLPService:
    """
    Bộ máy nhận diện ngôn ngữ tự nhiên và truy vấn tri thức hành chính giáo dục.
    """

    INTENT_KEYWORDS = {
        IntentType.CHAO_HOI: ['xin chào', 'chào bạn', 'hello', 'hi bot', 'bạn là ai', 'giúp gì'],
        IntentType.TIM_MAU: ['mẫu', 'biểu mẫu', 'tải mẫu', 'quyết định', 'kế hoạch', 'tờ trình', 'thông báo', 'hướng dẫn'],
        IntentType.HOI_THE_THUC: ['thể thức', 'nghị định 30', 'căn lề', 'phông chữ', 'cỡ chữ', 'số ký hiệu', 'tiêu ngữ'],
        IntentType.HOI_QUY_TRINH: ['quy trình', 'trình ký', 'phê duyệt', 'vào sổ', 'ban hành', 'thu hồi', 'luân chuyển'],
        IntentType.HOI_KY_SO: ['chữ ký số', 'ký số', 'con dấu', 'chứng thư', 'văn thư đóng dấu', 'xác thực'],
        IntentType.SOAN_VAN_BAN: ['soạn thảo', 'viết giúp', 'tạo dự thảo', 'khởi tạo văn bản'],
    }

    @classmethod
    def classify_intent(cls, message: str) -> str:
        """
        Phân loại ý định của câu hỏi dựa trên phân tích tập từ khóa hành chính.
        """
        lower_msg = message.lower().strip()

        for intent, keywords in cls.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in lower_msg:
                    return intent

        return IntentType.MAC_DINH

    @classmethod
    def search_templates(cls, query: str, limit: int = 4) -> List[MauVanBan]:
        """
        Tìm kiếm các mẫu văn bản liên quan trong kho mẫu văn bản hành chính của Sở GD&ĐT.
        """
        keywords = [k.strip() for k in query.lower().split() if len(k.strip()) > 2]
        if not keywords:
            return list(MauVanBan.objects.all().order_by('-luot_xem')[:limit])

        q_obj = Q()
        for kw in keywords:
            q_obj |= Q(ten_mau__icontains=kw) | Q(loai_van_ban__icontains=kw) | Q(linh_vuc__icontains=kw)

        matches = MauVanBan.objects.filter(q_obj).order_by('-luot_xem')[:limit]
        if not matches.exists():
            matches = MauVanBan.objects.all().order_by('-luot_xem')[:limit]

        return list(matches)

    @classmethod
    def process_message(
        cls,
        user_message: str,
        user: Optional[NguoiDung] = None
    ) -> Dict[str, Any]:
        """
        Xử lý tin nhắn người dùng, sinh câu trả lời hướng dẫn nghiệp vụ và đề xuất mẫu tài liệu liên quan.
        """
        intent = cls.classify_intent(user_message)
        suggested_templates = []
        answer = ""

        if intent == IntentType.CHAO_HOI:
            user_name = user.ho_va_ten if user else "Đồng chí"
            answer = (
                f"Kính chào {user_name}! Tôi là Trợ lý ảo quản lý văn bản và điều hành của Sở GD&ĐT TP. Đà Nẵng. "
                "Tôi có thể hỗ trợ đồng chí tra cứu mẫu văn bản, hướng dẫn quy chuẩn thể thức theo Nghị định 30/2020/NĐ-CP, "
                "và giải đáp quy trình luân chuyển hồ sơ."
            )

        elif intent == IntentType.TIM_MAU:
            suggested_templates = cls.search_templates(user_message, limit=3)
            templates_str = ", ".join([f"'{m.ten_mau}'" for m in suggested_templates])
            answer = (
                f"Dưới đây là các mẫu văn bản phù hợp nhất với yêu cầu của đồng chí trong kho mẫu chuẩn của Sở: "
                f"{templates_str}. Đồng chí có thể nhấn xem chi tiết hoặc tải xuống để sử dụng ngay."
            )

        elif intent == IntentType.HOI_THE_THUC:
            answer = (
                "Về quy chuẩn thể thức văn bản hành chính theo Nghị định 30/2020/NĐ-CP của Chính phủ:\n"
                "1. Phông chữ: Chuẩn Unicode Times New Roman, cỡ chữ 13 - 14.\n"
                "2. Căn lề khổ A4: Trên 20-25mm, Dưới 20-25mm, Trái 30-35mm, Phải 15-20mm.\n"
                "3. Số ký hiệu: Phải theo quy tắc Số/LoạiVB-TênViếtTắt (Ví dụ: 125/QĐ-SGDĐT).\n"
                "4. Dấu và chữ ký số: Đặt ngay ngắn tại vị trí thẩm quyền ký, không đè lên chữ."
            )

        elif intent == IntentType.HOI_QUY_TRINH:
            answer = (
                "Quy trình luân chuyển văn bản đi tại Sở GD&ĐT gồm 4 bước chính:\n"
                "1. Chuyên viên: Soạn thảo dự thảo và gửi đính kèm tệp văn bản.\n"
                "2. Văn thư Sở: Tiếp nhận và kiểm tra thể thức văn bản, trả lại nếu chưa đạt chuẩn.\n"
                "3. Lãnh đạo Sở: Xem xét nội dung và thực hiện ký số điện tử phê duyệt.\n"
                "4. Văn thư: Cấp số chính thức từ sổ đăng ký, đóng dấu số và ban hành tới các đơn vị nhận."
            )

        elif intent == IntentType.HOI_KY_SO:
            answer = (
                "Hệ thống tích hợp ký số xác thực chuẩn mật mã SHA-256 theo chứng thư số chuyên dùng Chính phủ. "
                "Lãnh đạo Sở có thể trực tiếp ký số trên giao diện 'Phê duyệt văn bản đi', hệ thống sẽ tự động ghim chứng thư "
                "và con dấu điện tử vào đúng tọa độ trang cuối tài liệu."
            )

        else:
            suggested_templates = cls.search_templates(user_message, limit=2)
            answer = (
                "Tôi đã tiếp nhận yêu cầu của đồng chí. Nếu đồng chí cần tìm mẫu văn bản cụ thể hoặc thắc mắc "
                "về quy chế lưu trữ, vui lòng nhập từ khóa như 'mẫu quyết định', 'quy trình ban hành', hoặc 'thể thức'."
            )

        # Lưu lịch sử hội thoại
        template_ids = ",".join([str(t.mau_id) for t in suggested_templates]) if suggested_templates else ""
        LichSuChat.objects.create(
            nguoi_dung=user,
            cau_hoi=sanitize_input_text(user_message),
            cau_tra_loi=answer,
            mau_de_xuat_ids=template_ids
        )

        return {
            'answer': answer,
            'intent': intent,
            'suggested_templates': [t.to_dict() for t in suggested_templates]
        }
