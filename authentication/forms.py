from django import forms
from .models import NguoiDung

class LoginForm(forms.Form):
    ten_dang_nhap = forms.CharField(max_length=150, label="Tên đăng nhập")
    mat_khau = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")

class RegisterForm(forms.ModelForm):
    mat_khau = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    xac_nhan_mat_khau = forms.CharField(widget=forms.PasswordInput, label="Xác nhận mật khẩu")
    ma_noi_bo = forms.CharField(required=False, label="Mã nội bộ (dành cho Văn thư)")

    class Meta:
        model = NguoiDung
        fields = ['ten_dang_nhap', 'ho_va_ten', 'email', 'sdt', 'phong_ban', 'chuc_vu', 'vai_tro']

class DoiMatKhauForm(forms.Form):
    mat_khau_cu = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu cũ")
    mat_khau_moi = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu mới")
    xac_nhan_mat_khau_moi = forms.CharField(widget=forms.PasswordInput, label="Xác nhận mật khẩu mới")
