from django import forms
from .models import VanBanDi, VanBanDen

class SoanThaoVanBanForm(forms.ModelForm):
    class Meta:
        model = VanBanDi
        fields = ['trich_yeu', 'loai_van_ban', 'do_khan', 'don_vi_soan_thao', 'noi_nhan', 'noi_dung_tom_tat']

class VanBanDenForm(forms.ModelForm):
    class Meta:
        model = VanBanDen
        fields = ['so_ky_hieu', 'co_quan_ban_hanh', 'ngay_ban_hanh', 'ngay_den', 'trich_yeu', 'loai_van_ban', 'do_khan', 'do_mat', 'han_xu_ly']
