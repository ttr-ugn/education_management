import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import ThongBao, ThongBaoDaDoc
from .services import NotificationPushService, NotificationReadService
from authentication.models import NguoiDung


def trang_thong_bao(request):
    """Trang giao diện trung tâm thông báo và nhắc nhở điều hành."""
    return render(request, 'thong_bao/thong-bao.html')


# ==============================================================================
# API THÔNG BÁO & NHẮC NHỞ
# ==============================================================================

@csrf_exempt
def api_thong_bao_list(request):
    """Danh sách thông báo hoặc tạo mới thông báo."""
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else None

        if user:
            data = NotificationReadService.get_user_notifications(user, limit=50)
        else:
            qs = ThongBao.objects.all().order_by('-ngay_tao')[:50]
            data = [tb.to_dict() for tb in qs]

        return JsonResponse({'thanh_cong': True, 'du_lieu': data, 'tong_so': len(data)})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

        tb = NotificationPushService.push_personal_notification(
            recipient=user,
            title=data.get('tieu_de', 'Thông báo mới'),
            content=data.get('noi_dung', ''),
            loai=data.get('loai', 'Điều hành'),
            muc_do=data.get('muc_do', 'Bình thường'),
            sender=user
        )
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Tạo thông báo thành công!', 'du_lieu': tb.to_dict()})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)


@csrf_exempt
def api_thong_bao_dem_chua_doc(request):
    """Đếm số thông báo chưa đọc phục vụ badge real-time mỗi 2 giây."""
    user_id = request.session.get('user_id')
    user = NguoiDung.objects.filter(pk=user_id).first() if user_id else None

    if user:
        chua_doc = NotificationReadService.get_unread_count(user)
    else:
        tong_so = ThongBao.objects.count()
        chua_doc = tong_so

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

    if user:
        NotificationReadService.mark_as_read(thong_bao_id, user)

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã đánh dấu thông báo là đã đọc.'})


@csrf_exempt
def api_thong_bao_doc_tat_ca(request):
    """Đánh dấu toàn bộ thông báo đã đọc."""
    user_id = request.session.get('user_id')
    user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

    if user:
        NotificationReadService.mark_all_as_read(user)

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã đánh dấu tất cả là đã đọc.'})


@csrf_exempt
def api_thong_bao_detail(request, thong_bao_id):
    """Xóa thông báo."""
    if request.method == 'DELETE':
        ThongBao.objects.filter(pk=thong_bao_id).delete()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã xóa thông báo.'})
    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)
