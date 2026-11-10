from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from dashboard.views import trang_chu

# Import các hàm API trực tiếp để tránh trùng lặp app_name namespace
import authentication.views as auth_views
import van_ban.views as vb_views
import cong_viec.views as cv_views
import ho_so.views as hs_views
import thong_bao.views as tb_views
import chatbot.views as cb_views

urlpatterns = [
    # Trang quản trị chuẩn Django Admin
    path('admin/', admin.site.urls),

    # Trang chủ hệ thống
    path('', trang_chu, name='home'),

    # Định tuyến tới từng Module (Django Apps)
    path('auth/', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('van-ban/', include('van_ban.urls')),
    path('cong-viec/', include('cong_viec.urls')),
    path('ho-so/', include('ho_so.urls')),
    path('thong-bao/', include('thong_bao.urls')),
    path('chatbot/', include('chatbot.urls')),

    # API Endpoints (tương thích 100% với Frontend Fetch hiện tại)
    path('api/auth/login', auth_views.api_login, name='api_auth_login'),
    path('api/auth/me', auth_views.api_me, name='api_auth_me'),
    path('api/auth/logout', auth_views.api_logout, name='api_auth_logout'),
    path('api/users', auth_views.api_users_list, name='api_users'),
    path('api/van-ban-di', vb_views.api_van_ban_di_list, name='api_van_ban_di'),
    path('api/cong-viec', cv_views.api_cong_viec_list, name='api_cong_viec'),
    path('api/ho-so', hs_views.api_ho_so_list, name='api_ho_so'),
    path('api/thong-bao', tb_views.api_thong_bao_list, name='api_thong_bao'),
    path('api/chatbot/hoi-dap', cb_views.api_hoi_dap, name='api_chatbot_hoi_dap'),

    # Phục vụ các file tĩnh views/ (HTML, CSS, JS, Assets)
    re_path(r'^(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'views'}),
]
