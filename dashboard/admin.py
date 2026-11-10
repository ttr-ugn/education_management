from django.contrib import admin
from .models import NhatKyHeThong

@admin.register(NhatKyHeThong)
class NhatKyHeThongAdmin(admin.ModelAdmin):
    list_display = ('hanh_dong', 'thoi_gian')
