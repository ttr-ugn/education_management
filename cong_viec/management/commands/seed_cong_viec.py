from django.core.management.base import BaseCommand
from datetime import date, timedelta
from authentication.models import NguoiDung
from cong_viec.models import CongViec, NhatKyCongViec

class Command(BaseCommand):
    help = 'Khởi tạo dữ liệu mẫu phong phú cho phân hệ Theo dõi tiến độ & Điều hành công việc'

    def handle(self, *args, **kwargs):
        u_giamdoc = NguoiDung.objects.filter(ten_dang_nhap='giamdoc_so').first()
        u_phogiamdoc = NguoiDung.objects.filter(ten_dang_nhap='phogiamdoc_so').first()
        u_nam = NguoiDung.objects.filter(ten_dang_nhap='minhcv').first()
        u_thao = NguoiDung.objects.filter(ten_dang_nhap='thaoltk').first()
        u_dung = NguoiDung.objects.filter(ten_dang_nhap='dungpt').first()
        u_hoang = NguoiDung.objects.filter(ten_dang_nhap='hoangnm').first()
        u_lan = NguoiDung.objects.filter(ten_dang_nhap='lanpt').first()

        today = date.today()

        tasks = CongViec.objects.all()
        for task in tasks:
            if task.trang_thai == 'CHO_PHE_DUYET':
                task.trang_thai = 'CHO_DANH_GIA'
            elif task.trang_thai == 'DA_HOAN_THANH':
                task.trang_thai = 'HOAN_THANH'
            task.save()

        self.stdout.write(self.style.SUCCESS(f"Tong so cong viec hien tai: {CongViec.objects.count()}"))
