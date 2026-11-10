import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MauVanBan, LichSuChat

def trang_chatbot(request):
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

        # Tìm kiếm mẫu văn bản phù hợp theo từ khóa
        matches = []
        if question:
            matches = list(MauVanBan.objects.filter(ten_mau__icontains=question)[:3])
        if not matches:
            matches = list(MauVanBan.objects.all()[:3])

        tra_loi = (
            f"Trợ lý ảo Sở GD&ĐT TP. Đà Nẵng: Tôi đã tìm thấy {len(matches)} mẫu văn bản hành chính "
            f"phù hợp với yêu cầu: \"{question}\". Bạn có thể tải mẫu về hoặc chỉnh sửa trực tiếp."
        )

        return JsonResponse({
            'thanh_cong': True,
            'du_lieu': {
                'cau_tra_loi': tra_loi,
                'tra_loi': tra_loi,
                'mau_de_xuat': [m.to_dict() for m in matches]
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
