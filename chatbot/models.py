from django.db import models
from authentication.models import NguoiDung

class MauVanBan(models.Model):
    mau_id = models.AutoField(primary_key=True)
    ma_mau = models.CharField(max_length=100, unique=True)
    ten_mau = models.CharField(max_length=255)
    loai_van_ban = models.CharField(max_length=100)
    linh_vuc = models.CharField(max_length=100)
    co_quan_ban_hanh = models.CharField(max_length=255, default='SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG')
    noi_dung_html = models.TextField()
    noi_dung_text = models.TextField()
    luot_xem = models.IntegerField(default=0)
    luot_tai = models.IntegerField(default=0)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mau_van_ban'
        verbose_name = 'Mẫu văn bản'
        verbose_name_plural = 'Kho mẫu văn bản'

    def __str__(self):
        return f"{self.ma_mau} - {self.ten_mau}"

    def to_dict(self):
        return {
            'mau_id': self.mau_id,
            'id': self.mau_id,
            'ma_mau': self.ma_mau,
            'ten_mau': self.ten_mau,
            'loai_van_ban': self.loai_van_ban,
            'linh_vuc': self.linh_vuc,
            'tham_quyen_ky': 'Giám đốc Sở' if self.loai_van_ban in ('Quyết định', 'Kế hoạch') else ('Trưởng phòng' if self.loai_van_ban == 'Tờ trình' else 'Lãnh đạo Sở'),
            'mo_ta': f"Mẫu {self.loai_van_ban.lower()} chuẩn thể thức Nghị định 30/2020/NĐ-CP - Lĩnh vực {self.linh_vuc}.",
            'noi_dung_html': self.noi_dung_html,
            'noi_dung_text': self.noi_dung_text,
            'luot_xem': self.luot_xem,
            'luot_tai': self.luot_tai,
        }

class LichSuChat(models.Model):
    tin_nhan_id = models.AutoField(primary_key=True)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, null=True, blank=True)
    cau_hoi = models.TextField()
    cau_tra_loi = models.TextField()
    mau_de_xuat_ids = models.CharField(max_length=255, blank=True, null=True)
    thoi_gian = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lich_su_chat'
