from django.urls import path
from . import views

app_name = 'van_ban'

urlpatterns = [
    # Văn bản đi
    path('van-ban-di/', views.van_ban_di_danh_sach, name='van_ban_di_danh_sach'),
    path('van-ban-di/soan-thao/', views.van_ban_di_soan_thao, name='van_ban_di_soan_thao'),
    path('van-ban-di/chi-tiet/', views.van_ban_di_chi_tiet, name='van_ban_di_chi_tiet'),
    path('van-ban-di/kiem-tra/', views.van_ban_di_kiem_tra, name='van_ban_di_kiem_tra'),
    path('van-ban-di/phe-duyet/', views.van_ban_di_phe_duyet, name='van_ban_di_phe_duyet'),
    path('van-ban-di/ban-hanh/', views.van_ban_di_ban_hanh, name='van_ban_di_ban_hanh'),

    # Văn bản đến
    path('van-ban-den/', views.van_ban_den_danh_sach, name='van_ban_den_danh_sach'),
    path('van-ban-den/them/', views.van_ban_den_them, name='van_ban_den_them'),
    path('van-ban-den/chi-tiet/', views.van_ban_den_chi_tiet, name='van_ban_den_chi_tiet'),
    path('van-ban-den/phe-duyet/', views.van_ban_den_phe_duyet, name='van_ban_den_phe_duyet'),

    # API
    path('api/van-ban-di', views.api_van_ban_di_list, name='api_van_ban_di_list'),
    path('api/van-ban-den', views.api_van_ban_den_list, name='api_van_ban_den_list'),
]
