from django.contrib import admin
from django.urls import path, include
from dashboard.views import trang_chu, trang_dashboard, trang_thong_ke
import authentication.views as auth_views
import thong_bao.views as tb_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', trang_chu, name='home'),
    path('auth/', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('thong-bao/', include('thong_bao.urls')),

    # Giao diện người dùng
    path('pages/login.html', auth_views.login_page),
    path('pages/register.html', auth_views.register_page),
    path('pages/doi-mat-khau.html', auth_views.doi_mat_khau_page),
    path('pages/ho-so-ca-nhan.html', auth_views.ho_so_ca_nhan_page),
    path('pages/dashboard.html', trang_dashboard),
    path('pages/thong-ke.html', trang_thong_ke),
    path('pages/thong-bao.html', tb_views.trang_thong_bao),

    # API Endpoints
    path('api/auth/login', auth_views.api_login, name='api_auth_login'),
    path('api/auth/dang-nhap', auth_views.api_login, name='api_auth_dang_nhap'),
    path('api/auth/me', auth_views.api_me, name='api_auth_me'),
    path('api/auth/toi', auth_views.api_me, name='api_auth_toi'),
    path('api/auth/logout', auth_views.api_logout, name='api_auth_logout'),
    path('api/auth/dang-xuat', auth_views.api_logout, name='api_auth_dang_xuat'),
    path('api/users', auth_views.api_users_list, name='api_users'),
    path('api/thong-bao', tb_views.api_thong_bao_list, name='api_thong_bao'),
    path('api/thong-bao/', tb_views.api_thong_bao_list, name='api_thong_bao_slash'),
    path('api/thong-bao/dem-chua-doc', tb_views.api_thong_bao_dem_chua_doc, name='api_thong_bao_dem_chua_doc'),
    path('api/thong-bao/<int:thong_bao_id>/da-doc', tb_views.api_thong_bao_da_doc, name='api_thong_bao_da_doc'),
    path('api/thong-ke/tong-hop', tb_views.api_thong_ke_tong_hop, name='api_thong_ke_tong_hop'),
]
