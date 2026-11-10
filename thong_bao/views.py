from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ThongBao

def trang_thong_bao(request):
    return render(request, 'thong_bao/thong-bao.html')

@csrf_exempt
def api_thong_bao_list(request):
    qs = ThongBao.objects.all().order_by('-ngay_tao')
    return JsonResponse({'thanh_cong': True, 'du_lieu': [tb.to_dict() for tb in qs]})
