from django import forms
from .models import HoSoLuuTru

class HoSoLuuTruForm(forms.ModelForm):
    class Meta:
        model = HoSoLuuTru
        fields = ['ma_ho_so', 'tieu_de', 'don_vi', 'nam_tai_lieu', 'thoi_han_bao_quan', 'mo_ta']
