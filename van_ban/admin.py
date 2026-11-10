from django.contrib import admin
from .models import VanBanDi, VanBanDen, LichSuXuLyVanBan

@admin.register(VanBanDi)
class VanBanDiAdmin(admin.ModelAdmin):
    list_display = ('so_ky_hieu', 'trich_yeu', 'loai_van_ban', 'trang_thai', 'nguoi_soan', 'ngay_tao')
    list_filter = ('trang_thai', 'loai_van_ban')
    search_fields = ('so_ky_hieu', 'trich_yeu')

@admin.register(VanBanDen)
class VanBanDenAdmin(admin.ModelAdmin):
    list_display = ('so_ky_hieu', 'co_quan_ban_hanh', 'trich_yeu', 'loai_van_ban', 'trang_thai')
    list_filter = ('trang_thai', 'loai_van_ban')
    search_fields = ('so_ky_hieu', 'trich_yeu', 'co_quan_ban_hanh')

@admin.register(LichSuXuLyVanBan)
class LichSuXuLyVanBanAdmin(admin.ModelAdmin):
    list_display = ('van_ban', 'nguoi_thuc_hien', 'hanh_dong', 'thoi_gian')
