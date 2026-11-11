from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from dashboard.views import trang_chu, trang_dashboard, trang_thong_ke, api_thong_ke

# Import các hàm view & API trực tiếp từ các module
import authentication.views as auth_views
import van_ban.views as vb_views
import cong_viec.views as cv_views
import ho_so.views as hs_views
import thong_bao.views as tb_views
import chatbot.views as cb_views

urlpatterns = [
    # 1. Trang quản trị chuẩn Django Admin
    path('admin/', admin.site.urls),

    # 2. Trang chủ hệ thống
    path('', trang_chu, name='home'),

    # 3. Định tuyến theo chuẩn App Django (MVT)
    path('auth/', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('van-ban/', include('van_ban.urls')),
    path('cong-viec/', include('cong_viec.urls')),
    path('ho-so/', include('ho_so.urls')),
    path('thong-bao/', include('thong_bao.urls')),
    path('chatbot/', include('chatbot.urls')),

    # 4. Định tuyến tương thích các đường dẫn giao diện (pages/...)
    path('pages/login.html', auth_views.login_page),
    path('pages/register.html', auth_views.register_page),
    path('pages/doi-mat-khau.html', auth_views.doi_mat_khau_page),
    path('pages/ho-so-ca-nhan.html', auth_views.ho_so_ca_nhan_page),
    path('pages/dashboard.html', trang_dashboard),
    path('pages/thong-ke.html', trang_thong_ke),
    path('pages/chatbot.html', cb_views.trang_chatbot),
    path('pages/thong-bao.html', tb_views.trang_thong_bao),

    # Phân hệ Admin
    path('pages/admin/duyet-tai-khoan.html', auth_views.admin_duyet_tai_khoan_page),
    path('pages/admin/quan-ly-nguoi-dung.html', auth_views.admin_quan_ly_nguoi_dung_page),
    path('pages/admin/tao-lanh-dao.html', auth_views.admin_tao_lanh_dao_page),

    # Phân hệ Văn bản đến / đi
    path('pages/van-ban-den/danh-sach.html', vb_views.van_ban_den_danh_sach),
    path('pages/van-ban-den/them.html', vb_views.van_ban_den_them),
    path('pages/van-ban-den/chi-tiet.html', vb_views.van_ban_den_chi_tiet),
    path('pages/van-ban-den/phe-duyet-phan-cong.html', vb_views.van_ban_den_phe_duyet),
    path('pages/van-ban-di/danh-sach.html', vb_views.van_ban_di_danh_sach),
    path('pages/van-ban-di/soan-thao.html', vb_views.van_ban_di_soan_thao),
    path('pages/van-ban-di/chi-tiet.html', vb_views.van_ban_di_chi_tiet),
    path('pages/van-ban-di/kiem-tra.html', vb_views.van_ban_di_kiem_tra),
    path('pages/van-ban-di/phe-duyet.html', vb_views.van_ban_di_phe_duyet),
    path('pages/van-ban-di/ban-hanh.html', vb_views.van_ban_di_ban_hanh),

    # Phân hệ Công việc
    path('pages/cong-viec/danh-sach.html', cv_views.danh_sach_cong_viec),
    path('pages/cong-viec/giao-viec.html', cv_views.giao_viec),
    path('pages/cong-viec/xu-ly.html', cv_views.xu_ly_cong_viec),
    path('pages/cong-viec/phe-duyet-ket-qua.html', cv_views.phe_duyet_ket_qua),

    # Phân hệ Hồ sơ
    path('pages/ho-so/danh-sach.html', hs_views.danh_sach_ho_so),
    path('pages/ho-so/chi-tiet.html', hs_views.chi_tiet_ho_so),
    path('pages/ho-so/them-sua.html', hs_views.them_sua_ho_so),

    # 5. API Endpoints (tương thích 100% với Frontend Fetch)
    # Xác thực & Người dùng
    path('api/auth/login', auth_views.api_login, name='api_auth_login'),
    path('api/auth/dang-nhap', auth_views.api_login, name='api_auth_dang_nhap'),
    path('api/auth/me', auth_views.api_me, name='api_auth_me'),
    path('api/auth/toi', auth_views.api_me, name='api_auth_toi'),
    path('api/auth/logout', auth_views.api_logout, name='api_auth_logout'),
    path('api/auth/dang-xuat', auth_views.api_logout, name='api_auth_dang_xuat'),
    path('api/auth/register', auth_views.api_register, name='api_auth_register'),
    path('api/auth/dang-ky', auth_views.api_register, name='api_auth_dang_ky'),
    path('api/auth/doi-mat-khau', auth_views.api_doi_mat_khau, name='api_auth_doi_mat_khau'),
    path('api/users', auth_views.api_users_list, name='api_users'),
    path('api/users/<int:user_id>/duyet', auth_views.api_user_duyet, name='api_user_duyet'),
    path('api/users/<int:user_id>/tu-choi', auth_views.api_user_tu_choi, name='api_user_tu_choi'),
    path('api/users/<int:user_id>/khoa', auth_views.api_user_khoa, name='api_user_khoa'),
    path('api/users/<int:user_id>/mo-khoa', auth_views.api_user_mo_khoa, name='api_user_mo_khoa'),
    path('api/users/<int:user_id>/dat-lai-mat-khau', auth_views.api_user_dat_lai_mat_khau, name='api_user_dat_lai_mat_khau'),
    path('api/users/lanh-dao', auth_views.api_user_tao_lanh_dao, name='api_user_tao_lanh_dao'),

    # Văn bản đi
    path('api/van-ban-di', vb_views.api_van_ban_di_list, name='api_van_ban_di'),
    path('api/van-ban-di/', vb_views.api_van_ban_di_list, name='api_van_ban_di_slash'),
    path('api/van-ban-di/<int:van_ban_id>', vb_views.api_van_ban_di_detail, name='api_van_ban_di_detail'),
    path('api/van-ban-di/<int:van_ban_id>/trang-thai', vb_views.api_van_ban_di_trang_thai, name='api_van_ban_di_trang_thai'),
    path('api/van-ban-di/<int:van_ban_id>/ban-hanh', vb_views.api_van_ban_di_ban_hanh, name='api_van_ban_di_ban_hanh'),

    # Văn bản đến
    path('api/van-ban-den', vb_views.api_van_ban_den_list, name='api_van_ban_den'),
    path('api/van-ban-den/<int:van_ban_id>', vb_views.api_van_ban_den_detail, name='api_van_ban_den_detail'),
    path('api/van-ban-den/<int:van_ban_id>/phan-cong', vb_views.api_van_ban_den_phan_cong, name='api_van_ban_den_phan_cong'),

    # Công việc
    path('api/cong-viec', cv_views.api_cong_viec_list, name='api_cong_viec'),
    path('api/cong-viec/<int:cong_viec_id>', cv_views.api_cong_viec_detail, name='api_cong_viec_detail'),
    path('api/cong-viec/<int:cong_viec_id>/tien-do', cv_views.api_cong_viec_tien_do, name='api_cong_viec_tien_do'),
    path('api/cong-viec/<int:cong_viec_id>/danh-gia', cv_views.api_cong_viec_danh_gia, name='api_cong_viec_danh_gia'),
    path('api/cong-viec/thong-ke', cv_views.api_cong_viec_thong_ke, name='api_cong_viec_thong_ke'),

    # Hồ sơ lưu trữ
    path('api/ho-so', hs_views.api_ho_so_list, name='api_ho_so'),
    path('api/ho-so/<int:ho_so_id>', hs_views.api_ho_so_detail, name='api_ho_so_detail'),
    path('api/ho-so/<int:ho_so_id>/van-ban', hs_views.api_ho_so_van_ban, name='api_ho_so_van_ban'),
    path('api/ho-so/<int:ho_so_id>/van-ban-kha-dung', hs_views.api_ho_so_van_ban_kha_dung, name='api_ho_so_van_ban_kha_dung'),
    path('api/ho-so/<int:ho_so_id>/them-van-ban', hs_views.api_ho_so_them_van_ban, name='api_ho_so_them_van_ban'),
    path('api/ho-so/<int:ho_so_id>/xoa-van-ban', hs_views.api_ho_so_xoa_van_ban, name='api_ho_so_xoa_van_ban'),
    path('api/ho-so/<int:ho_so_id>/nop-luu-tru', hs_views.api_ho_so_nop_luu_tru, name='api_ho_so_nop_luu_tru'),
    path('api/ho-so/<int:ho_so_id>/dong', hs_views.api_ho_so_dong, name='api_ho_so_dong'),

    # Thông báo & Nhắc nhở
    path('api/thong-bao', tb_views.api_thong_bao_list, name='api_thong_bao'),
    path('api/thong-bao/<int:thong_bao_id>', tb_views.api_thong_bao_detail, name='api_thong_bao_detail'),
    path('api/thong-bao/<int:thong_bao_id>/da-doc', tb_views.api_thong_bao_da_doc, name='api_thong_bao_da_doc'),
    path('api/thong-bao/dem-chua-doc', tb_views.api_thong_bao_dem_chua_doc, name='api_thong_bao_dem_chua_doc'),
    path('api/thong-bao/doc-tat-ca', tb_views.api_thong_bao_doc_tat_ca, name='api_thong_bao_doc_tat_ca'),
    path('api/thong-bao/kiem-tra-den-han', tb_views.api_thong_bao_kiem_tra_den_han, name='api_thong_bao_kiem_tra_den_han'),

    # Chatbot & Mẫu văn bản
    path('api/chatbot', cb_views.api_hoi_dap, name='api_chatbot'),
    path('api/chatbot/hoi-dap', cb_views.api_hoi_dap, name='api_chatbot_hoi_dap'),
    path('api/chatbot/kho-mau', cb_views.api_kho_mau, name='api_chatbot_kho_mau'),
    path('api/chatbot/mau-van-ban/<int:mau_id>', cb_views.api_mau_van_ban_detail, name='api_chatbot_mau_detail'),
    path('api/chatbot/mau-van-ban/<int:mau_id>/tai-ve', cb_views.api_mau_van_ban_tai_ve, name='api_chatbot_mau_tai_ve'),
    path('api/chatbot/xem-truoc/<str:loai>/<int:item_id>', cb_views.api_xem_truoc_tai_lieu, name='api_chatbot_xem_truoc'),

    # Báo cáo Thống kê tổng hợp điều hành văn bản
    path('api/thong-ke', api_thong_ke, name='api_thong_ke'),
    path('api/dashboard/thong-ke', api_thong_ke, name='api_dashboard_thong_ke'),

    # 6. Phục vụ static assets (CSS, JS, Assets)
    re_path(r'^(?P<path>(css|js|assets)/.*)$', serve, {'document_root': settings.BASE_DIR / 'static'}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'static'}),
]
