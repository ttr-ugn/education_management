import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import VanBanDi, VanBanDen, LichSuXuLyVanBan
from authentication.models import NguoiDung

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

# ==============================================================================
# API VĂN BẢN ĐI
# ==============================================================================

@csrf_exempt
def api_van_ban_di_list(request):
    """Danh sách văn bản đi hoặc tạo mới văn bản đi."""
    if request.method == 'GET':
        q = request.GET.get('q')
        trang_thai = request.GET.get('trang_thai')
        loai_van_ban = request.GET.get('loai_van_ban')

        qs = VanBanDi.objects.all().order_by('-ngay_tao')
        if q:
            qs = qs.filter(Q(trich_yeu__icontains=q) | Q(so_ky_hieu__icontains=q))
        if trang_thai:
            if trang_thai in ['DA_DUYET', 'DA_KY_CHO_BAN_HANH']:
                qs = qs.filter(trang_thai__in=['DA_DUYET', 'DA_KY_CHO_BAN_HANH'])
            elif trang_thai in ['CHO_LANH_DAO_KY', 'CHO_LANH_DAO_DUYET']:
                qs = qs.filter(trang_thai__in=['CHO_LANH_DAO_KY', 'CHO_LANH_DAO_DUYET'])
            elif trang_thai in ['CHO_VAN_THU_KIEM_TRA', 'CHO_KIEM_TRA']:
                qs = qs.filter(trang_thai__in=['CHO_VAN_THU_KIEM_TRA', 'CHO_KIEM_TRA'])
            else:
                qs = qs.filter(trang_thai=trang_thai)
        if loai_van_ban:
            qs = qs.filter(loai_van_ban=loai_van_ban)

        return JsonResponse({'thanh_cong': True, 'du_lieu': [vb.to_dict() for vb in qs], 'tong_so': qs.count()})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

        vb = VanBanDi.objects.create(
            so_ky_hieu=data.get('so_ky_hieu', ''),
            trich_yeu=data.get('trich_yeu', 'Dự thảo văn bản mới'),
            loai_van_ban=data.get('loai_van_ban', 'Công văn'),
            do_khan=data.get('do_khan', 'Bình thường'),
            don_vi_soan_thao=data.get('don_vi_soan_thao', 'Phòng Giáo dục Trung học'),
            noi_nhan=data.get('noi_nhan', 'Các đơn vị trực thuộc'),
            noi_dung_tom_tat=data.get('noi_dung_tom_tat', ''),
            nguoi_soan=user,
            trang_thai='CHO_VAN_THU_KIEM_TRA'
        )
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Tạo dự thảo văn bản đi thành công!', 'van_ban_id': vb.van_ban_id})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_van_ban_di_detail(request, van_ban_id):
    """Chi tiết, cập nhật hoặc xóa văn bản đi."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đi.'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'thanh_cong': True, 'du_lieu': vb.to_dict()})
    elif request.method in ('PUT', 'POST'):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        for field in ['trich_yeu', 'so_ky_hieu', 'loai_van_ban', 'do_khan', 'noi_nhan', 'noi_dung_tom_tat', 'trang_thai']:
            if field in data:
                setattr(vb, field, data[field])
        vb.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Cập nhật văn bản đi thành công!', 'du_lieu': vb.to_dict()})
    elif request.method == 'DELETE':
        vb.delete()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã xóa văn bản đi thành công.'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_van_ban_di_trang_thai(request, van_ban_id):
    """Chuyển trạng thái văn bản đi (duyệt, trả lại, ký, ban hành)."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đi.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    trang_thai_moi = data.get('trang_thai')
    if trang_thai_moi:
        vb.trang_thai = trang_thai_moi
        if trang_thai_moi == 'DA_BAN_HANH':
            from django.utils import timezone
            vb.ngay_ban_hanh = timezone.now()
        vb.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': f'Chuyển trạng thái thành {trang_thai_moi} thành công.'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Thiếu tham số trang_thai.'}, status=400)

@csrf_exempt
def api_van_ban_di_ban_hanh(request, van_ban_id):
    """Cấp số và ban hành văn bản đi chính thức."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đi.'}, status=404)

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        so_ky_hieu = data.get('so_ky_hieu')
        if so_ky_hieu:
            vb.so_ky_hieu = so_ky_hieu
        
        from django.utils import timezone
        vb.trang_thai = 'DA_BAN_HANH'
        vb.ngay_ban_hanh = timezone.now()
        vb.save()

        # Nếu có chọn hồ sơ thì liên kết
        ho_so_id = data.get('ho_so_id')
        if ho_so_id:
            try:
                from ho_so.models import HoSoTaiLieu
                hs = HoSoTaiLieu.objects.get(pk=ho_so_id)
                hs.so_luong_van_ban = (hs.so_luong_van_ban or 0) + 1
                hs.save()
            except Exception:
                pass

        return JsonResponse({'thanh_cong': True, 'thong_bao': f'Đã ban hành văn bản {vb.so_ky_hieu} thành công!', 'du_lieu': vb.to_dict()})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

# ==============================================================================
# API VĂN BẢN ĐẾN
# ==============================================================================

@csrf_exempt
def api_van_ban_den_list(request):
    """Danh sách văn bản đến hoặc tiếp nhận văn bản đến mới."""
    if request.method == 'GET':
        q = request.GET.get('q')
        trang_thai = request.GET.get('trang_thai')
        loai_van_ban = request.GET.get('loai_van_ban')
        do_khan = request.GET.get('do_khan')

        qs = VanBanDen.objects.all().order_by('-ngay_den')
        if q:
            qs = qs.filter(Q(trich_yeu__icontains=q) | Q(so_ky_hieu__icontains=q) | Q(co_quan_ban_hanh__icontains=q))
        if trang_thai:
            if trang_thai in ['DA_DUYET', 'DA_KY_CHO_BAN_HANH']:
                qs = qs.filter(trang_thai__in=['DA_DUYET', 'DA_KY_CHO_BAN_HANH'])
            elif trang_thai in ['CHO_LANH_DAO_KY', 'CHO_LANH_DAO_DUYET']:
                qs = qs.filter(trang_thai__in=['CHO_LANH_DAO_KY', 'CHO_LANH_DAO_DUYET'])
            elif trang_thai in ['CHO_VAN_THU_KIEM_TRA', 'CHO_KIEM_TRA']:
                qs = qs.filter(trang_thai__in=['CHO_VAN_THU_KIEM_TRA', 'CHO_KIEM_TRA'])
            else:
                qs = qs.filter(trang_thai=trang_thai)
        if loai_van_ban:
            qs = qs.filter(loai_van_ban=loai_van_ban)
        if do_khan:
            qs = qs.filter(do_khan=do_khan)

        return JsonResponse({'thanh_cong': True, 'du_lieu': [vb.to_dict() for vb in qs], 'tong_so': qs.count()})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        from datetime import date
        vb = VanBanDen.objects.create(
            so_den=data.get('so_den'),
            so_ky_hieu=data.get('so_ky_hieu', 'SĐ/2026'),
            co_quan_ban_hanh=data.get('co_quan_ban_hanh', 'Bộ GD&ĐT'),
            ngay_ban_hanh=data.get('ngay_ban_hanh') or date.today(),
            ngay_den=data.get('ngay_den') or date.today(),
            trich_yeu=data.get('trich_yeu', 'Văn bản đến mới tiếp nhận'),
            loai_van_ban=data.get('loai_van_ban', 'Công văn'),
            do_khan=data.get('do_khan', 'Bình thường'),
            do_mat=data.get('do_mat', 'Thường'),
            trang_thai='CHO_TIEP_NHAN'
        )
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Tiếp nhận văn bản đến thành công!', 'van_ban_id': vb.van_ban_id})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_van_ban_den_detail(request, van_ban_id):
    """Chi tiết, cập nhật hoặc xóa văn bản đến."""
    try:
        vb = VanBanDen.objects.get(pk=van_ban_id)
    except VanBanDen.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đến.'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'thanh_cong': True, 'du_lieu': vb.to_dict()})
    elif request.method in ('PUT', 'POST'):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        for field in ['trich_yeu', 'so_ky_hieu', 'co_quan_ban_hanh', 'loai_van_ban', 'do_khan', 'do_mat', 'trang_thai']:
            if field in data:
                setattr(vb, field, data[field])
        vb.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Cập nhật văn bản đến thành công!', 'du_lieu': vb.to_dict()})
    elif request.method == 'DELETE':
        vb.delete()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã xóa văn bản đến thành công.'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_van_ban_den_phan_cong(request, van_ban_id):
    """Phân công xử lý văn bản đến."""
    try:
        vb = VanBanDen.objects.get(pk=van_ban_id)
    except VanBanDen.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đến.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    chu_tri_id = data.get('nguoi_chu_tri_id') or data.get('chuyen_vien_id')
    if chu_tri_id:
        chu_tri = NguoiDung.objects.filter(pk=chu_tri_id).first()
        if chu_tri:
            vb.nguoi_chu_tri = chu_tri

    vb.noi_dung_chi_dao = data.get('noi_dung_chi_dao', vb.noi_dung_chi_dao)
    vb.han_xu_ly = data.get('han_xu_ly', vb.han_xu_ly)
    vb.trang_thai = 'DA_PHAN_CONG'
    vb.save()

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Phân công chỉ đạo văn bản đến thành công!'})
