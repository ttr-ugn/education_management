from django.contrib import admin
from django.urls import path, include
from dashboard.views import trang_chu, trang_dashboard
import authentication.views as auth_views
import cong_viec.views as cv_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', trang_chu, name='home'),
    path('auth/', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('cong-viec/', include('cong_viec.urls')),

    # Giao diện người dùng
    path('pages/login.html', auth_views.login_page),
    path('pages/register.html', auth_views.register_page),
    path('pages/doi-mat-khau.html', auth_views.doi_mat_khau_page),
    path('pages/ho-so-ca-nhan.html', auth_views.ho_so_ca_nhan_page),
    path('pages/dashboard.html', trang_dashboard),
    path('pages/cong-viec/danh-sach.html', cv_views.trang_danh_sach),
    path('pages/cong-viec/giao-viec.html', cv_views.trang_giao_viec),
    path('pages/cong-viec/xu-ly.html', cv_views.trang_xu_ly),
    path('pages/cong-viec/phe-duyet-ket-qua.html', cv_views.trang_phe_duyet),

    # API Endpoints
    path('api/auth/login', auth_views.api_login, name='api_auth_login'),
    path('api/auth/dang-nhap', auth_views.api_login, name='api_auth_dang_nhap'),
    path('api/auth/me', auth_views.api_me, name='api_auth_me'),
    path('api/auth/toi', auth_views.api_me, name='api_auth_toi'),
    path('api/auth/logout', auth_views.api_logout, name='api_auth_logout'),
    path('api/auth/dang-xuat', auth_views.api_logout, name='api_auth_dang_xuat'),
    path('api/users', auth_views.api_users_list, name='api_users'),
    path('api/cong-viec', cv_views.api_cong_viec_list, name='api_cong_viec'),
    path('api/cong-viec/', cv_views.api_cong_viec_list, name='api_cong_viec_slash'),
    path('api/cong-viec/<int:cv_id>', cv_views.api_cong_viec_detail, name='api_cong_viec_detail'),
    path('api/cong-viec/<int:cv_id>/tien-do', cv_views.api_cong_viec_tien_do, name='api_cong_viec_tien_do'),
    path('api/cong-viec/<int:cv_id>/phe-duyet', cv_views.api_cong_viec_phe_duyet, name='api_cong_viec_phe_duyet'),
    path('api/cong-viec/thong-ke', cv_views.api_cong_viec_thong_ke, name='api_cong_viec_thong_ke'),
]
