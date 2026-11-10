from django.contrib import admin
from django.urls import path, include
from dashboard.views import trang_chu, trang_dashboard
import authentication.views as auth_views
import van_ban.views as vb_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', trang_chu, name='home'),
    path('auth/', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('van-ban/', include('van_ban.urls')),

    # Giao diện người dùng & Quản trị
    path('pages/login.html', auth_views.login_page),
    path('pages/register.html', auth_views.register_page),
    path('pages/doi-mat-khau.html', auth_views.doi_mat_khau_page),
    path('pages/ho-so-ca-nhan.html', auth_views.ho_so_ca_nhan_page),
    path('pages/dashboard.html', trang_dashboard),
    path('pages/admin/duyet-tai-khoan.html', auth_views.admin_duyet_tai_khoan_page),
    path('pages/admin/quan-ly-nguoi-dung.html', auth_views.admin_quan_ly_nguoi_dung_page),
    path('pages/admin/tao-lanh-dao.html', auth_views.admin_tao_lanh_dao_page),

    # Giao diện Văn bản đến / Văn bản đi & Dự thảo
    path('pages/van-ban-den/danh-sach.html', vb_views.van_ban_den_danh_sach),
    path('pages/van-ban-den/them.html', vb_views.van_ban_den_them),
    path('pages/van-ban-den/chi-tiet.html', vb_views.van_ban_den_chi_tiet),
    path('pages/van-ban-den/phe-duyet-phan-cong.html', vb_views.van_ban_den_phe_duyet),
    path('pages/van-ban-di/danh-sach.html', vb_views.van_ban_di_danh_sach),
    path('pages/van-ban-di/soan-thao.html', vb_views.van_ban_di_soan_thao),
    path('pages/van-ban-di/chi-tiet.html', vb_views.van_ban_di_chi_tiet),
    path('pages/van-ban-di/kiem-tra.html', vb_views.van_ban_di_kiem_tra),
    path('pages/van-ban-di/phe-duyet.html', vb_views.van_ban_di_phe_duyet),
    path('pages/van-ban-di/ban-hanh.html', vb_views.van_ban_di_ban_hanh),

    # API Endpoints
    path('api/auth/login', auth_views.api_login, name='api_auth_login'),
    path('api/auth/dang-nhap', auth_views.api_login, name='api_auth_dang_nhap'),
    path('api/auth/me', auth_views.api_me, name='api_auth_me'),
    path('api/auth/toi', auth_views.api_me, name='api_auth_toi'),
    path('api/auth/logout', auth_views.api_logout, name='api_auth_logout'),
    path('api/auth/dang-xuat', auth_views.api_logout, name='api_auth_dang_xuat'),
    path('api/auth/register', auth_views.api_register, name='api_auth_register'),
    path('api/auth/dang-ky', auth_views.api_register, name='api_auth_dang_ky'),
    path('api/auth/doi-mat-khau', auth_views.api_doi_mat_khau, name='api_auth_doi_mat_khau'),
    path('api/users', auth_views.api_users_list, name='api_users'),
    path('api/users/<int:user_id>/duyet', auth_views.api_user_duyet, name='api_user_duyet'),
    path('api/users/<int:user_id>/tu-choi', auth_views.api_user_tu_choi, name='api_user_tu_choi'),
    path('api/users/<int:user_id>/khoa', auth_views.api_user_khoa, name='api_user_khoa'),
    path('api/users/<int:user_id>/mo-khoa', auth_views.api_user_mo_khoa, name='api_user_mo_khoa'),
    path('api/users/<int:user_id>/dat-lai-mat-khau', auth_views.api_user_dat_lai_mat_khau, name='api_user_dat_lai_mat_khau'),
    path('api/users/lanh-dao', auth_views.api_user_tao_lanh_dao, name='api_user_tao_lanh_dao'),
    path('api/van-ban-di', vb_views.api_van_ban_di_list, name='api_van_ban_di'),
    path('api/van-ban-di/', vb_views.api_van_ban_di_list, name='api_van_ban_di_slash'),
    path('api/van-ban-di/<int:van_ban_id>', vb_views.api_van_ban_di_detail, name='api_van_ban_di_detail'),
    path('api/van-ban-di/<int:van_ban_id>/trang-thai', vb_views.api_van_ban_di_trang_thai, name='api_van_ban_di_trang_thai'),
    path('api/van-ban-di/<int:van_ban_id>/ban-hanh', vb_views.api_van_ban_di_ban_hanh, name='api_van_ban_di_ban_hanh'),
    path('api/van-ban-den', vb_views.api_van_ban_den_list, name='api_van_ban_den'),
    path('api/van-ban-den/<int:van_ban_id>', vb_views.api_van_ban_den_detail, name='api_van_ban_den_detail'),
    path('api/van-ban-den/<int:van_ban_id>/phan-cong', vb_views.api_van_ban_den_phan_cong, name='api_van_ban_den_phan_cong'),
]
