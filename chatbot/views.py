import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MauVanBan, LichSuChat
from .services import ChatbotNLPService
from authentication.models import NguoiDung


def trang_chatbot(request):
    """Trang giao diện Trợ lý ảo AI tư vấn văn bản điều hành."""
    return render(request, 'chatbot/chatbot.html')


@csrf_exempt
def api_hoi_dap(request):
    """Tiếp nhận câu hỏi từ cán bộ và gợi ý mẫu văn bản theo Nghị định 30/2020/NĐ-CP."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        question = data.get('cau_hoi') or data.get('tin_nhan') or data.get('query') or ''

        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else None

        result = ChatbotNLPService.process_message(question, user=user)

        return JsonResponse({
            'thanh_cong': True,
            'du_lieu': {
                'cau_tra_loi': result['answer'],
                'tra_loi': result['answer'],
                'intent': result['intent'],
                'mau_de_xuat': result['suggested_templates']
            }
        })
    elif request.method == 'GET':
        templates = MauVanBan.objects.all()
        return JsonResponse({
            'thanh_cong': True,
            'du_lieu': [t.to_dict() for t in templates],
            'tong_so': templates.count()
        })

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Yêu cầu không hợp lệ'}, status=400)
