from django.contrib import admin
from .models import HoSoLuuTru, VanBanBanHanh

@admin.register(HoSoLuuTru)
class HoSoLuuTruAdmin(admin.ModelAdmin):
    list_display = ('ma_ho_so', 'tieu_de', 'don_vi', 'nam_tai_lieu', 'tinh_trang')
    list_filter = ('tinh_trang', 'nam_tai_lieu')
    search_fields = ('ma_ho_so', 'tieu_de')

@admin.register(VanBanBanHanh)
class VanBanBanHanhAdmin(admin.ModelAdmin):
    list_display = ('so_ky_hieu', 'trich_yeu', 'loai_van_ban', 'ngay_ban_hanh', 'nguoi_ky')
