import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MauVanBan, LichSuChat

def trang_chatbot(request):
    return render(request, 'chatbot/chatbot.html')

@csrf_exempt
def api_hoi_dap(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        question = data.get('cau_hoi', '')

        # Tìm kiếm mẫu văn bản phù hợp theo từ khóa
        matches = MauVanBan.objects.filter(ten_mau__icontains=question)[:3]
        if not matches:
            matches = MauVanBan.objects.all()[:3]

        tra_loi = f"Trợ lý ảo Sở GD&ĐT Đà Nẵng: Tôi đã tìm thấy {len(matches)} mẫu văn bản liên quan đến yêu cầu '{question}' của bạn."
        return JsonResponse({
            'thanh_cong': True,
            'du_lieu': {
                'cau_tra_loi': tra_loi,
                'mau_de_xuat': [m.to_dict() for m in matches]
            }
        })
    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Yêu cầu không hợp lệ'}, status=400)
