from django.urls import path
from . import views

app_name = 'ho_so'

urlpatterns = [
    path('danh-sach/', views.danh_sach_ho_so, name='danh_sach'),
    path('chi-tiet/', views.chi_tiet_ho_so, name='chi_tiet'),
    path('them-sua/', views.them_sua_ho_so, name='them_sua'),
    path('api/ho-so', views.api_ho_so_list, name='api_ho_so_list'),
]
