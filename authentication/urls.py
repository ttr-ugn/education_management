from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Giao diện người dùng
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('doi-mat-khau/', views.doi_mat_khau_page, name='doi_mat_khau'),
    path('ho-so-ca-nhan/', views.ho_so_ca_nhan_page, name='ho_so_ca_nhan'),
    path('admin/duyet-tai-khoan/', views.admin_duyet_tai_khoan_page, name='admin_duyet_tai_khoan'),
    path('admin/quan-ly-nguoi-dung/', views.admin_quan_ly_nguoi_dung_page, name='admin_quan_ly_nguoi_dung'),
    path('admin/tao-lanh-dao/', views.admin_tao_lanh_dao_page, name='admin_tao_lanh_dao'),

    # API Xác thực
    path('api/auth/login', views.api_login, name='api_login'),
    path('api/auth/dang-nhap', views.api_login, name='api_dang_nhap'),
    path('api/auth/me', views.api_me, name='api_me'),
    path('api/auth/toi', views.api_me, name='api_toi'),
    path('api/auth/logout', views.api_logout, name='api_logout'),
    path('api/auth/dang-xuat', views.api_logout, name='api_dang_xuat'),
    path('api/auth/register', views.api_register, name='api_register'),
    path('api/auth/dang-ky', views.api_register, name='api_dang_ky'),
    path('api/auth/doi-mat-khau', views.api_doi_mat_khau, name='api_doi_mat_khau'),

    # API Quản lý người dùng
    path('api/users', views.api_users_list, name='api_users_list'),
    path('api/users/<int:user_id>/duyet', views.api_user_duyet, name='api_user_duyet'),
    path('api/users/<int:user_id>/tu-choi', views.api_user_tu_choi, name='api_user_tu_choi'),
    path('api/users/<int:user_id>/khoa', views.api_user_khoa, name='api_user_khoa'),
    path('api/users/<int:user_id>/mo-khoa', views.api_user_mo_khoa, name='api_user_mo_khoa'),
    path('api/users/<int:user_id>/dat-lai-mat-khau', views.api_user_dat_lai_mat_khau, name='api_user_dat_lai_mat_khau'),
    path('api/users/lanh-dao', views.api_user_tao_lanh_dao, name='api_user_tao_lanh_dao'),
]
