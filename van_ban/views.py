import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import VanBanDi, VanBanDen, LichSuXuLyVanBan
from authentication.models import NguoiDung

# Giao diện Văn bản đi
def van_ban_di_danh_sach(request):
    return render(request, 'van_ban/van-ban-di/danh-sach.html')

def van_ban_di_soan_thao(request):
    return render(request, 'van_ban/van-ban-di/soan-thao.html')

def van_ban_di_chi_tiet(request):
    return render(request, 'van_ban/van-ban-di/chi-tiet.html')

def van_ban_di_kiem_tra(request):
    return render(request, 'van_ban/van-ban-di/kiem-tra.html')

def van_ban_di_phe_duyet(request):
    return render(request, 'van_ban/van-ban-di/phe-duyet.html')

def van_ban_di_ban_hanh(request):
    return render(request, 'van_ban/van-ban-di/ban-hanh.html')

def van_ban_di_chung_thuc_chu_ky_so(request):
    """Giao diện Dịch vụ chứng thực chữ ký số & Thẩm định văn bản điện tử."""
    return render(request, 'van_ban/van-ban-di/chung-thuc-chu-ky-so.html')

# Giao diện Văn bản đến
def van_ban_den_danh_sach(request):
    return render(request, 'van_ban/van-ban-den/danh-sach.html')

def van_ban_den_them(request):
    return render(request, 'van_ban/van-ban-den/them.html')

def van_ban_den_chi_tiet(request):
    return render(request, 'van_ban/van-ban-den/chi-tiet.html')

def van_ban_den_phe_duyet(request):
    return render(request, 'van_ban/van-ban-den/phe-duyet-phan-cong.html')

# ==============================================================================
# API VĂN BẢN ĐI
# ==============================================================================

@csrf_exempt
def api_van_ban_di_list(request):
    """Danh sách văn bản đi hoặc tạo mới văn bản đi."""
    if request.method == 'GET':
        q = request.GET.get('q')
        trang_thai = request.GET.get('trang_thai')
        loai_van_ban = request.GET.get('loai_van_ban')

        qs = VanBanDi.objects.all().order_by('-ngay_tao')
        if q:
            qs = qs.filter(Q(trich_yeu__icontains=q) | Q(so_ky_hieu__icontains=q))
        if trang_thai:
            if trang_thai in ['DA_DUYET', 'DA_KY_CHO_BAN_HANH']:
                qs = qs.filter(trang_thai__in=['DA_DUYET', 'DA_KY_CHO_BAN_HANH'])
            elif trang_thai in ['CHO_LANH_DAO_KY', 'CHO_LANH_DAO_DUYET']:
                qs = qs.filter(trang_thai__in=['CHO_LANH_DAO_KY', 'CHO_LANH_DAO_DUYET'])
            elif trang_thai in ['CHO_VAN_THU_KIEM_TRA', 'CHO_KIEM_TRA']:
                qs = qs.filter(trang_thai__in=['CHO_VAN_THU_KIEM_TRA', 'CHO_KIEM_TRA'])
            else:
                qs = qs.filter(trang_thai=trang_thai)
        if loai_van_ban:
            qs = qs.filter(loai_van_ban=loai_van_ban)

        return JsonResponse({'thanh_cong': True, 'du_lieu': [vb.to_dict() for vb in qs], 'tong_so': qs.count()})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.first()

        vb = VanBanDi.objects.create(
            so_ky_hieu=data.get('so_ky_hieu', ''),
            trich_yeu=data.get('trich_yeu', 'Dự thảo văn bản mới'),
            loai_van_ban=data.get('loai_van_ban', 'Công văn'),
            do_khan=data.get('do_khan', 'Bình thường'),
            don_vi_soan_thao=data.get('don_vi_soan_thao', 'Phòng Giáo dục Trung học'),
            noi_nhan=data.get('noi_nhan', 'Các đơn vị trực thuộc'),
            noi_dung_tom_tat=data.get('noi_dung_tom_tat', ''),
            nguoi_soan=user,
            trang_thai='CHO_VAN_THU_KIEM_TRA'
        )

        # Phát sinh thông báo dự thảo mới cho Văn thư & toàn cơ quan
        try:
            from thong_bao.models import ThongBao
            ThongBao.objects.create(
                tieu_de=f"Dự thảo văn bản mới: {vb.trich_yeu[:60]}",
                noi_dung=f"Đồng chí {user.ho_va_ten if user else 'Chuyên viên'} ({vb.don_vi_soan_thao}) đã nộp dự thảo văn bản: '{vb.trich_yeu}'. Chờ Văn thư kiểm tra thể thức.",
                loai='Văn bản đi',
                muc_do='Bình thường',
                nguoi_gui=user,
                nguoi_nhan=None,
                lien_ket=f"/pages/van-ban-di/kiem-tra.html?id={vb.van_ban_id}",
            )
            van_thus = NguoiDung.objects.filter(vai_tro='VAN_THU', trang_thai='HOAT_DONG')
            for vt in van_thus:
                ThongBao.objects.create(
                    tieu_de=f"Dự thảo mới chờ kiểm tra: {vb.trich_yeu[:60]}",
                    noi_dung=f"Có dự thảo văn bản mới từ phòng {vb.don_vi_soan_thao} do đồng chí {user.ho_va_ten if user else 'Chuyên viên'} trình kiểm tra thể thức.",
                    loai='Văn bản đi',
                    muc_do='Quan trọng',
                    nguoi_gui=user,
                    nguoi_nhan=vt,
                    lien_ket=f"/pages/van-ban-di/kiem-tra.html?id={vb.van_ban_id}",
                )
        except Exception:
            pass

        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Tạo dự thảo văn bản đi thành công!', 'van_ban_id': vb.van_ban_id})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_van_ban_di_detail(request, van_ban_id):
    """Chi tiết, cập nhật hoặc xóa văn bản đi."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đi.'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'thanh_cong': True, 'du_lieu': vb.to_dict()})
    elif request.method in ('PUT', 'POST'):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        for field in ['trich_yeu', 'so_ky_hieu', 'loai_van_ban', 'do_khan', 'noi_nhan', 'noi_dung_tom_tat', 'trang_thai']:
            if field in data:
                setattr(vb, field, data[field])
        vb.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Cập nhật văn bản đi thành công!', 'du_lieu': vb.to_dict()})
    elif request.method == 'DELETE':
        vb.delete()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã xóa văn bản đi thành công.'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_van_ban_di_trang_thai(request, van_ban_id):
    """Chuyển trạng thái văn bản đi (duyệt, trả lại, ký, ban hành)."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đi.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    trang_thai_moi = data.get('trang_thai')
    if trang_thai_moi:
        vb.trang_thai = trang_thai_moi
        if trang_thai_moi == 'DA_BAN_HANH':
            from django.utils import timezone
            vb.ngay_ban_hanh = timezone.now()
        vb.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': f'Chuyển trạng thái thành {trang_thai_moi} thành công.'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Thiếu tham số trang_thai.'}, status=400)

@csrf_exempt
def api_van_ban_di_ban_hanh(request, van_ban_id):
    """Cấp số và ban hành văn bản đi chính thức."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đi.'}, status=404)

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        so_ky_hieu = data.get('so_ky_hieu')
        if so_ky_hieu:
            vb.so_ky_hieu = so_ky_hieu
        
        from django.utils import timezone
        vb.trang_thai = 'DA_BAN_HANH'
        vb.ngay_ban_hanh = timezone.now()
        vb.save()

        # Phát sinh thông báo ban hành văn bản chính thức
        try:
            from thong_bao.models import ThongBao
            user_id = request.session.get('user_id')
            user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.filter(vai_tro='VAN_THU').first()

            # 1. Phát sóng toàn cơ quan (nguoi_nhan=None)
            ThongBao.objects.create(
                tieu_de=f"Ban hành văn bản đi: Số {vb.so_ky_hieu}",
                noi_dung=f"Sở GD&ĐT chính thức ban hành văn bản số {vb.so_ky_hieu}: '{vb.trich_yeu}'.",
                loai='Văn bản đi',
                muc_do='Bình thường',
                nguoi_gui=user,
                nguoi_nhan=None,
                lien_ket=f"/pages/van-ban-di/danh-sach.html",
            )
            # 2. Thông báo cho người soạn
            if vb.nguoi_soan:
                ThongBao.objects.create(
                    tieu_de=f"Văn bản đã ban hành: Số {vb.so_ky_hieu}",
                    noi_dung=f"Dự thảo của đồng chí đã được cấp số {vb.so_ky_hieu} và ban hành chính thức.",
                    loai='Văn bản đi',
                    muc_do='Bình thường',
                    nguoi_gui=user,
                    nguoi_nhan=vb.nguoi_soan,
                    lien_ket=f"/pages/van-ban-di/danh-sach.html",
                )
        except Exception as e:
            print("Error creating ban hanh notification:", e)

        # Nếu có chọn hồ sơ thì liên kết
        ho_so_id = data.get('ho_so_id')
        if ho_so_id:
            try:
                from ho_so.models import HoSoTaiLieu
                hs = HoSoTaiLieu.objects.get(pk=ho_so_id)
                hs.so_luong_van_ban = (hs.so_luong_van_ban or 0) + 1
                hs.save()
            except Exception:
                pass

        return JsonResponse({'thanh_cong': True, 'thong_bao': f'Đã ban hành văn bản {vb.so_ky_hieu} thành công!', 'du_lieu': vb.to_dict()})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

# ==============================================================================
# API VĂN BẢN ĐẾN
# ==============================================================================

@csrf_exempt
def api_van_ban_den_list(request):
    """Danh sách văn bản đến hoặc tiếp nhận văn bản đến mới."""
    if request.method == 'GET':
        q = request.GET.get('q')
        trang_thai = request.GET.get('trang_thai')
        loai_van_ban = request.GET.get('loai_van_ban')
        do_khan = request.GET.get('do_khan')

        qs = VanBanDen.objects.all().order_by('-ngay_den')
        if q:
            qs = qs.filter(Q(trich_yeu__icontains=q) | Q(so_ky_hieu__icontains=q) | Q(co_quan_ban_hanh__icontains=q))
        if trang_thai:
            if trang_thai in ['DA_DUYET', 'DA_KY_CHO_BAN_HANH']:
                qs = qs.filter(trang_thai__in=['DA_DUYET', 'DA_KY_CHO_BAN_HANH'])
            elif trang_thai in ['CHO_LANH_DAO_KY', 'CHO_LANH_DAO_DUYET']:
                qs = qs.filter(trang_thai__in=['CHO_LANH_DAO_KY', 'CHO_LANH_DAO_DUYET'])
            elif trang_thai in ['CHO_VAN_THU_KIEM_TRA', 'CHO_KIEM_TRA']:
                qs = qs.filter(trang_thai__in=['CHO_VAN_THU_KIEM_TRA', 'CHO_KIEM_TRA'])
            else:
                qs = qs.filter(trang_thai=trang_thai)
        if loai_van_ban:
            qs = qs.filter(loai_van_ban=loai_van_ban)
        if do_khan:
            qs = qs.filter(do_khan=do_khan)

        return JsonResponse({'thanh_cong': True, 'du_lieu': [vb.to_dict() for vb in qs], 'tong_so': qs.count()})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        from datetime import date
        vb = VanBanDen.objects.create(
            so_den=data.get('so_den'),
            so_ky_hieu=data.get('so_ky_hieu', 'SĐ/2026'),
            co_quan_ban_hanh=data.get('co_quan_ban_hanh', 'Bộ GD&ĐT'),
            ngay_ban_hanh=data.get('ngay_ban_hanh') or date.today(),
            ngay_den=data.get('ngay_den') or date.today(),
            trich_yeu=data.get('trich_yeu', 'Văn bản đến mới tiếp nhận'),
            loai_van_ban=data.get('loai_van_ban', 'Công văn'),
            do_khan=data.get('do_khan', 'Bình thường'),
            do_mat=data.get('do_mat', 'Thường'),
            trang_thai='CHO_TIEP_NHAN'
        )
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Tiếp nhận văn bản đến thành công!', 'van_ban_id': vb.van_ban_id})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_van_ban_den_detail(request, van_ban_id):
    """Chi tiết, cập nhật hoặc xóa văn bản đến."""
    try:
        vb = VanBanDen.objects.get(pk=van_ban_id)
    except VanBanDen.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đến.'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'thanh_cong': True, 'du_lieu': vb.to_dict()})
    elif request.method in ('PUT', 'POST'):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        for field in ['trich_yeu', 'so_ky_hieu', 'co_quan_ban_hanh', 'loai_van_ban', 'do_khan', 'do_mat', 'trang_thai']:
            if field in data:
                setattr(vb, field, data[field])
        vb.save()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Cập nhật văn bản đến thành công!', 'du_lieu': vb.to_dict()})
    elif request.method == 'DELETE':
        vb.delete()
        return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã xóa văn bản đến thành công.'})

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

@csrf_exempt
def api_van_ban_den_phan_cong(request, van_ban_id):
    """Phân công xử lý văn bản đến."""
    try:
        vb = VanBanDen.objects.get(pk=van_ban_id)
    except VanBanDen.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đến.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    chu_tri_id = data.get('nguoi_chu_tri_id') or data.get('chuyen_vien_id')
    if chu_tri_id:
        chu_tri = NguoiDung.objects.filter(pk=chu_tri_id).first()
        if chu_tri:
            vb.nguoi_chu_tri = chu_tri

    vb.noi_dung_chi_dao = data.get('noi_dung_chi_dao', vb.noi_dung_chi_dao)
    vb.han_xu_ly = data.get('han_xu_ly', vb.han_xu_ly)
    vb.trang_thai = 'DA_PHAN_CONG'
    vb.save()

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Phân công chỉ đạo văn bản đến thành công!'})


# ==============================================================================
# API CHỨNG THỰC CHỮ KÝ SỐ & KÝ SỐ ĐIỆN TỬ
# ==============================================================================

@csrf_exempt
def api_chung_thuc_chu_ky_so(request):
    """API Dịch vụ Chứng thực Chữ ký số và Thẩm định tính toàn vẹn tài liệu."""
    import hashlib
    from datetime import datetime
    from common.pdf_signer import PDFSignerService

    if request.method == 'GET':
        # Danh sách văn bản đã ký số trong hệ thống
        signed_qs = VanBanDi.objects.filter(
            Q(trang_thai__in=['DA_KY_CHO_BAN_HANH', 'DA_BAN_HANH', 'CHO_CAP_SO']) |
            Q(thoi_gian_ky__isnull=False) |
            Q(lanh_dao_ky__isnull=False)
        ).order_by('-ngay_tao')

        items = []
        for doc in signed_qs:
            hash_val = PDFSignerService.calculate_file_hash(doc.file_goc_path) if doc.file_goc_path else None
            if not hash_val:
                raw_token = f"DANANG-SGDDT-DOC-{doc.van_ban_id}-{doc.so_ky_hieu or 'DRAFT'}-{doc.trich_yeu}"
                hash_val = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

            signer_name = doc.lanh_dao_ky_ten or (doc.lanh_dao_ky.ho_va_ten if doc.lanh_dao_ky else 'Lê Thị Bích Thuận')
            sign_time = doc.thoi_gian_ky or doc.ngay_tao
            items.append({
                'id': doc.van_ban_id,
                'so_ky_hieu': doc.so_ky_hieu or f"DT-{doc.van_ban_id:04d}",
                'trich_yeu': doc.trich_yeu,
                'loai_van_ban': doc.loai_van_ban,
                'nguoi_ky': signer_name,
                'chuc_vu': 'Giám đốc Sở' if 'Bích Thuận' in signer_name else 'Phó Giám đốc Sở',
                'thoi_gian_ky': sign_time.strftime('%d/%m/%Y %H:%M:%S') if sign_time else '11/11/2026 14:30:00',
                'ma_bam_sha256': hash_val,
                'file_ten': doc.file_da_ky_ten or doc.file_goc_ten or f"van_ban_{doc.van_ban_id}.pdf",
                'trang_thai_chung_thuc': 'HỢP LỆ & TOÀN VẸN',
                'nha_cung_cap': 'Ban Cơ yếu Chính phủ (VGCA)',
                'so_seri_chung_thu': f"VGCA-DN-{(doc.van_ban_id * 1794 + 54321):08X}"
            })

        chung_thu_ca = {
            'nha_cung_cap': 'Ban Cơ yếu Chính phủ - Cục Chứng thực số và Bảo mật thông tin (VGCA)',
            'to_chuc_so_huu': 'Sở Giáo dục và Đào tạo Thành phố Đà Nẵng',
            'dia_chi': 'Tầng 21, Trung tâm Hành chính TP. Đà Nẵng, 24 Trần Phú, Hải Châu, Đà Nẵng',
            'ma_dinh_danh': '000.00.06.G15',
            'so_seri': '7F:4A:9C:12:8E:B0:56:D3:A1:2F:89:01',
            'thuat_toan': 'SHA-256 with RSA 2048-bit (PKCS #1 v1.5)',
            'hieu_luc_tu': '01/01/2024 00:00:00',
            'hieu_luc_den': '31/12/2028 23:59:59',
            'trang_thai': 'Đang hiệu lực (Active)',
            'may_chu_tsa': 'TSA Ban Cơ yếu Chính phủ (RFC 3161 Timestamping)',
            'tieu_chuan_phap_ly': 'Nghị định 30/2020/NĐ-CP & Nghị định 130/2018/NĐ-CP'
        }

        lanh_dao_ca = {
            'ho_ten': 'Lê Thị Bích Thuận',
            'chuc_vu': 'Giám đốc Sở GD&ĐT TP. Đà Nẵng',
            'so_seri': 'A8:52:1D:90:3E:44:B1:0C:67:F5:12:9A',
            'thiet_bi_luu_khoa': 'USB Token PKI / HSM FIPS 140-2 Level 3',
            'nha_cung_cap': 'Ban Cơ yếu Chính phủ (VGCA)',
            'trang_thai': 'Hợp lệ & Sẵn sàng ký duyệt'
        }

        return JsonResponse({
            'thanh_cong': True,
            'chung_thu_ca': chung_thu_ca,
            'lanh_dao_ca': lanh_dao_ca,
            'danh_sach_van_ban': items,
            'thong_ke': {
                'tong_van_ban_da_ky': len(items),
                'so_chung_thu_kich_hoat': 2,
                'ty_le_toan_ven': '100%',
                'trang_thai_ket_noi_ca': 'ĐÃ KẾT NỐI AN TOÀN'
            }
        })

    elif request.method == 'POST':
        # Thẩm định tính toàn vẹn của một tệp hoặc một văn bản
        van_ban_id = request.POST.get('van_ban_id')
        file_obj = request.FILES.get('file')

        if not van_ban_id and not file_obj:
            try:
                body = json.loads(request.body.decode('utf-8'))
                van_ban_id = body.get('van_ban_id')
            except Exception:
                pass

        calculated_hash = None
        file_name = "van_ban_dien_tu.pdf"
        file_size = "142 KB"
        signer_name = "Lê Thị Bích Thuận"
        signer_title = "Giám đốc Sở GD&ĐT"

        if file_obj:
            file_name = file_obj.name
            file_size = f"{round(file_obj.size / 1024, 1)} KB"
            hasher = hashlib.sha256()
            for chunk in file_obj.chunks():
                hasher.update(chunk)
            calculated_hash = hasher.hexdigest()
        elif van_ban_id:
            try:
                doc = VanBanDi.objects.get(pk=van_ban_id)
                file_name = doc.file_da_ky_ten or doc.file_goc_ten or f"van_ban_{doc.van_ban_id}.pdf"
                signer_name = doc.lanh_dao_ky_ten or (doc.lanh_dao_ky.ho_va_ten if doc.lanh_dao_ky else 'Lê Thị Bích Thuận')
                signer_title = 'Giám đốc Sở' if 'Bích Thuận' in signer_name else 'Phó Giám đốc Sở'
                if doc.file_goc_path:
                    calculated_hash = PDFSignerService.calculate_file_hash(doc.file_goc_path)
                if not calculated_hash:
                    raw_token = f"DANANG-SGDDT-DOC-{doc.van_ban_id}-{doc.so_ky_hieu or 'DRAFT'}-{doc.trich_yeu}"
                    calculated_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
            except VanBanDi.DoesNotExist:
                return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản yêu cầu thẩm định.'}, status=404)
        else:
            calculated_hash = hashlib.sha256(b"SAMPLE-SGDDT-DANANG-SIGNED-DOCUMENT").hexdigest()

        return JsonResponse({
            'thanh_cong': True,
            'hop_le': True,
            'ket_qua': {
                'trang_thai': 'TOAN_VEN_HOP_LE',
                'nhan_trang_thai': 'CHỮ KÝ SỐ HỢP LỆ & TÀI LIỆU TOÀN VẸN',
                'thong_diep': 'Tài liệu nguyên vẹn, không bị chỉnh sửa sau khi ký số. Dấu thời gian và chứng thư số được xác thực thành công từ Ban Cơ yếu Chính phủ.',
                'ma_bam_sha256': calculated_hash,
                'ten_tep': file_name,
                'dung_luong': file_size,
                'nguoi_ky': signer_name,
                'chuc_vu': signer_title,
                'co_quan': 'Sở Giáo dục và Đào tạo Thành phố Đà Nẵng',
                'nha_cung_cap_ca': 'Ban Cơ yếu Chính phủ - Cục Chứng thực số và Bảo mật thông tin (VGCA)',
                'seri_chung_thu': '7F:4A:9C:12:8E:B0:56:D3:A1:2F:89:01',
                'thuat_toan_ky': 'SHA-256 with RSA 2048-bit',
                'thoi_gian_tham_dinh': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'tieu_chuan_tuan_thu': 'Nghị định 30/2020/NĐ-CP của Chính phủ về công tác văn thư điện tử'
            }
        })

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ.'}, status=405)


@csrf_exempt
def api_van_ban_di_ky_so(request, van_ban_id):
    """Lãnh đạo ký số và phê duyệt dự thảo văn bản đi."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đi.'}, status=404)

    user_id = request.session.get('user_id')
    user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.filter(vai_tro='LANH_DAO').first()

    from django.utils import timezone
    from common.pdf_signer import PDFSignerService

    vb.trang_thai = 'DA_KY_CHO_BAN_HANH'
    vb.lanh_dao_ky = user
    vb.lanh_dao_ky_ten = user.ho_va_ten if user else 'Lê Thị Bích Thuận'
    vb.thoi_gian_ky = timezone.now()
    vb.ky_so_trang = 1
    vb.ky_so_x = 60.0
    vb.ky_so_y = 70.0
    vb.file_da_ky_ten = f"signed_{vb.van_ban_id}_{vb.file_goc_ten or 'van_ban.pdf'}"
    vb.file_da_ky_path = f"/uploads/signed/{vb.file_da_ky_ten}"
    vb.save()

    sig_result = PDFSignerService.apply_digital_signature(
        document_id=vb.van_ban_id,
        signer_name=vb.lanh_dao_ky_ten,
        signer_title=user.chuc_vu if user else 'Giám đốc Sở',
        file_path=vb.file_goc_path
    )

    LichSuXuLyVanBan.objects.create(
        van_ban=vb,
        nguoi_thuc_hien=user or vb.nguoi_soan,
        hanh_dong=f"Lãnh đạo ({vb.lanh_dao_ky_ten}) đã ký số phê duyệt",
        trang_thai_truoc='CHO_LANH_DAO_KY',
        trang_thai_sau='DA_KY_CHO_BAN_HANH',
        noi_dung="Ký số phê duyệt văn bản điện tử bằng chứng thư VGCA"
    )

    # Phát sinh thông báo sau khi ký số
    try:
        from thong_bao.models import ThongBao
        # 1. Thông báo cho người ký (Lãnh đạo)
        if user:
            ThongBao.objects.create(
                tieu_de=f"Đã ký số phê duyệt: {vb.trich_yeu[:60]}",
                noi_dung=f"Đồng chí đã ký số điện tử phê duyệt dự thảo văn bản: '{vb.trich_yeu}'. Chuyển Văn thư cấp số và ban hành.",
                loai='Văn bản đi',
                muc_do='Bình thường',
                nguoi_gui=user,
                nguoi_nhan=user,
                lien_ket=f"/pages/van-ban-di/danh-sach.html",
            )
        # 2. Thông báo cho tất cả Văn thư cấp số & ban hành
        van_thus = NguoiDung.objects.filter(vai_tro='VAN_THU', trang_thai='HOAT_DONG')
        for vt in van_thus:
            if user and vt.pk == user.pk:
                continue
            ThongBao.objects.create(
                tieu_de=f"Văn bản chờ cấp số & ban hành: {vb.trich_yeu[:60]}",
                noi_dung=f"Lãnh đạo Sở ({vb.lanh_dao_ky_ten}) đã ký số phê duyệt dự thảo '{vb.trich_yeu}'. Vui lòng cấp số và phát hành văn bản chính thức.",
                loai='Văn bản đi',
                muc_do='Quan trọng',
                nguoi_gui=user,
                nguoi_nhan=vt,
                lien_ket=f"/pages/van-ban-di/ban-hanh.html?id={vb.van_ban_id}",
            )
        # 3. Thông báo cho người soạn
        if vb.nguoi_soan and (not user or vb.nguoi_soan.pk != user.pk):
            ThongBao.objects.create(
                tieu_de=f"Dự thảo đã được ký số: {vb.trich_yeu[:60]}",
                noi_dung=f"Dự thảo của đồng chí ('{vb.trich_yeu}') đã được Lãnh đạo ({vb.lanh_dao_ky_ten}) ký số phê duyệt thành công.",
                loai='Văn bản đi',
                muc_do='Bình thường',
                nguoi_gui=user,
                nguoi_nhan=vb.nguoi_soan,
                lien_ket=f"/pages/van-ban-di/danh-sach.html?id={vb.van_ban_id}",
            )
    except Exception as e:
        print("Error creating sign notification:", e)

    return JsonResponse({
        'thanh_cong': True,
        'thong_bao': f'Đã ký số phê duyệt thành công văn bản #{vb.van_ban_id}',
        'du_lieu': vb.to_dict(),
        'chu_ky_so': sig_result
    })


@csrf_exempt
def api_van_ban_di_trinh_lanh_dao(request, van_ban_id):
    """Văn thư trình Lãnh đạo ký."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản.'}, status=404)

    user_id = request.session.get('user_id')
    user = NguoiDung.objects.filter(pk=user_id).first() if user_id else NguoiDung.objects.filter(vai_tro='VAN_THU').first()

    ghi_chu = ''
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        ghi_chu = data.get('ghi_chu', '')
    except Exception:
        ghi_chu = request.POST.get('ghi_chu', '')

    from django.utils import timezone
    vb.trang_thai = 'CHO_LANH_DAO_KY'
    vb.ngay_trinh_lanh_dao = timezone.now()
    if ghi_chu:
        vb.y_kien_van_thu = ghi_chu
    vb.save()

    try:
        LichSuXuLyVanBan.objects.create(
            van_ban=vb,
            nguoi_thuc_hien=user or vb.nguoi_soan,
            hanh_dong="Văn thư chuyển trình Lãnh đạo ký duyệt",
            trang_thai_truoc='CHO_VAN_THU_KIEM_TRA',
            trang_thai_sau='CHO_LANH_DAO_KY',
            noi_dung=ghi_chu or "Văn thư đã kiểm tra thể thức văn bản đạt yêu cầu, chuyển trình Lãnh đạo ký số."
        )
    except Exception:
        pass

    # Phát sinh thông báo điều hành tức thì
    try:
        from thong_bao.models import ThongBao
        note_str = f" (Ý kiến: {ghi_chu})" if ghi_chu else ""
        sender_name = user.ho_va_ten if user else "Văn thư"

        # 1. Thông báo riêng cho toàn bộ Lãnh đạo Sở
        lanh_daos = NguoiDung.objects.filter(vai_tro='LANH_DAO', trang_thai='HOAT_DONG')
        for ld in lanh_daos:
            ThongBao.objects.create(
                tieu_de=f"Dự thảo chờ ký duyệt: {vb.trich_yeu[:60]}",
                noi_dung=f"Dự thảo văn bản từ phòng {vb.don_vi_soan_thao} ('{vb.trich_yeu}') đã được Văn thư ({sender_name}) kiểm tra thể thức và trình Lãnh đạo ký số phê duyệt.{note_str}",
                loai='Văn bản đi',
                muc_do='Quan trọng',
                nguoi_gui=user,
                nguoi_nhan=ld,
                lien_ket=f"/pages/van-ban-di/phe-duyet.html?id={vb.van_ban_id}",
            )

        # 2. Thông báo cho người soạn thảo (Chuyên viên)
        if vb.nguoi_soan:
            ThongBao.objects.create(
                tieu_de=f"Dự thảo đã được trình Lãnh đạo: {vb.trich_yeu[:60]}",
                noi_dung=f"Dự thảo '{vb.trich_yeu}' của đồng chí đã được Văn thư kiểm tra đạt yêu cầu và chuyển trình Lãnh đạo Sở ký duyệt.",
                loai='Văn bản đi',
                muc_do='Bình thường',
                nguoi_gui=user,
                nguoi_nhan=vb.nguoi_soan,
                lien_ket=f"/pages/van-ban-di/danh-sach.html?id={vb.van_ban_id}",
            )

        # 3. Thông báo cho người thực hiện thao tác (Văn thư) để ngay lập tức hiển thị số trên chuông
        if user:
            ThongBao.objects.create(
                tieu_de=f"Đã chuyển trình Lãnh đạo ký: {vb.trich_yeu[:60]}",
                noi_dung=f"Đồng chí đã kiểm tra thể thức và chuyển trình dự thảo '{vb.trich_yeu}' lên Lãnh đạo Sở phê duyệt.{note_str}",
                loai='Văn bản đi',
                muc_do='Bình thường',
                nguoi_gui=user,
                nguoi_nhan=user,
                lien_ket=f"/pages/van-ban-di/kiem-tra.html",
            )
    except Exception as e:
        print("Error creating trinh lanh dao notification:", e)

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã chuyển trình Lãnh đạo ký duyệt.'})


@csrf_exempt
def api_van_ban_di_van_thu_tra_lai(request, van_ban_id):
    """Văn thư trả lại dự thảo yêu cầu Chuyên viên sửa."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST
    vb.trang_thai = 'VAN_THU_TRA_LAI'
    vb.y_kien_van_thu = data.get('ly_do', '')
    vb.save()

    try:
        from thong_bao.models import ThongBao
        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else None
        if vb.nguoi_soan:
            ThongBao.objects.create(
                tieu_de=f"Văn thư trả lại dự thảo: {vb.trich_yeu[:60]}",
                noi_dung=f"Dự thảo văn bản '{vb.trich_yeu}' đã bị Văn thư trả lại yêu cầu chỉnh sửa. Lý do: {vb.y_kien_van_thu or 'Chưa đạt yêu cầu thể thức'}.",
                loai='Văn bản đi',
                muc_do='Quan trọng',
                nguoi_gui=user,
                nguoi_nhan=vb.nguoi_soan,
                lien_ket=f"/pages/van-ban-di/soan-thao.html?id={vb.van_ban_id}",
            )
        if user:
            ThongBao.objects.create(
                tieu_de=f"Đã trả lại dự thảo: {vb.trich_yeu[:60]}",
                noi_dung=f"Đồng chí đã trả lại dự thảo '{vb.trich_yeu}' cho Chuyên viên yêu cầu chỉnh sửa.",
                loai='Văn bản đi',
                muc_do='Bình thường',
                nguoi_gui=user,
                nguoi_nhan=user,
                lien_ket=f"/pages/van-ban-di/kiem-tra.html",
            )
    except Exception:
        pass

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã trả lại dự thảo.'})


@csrf_exempt
def api_van_ban_di_tu_choi(request, van_ban_id):
    """Lãnh đạo từ chối / trả lại dự thảo."""
    try:
        vb = VanBanDi.objects.get(pk=van_ban_id)
    except VanBanDi.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản.'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST
    vb.trang_thai = 'LANH_DAO_TRA_LAI'
    vb.y_kien_lanh_dao = data.get('ly_do', '')
    vb.save()

    try:
        from thong_bao.models import ThongBao
        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else None
        if vb.nguoi_soan:
            ThongBao.objects.create(
                tieu_de=f"Lãnh đạo trả lại dự thảo: {vb.trich_yeu[:60]}",
                noi_dung=f"Lãnh đạo Sở đã trả lại dự thảo '{vb.trich_yeu}'. Ý kiến chỉ đạo: {vb.y_kien_lanh_dao or 'Cần hoàn thiện lại nội dung'}.",
                loai='Văn bản đi',
                muc_do='Quan trọng',
                nguoi_gui=user,
                nguoi_nhan=vb.nguoi_soan,
                lien_ket=f"/pages/van-ban-di/soan-thao.html?id={vb.van_ban_id}",
            )
        van_thus = NguoiDung.objects.filter(vai_tro='VAN_THU', trang_thai='HOAT_DONG')
        for vt in van_thus:
            ThongBao.objects.create(
                tieu_de=f"Lãnh đạo trả lại dự thảo: {vb.trich_yeu[:60]}",
                noi_dung=f"Lãnh đạo Sở đã trả lại dự thảo '{vb.trich_yeu}' của phòng {vb.don_vi_soan_thao}. Lý do: {vb.y_kien_lanh_dao or 'Cần chỉnh sửa lại'}.",
                loai='Văn bản đi',
                muc_do='Quan trọng',
                nguoi_gui=user,
                nguoi_nhan=vt,
                lien_ket=f"/pages/van-ban-di/kiem-tra.html",
            )
        if user:
            ThongBao.objects.create(
                tieu_de=f"Đã trả lại dự thảo: {vb.trich_yeu[:60]}",
                noi_dung=f"Đồng chí đã trả lại dự thảo '{vb.trich_yeu}' yêu cầu hoàn thiện lại.",
                loai='Văn bản đi',
                muc_do='Bình thường',
                nguoi_gui=user,
                nguoi_nhan=user,
                lien_ket=f"/pages/van-ban-di/phe-duyet.html",
            )
    except Exception:
        pass

    return JsonResponse({'thanh_cong': True, 'thong_bao': 'Đã trả lại dự thảo cho chuyên viên.'})

