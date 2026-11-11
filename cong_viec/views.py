import json
import mimetypes
from datetime import date, timedelta
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from .models import CongViec, NhatKyCongViec
from .services import TaskAttachmentService, TaskServiceException
from authentication.models import NguoiDung


def danh_sach_cong_viec(request):
    """Trang giao diện Theo dõi tiến độ & Điều hành công việc."""
    return render(request, 'cong_viec/danh-sach.html')


def giao_viec(request):
    """Trang giao nhiệm vụ mới."""
    return render(request, 'cong_viec/giao-viec.html')


def xu_ly_cong_viec(request):
    """Trang xử lý / cập nhật tiến độ công việc."""
    return render(request, 'cong_viec/xu-ly.html')


def phe_duyet_ket_qua(request):
    """Trang nghiệm thu, đánh giá kết quả công việc."""
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
        if request.FILES or (request.content_type or '').startswith('multipart/form-data'):
            data = request.POST
        else:
            try:
                data = json.loads(request.body.decode('utf-8')) if request.body else {}
            except Exception:
                data = request.POST

        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

        assignee_id = data.get('nguoi_xu_ly_id')
        chuyen_vien = NguoiDung.objects.filter(pk=assignee_id).first() if assignee_id else None
        if not chuyen_vien and data.get('nguoi_xu_ly'):
            chuyen_vien = NguoiDung.objects.filter(ho_va_ten__iexact=str(data.get('nguoi_xu_ly')).strip()).first()
        if not chuyen_vien:
            chuyen_vien = user

        try:
            ngay_van_ban = TaskAttachmentService.parse_optional_date(data.get('ngay_van_ban'))
            han_hoan_thanh = TaskAttachmentService.parse_optional_date(data.get('han_hoan_thanh')) or (date.today() + timedelta(days=7))

            uploaded_file = request.FILES.get('tep_dinh_kem')
            if uploaded_file:
                tep_dinh_kem, ten_tep_dinh_kem = TaskAttachmentService.save_uploaded_attachment(uploaded_file)
            else:
                tep_dinh_kem, ten_tep_dinh_kem = TaskAttachmentService.normalize_existing_attachment(
                    data.get('tep_dinh_kem'),
                    data.get('ten_tep_dinh_kem'),
                )
        except TaskServiceException as exc:
            return JsonResponse({'thanh_cong': False, 'thong_bao': str(exc)}, status=400)

        ten_cong_viec = (data.get('ten_cong_viec') or '').strip() or 'Công việc mới'
        cv = CongViec.objects.create(
            ten_cong_viec=ten_cong_viec,
            noi_dung=data.get('noi_dung', ''),
            nguoi_giao=user,
            nguoi_xu_ly=chuyen_vien,
            phong_ban=data.get('phong_ban') or (chuyen_vien.phong_ban if chuyen_vien else 'Văn phòng Sở'),
            han_hoan_thanh=han_hoan_thanh,
            do_uu_tien=data.get('do_uu_tien', 'TRUNG_BINH'),
            tien_do=0,
            trang_thai='CHUA_THUC_HIEN',
            so_ky_hieu_vb=(data.get('so_ky_hieu_vb') or '').strip(),
            ngay_van_ban=ngay_van_ban,
            trich_yeu_vb=data.get('trich_yeu_vb', ''),
            tep_dinh_kem=tep_dinh_kem or '',
            ten_tep_dinh_kem=ten_tep_dinh_kem or '',
        )
        return JsonResponse({
            'thanh_cong': True,
            'thong_bao': 'Giao nhiệm vụ thành công!',
            'cong_viec_id': cv.cong_viec_id,
            'du_lieu': cv.to_dict(),
        })

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
    tien_do_moi = int(data.get('tien_do', tien_do_cu))
    ghi_chu = data.get('ghi_chu', data.get('bao_cao_noi_dung', ''))
    tep_dinh_kem = data.get('tep_dinh_kem')

    cv.tien_do = tien_do_moi
    if ghi_chu:
        cv.ket_qua_bao_cao = ghi_chu
    if tep_dinh_kem:
        cv.tep_dinh_kem_ket_qua = tep_dinh_kem

    if tien_do_moi == 100:
        cv.trang_thai = 'CHO_DANH_GIA'
    elif tien_do_moi > 0:
        cv.trang_thai = 'DANG_THUC_HIEN'

    cv.save()

    # Ghi nhật ký
    user_id = request.session.get('user_id')
    user = NguoiDung.objects.filter(pk=user_id).first() if user_id else cv.nguoi_xu_ly
    NhatKyCongViec.objects.create(
        cong_viec=cv,
        nguoi_cap_nhat=user,
        tien_do_cu=tien_do_cu,
        tien_do_moi=tien_do_moi,
        noi_dung_ghi_chu=ghi_chu or f"Cập nhật tiến độ từ {tien_do_cu}% lên {tien_do_moi}%"
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
            'hoan_thanh': theo_trang_thai['HOAN_THANH'],
            'da_hoan_thanh': theo_trang_thai['HOAN_THANH'],
            'ty_le_dung_han': ty_le_dung_han,
            'chart_doughnut': chart_doughnut,
            'chart_bar': chart_bar
        }
    })


def api_cong_viec_tai_dinh_kem(request, cong_viec_id):
    """Tải về hoặc xem trước tệp văn bản đính kèm khi giao việc."""
    try:
        cv = CongViec.objects.get(pk=cong_viec_id)
    except CongViec.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy công việc.'}, status=404)

    if not cv.tep_dinh_kem:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Công việc chưa có văn bản đính kèm.'}, status=404)

    preview = request.GET.get('xem_truoc') in ('1', 'true', 'yes')
    archival_id = TaskAttachmentService.parse_archival_ref(cv.tep_dinh_kem)
    if archival_id is not None:
        from ho_so.views import _render_van_ban_ban_hanh_response
        return _render_van_ban_ban_hanh_response(archival_id, as_download=not preview)

    disk_path = TaskAttachmentService.resolve_media_path(cv.tep_dinh_kem)
    if disk_path is None:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy tệp văn bản đính kèm trên máy chủ.'}, status=404)

    content_type = mimetypes.guess_type(disk_path.name)[0] or 'application/octet-stream'
    if preview:
        return FileResponse(open(disk_path, 'rb'), as_attachment=False, content_type=content_type)

    download_name = cv.ten_tep_dinh_kem or disk_path.name
    return FileResponse(open(disk_path, 'rb'), as_attachment=True, filename=download_name, content_type=content_type)


def api_cong_viec_van_ban_goi_y(request):
    """Lấy danh sách văn bản hiện có trong hệ thống để chọn nhanh khi giao việc."""
    if request.method != 'GET':
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

    q = (request.GET.get('q') or '').strip().lower()
    docs = TaskAttachmentService.get_suggested_documents(limit=40)
    if q:
        docs = [
            d for d in docs
            if q in (d.get('so_ky_hieu') or '').lower()
            or q in (d.get('trich_yeu') or '').lower()
            or q in (d.get('loai_van_ban') or '').lower()
        ]
    return JsonResponse({'thanh_cong': True, 'du_lieu': docs, 'tong_so': len(docs)})
