from django.db import models
from werkzeug.security import generate_password_hash, check_password_hash

class NguoiDung(models.Model):
    VAI_TRO_CHOICES = [
        ('VAN_THU', 'Văn thư'),
        ('CHUYEN_VIEN', 'Chuyên viên'),
        ('LANH_DAO', 'Lãnh đạo'),
    ]
    TRANG_THAI_CHOICES = [
        ('CHO_DUYET', 'Chờ duyệt'),
        ('HOAT_DONG', 'Hoạt động'),
        ('TU_CHOI', 'Từ chối'),
        ('BI_KHOA', 'Bị khóa'),
    ]

    nguoi_dung_id = models.AutoField(primary_key=True)
    ten_dang_nhap = models.CharField(max_length=150, unique=True, verbose_name="Tên đăng nhập")
    mat_khau_hash = models.CharField(max_length=255, verbose_name="Mật khẩu mã hóa")
    ho_va_ten = models.CharField(max_length=255, verbose_name="Họ và tên")
    email = models.EmailField(unique=True, verbose_name="Email")
    sdt = models.CharField(max_length=50, blank=True, null=True, verbose_name="Số điện thoại")
    phong_ban = models.CharField(max_length=255, blank=True, null=True, verbose_name="Phòng ban")
    chuc_vu = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chức vụ")
    vai_tro = models.CharField(max_length=50, choices=VAI_TRO_CHOICES, verbose_name="Vai trò")
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='HOAT_DONG', verbose_name="Trạng thái")
    ly_do_tu_choi = models.TextField(blank=True, null=True, verbose_name="Lý do từ chối")
    bat_buoc_doi_mat_khau = models.IntegerField(default=0, verbose_name="Bắt buộc đổi mật khẩu")
    so_lan_dang_nhap_sai = models.IntegerField(default=0, verbose_name="Số lần đăng nhập sai")
    khoa_den = models.DateTimeField(blank=True, null=True, verbose_name="Khóa đến")
    nguoi_tao = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_duyet = models.DateTimeField(blank=True, null=True, verbose_name="Ngày duyệt")
    lan_dang_nhap_cuoi = models.DateTimeField(blank=True, null=True, verbose_name="Lần đăng nhập cuối")

    class Meta:
        db_table = 'nguoi_dung'
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Danh sách Người dùng'

    def __str__(self):
        return f"{self.ho_va_ten} ({self.ten_dang_nhap} - {self.vai_tro})"

    def set_password(self, password):
        self.mat_khau_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.mat_khau_hash, password)

    def to_dict(self):
        return {
            'nguoi_dung_id': self.nguoi_dung_id,
            'ten_dang_nhap': self.ten_dang_nhap,
            'ho_va_ten': self.ho_va_ten,
            'email': self.email,
            'sdt': self.sdt or '',
            'phong_ban': self.phong_ban or '',
            'chuc_vu': self.chuc_vu or '',
            'vai_tro': self.vai_tro,
            'trang_thai': self.trang_thai,
            'bat_buoc_doi_mat_khau': bool(self.bat_buoc_doi_mat_khau),
            'ngay_tao': self.ngay_tao.strftime('%Y-%m-%d %H:%M:%S') if self.ngay_tao else '',
        }
