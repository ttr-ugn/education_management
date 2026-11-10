from django.db import models
from authentication.models import NguoiDung

class HoSoLuuTru(models.Model):
    TINH_TRANG_CHOICES = [
        ('DANG_THU_THAP', 'Đang thu thập'),
        ('DA_NOP_LUU_TRU', 'Đã nộp lưu trữ'),
        ('DA_DONG', 'Đã đóng'),
    ]

    ho_so_id = models.AutoField(primary_key=True)
    ma_ho_so = models.CharField(max_length=100, unique=True, verbose_name="Mã hồ sơ")
    tieu_de = models.CharField(max_length=255, verbose_name="Tiêu đề hồ sơ")
    nguoi_lap = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True)
    don_vi = models.CharField(max_length=255, verbose_name="Đơn vị")
    nam_tai_lieu = models.IntegerField(default=2026, verbose_name="Năm tài liệu")
    thoi_han_bao_quan = models.CharField(max_length=50, default='10 năm')
    so_luong_van_ban = models.IntegerField(default=0)
    tinh_trang = models.CharField(max_length=50, choices=TINH_TRANG_CHOICES, default='DANG_THU_THAP')
    mo_ta = models.TextField(blank=True, null=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ho_so_luu_tru'
        verbose_name = 'Hồ sơ lưu trữ'
        verbose_name_plural = 'Danh sách Hồ sơ lưu trữ'

    def __str__(self):
        return f"{self.ma_ho_so} - {self.tieu_de}"

    def to_dict(self):
        return {
            'ho_so_id': self.ho_so_id,
            'ma_ho_so': self.ma_ho_so,
            'tieu_de': self.tieu_de,
            'don_vi': self.don_vi,
            'nam_tai_lieu': self.nam_tai_lieu,
            'thoi_han_bao_quan': self.thoi_han_bao_quan,
            'so_luong_van_ban': self.so_luong_van_ban,
            'tinh_trang': self.tinh_trang,
        }

class VanBanBanHanh(models.Model):
    van_ban_id = models.AutoField(primary_key=True)
    so_ky_hieu = models.CharField(max_length=100, unique=True)
    trich_yeu = models.TextField()
    loai_van_ban = models.CharField(max_length=100)
    co_quan_ban_hanh = models.CharField(max_length=255, default='Sở Giáo dục và Đào tạo TP. Đà Nẵng')
    nguoi_ky = models.CharField(max_length=255)
    chuc_vu_nguoi_ky = models.CharField(max_length=255)
    ngay_ky = models.DateField()
    ngay_ban_hanh = models.DateField()
    nam_luu_tru = models.IntegerField(default=2026)
    thang_luu_tru = models.IntegerField(default=1)
    quy_luu_tru = models.IntegerField(default=1)
    thoi_han_bao_quan = models.CharField(max_length=50, default='10 năm')
    muc_do_mat = models.CharField(max_length=50, default='THUONG')
    do_khan = models.CharField(max_length=50, default='THUONG')
    ho_so = models.ForeignKey(HoSoLuuTru, on_delete=models.SET_NULL, null=True, blank=True, related_name='van_ban')
    tep_dinh_kem = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'van_ban_ban_hanh'
