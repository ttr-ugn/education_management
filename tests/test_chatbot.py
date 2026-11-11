"""
Education Management - Unit Tests for AI Chatbot Service (Chatbot)
Kiểm tra bộ phân loại ý định (Intent Classification), tìm kiếm mẫu văn bản và sinh câu trả lời.
"""

from django.test import TestCase

from chatbot.models import MauVanBan, LichSuChat
from chatbot.services import ChatbotNLPService, IntentType


class ChatbotServiceTestCase(TestCase):
    """Kiểm tra trợ lý ảo chatbot"""

    def setUp(self):
        # Tạo 2 mẫu văn bản mẫu
        MauVanBan.objects.create(
            ma_mau="MAU-QD-01",
            ten_mau="Quyết định ban hành quy chế làm việc cơ quan",
            loai_van_ban="Quyết định",
            linh_vuc="Tổ chức cán bộ",
            noi_dung_html="<p>QUYẾT ĐỊNH Ban hành quy chế làm việc...</p>",
            noi_dung_text="QUYẾT ĐỊNH Ban hành quy chế làm việc"
        )
        MauVanBan.objects.create(
            ma_mau="MAU-KH-01",
            ten_mau="Kế hoạch kiểm tra chuyên môn học kỳ 2",
            loai_van_ban="Kế hoạch",
            linh_vuc="Giáo dục Trung học",
            noi_dung_html="<p>KẾ HOẠCH Kiểm tra chuyên môn...</p>",
            noi_dung_text="KẾ HOẠCH Kiểm tra chuyên môn"
        )

    def test_classify_intent(self):
        self.assertEqual(ChatbotNLPService.classify_intent("Xin chào bạn trợ lý ảo"), IntentType.CHAO_HOI)
        self.assertEqual(ChatbotNLPService.classify_intent("Cho tôi xem mẫu quyết định thành lập hội đồng"), IntentType.TIM_MAU)
        self.assertEqual(ChatbotNLPService.classify_intent("Căn lề chuẩn theo nghị định 30 như thế nào?"), IntentType.HOI_THE_THUC)
        self.assertEqual(ChatbotNLPService.classify_intent("Quy trình phê duyệt văn bản đi gồm các bước nào?"), IntentType.HOI_QUY_TRINH)
        self.assertEqual(ChatbotNLPService.classify_intent("Cách thức thực hiện chữ ký số"), IntentType.HOI_KY_SO)

    def test_search_templates(self):
        results = ChatbotNLPService.search_templates("quyết định")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0].loai_van_ban, "Quyết định")

    def test_process_message_with_history(self):
        res = ChatbotNLPService.process_message("Tôi muốn tìm mẫu kế hoạch năm học mới")
        self.assertIn("kế hoạch", res['answer'].lower())
        self.assertEqual(res['intent'], IntentType.TIM_MAU)
        self.assertGreaterEqual(len(res['suggested_templates']), 1)

        # Kiểm tra bản ghi lịch sử chat được lưu trong database
        self.assertEqual(LichSuChat.objects.count(), 1)
