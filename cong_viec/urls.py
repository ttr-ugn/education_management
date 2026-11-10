from django.urls import path
from . import views

app_name = 'cong_viec'

urlpatterns = [
    path('danh-sach/', views.danh_sach_cong_viec, name='danh_sach'),
    path('giao-viec/', views.giao_viec, name='giao_viec'),
    path('xu-ly/', views.xu_ly_cong_viec, name='xu_ly'),
    path('phe-duyet-ket-qua/', views.phe_duyet_ket_qua, name='phe_duyet_ket_qua'),
    path('api/cong-viec', views.api_cong_viec_list, name='api_cong_viec_list'),
]
