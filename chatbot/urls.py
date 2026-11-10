from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.trang_chatbot, name='trang_chatbot'),
    path('api/chatbot/hoi-dap', views.api_hoi_dap, name='api_hoi_dap'),
]
