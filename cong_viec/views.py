import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from .models import CongViec
from authentication.models import NguoiDung

def danh_sach_cong_viec(request):
    return render(request, 'cong_viec/danh-sach.html')

def giao_viec(request):
    return render(request, 'cong_viec/giao-viec.html')

def xu_ly_cong_viec(request):
    return render(request, 'cong_viec/xu-ly.html')

def phe_duyet_ket_qua(request):
    return render(request, 'cong_viec/phe-duyet-ket-qua.html')

# ==============================================================================
# API CÔNG VIỆC
# ==============================================================================

@csrf_exempt
def api_cong_viec_list(request):
    """Lấy danh sách công việc hoặc giao việc mới."""
    if request.method == 'GET':
        q = request.GET.get('q')
        trang_thai = request.GET.get('trang_thai')
        do_uu_tien = request.GET.get('do_uu_tien')
        phong_ban = request.GET.get('phong_ban')

        qs = CongViec.objects.all().order_by('-ngay_tao')
        if q:
            qs = qs.filter(Q(ten_cong_viec__icontains=q) | Q(noi_dung__icontains=q))
        if trang_thai:
            qs = qs.filter(trang_thai=trang_thai)
        if do_uu_tien:
            qs = qs.filter(do_uu_tien=do_uu_tien)
        if phong_ban:
            qs = qs.filter(phong_ban__icontains=phong_ban)

        return JsonResponse({'thanh_cong': True, 'du_lieu': [cv.to_dict() for cv in qs], 'tong_so': qs.count()})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        from datetime import date, timedelta
        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

        chuyen_vien = NguoiDung.objects.filter(pk=data.get('nguoi_xu_ly_id')).first() if data.get('nguoi_xu_ly_id') else user

        cv = CongViec.objects.create(
            ten_cong_viec=data.get('ten_cong_viec', 'Công việc mới'),
            noi_dung=data.get('noi_dung', ''),
            nguoi_giao=user,
            nguoi_xu_ly=chuyen_vien,
            phong_ban=data.get('phong_ban') or (chuyen_vien.phong_ban if chuyen_vien else 'Văn phòng Sở'),
            han_hoan_thanh=data.get('han_hoan_thanh') or (date.today() + timedelta(days=7)),
            do_uu_tien=data.get('do_uu_tien', 'TRUNG_BINH'),
            tien_do=0,
            trang_thai='CHUA_THUC_HIEN'
        )
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Giao nhiệm vụ thành công!', 'cong_viec_id': cv.cong_viec_id})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_cong_viec_detail(request, cong_viec_id):
    """Chi tiết hoặc xóa công việc."""
    try:
        cv = CongViec.objects.get(pk=cong_viec_id)
    except CongViec.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy công việc.'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'thanh_cong': True, 'du_lieu': cv.to_dict()})
    elif request.method == 'DELETE':
        cv.delete()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã xóa công việc.'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_cong_viec_tien_do(request, cong_viec_id):
    """Cập nhật tiến độ công việc."""
    try:
        cv = CongViec.objects.get(pk=cong_viec_id)
    except CongViec.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy công việc.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    tien_do = int(data.get('tien_do', cv.tien_do))
    cv.tien_do = tien_do
    cv.ket_qua_bao_cao = data.get('bao_cao') or data.get('ket_qua_bao_cao', cv.ket_qua_bao_cao)

    if tien_do >= 100:
        cv.trang_thai = 'CHO_DANH_GIA'
    elif tien_do > 0:
        cv.trang_thai = 'DANG_THUC_HIEN'

    cv.save()
    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Cập nhật tiến độ thành công!'})

@csrf_exempt
def api_cong_viec_danh_gia(request, cong_viec_id):
    """Lãnh đạo/Văn thư nghiệm thu, đánh giá kết quả công việc."""
    try:
        cv = CongViec.objects.get(pk=cong_viec_id)
    except CongViec.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy công việc.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    cv.danh_gia_lanh_dao = data.get('danh_gia') or data.get('nhan_xet', 'Đạt yêu cầu')
    cv.trang_thai = 'HOAN_THANH'
    cv.tien_do = 100
    cv.save()
    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã nghiệm thu kết quả công việc thành công!'})

@csrf_exempt
def api_cong_viec_thong_ke(request):
    """Thống kê khối lượng công việc cho biểu đồ và Dashboard."""
    tong_so = CongViec.objects.count()
    hoan_thanh = CongViec.objects.filter(trang_thai='HOAN_THANH').count()
    dang_thuc_hien = CongViec.objects.filter(trang_thai='DANG_THUC_HIEN').count()
    chua_thuc_hien = CongViec.objects.filter(trang_thai='CHUA_THUC_HIEN').count()
    qua_han = CongViec.objects.filter(trang_thai='QUA_HAN').count()

    return JsonResponse({
        'thanh_cong': True,
        'du_lieu': {
            'tong_so': tong_so,
            'hoan_thanh': hoan_thanh,
            'dang_thuc_hien': dang_thuc_hien,
            'chua_thuc_hien': chua_thuc_hien,
            'qua_han': qua_han,
            'ty_le_hoan_thanh': round((hoan_thanh / tong_so * 100), 1) if tong_so > 0 else 0
        }
    })
