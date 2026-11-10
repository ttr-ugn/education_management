from django import forms
from .models import MauVanBan

class MauVanBanForm(forms.ModelForm):
    class Meta:
        model = MauVanBan
        fields = ['ma_mau', 'ten_mau', 'loai_van_ban', 'linh_vuc', 'noi_dung_html', 'noi_dung_text']
