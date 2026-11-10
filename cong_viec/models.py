from django.db import models
from authentication.models import NguoiDung

class CongViec(models.Model):
    DO_UU_TIEN_CHOICES = [
        ('THAP', 'Thấp'),
        ('TRUNG_BINH', 'Trung bình'),
        ('CAO', 'Cao'),
        ('KHAN_CAP', 'Khẩn cấp'),
    ]
    TRANG_THAI_CHOICES = [
        ('CHUA_THUC_HIEN', 'Chưa thực hiện'),
        ('DANG_THUC_HIEN', 'Đang thực hiện'),
        ('CHO_DANH_GIA', 'Chờ đánh giá'),
        ('HOAN_THANH', 'Hoàn thành'),
        ('QUA_HAN', 'Quá hạn'),
    ]

    cong_viec_id = models.AutoField(primary_key=True)
    ten_cong_viec = models.CharField(max_length=255, verbose_name="Tên công việc")
    noi_dung = models.TextField(blank=True, null=True, verbose_name="Nội dung")
    nguoi_giao = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True, related_name='cong_viec_giao')
    nguoi_xu_ly = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True, related_name='cong_viec_xu_ly')
    phong_ban = models.CharField(max_length=255, verbose_name="Phòng ban")
    ngay_giao = models.DateField(auto_now_add=True)
    han_hoan_thanh = models.DateField()
    do_uu_tien = models.CharField(max_length=50, choices=DO_UU_TIEN_CHOICES, default='TRUNG_BINH')
    tien_do = models.IntegerField(default=0, verbose_name="Tiến độ (%)")
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='CHUA_THUC_HIEN')
    ket_qua_bao_cao = models.TextField(blank=True, null=True)
    danh_gia_lanh_dao = models.TextField(blank=True, null=True)
    tep_dinh_kem_ket_qua = models.CharField(max_length=500, blank=True, null=True)
    so_ky_hieu_vb = models.CharField(max_length=100, blank=True, null=True)
    trich_yeu_vb = models.TextField(blank=True, null=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cong_viec'
        verbose_name = 'Công việc'
        verbose_name_plural = 'Danh sách Công việc'

    def __str__(self):
        return f"{self.ten_cong_viec} ({self.trang_thai} - {self.tien_do}%)"

    def to_dict(self):
        status = self.trang_thai
        if status == 'CHO_PHE_DUYET':
            status = 'CHO_DANH_GIA'
        elif status == 'DA_HOAN_THANH':
            status = 'HOAN_THANH'

        return {
            'id': self.cong_viec_id,
            'cong_viec_id': self.cong_viec_id,
            'ten_cong_viec': self.ten_cong_viec,
            'noi_dung': self.noi_dung or '',
            'nguoi_giao': self.nguoi_giao.ho_va_ten if self.nguoi_giao else 'Lãnh đạo Sở',
            'nguoi_giao_ten': self.nguoi_giao.ho_va_ten if self.nguoi_giao else 'Lãnh đạo Sở',
            'nguoi_xu_ly': self.nguoi_xu_ly.ho_va_ten if self.nguoi_xu_ly else 'Cán bộ xử lý',
            'nguoi_xu_ly_ten': self.nguoi_xu_ly.ho_va_ten if self.nguoi_xu_ly else 'Cán bộ xử lý',
            'phong_ban': self.phong_ban or 'Văn phòng Sở',
            'han_hoan_thanh': self.han_hoan_thanh.strftime('%Y-%m-%d') if self.han_hoan_thanh else '',
            'do_uu_tien': self.do_uu_tien or 'TRUNG_BINH',
            'tien_do': self.tien_do if self.tien_do is not None else 0,
            'trang_thai': status,
            'ket_qua_bao_cao': self.ket_qua_bao_cao or '',
            'danh_gia_lanh_dao': self.danh_gia_lanh_dao or '',
            'tep_dinh_kem_ket_qua': self.tep_dinh_kem_ket_qua or '',
            'so_ky_hieu_vb': self.so_ky_hieu_vb or '',
            'trich_yeu_vb': self.trich_yeu_vb or '',
            'ngay_tao': self.ngay_tao.strftime('%Y-%m-%d %H:%M:%S') if self.ngay_tao else '',
            'nhat_ky': [
                {
                    'thoi_gian': nk.thoi_gian.strftime('%d/%m/%Y %H:%M'),
                    'nguoi_cap_nhat_ten': nk.nguoi_cap_nhat.ho_va_ten if nk.nguoi_cap_nhat else 'Cán bộ',
                    'tien_do_cu': nk.tien_do_cu,
                    'tien_do_moi': nk.tien_do_moi,
                    'noi_dung_ghi_chu': nk.noi_dung_ghi_chu
                }
                for nk in self.nhat_ky.all().order_by('-thoi_gian')
            ]
        }

class NhatKyCongViec(models.Model):
    nhat_ky_id = models.AutoField(primary_key=True)
    cong_viec = models.ForeignKey(CongViec, on_delete=models.CASCADE, related_name='nhat_ky')
    nguoi_cap_nhat = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True)
    tien_do_cu = models.IntegerField(default=0)
    tien_do_moi = models.IntegerField(default=0)
    noi_dung_ghi_chu = models.TextField()
    thoi_gian = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nhat_ky_cong_viec'
