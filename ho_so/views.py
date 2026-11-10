from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import HoSoLuuTru, VanBanBanHanh

def danh_sach_ho_so(request):
    return render(request, 'ho_so/danh-sach.html')

def chi_tiet_ho_so(request):
    return render(request, 'ho_so/chi-tiet.html')

def them_sua_ho_so(request):
    return render(request, 'ho_so/them-sua.html')

@csrf_exempt
def api_ho_so_list(request):
    qs = HoSoLuuTru.objects.all().order_by('-ngay_tao')
    return JsonResponse({'thanh_cong': True, 'du_lieu': [hs.to_dict() for hs in qs]})
