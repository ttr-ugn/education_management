from django.contrib import admin
from .models import CongViec, NhatKyCongViec

@admin.register(CongViec)
class CongViecAdmin(admin.ModelAdmin):
    list_display = ('ten_cong_viec', 'phong_ban', 'han_hoan_thanh', 'do_uu_tien', 'tien_do', 'trang_thai')
    list_filter = ('trang_thai', 'do_uu_tien', 'phong_ban')
    search_fields = ('ten_cong_viec', 'noi_dung')

@admin.register(NhatKyCongViec)
class NhatKyCongViecAdmin(admin.ModelAdmin):
    list_display = ('cong_viec', 'tien_do_cu', 'tien_do_moi', 'thoi_gian')
