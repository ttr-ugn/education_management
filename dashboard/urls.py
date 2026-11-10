from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.trang_dashboard, name='dashboard'),
    path('thong-ke/', views.trang_thong_ke, name='thong_ke'),
]
