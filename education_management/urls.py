from django.contrib import admin
from django.urls import path, include
from dashboard.views import trang_chu, trang_dashboard
import authentication.views as auth_views
import ho_so.views as hs_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', trang_chu, name='home'),
    path('auth/', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('ho-so/', include('ho_so.urls')),

    # Giao diện người dùng
    path('pages/login.html', auth_views.login_page),
    path('pages/register.html', auth_views.register_page),
    path('pages/doi-mat-khau.html', auth_views.doi_mat_khau_page),
    path('pages/ho-so-ca-nhan.html', auth_views.ho_so_ca_nhan_page),
    path('pages/dashboard.html', trang_dashboard),
    path('pages/ho-so/danh-sach.html', hs_views.trang_danh_sach),
    path('pages/ho-so/them-sua.html', hs_views.trang_them_sua),
    path('pages/ho-so/chi-tiet.html', hs_views.trang_chi_tiet),

    # API Endpoints
    path('api/auth/login', auth_views.api_login, name='api_auth_login'),
    path('api/auth/dang-nhap', auth_views.api_login, name='api_auth_dang_nhap'),
    path('api/auth/me', auth_views.api_me, name='api_auth_me'),
    path('api/auth/toi', auth_views.api_me, name='api_auth_toi'),
    path('api/auth/logout', auth_views.api_logout, name='api_auth_logout'),
    path('api/auth/dang-xuat', auth_views.api_logout, name='api_auth_dang_xuat'),
    path('api/users', auth_views.api_users_list, name='api_users'),
    path('api/ho-so', hs_views.api_ho_so_list, name='api_ho_so'),
    path('api/ho-so/', hs_views.api_ho_so_list, name='api_ho_so_slash'),
    path('api/ho-so/<int:ho_so_id>', hs_views.api_ho_so_detail, name='api_ho_so_detail'),
    path('api/ho-so/<int:ho_so_id>/tai-lieu', hs_views.api_ho_so_tai_lieu, name='api_ho_so_tai_lieu'),
    path('api/ho-so/<int:ho_so_id>/tai-lieu/<int:tai_lieu_id>', hs_views.api_ho_so_xoa_tai_lieu, name='api_ho_so_xoa_tai_lieu'),
]
