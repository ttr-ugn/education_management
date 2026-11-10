import json
from datetime import date, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from .models import CongViec, NhatKyCongViec
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
        q = request.GET.get('q', '').strip()
        trang_thai = request.GET.get('trang_thai', '').strip()
        do_uu_tien = request.GET.get('do_uu_tien', '').strip()
        phong_ban = request.GET.get('phong_ban', '').strip()

        qs = CongViec.objects.all().order_by('-ngay_tao')
        if q:
            qs = qs.filter(
                Q(ten_cong_viec__icontains=q) | 
                Q(noi_dung__icontains=q) | 
                Q(so_ky_hieu_vb__icontains=q) |
                Q(trich_yeu_vb__icontains=q) |
                Q(nguoi_xu_ly__ho_va_ten__icontains=q) |
                Q(phong_ban__icontains=q)
            )
        if trang_thai:
            if trang_thai in ('CHO_DANH_GIA', 'CHO_PHE_DUYET'):
                qs = qs.filter(trang_thai__in=['CHO_DANH_GIA', 'CHO_PHE_DUYET'])
            elif trang_thai in ('HOAN_THANH', 'DA_HOAN_THANH'):
                qs = qs.filter(trang_thai__in=['HOAN_THANH', 'DA_HOAN_THANH'])
            else:
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
            trang_thai='CHUA_THUC_HIEN',
            so_ky_hieu_vb=data.get('so_ky_hieu_vb', ''),
            trich_yeu_vb=data.get('trich_yeu_vb', '')
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

    tien_do_cu = cv.tien_do
    tien_do = int(data.get('tien_do', cv.tien_do))
    cv.tien_do = tien_do
    ghi_chu = data.get('bao_cao') or data.get('ket_qua_bao_cao', '')
    if ghi_chu:
        cv.ket_qua_bao_cao = ghi_chu
    if data.get('tep_dinh_kem_ket_qua'):
        cv.tep_dinh_kem_ket_qua = data.get('tep_dinh_kem_ket_qua')

    if tien_do >= 100:
        cv.trang_thai = 'CHO_DANH_GIA'
    elif tien_do > 0:
        cv.trang_thai = 'DANG_THUC_HIEN'

    cv.save()

    # Ghi nhận lịch sử vào NhatKyCongViec
    user_id = request.session.get('user_id')
    user = NguoiDung.objects.filter(pk=user_id).first() if user_id else cv.nguoi_xu_ly
    NhatKyCongViec.objects.create(
        cong_viec=cv,
        nguoi_cap_nhat=user,
        tien_do_cu=tien_do_cu,
        tien_do_moi=tien_do,
        noi_dung_ghi_chu=ghi_chu or f'Cập nhật tiến độ hoàn thành {tien_do}%'
    )

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

    ket_luan = data.get('ket_luan', 'DAT')
    nhan_xet = data.get('nhan_xet') or data.get('danh_gia', 'Đạt yêu cầu và nghiệm thu thành công.')
    cv.danh_gia_lanh_dao = f'[{ket_luan}] {nhan_xet}'
    cv.trang_thai = 'HOAN_THANH'
    cv.tien_do = 100
    cv.save()

    # Ghi nhật ký
    user_id = request.session.get('user_id')
    user = NguoiDung.objects.filter(pk=user_id).first() if user_id else cv.nguoi_giao
    NhatKyCongViec.objects.create(
        cong_viec=cv,
        nguoi_cap_nhat=user,
        tien_do_cu=100,
        tien_do_moi=100,
        noi_dung_ghi_chu=f'Nghiệm thu: {cv.danh_gia_lanh_dao}'
    )

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã nghiệm thu kết quả công việc thành công!'})

@csrf_exempt
def api_cong_viec_thong_ke(request):
    """Thống kê khối lượng công việc cho biểu đồ và Dashboard."""
    all_tasks = list(CongViec.objects.all())
    tong_so = len(all_tasks)

    theo_trang_thai = {
        'DANG_THUC_HIEN': 0,
        'CHO_DANH_GIA': 0,
        'HOAN_THANH': 0,
        'CHUA_THUC_HIEN': 0,
        'QUA_HAN': 0,
    }

    dept_stats = {}

    for t in all_tasks:
        st = t.trang_thai
        if st in ('CHO_PHE_DUYET', 'CHO_DANH_GIA'):
            st = 'CHO_DANH_GIA'
        elif st in ('DA_HOAN_THANH', 'HOAN_THANH'):
            st = 'HOAN_THANH'
        elif st == 'QUA_HAN':
            st = 'QUA_HAN'
        elif st == 'CHUA_THUC_HIEN':
            st = 'CHUA_THUC_HIEN'
        else:
            st = 'DANG_THUC_HIEN'

        theo_trang_thai[st] = theo_trang_thai.get(st, 0) + 1

        dept = t.phong_ban or 'Văn phòng Sở'
        # Rút gọn tên phòng ban cho biểu đồ hiển thị đẹp, không bị nghiêng chữ
        short_dept = dept.replace('Phòng Giáo dục Trung học', 'GD Trung học')\
                         .replace('Phòng Kế hoạch - Tài chính', 'Kế hoạch - TC')\
                         .replace('Phòng Tổ chức cán bộ', 'Tổ chức CB')\
                         .replace('Phòng Giáo dục Mầm non - Tiểu học', 'Mầm non - TH')\
                         .replace('Phòng Khảo thí & Quản lý chất lượng', 'Khảo thí & QLCL')\
                         .replace('Văn phòng Sở GD&ĐT', 'Văn phòng Sở')\
                         .replace('Phòng ', '').replace('thành phố Đà Nẵng', '').strip()
        if short_dept not in dept_stats:
            dept_stats[short_dept] = {'duoc_giao': 0, 'da_xong': 0, 'qua_han': 0}
        dept_stats[short_dept]['duoc_giao'] += 1
        if st == 'HOAN_THANH':
            dept_stats[short_dept]['da_xong'] += 1
        elif st == 'QUA_HAN':
            dept_stats[short_dept]['qua_han'] += 1

    qua_han_cnt = theo_trang_thai['QUA_HAN']
    ty_le_dung_han = round(((tong_so - qua_han_cnt) / tong_so * 100), 1) if tong_so > 0 else 100

    chart_doughnut = {
        'labels': ['Đang thực hiện', 'Chờ nghiệm thu', 'Đã hoàn thành', 'Quá hạn', 'Chưa thực hiện'],
        'data': [
            theo_trang_thai['DANG_THUC_HIEN'],
            theo_trang_thai['CHO_DANH_GIA'],
            theo_trang_thai['HOAN_THANH'],
            theo_trang_thai['QUA_HAN'],
            theo_trang_thai['CHUA_THUC_HIEN']
        ],
        'colors': ['#0284c7', '#f59e0b', '#10b981', '#ef4444', '#94a3b8']
    }

    dept_labels = list(dept_stats.keys())
    chart_bar = {
        'labels': dept_labels,
        'duoc_giao': [dept_stats[d]['duoc_giao'] for d in dept_labels],
        'da_xong': [dept_stats[d]['da_xong'] for d in dept_labels],
        'qua_han': [dept_stats[d]['qua_han'] for d in dept_labels]
    }

    return JsonResponse({
        'thanh_cong': True,
        'du_lieu': {
            'tong_so': tong_so,
            'theo_trang_thai': theo_trang_thai,
            'ty_le_dung_han': ty_le_dung_han,
            'chart_doughnut': chart_doughnut,
            'chart_bar': chart_bar
        }
    })
