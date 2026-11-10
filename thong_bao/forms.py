from django import forms
from .models import ThongBao

class ThongBaoForm(forms.ModelForm):
    class Meta:
        model = ThongBao
        fields = ['tieu_de', 'noi_dung', 'loai', 'muc_do']
