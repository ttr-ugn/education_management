from django.contrib import admin
from .models import MauVanBan, LichSuChat

@admin.register(MauVanBan)
class MauVanBanAdmin(admin.ModelAdmin):
    list_display = ('ma_mau', 'ten_mau', 'loai_van_ban', 'linh_vuc')
    search_fields = ('ma_mau', 'ten_mau', 'loai_van_ban')

@admin.register(LichSuChat)
class LichSuChatAdmin(admin.ModelAdmin):
    list_display = ('tin_nhan_id', 'cau_hoi', 'thoi_gian')
