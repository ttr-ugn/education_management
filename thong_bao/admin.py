from django.contrib import admin
from .models import ThongBao, ThongBaoDaDoc

@admin.register(ThongBao)
class ThongBaoAdmin(admin.ModelAdmin):
    list_display = ('tieu_de', 'loai', 'muc_do', 'ngay_tao')
    list_filter = ('loai', 'muc_do')
    search_fields = ('tieu_de', 'noi_dung')

@admin.register(ThongBaoDaDoc)
class ThongBaoDaDocAdmin(admin.ModelAdmin):
    list_display = ('thong_bao', 'nguoi_dung', 'ngay_doc')
