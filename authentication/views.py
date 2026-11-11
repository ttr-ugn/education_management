import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import NguoiDung

def login_page(request):
    """Hiển thị trang đăng nhập."""
    return render(request, 'authentication/login.html')

def register_page(request):
    """Hiển thị trang đăng ký."""
    return render(request, 'authentication/register.html')

def doi_mat_khau_page(request):
    """Hiển thị trang đổi mật khẩu."""
    return render(request, 'authentication/doi-mat-khau.html')

def ho_so_ca_nhan_page(request):
    """Hiển thị trang hồ sơ cá nhân."""
    return render(request, 'authentication/ho-so-ca-nhan.html')

def admin_duyet_tai_khoan_page(request):
    """Trang Văn thư duyệt tài khoản."""
    return render(request, 'authentication/admin/duyet-tai-khoan.html')

def admin_quan_ly_nguoi_dung_page(request):
    """Trang Quản lý người dùng."""
    return render(request, 'authentication/admin/quan-ly-nguoi-dung.html')

def admin_tao_lanh_dao_page(request):
    """Trang Văn thư tạo tài khoản Lãnh đạo."""
    return render(request, 'authentication/admin/tao-lanh-dao.html')

# ==============================================================================
# API ENDPOINTS CHO FRONTEND FETCH
# ==============================================================================

@csrf_exempt
def api_login(request):
    """Xác thực đăng nhập và thiết lập session."""
    if request.method != 'POST':
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hợp lệ.'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    username = (data.get('ten_dang_nhap') or data.get('username') or '').strip()
    password = data.get('mat_khau') or data.get('password') or ''

    if not username or not password:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Vui lòng nhập tên đăng nhập và mật khẩu.'}, status=400)

    try:
        user = NguoiDung.objects.get(ten_dang_nhap=username)
    except NguoiDung.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Tên đăng nhập hoặc mật khẩu không chính xác.'}, status=401)

    if user.trang_thai == 'BI_KHOA':
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Tài khoản của bạn đã bị khóa.'}, status=403)
    if user.trang_thai == 'CHO_DUYET':
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Tài khoản đang chờ Văn thư phê duyệt.'}, status=403)
    if user.trang_thai == 'TU_CHOI':
        return JsonResponse({'thanh_cong': False, 'thong_bao': f'Tài khoản bị từ chối: {user.ly_do_tu_choi or "Không rõ lý do"}'}, status=403)

    if not user.check_password(password):
        user.so_lan_dang_nhap_sai += 1
        user.save()
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Tên đăng nhập hoặc mật khẩu không chính xác.'}, status=401)

    # Đăng nhập thành công -> lưu session
    user.so_lan_dang_nhap_sai = 0
    user.save()
    request.session['user_id'] = user.nguoi_dung_id
    request.session['username'] = user.ten_dang_nhap
    request.session['role'] = user.vai_tro
    request.session['fullname'] = user.ho_va_ten

    return JsonResponse({
        'thanh_cong': True,
        'thong_bao': 'Đăng nhập thành công!',
        'du_lieu': user.to_dict()
    })

@csrf_exempt
def api_me(request):
    """Lấy thông tin người dùng hiện tại đang đăng nhập."""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Chưa đăng nhập.'}, status=401)

    try:
        user = NguoiDung.objects.get(pk=user_id)
        return JsonResponse({'thanh_cong': True, 'du_lieu': user.to_dict()})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Người dùng không tồn tại.'}, status=404)

@csrf_exempt
def api_logout(request):
    """Đăng xuất khỏi hệ thống."""
    request.session.flush()
    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đăng xuất thành công!'})

@csrf_exempt
def api_register(request):
    """Đăng ký tài khoản người dùng mới (Chuyên viên hoặc Văn thư)."""
    if request.method != 'POST':
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hợp lệ.'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    username = (data.get('ten_dang_nhap') or '').strip()
    if not username:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Vui lòng nhập tên đăng nhập.'}, status=400)
    if NguoiDung.objects.filter(ten_dang_nhap=username).exists():
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Tên đăng nhập đã tồn tại.'}, status=400)

    user = NguoiDung(
        ten_dang_nhap=username,
        ho_va_ten=data.get('ho_va_ten', ''),
        email=data.get('email', ''),
        sdt=data.get('sdt', ''),
        phong_ban=data.get('phong_ban', ''),
        chuc_vu=data.get('chuc_vu', ''),
        vai_tro=data.get('vai_tro', 'CHUYEN_VIEN'),
        trang_thai='CHO_DUYET'
    )
    user.set_password(data.get('mat_khau', '123456'))
    user.save()
    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đăng ký thành công! Vui lòng chờ Văn thư phê duyệt.'})

@csrf_exempt
def api_doi_mat_khau(request):
    """Đổi mật khẩu tài khoản hiện tại."""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Chưa đăng nhập.'}, status=401)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    user = NguoiDung.objects.get(pk=user_id)
    mat_khau_cu = data.get('mat_khau_cu')
    mat_khau_moi = data.get('mat_khau_moi')

    if not user.check_password(mat_khau_cu):
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Mật khẩu cũ không chính xác.'}, status=400)

    user.set_password(mat_khau_moi)
    user.bat_buoc_doi_mat_khau = False
    user.save()
    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đổi mật khẩu thành công!'})

@csrf_exempt
def api_users_list(request):
    """Lấy danh sách người dùng có lọc và tìm kiếm."""
    role = request.GET.get('vai_tro')
    status = request.GET.get('trang_thai')
    q = request.GET.get('q')

    qs = NguoiDung.objects.all().order_by('-ngay_tao')
    if role:
        qs = qs.filter(vai_tro=role)
    if status:
        qs = qs.filter(trang_thai=status)
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(ho_va_ten__icontains=q) | Q(ten_dang_nhap__icontains=q) | Q(email__icontains=q))

    data = [u.to_dict() for u in qs]
    return JsonResponse({'thanh_cong': True, 'du_lieu': data, 'tong_so': len(data)})

@csrf_exempt
def api_user_duyet(request, user_id):
    """Phê duyệt tài khoản chuyên viên."""
    try:
        u = NguoiDung.objects.get(pk=user_id)
        u.trang_thai = 'HOAT_DONG'
        u.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': f'Đã phê duyệt tài khoản {u.ten_dang_nhap}.'})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Người dùng không tồn tại.'}, status=404)

@csrf_exempt
def api_user_tu_choi(request, user_id):
    """Từ chối tài khoản chuyên viên."""
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        u = NguoiDung.objects.get(pk=user_id)
        u.trang_thai = 'TU_CHOI'
        u.ly_do_tu_choi = data.get('ly_do', 'Không đủ điều kiện')
        u.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': f'Đã từ chối tài khoản {u.ten_dang_nhap}.'})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Người dùng không tồn tại.'}, status=404)

@csrf_exempt
def api_user_khoa(request, user_id):
    """Khóa tài khoản người dùng."""
    try:
        u = NguoiDung.objects.get(pk=user_id)
        u.trang_thai = 'BI_KHOA'
        u.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': f'Đã khóa tài khoản {u.ten_dang_nhap}.'})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Người dùng không tồn tại.'}, status=404)

@csrf_exempt
def api_user_mo_khoa(request, user_id):
    """Mở khóa tài khoản người dùng."""
    try:
        u = NguoiDung.objects.get(pk=user_id)
        u.trang_thai = 'HOAT_DONG'
        u.so_lan_dang_nhap_sai = 0
        u.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': f'Đã mở khóa tài khoản {u.ten_dang_nhap}.'})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Người dùng không tồn tại.'}, status=404)

@csrf_exempt
def api_user_dat_lai_mat_khau(request, user_id):
    """Đặt lại mật khẩu cho tài khoản người dùng."""
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        mat_khau_moi = data.get('mat_khau_moi') or 'MatKhau@123'
        u = NguoiDung.objects.get(pk=user_id)
        u.set_password(mat_khau_moi)
        u.bat_buoc_doi_mat_khau = True
        u.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': f'Đã đặt lại mật khẩu cho {u.ten_dang_nhap}.', 'mat_khau_moi': mat_khau_moi})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Người dùng không tồn tại.'}, status=404)

@csrf_exempt
def api_user_tao_lanh_dao(request):
    """Văn thư tạo tài khoản Lãnh đạo."""
    if request.method != 'POST':
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hợp lệ.'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    username = (data.get('ten_dang_nhap') or '').strip()
    if not username:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Vui lòng nhập tên đăng nhập.'}, status=400)

    u, created = NguoiDung.objects.get_or_create(ten_dang_nhap=username, defaults={
        'ho_va_ten': data.get('ho_va_ten', ''),
        'email': data.get('email', ''),
        'sdt': data.get('sdt', ''),
        'phong_ban': data.get('phong_ban', 'Ban Giám đốc Sở'),
        'chuc_vu': data.get('chuc_vu', 'Phó Giám đốc Sở'),
        'vai_tro': 'LANH_DAO',
        'trang_thai': 'HOAT_DONG',
        'bat_buoc_doi_mat_khau': True
    })
    mat_khau_tam = data.get('mat_khau') or 'LanhDao@123'
    u.set_password(mat_khau_tam)
    u.save()
    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Tạo tài khoản Lãnh đạo thành công!', 'du_lieu': {'ten_dang_nhap': u.ten_dang_nhap, 'mat_khau_tam': mat_khau_tam}})
