import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import ThongBao, ThongBaoDaDoc
from authentication.models import NguoiDung

def trang_thong_bao(request):
    return render(request, 'thong_bao/thong-bao.html')

# ==============================================================================
# API THÔNG BÁO & NHẮC NHỞ
# ==============================================================================

@csrf_exempt
def api_thong_bao_list(request):
    """Danh sách thông báo hoặc tạo mới thông báo."""
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        loai = request.GET.get('loai')
        muc_do = request.GET.get('muc_do')

        qs = ThongBao.objects.all().order_by('-ngay_tao')
        if loai:
            qs = qs.filter(loai=loai)
        if muc_do:
            qs = qs.filter(muc_do=muc_do)

        read_ids = set()
        if user_id:
            read_ids = set(ThongBaoDaDoc.objects.filter(nguoi_dung_id=user_id).values_list('thong_bao_id', flat=True))

        data = []
        for tb in qs:
            d = tb.to_dict()
            d['da_doc'] = tb.thong_bao_id in read_ids
            data.append(d)

        return JsonResponse({'thanh_cong': True, 'du_lieu': data, 'tong_so': len(data)})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

        tb = ThongBao.objects.create(
            tieu_de=data.get('tieu_de', 'Thông báo mới'),
            noi_dung=data.get('noi_dung', ''),
            loai=data.get('loai', 'Điều hành'),
            muc_do=data.get('muc_do', 'Bình thường'),
            nguoi_gui=user
        )
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Tạo thông báo thành công!', 'du_lieu': tb.to_dict()})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_thong_bao_dem_chua_doc(request):
    """Đếm số thông báo chưa đọc."""
    user_id = request.session.get('user_id')
    tong_so = ThongBao.objects.count()
    da_doc = ThongBaoDaDoc.objects.filter(nguoi_dung_id=user_id).count() if user_id else 0
    chua_doc = max(0, tong_so - da_doc)

    return JsonResponse({
        'thanh_cong': True,
        'chua_doc': chua_doc,
        'den_han': 0
    })

@csrf_exempt
def api_thong_bao_kiem_tra_den_han(request):
    """Kiểm tra việc đến hạn."""
    return JsonResponse({
        'thanh_cong': True,
        'nhac_nho_den_han': [],
        'so_luong': 0
    })

@csrf_exempt
def api_thong_bao_da_doc(request, thong_bao_id):
    """Đánh dấu thông báo đã đọc."""
    user_id = request.session.get('user_id')
    user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

    tb = ThongBao.objects.filter(pk=thong_bao_id).first()
    if tb and user:
        ThongBaoDaDoc.objects.get_or_create(thong_bao=tb, nguoi_dung=user)

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã đánh dấu thông báo là đã đọc.'})

@csrf_exempt
def api_thong_bao_doc_tat_ca(request):
    """Đánh dấu toàn bộ thông báo đã đọc."""
    user_id = request.session.get('user_id')
    user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

    if user:
        all_tb = ThongBao.objects.all()
        for tb in all_tb:
            ThongBaoDaDoc.objects.get_or_create(thong_bao=tb, nguoi_dung=user)

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã đánh dấu tất cả là đã đọc.'})

@csrf_exempt
def api_thong_bao_detail(request, thong_bao_id):
    """Xóa thông báo."""
    if request.method == 'DELETE':
        ThongBao.objects.filter(pk=thong_bao_id).delete()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã xóa thông báo.'})
    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)
