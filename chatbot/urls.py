from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.trang_chatbot, name='trang_chatbot'),
    path('api/chatbot/hoi-dap', views.api_hoi_dap, name='api_hoi_dap'),
    path('api/chatbot/kho-mau', views.api_kho_mau, name='api_kho_mau'),
    path('api/chatbot/mau-van-ban/<int:mau_id>', views.api_mau_van_ban_detail, name='api_mau_van_ban_detail'),
    path('api/chatbot/mau-van-ban/<int:mau_id>/tai-ve', views.api_mau_van_ban_tai_ve, name='api_mau_van_ban_tai_ve'),
    path('api/chatbot/xem-truoc/<str:loai>/<int:item_id>', views.api_xem_truoc_tai_lieu, name='api_xem_truoc_tai_lieu'),
    path('api/chatbot/upload', views.api_upload_kho_luu_tru, name='api_upload_kho_luu_tru'),
]
