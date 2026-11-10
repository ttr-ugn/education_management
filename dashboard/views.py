from django.shortcuts import render
from django.http import JsonResponse

def trang_chu(request):
    """Trang chủ ứng dụng SPA / chuyển hướng."""
    return render(request, 'index.html')

def trang_dashboard(request):
    """Trang tổng quan Dashboard."""
    return render(request, 'dashboard/dashboard.html')

def trang_thong_ke(request):
    """Trang báo cáo thống kê."""
    return render(request, 'dashboard/thong-ke.html')
