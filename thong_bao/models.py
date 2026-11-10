from django.db import models
from authentication.models import NguoiDung

class ThongBao(models.Model):
    thong_bao_id = models.AutoField(primary_key=True)
    tieu_de = models.CharField(max_length=255, verbose_name="Tiêu đề")
    noi_dung = models.TextField(verbose_name="Nội dung")
    loai = models.CharField(max_length=50, default='Hệ thống')
    muc_do = models.CharField(max_length=50, default='Bình thường')
    nguoi_gui = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True, related_name='thong_bao_gui')
    nguoi_nhan = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, null=True, blank=True, related_name='thong_bao_nhan')
    lien_ket = models.CharField(max_length=500, blank=True, null=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'thong_bao'
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Danh sách Thông báo'

    def __str__(self):
        return self.tieu_de

    def to_dict(self):
        return {
            'thong_bao_id': self.thong_bao_id,
            'tieu_de': self.tieu_de,
            'noi_dung': self.noi_dung,
            'loai': self.loai,
            'muc_do': self.muc_do,
            'ngay_tao': self.ngay_tao.strftime('%Y-%m-%d %H:%M:%S') if self.ngay_tao else '',
        }

class ThongBaoDaDoc(models.Model):
    thong_bao = models.ForeignKey(ThongBao, on_delete=models.CASCADE)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    ngay_doc = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'thong_bao_da_doc'
        unique_together = ('thong_bao', 'nguoi_dung')
