from django import forms
from .models import CongViec

class CongViecForm(forms.ModelForm):
    class Meta:
        model = CongViec
        fields = ['ten_cong_viec', 'noi_dung', 'phong_ban', 'han_hoan_thanh', 'do_uu_tien']
