from django.urls import path
from . import views

app_name = 'thong_bao'

urlpatterns = [
    path('', views.trang_thong_bao, name='danh_sach'),
    path('api/thong-bao', views.api_thong_bao_list, name='api_thong_bao_list'),
]
