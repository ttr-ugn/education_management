from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CongViec

def danh_sach_cong_viec(request):
    return render(request, 'cong_viec/danh-sach.html')

def giao_viec(request):
    return render(request, 'cong_viec/giao-viec.html')

def xu_ly_cong_viec(request):
    return render(request, 'cong_viec/xu-ly.html')

def phe_duyet_ket_qua(request):
    return render(request, 'cong_viec/phe-duyet-ket-qua.html')

@csrf_exempt
def api_cong_viec_list(request):
    qs = CongViec.objects.all().order_by('-ngay_tao')
    return JsonResponse({'thanh_cong': True, 'du_lieu': [cv.to_dict() for cv in qs]})
