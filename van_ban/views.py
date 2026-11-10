import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import VanBanDi, VanBanDen

# Giao diện Văn bản đi
def van_ban_di_danh_sach(request):
    return render(request, 'van_ban/van-ban-di/danh-sach.html')

def van_ban_di_soan_thao(request):
    return render(request, 'van_ban/van-ban-di/soan-thao.html')

def van_ban_di_chi_tiet(request):
    return render(request, 'van_ban/van-ban-di/chi-tiet.html')

def van_ban_di_kiem_tra(request):
    return render(request, 'van_ban/van-ban-di/kiem-tra.html')

def van_ban_di_phe_duyet(request):
    return render(request, 'van_ban/van-ban-di/phe-duyet.html')

def van_ban_di_ban_hanh(request):
    return render(request, 'van_ban/van-ban-di/ban-hanh.html')

# Giao diện Văn bản đến
def van_ban_den_danh_sach(request):
    return render(request, 'van_ban/van-ban-den/danh-sach.html')

def van_ban_den_them(request):
    return render(request, 'van_ban/van-ban-den/them.html')

def van_ban_den_chi_tiet(request):
    return render(request, 'van_ban/van-ban-den/chi-tiet.html')

def van_ban_den_phe_duyet(request):
    return render(request, 'van_ban/van-ban-den/phe-duyet-phan-cong.html')

# API Endpoints
@csrf_exempt
def api_van_ban_di_list(request):
    if request.method == 'GET':
        qs = VanBanDi.objects.all().order_by('-ngay_tao')
        return JsonResponse({'thanh_cong': True, 'du_lieu': [vb.to_dict() for vb in qs]})
    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Lưu văn bản thành công'})
