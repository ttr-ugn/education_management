import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import HoSoLuuTru, VanBanBanHanh
from authentication.models import NguoiDung

def danh_sach_ho_so(request):
    return render(request, 'ho_so/danh-sach.html')

def chi_tiet_ho_so(request):
    return render(request, 'ho_so/chi-tiet.html')

def them_sua_ho_so(request):
    return render(request, 'ho_so/them-sua.html')

# ==============================================================================
# API HỒ SƠ LƯU TRỮ
# ==============================================================================

@csrf_exempt
def api_ho_so_list(request):
    """Danh sách hồ sơ lưu trữ hoặc lập mới hồ sơ."""
    if request.method == 'GET':
        q = request.GET.get('q')
        tinh_trang = request.GET.get('tinh_trang')
        nam_tai_lieu = request.GET.get('nam_tai_lieu')
        don_vi = request.GET.get('don_vi')

        qs = HoSoLuuTru.objects.all().order_by('-ngay_tao')
        if q:
            qs = qs.filter(Q(tieu_de__icontains=q) | Q(ma_ho_so__icontains=q))
        if tinh_trang:
            if tinh_trang in ['DA_LUU_TRU', 'DA_NOP_LUU_TRU']:
                qs = qs.filter(Q(tinh_trang='DA_LUU_TRU') | Q(tinh_trang='DA_NOP_LUU_TRU'))
            else:
                qs = qs.filter(tinh_trang=tinh_trang)
        if nam_tai_lieu:
            qs = qs.filter(nam_tai_lieu=nam_tai_lieu)
        if don_vi:
            qs = qs.filter(don_vi__icontains=don_vi)

        return JsonResponse({'thanh_cong': True, 'du_lieu': [hs.to_dict() for hs in qs], 'tong_so': qs.count()})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

        import time
        ma_hs = data.get('ma_ho_so') or f"HS-{int(time.time())}"
        hs = HoSoLuuTru.objects.create(
            ma_ho_so=ma_hs,
            tieu_de=data.get('tieu_de', 'Hồ sơ tài liệu lưu trữ'),
            don_vi=data.get('don_vi', 'Văn phòng Sở GD&ĐT'),
            nam_tai_lieu=int(data.get('nam_tai_lieu', 2026)),
            thoi_han_bao_quan=data.get('thoi_han_bao_quan', '10 năm'),
            mo_ta=data.get('mo_ta', ''),
            nguoi_lap=user,
            tinh_trang='DANG_THU_THAP'
        )
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Lập hồ sơ lưu trữ mới thành công!', 'du_lieu': hs.to_dict()})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_ho_so_detail(request, ho_so_id):
    """Chi tiết, cập nhật hoặc xóa hồ sơ."""
    try:
        hs = HoSoLuuTru.objects.get(pk=ho_so_id)
    except HoSoLuuTru.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy hồ sơ lưu trữ.'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'thanh_cong': True, 'du_lieu': hs.to_dict()})
    elif request.method in ('PUT', 'POST'):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        for f in ['tieu_de', 'don_vi', 'nam_tai_lieu', 'thoi_han_bao_quan', 'mo_ta', 'tinh_trang']:
            if f in data:
                setattr(hs, f, data[f])
        hs.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Cập nhật hồ sơ thành công!', 'du_lieu': hs.to_dict()})
    elif request.method == 'DELETE':
        hs.delete()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã xóa hồ sơ thành công.'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_ho_so_van_ban(request, ho_so_id):
    """Danh sách văn bản trong hồ sơ."""
    try:
        hs = HoSoLuuTru.objects.get(pk=ho_so_id)
    except HoSoLuuTru.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy hồ sơ.'}, status=404)

    docs = VanBanBanHanh.objects.filter(ho_so=hs)
    du_lieu = []
    for d in docs:
        du_lieu.append({
            'van_ban_id': d.van_ban_id,
            'so_ky_hieu': d.so_ky_hieu,
            'trich_yeu': d.trich_yeu,
            'loai_van_ban': d.loai_van_ban,
            'nguoi_ky': d.nguoi_ky,
            'ngay_ban_hanh': d.ngay_ban_hanh.strftime('%Y-%m-%d') if d.ngay_ban_hanh else '',
        })
    return JsonResponse({'thanh_cong': True, 'du_lieu': du_lieu, 'tong_so': len(du_lieu)})

@csrf_exempt
def api_ho_so_van_ban_kha_dung(request, ho_so_id):
    """Danh sách văn bản khả dụng để thêm vào hồ sơ."""
    docs = VanBanBanHanh.objects.filter(ho_so__isnull=True)[:20]
    du_lieu = []
    for d in docs:
        du_lieu.append({
            'van_ban_id': d.van_ban_id,
            'so_ky_hieu': d.so_ky_hieu,
            'trich_yeu': d.trich_yeu,
            'loai_van_ban': d.loai_van_ban,
            'nguoi_ky': d.nguoi_ky,
            'ngay_ban_hanh': d.ngay_ban_hanh.strftime('%Y-%m-%d') if d.ngay_ban_hanh else '',
        })
    return JsonResponse({'thanh_cong': True, 'du_lieu': du_lieu, 'tong_so': len(du_lieu)})

@csrf_exempt
def api_ho_so_them_van_ban(request, ho_so_id):
    """Bổ sung văn bản vào hồ sơ."""
    try:
        hs = HoSoLuuTru.objects.get(pk=ho_so_id)
    except HoSoLuuTru.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy hồ sơ.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    vb_id = data.get('van_ban_id')
    vb = VanBanBanHanh.objects.filter(pk=vb_id).first()
    if vb:
        vb.ho_so = hs
        vb.save()
        hs.so_luong_van_ban = VanBanBanHanh.objects.filter(ho_so=hs).count()
        hs.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Bổ sung văn bản vào hồ sơ thành công!'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản yêu cầu.'}, status=404)

@csrf_exempt
def api_ho_so_xoa_van_ban(request, ho_so_id):
    """Gỡ văn bản khỏi hồ sơ."""
    try:
        hs = HoSoLuuTru.objects.get(pk=ho_so_id)
    except HoSoLuuTru.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy hồ sơ.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    vb_id = data.get('van_ban_id')
    vb = VanBanBanHanh.objects.filter(pk=vb_id, ho_so=hs).first()
    if vb:
        vb.ho_so = None
        vb.save()
        hs.so_luong_van_ban = VanBanBanHanh.objects.filter(ho_so=hs).count()
        hs.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã gỡ văn bản khỏi hồ sơ thành công!'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Văn bản không tồn tại trong hồ sơ.'}, status=404)

@csrf_exempt
def api_ho_so_nop_luu_tru(request, ho_so_id):
    """Nộp hồ sơ vào kho lưu trữ cơ quan."""
    try:
        hs = HoSoLuuTru.objects.get(pk=ho_so_id)
        hs.tinh_trang = 'DA_NOP_LUU_TRU'
        hs.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã nộp hồ sơ vào kho lưu trữ cơ quan.'})
    except HoSoLuuTru.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy hồ sơ.'}, status=404)

@csrf_exempt
def api_ho_so_dong(request, ho_so_id):
    """Đóng hồ sơ lưu trữ."""
    try:
        hs = HoSoLuuTru.objects.get(pk=ho_so_id)
        hs.tinh_trang = 'DA_DONG'
        hs.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã đóng hồ sơ lưu trữ thành công.'})
    except HoSoLuuTru.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy hồ sơ.'}, status=404)
