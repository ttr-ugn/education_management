from django.db import models
from authentication.models import NguoiDung

class VanBanDi(models.Model):
    TRANG_THAI_CHOICES = [
        ('CHO_VAN_THU_KIEM_TRA', 'Chờ Văn thư kiểm tra'),
        ('VAN_THU_TRA_LAI', 'Văn thư trả lại'),
        ('CHO_LANH_DAO_KY', 'Chờ Lãnh đạo ký'),
        ('LANH_DAO_TRA_LAI', 'Lãnh đạo trả lại'),
        ('DA_KY_CHO_BAN_HANH', 'Đã ký chờ ban hành'),
        ('DA_BAN_HANH', 'Đã ban hành'),
    ]

    van_ban_id = models.AutoField(primary_key=True)
    so_ky_hieu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Số ký hiệu")
    trich_yeu = models.TextField(verbose_name="Trích yếu")
    loai_van_ban = models.CharField(max_length=100, verbose_name="Loại văn bản")
    do_khan = models.CharField(max_length=50, default='Bình thường', verbose_name="Độ khẩn")
    don_vi_soan_thao = models.CharField(max_length=255, verbose_name="Đơn vị soạn thảo")
    noi_nhan = models.CharField(max_length=255, verbose_name="Nơi nhận")
    noi_dung_tom_tat = models.TextField(blank=True, null=True, verbose_name="Nội dung tóm tắt")
    file_goc_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Đường dẫn file gốc")
    file_goc_ten = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên file gốc")
    file_goc_dung_luong = models.CharField(max_length=50, blank=True, null=True, verbose_name="Dung lượng file")
    file_da_ky_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="File đã ký")
    file_da_ky_ten = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên file đã ký")
    nguoi_soan = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='van_ban_soan', verbose_name="Người soạn")
    van_thu = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True, related_name='van_ban_van_thu')
    lanh_dao_ky = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True, related_name='van_ban_lanh_dao')
    lanh_dao_ky_ten = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên lãnh đạo ký")
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='CHO_VAN_THU_KIEM_TRA')
    y_kien_van_thu = models.TextField(blank=True, null=True, verbose_name="Ý kiến Văn thư")
    y_kien_lanh_dao = models.TextField(blank=True, null=True, verbose_name="Ý kiến Lãnh đạo")
    ky_so_trang = models.IntegerField(blank=True, null=True)
    ky_so_x = models.FloatField(blank=True, null=True)
    ky_so_y = models.FloatField(blank=True, null=True)
    thoi_gian_ky = models.DateTimeField(blank=True, null=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_trinh_van_thu = models.DateTimeField(blank=True, null=True)
    ngay_trinh_lanh_dao = models.DateTimeField(blank=True, null=True)
    ngay_ban_hanh = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'van_ban_di'
        verbose_name = 'Văn bản đi'
        verbose_name_plural = 'Danh sách Văn bản đi'

    def __str__(self):
        return f"{self.so_ky_hieu or 'Dự thảo'} - {self.trich_yeu[:40]}"

    def to_dict(self):
        author_name = self.nguoi_soan.ho_va_ten if self.nguoi_soan else 'Nguyễn Văn Nam'
        leader_name = self.lanh_dao_ky_ten or (self.lanh_dao_ky.ho_va_ten if self.lanh_dao_ky else 'Lãnh đạo Sở')
        formatted_date = self.ngay_tao.strftime('%Y-%m-%d %H:%M:%S') if self.ngay_tao else ''
        return {
            'id': self.van_ban_id,
            'van_ban_id': self.van_ban_id,
            'so_ky_hieu': self.so_ky_hieu or '',
            'trich_yeu': self.trich_yeu,
            'loai_van_ban': self.loai_van_ban,
            'do_khan': self.do_khan,
            'don_vi_soan_thao': self.don_vi_soan_thao or 'Phòng Giáo dục Trung học',
            'noi_nhan': self.noi_nhan,
            'noi_dung_tom_tat': self.noi_dung_tom_tat or '',
            'trang_thai': self.trang_thai,
            'nguoi_soan_ten': author_name,
            'nguoi_soan_thao': author_name,
            'lanh_dao_ky': leader_name,
            'lanh_dao_ky_ten': leader_name,
            'ngay_tao': formatted_date,
            'ngay_soan': formatted_date,
            'file_goc_ten': self.file_goc_ten or '',
            'file_da_ky_ten': self.file_da_ky_ten or '',
            'co_file_da_ky': bool(self.file_da_ky_path or self.file_da_ky_ten),
            'co_file_goc': bool(self.file_goc_path or self.file_goc_ten),
            'ly_do_chinh_sua': self.y_kien_van_thu or self.y_kien_lanh_dao or '',
        }

class LichSuXuLyVanBan(models.Model):
    van_ban = models.ForeignKey(VanBanDi, on_delete=models.CASCADE, related_name='lich_su')
    nguoi_thuc_hien = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    hanh_dong = models.CharField(max_length=255)
    trang_thai_truoc = models.CharField(max_length=100, blank=True, null=True)
    trang_thai_sau = models.CharField(max_length=100)
    noi_dung = models.TextField(blank=True, null=True)
    thoi_gian = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lich_su_xu_ly_van_ban'

class VanBanDen(models.Model):
    van_ban_id = models.AutoField(primary_key=True)
    so_den = models.IntegerField(blank=True, null=True)
    so_ky_hieu = models.CharField(max_length=100)
    co_quan_ban_hanh = models.CharField(max_length=255)
    ngay_ban_hanh = models.DateField(blank=True, null=True)
    ngay_den = models.DateField(blank=True, null=True)
    trich_yeu = models.TextField()
    loai_van_ban = models.CharField(max_length=100)
    do_khan = models.CharField(max_length=50, default='Bình thường')
    do_mat = models.CharField(max_length=50, default='Thường')
    nguoi_chi_dao = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True, related_name='vb_den_chi_dao')
    nguoi_chu_tri = models.ForeignKey(NguoiDung, on_delete=models.SET_NULL, null=True, blank=True, related_name='vb_den_chu_tri')
    trang_thai = models.CharField(max_length=50, default='CHO_TIEP_NHAN')
    han_xu_ly = models.DateField(blank=True, null=True)
    noi_dung_chi_dao = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'van_ban_den'
        verbose_name = 'Văn bản đến'
        verbose_name_plural = 'Danh sách Văn bản đến'

    def to_dict(self):
        return {
            'van_ban_id': self.van_ban_id,
            'so_den': self.so_den or '',
            'so_ky_hieu': self.so_ky_hieu,
            'co_quan_ban_hanh': self.co_quan_ban_hanh,
            'ngay_ban_hanh': self.ngay_ban_hanh.strftime('%Y-%m-%d') if self.ngay_ban_hanh else '',
            'ngay_den': self.ngay_den.strftime('%Y-%m-%d') if self.ngay_den else '',
            'trich_yeu': self.trich_yeu,
            'loai_van_ban': self.loai_van_ban,
            'do_khan': self.do_khan,
            'do_mat': self.do_mat,
            'nguoi_chi_dao_ten': self.nguoi_chi_dao.ho_va_ten if self.nguoi_chi_dao else '',
            'nguoi_chu_tri_ten': self.nguoi_chu_tri.ho_va_ten if self.nguoi_chu_tri else '',
            'trang_thai': self.trang_thai,
            'han_xu_ly': self.han_xu_ly.strftime('%Y-%m-%d') if self.han_xu_ly else '',
            'noi_dung_chi_dao': self.noi_dung_chi_dao or '',
        }
