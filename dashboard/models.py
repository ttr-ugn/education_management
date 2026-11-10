from django.db import models

class NhatKyHeThong(models.Model):
    hanh_dong = models.CharField(max_length=255)
    chi_tiet = models.TextField(blank=True, null=True)
    thoi_gian = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nhat_ky_he_thong'
