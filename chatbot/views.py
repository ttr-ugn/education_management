import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import MauVanBan, LichSuChat
from .services import ChatbotNLPService
from van_ban.models import VanBanDi, VanBanDen
from ho_so.models import HoSoLuuTru
from authentication.models import NguoiDung


def trang_chatbot(request):
    """Trang giao diện Trợ lý ảo AI tư vấn văn bản điều hành và kho lưu trữ."""
    return render(request, 'chatbot/chatbot.html')


@csrf_exempt
def api_hoi_dap(request):
    """
    Tiếp nhận câu hỏi/nội dung từ cán bộ, tra cứu kho lưu trữ và đề xuất danh sách file.
    Hỗ trợ cả POST (chat hội thoại) và GET (tra cứu nhanh danh mục).
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        question = (
            data.get('message') or 
            data.get('cau_hoi') or 
            data.get('tin_nhan') or 
            data.get('query') or 
            ''
        )

        user_id = request.session.get('user_id')
        user = NguoiDung.objects.filter(pk=user_id).first() if user_id else None

        result = ChatbotNLPService.process_message(question, user=user)

        response_payload = {
            'thanh_cong': True,
            'cau_tra_loi': result['answer'],
            'tra_loi': result['answer'],
            'intent': result['intent'],
            'mau_de_xuat': result['suggested_templates'],
            'goi_y_tiep_theo': result.get('next_suggestions', []),
            'du_lieu': {
                'cau_tra_loi': result['answer'],
                'tra_loi': result['answer'],
                'intent': result['intent'],
                'mau_de_xuat': result['suggested_templates'],
                'goi_y_tiep_theo': result.get('next_suggestions', []),
            }
        }
        return JsonResponse(response_payload)

    elif request.method == 'GET':
        query = request.GET.get('q', '').strip()
        if query:
            matches = ChatbotNLPService.search_repository(query, limit=10)
            return JsonResponse({
                'thanh_cong': True,
                'danh_sach_mau': matches,
                'tong_so': len(matches)
            })

        templates = MauVanBan.objects.all().order_by('-luot_xem')
        return JsonResponse({
            'thanh_cong': True,
            'du_lieu': [t.to_dict() for t in templates],
            'danh_sach_mau': [t.to_dict() for t in templates],
            'tong_so': templates.count()
        })

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hợp lệ'}, status=405)


@csrf_exempt
def api_kho_mau(request):
    """Tra cứu kho lưu trữ toàn bộ mẫu văn bản với các bộ lọc nghiệp vụ."""
    keyword = request.GET.get('keyword', '').strip()
    loai = request.GET.get('loai', '').strip()
    linh_vuc = request.GET.get('linh_vuc', '').strip()

    qs = MauVanBan.objects.all()

    if keyword:
        qs = qs.filter(
            Q(ten_mau__icontains=keyword) |
            Q(ma_mau__icontains=keyword) |
            Q(loai_van_ban__icontains=keyword) |
            Q(linh_vuc__icontains=keyword) |
            Q(noi_dung_text__icontains=keyword)
        )

    if loai:
        qs = qs.filter(loai_van_ban__icontains=loai)

    if linh_vuc:
        qs = qs.filter(linh_vuc__icontains=linh_vuc)

    list_data = [t.to_dict() for t in qs.order_by('-luot_xem')]

    return JsonResponse({
        'thanh_cong': True,
        'danh_sach_mau': list_data,
        'tong_so': len(list_data)
    })


@csrf_exempt
def api_mau_van_ban_detail(request, mau_id):
    """Lấy chi tiết và mã HTML xem trước A4 của một mẫu văn bản."""
    try:
        mau = MauVanBan.objects.get(pk=mau_id)
        mau.luot_xem += 1
        mau.save(update_fields=['luot_xem'])
        return JsonResponse({
            'thanh_cong': True,
            'mau': mau.to_dict(),
            'du_lieu': mau.to_dict()
        })
    except MauVanBan.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': f'Không tìm thấy mẫu văn bản ID {mau_id}'}, status=404)


@csrf_exempt
def api_mau_van_ban_tai_ve(request, mau_id):
    """Tải mẫu văn bản dưới định dạng Microsoft Word (.doc) tương thích cao."""
    try:
        mau = MauVanBan.objects.get(pk=mau_id)
        mau.luot_tai += 1
        mau.save(update_fields=['luot_tai'])

        word_html = f"""<!DOCTYPE html>
<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
<head>
<meta charset='utf-8'>
<title>{mau.ten_mau}</title>
<!--[if gte mso 9]>
<xml>
 <w:WordDocument>
  <w:View>Print</w:View>
  <w:Zoom>100</w:Zoom>
  <w:DoNotOptimizeForBrowser/>
 </w:WordDocument>
</xml>
<![endif]-->
<style>
@page {{
  size: 210mm 297mm; /* Chuẩn A4 */
  margin: 20mm 20mm 20mm 30mm; /* Chuẩn căn lề NĐ 30 */
}}
body {{
  font-family: 'Times New Roman', serif;
  font-size: 13pt;
  line-height: 1.4;
  color: #000;
}}
table {{ width: 100%; border-collapse: collapse; }}
td {{ border: none; padding: 2px 4px; }}
.vb-agency-parent {{ font-size: 12pt; text-transform: uppercase; text-align: center; }}
.vb-agency-name {{ font-size: 13pt; font-weight: bold; text-transform: uppercase; text-align: center; }}
.vb-nation-title {{ font-size: 12pt; font-weight: bold; text-transform: uppercase; text-align: center; }}
.vb-motto {{ font-size: 13pt; font-weight: bold; text-align: center; }}
.vb-title-type {{ font-size: 15pt; font-weight: bold; text-transform: uppercase; text-align: center; margin-top: 15px; }}
.vb-subject {{ font-size: 13pt; font-weight: bold; text-align: center; margin-bottom: 15px; }}
.vb-content p {{ text-indent: 1.27cm; text-align: justify; margin: 6px 0; }}
.vb-sign-role {{ font-size: 13pt; font-weight: bold; text-transform: uppercase; text-align: center; }}
.vb-sign-name {{ font-size: 13pt; font-weight: bold; text-align: center; }}
</style>
</head>
<body>
{mau.noi_dung_html}
</body>
</html>"""
        response = HttpResponse(word_html, content_type='application/msword; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{mau.ma_mau}.doc"'
        return response

    except MauVanBan.DoesNotExist:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy mẫu văn bản'}, status=404)


@csrf_exempt
def api_xem_truoc_tai_lieu(request, loai, item_id):
    """
    API xem trước đa năng cho mọi tài liệu trong kho lưu trữ:
    - loai = 'mau': Mẫu văn bản biểu mẫu
    - loai = 'van_ban_di': Văn bản đi / dự thảo
    - loai = 'van_ban_den': Văn bản đến
    - loai = 'ho_so': Hồ sơ lưu trữ
    """
    if loai in ('mau', 'mau_van_ban'):
        try:
            m = MauVanBan.objects.get(pk=item_id)
            return JsonResponse({
                'thanh_cong': True,
                'tieu_de': f"{m.ma_mau} - {m.ten_mau}",
                'noi_dung_html': m.noi_dung_html,
                'loai_tep': 'mau_van_ban',
                'download_url': f"/api/chatbot/mau-van-ban/{m.mau_id}/tai-ve"
            })
        except MauVanBan.DoesNotExist:
            return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy mẫu văn bản'}, status=404)

    elif loai == 'van_ban_di':
        try:
            vb = VanBanDi.objects.get(pk=item_id)
            html = ChatbotNLPService.generate_van_ban_di_html(vb)
            return JsonResponse({
                'thanh_cong': True,
                'tieu_de': f"{vb.so_ky_hieu or 'Dự thảo'} - {vb.trich_yeu}",
                'noi_dung_html': html,
                'loai_tep': 'van_ban_di',
                'download_url': f"/api/van-ban-di/{vb.van_ban_id}/download"
            })
        except VanBanDi.DoesNotExist:
            return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đi'}, status=404)

    elif loai == 'van_ban_den':
        try:
            vd = VanBanDen.objects.get(pk=item_id)
            html = ChatbotNLPService.generate_van_ban_den_html(vd)
            return JsonResponse({
                'thanh_cong': True,
                'tieu_de': f"Số đến {vd.so_den} - {vd.trich_yeu}",
                'noi_dung_html': html,
                'loai_tep': 'van_ban_den'
            })
        except VanBanDen.DoesNotExist:
            return JsonResponse({'thanh_cong': False, 'thong_bao': 'Không tìm thấy văn bản đến'}, status=404)

    return JsonResponse({'thanh_cong': False, 'thong_bao': 'Loại tài liệu không hỗ trợ'}, status=400)
