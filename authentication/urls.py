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

    # API Endpoints (ho tro ca ten tieng Viet va tieng Anh)
    path('api/auth/login', views.api_login, name='api_login'),
    path('api/auth/dang-nhap', views.api_login, name='api_dang_nhap'),
    path('api/auth/me', views.api_me, name='api_me'),
    path('api/auth/toi', views.api_me, name='api_toi'),
    path('api/auth/logout', views.api_logout, name='api_logout'),
    path('api/auth/dang-xuat', views.api_logout, name='api_dang_xuat'),
    path('api/users', views.api_users_list, name='api_users_list'),
]
