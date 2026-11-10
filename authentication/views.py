import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from werkzeug.security import generate_password_hash
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
    """Xử lý đăng nhập hệ thống."""
    if request.method != 'POST':
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hợp lệ.'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    username = (data.get('ten_dang_nhap') or '').strip()
    password = data.get('mat_khau') or ''

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
        'du_lieu': {
            'nguoi_dung': user.to_dict(),
            'token': 'session_auth_token_2026',
            'bat_buoc_doi_mat_khau': bool(user.bat_buoc_doi_mat_khau)
        }
    })

@csrf_exempt
def api_me(request):
    """Lấy thông tin người dùng hiện tại."""
    user_id = request.session.get('user_id')
    if not user_id:
        # Nếu chưa có session, fallback kiểm tra user admin đầu tiên để test
        user = NguoiDung.objects.filter(vai_tro='VAN_THU').first()
        if user:
            return JsonResponse({'thanh_cong': True, 'du_lieu': user.to_dict()})
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
def api_users_list(request):
    """Danh sách người dùng cho Admin."""
    role = request.GET.get('vai_tro')
    status = request.GET.get('trang_thai')
    qs = NguoiDung.objects.all()
    if role:
        qs = qs.filter(vai_tro=role)
    if status:
        qs = qs.filter(trang_thai=status)
    return JsonResponse({'thanh_cong': True, 'du_lieu': [u.to_dict() for u in qs]})
