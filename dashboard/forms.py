from django import forms
from .models import NhatKyHeThong

class NhatKyHeThongForm(forms.ModelForm):
    class Meta:
        model = NhatKyHeThong
        fields = ['hanh_dong', 'chi_tiet']
