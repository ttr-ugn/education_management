from django.contrib import admin
from .models import NguoiDung

@admin.register(NguoiDung)
class NguoiDungAdmin(admin.ModelAdmin):
    list_display = ('ten_dang_nhap', 'ho_va_ten', 'email', 'vai_tro', 'trang_thai', 'phong_ban')
    list_filter = ('vai_tro', 'trang_thai', 'phong_ban')
    search_fields = ('ten_dang_nhap', 'ho_va_ten', 'email')
