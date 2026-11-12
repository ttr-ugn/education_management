import json
import os
import re
import html
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.conf import settings

from .models import MauVanBan, LichSuChat
from .services import ChatbotNLPService
from van_ban.models import VanBanDi, VanBanDen
from ho_so.models import HoSoLuuTru
from authentication.models import NguoiDung


def trang_chatbot(request):
    """Trang giao diện Trợ lý ảo AI tư vấn văn bản điều hành và kho lưu trữ."""
    total_docs = MauVanBan.objects.count()
    return render(request, 'chatbot/chatbot.html', {'total_docs': total_docs})


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

        clean_html = re.sub(r'<div class="pdf-preview-embed".*?</div>\s*</div>', '', mau.noi_dung_html, flags=re.DOTALL)
        clean_html = re.sub(r'<iframe.*?</iframe>', '', clean_html, flags=re.DOTALL)

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
{clean_html}
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
            html_content = ChatbotNLPService.generate_van_ban_di_html(vb)
            return JsonResponse({
                'thanh_cong': True,
                'tieu_de': f"{vb.so_ky_hieu or 'Dự thảo'} - {vb.trich_yeu}",
                'noi_dung_html': html_content,
                'loai_tep': 'van_ban_di'
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


@csrf_exempt
def api_upload_kho_luu_tru(request):
    """Tiếp nhận văn bản tải lên kho lưu trữ để AI đọc và trích xuất dữ liệu."""
    if request.method != 'POST':
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Phương thức không hỗ trợ'}, status=405)

    files = request.FILES.getlist('files') or ([request.FILES['file']] if 'file' in request.FILES else [])
    if not files:
        return JsonResponse({'thanh_cong': False, 'thong_bao': 'Vui lòng chọn ít nhất một tệp văn bản PDF'}, status=400)

    dest_dir = settings.BASE_DIR / 'media' / 'van_ban_dieu_hanh'
    dest_dir.mkdir(parents=True, exist_ok=True)

    imported_items = []
    ts = int(datetime.now().timestamp())
    for idx, f in enumerate(files):
        safe_filename = os.path.basename(f.name)
        file_path = dest_dir / safe_filename
        with open(file_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        ext = os.path.splitext(safe_filename)[1].lower()
        extracted_text = ""
        num_pages = 0
        if ext == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as tf:
                    extracted_text = tf.read()
            except Exception:
                extracted_text = safe_filename
        else:
            try:
                import pypdf
                reader = pypdf.PdfReader(str(file_path))
                num_pages = len(reader.pages)
                for page in reader.pages:
                    extracted_text += (page.extract_text() or "") + "\n"
            except Exception:
                extracted_text = ""

        extracted_text = extracted_text.strip() or f"Văn bản điều hành số hóa: {safe_filename}"
        base_name = os.path.splitext(safe_filename)[0]
        item_code = f"DOC-{ts}-{idx + 1}"
        media_url = f"/media/van_ban_dieu_hanh/{safe_filename}"

        paragraphs_html = "".join(
            f"<p>{html.escape(line.strip())}</p>"
            for line in extracted_text[:3000].splitlines()
            if line.strip()
        ) or f"<p>{html.escape(base_name)}</p>"

        pdf_embed_html = f"""
  <div class="pdf-preview-embed" style="margin-top: 18px; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; background: #f8fafc;">
    <div style="padding: 8px 14px; background: #1e293b; color: #f8fafc; font-size: 12px; font-weight: 600; display: flex; justify-content: space-between; align-items: center;">
      <span>BẢN XEM TRƯỚC PDF TRỰC TIẾP ({num_pages} trang)</span>
      <a href="{media_url}" target="_blank" style="color: #38bdf8; text-decoration: none;">Mở tab mới &rarr;</a>
    </div>
    <iframe src="{media_url}" style="width: 100%; height: 760px; border: none; display: block;" title="PDF Preview"></iframe>
  </div>""" if ext == '.pdf' else ""

        obj = MauVanBan.objects.create(
            ma_mau=item_code,
            ten_mau=base_name,
            loai_van_ban='Văn bản điều hành',
            linh_vuc='Kho lưu trữ số',
            co_quan_ban_hanh='SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG',
            noi_dung_text=extracted_text[:10000],
            noi_dung_html=f"""
<div class="vb-container">
  <div style="margin-bottom: 20px; padding: 12px 16px; background: #e0f2fe; border: 1px solid #7dd3fc; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
    <span>Tệp gốc: <b>{html.escape(safe_filename)}</b></span>
    <div style="display: flex; gap: 8px;">
      <a href="{media_url}" target="_blank" class="btn btn-sm btn-primary" style="padding: 5px 12px; background: #0284c7; color: #fff; text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: 600;">Mở tệp gốc &rarr;</a>
      <a href="{media_url}" download class="btn btn-sm" style="padding: 5px 12px; background: #f1f5f9; color: #334155; text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: 600; border: 1px solid #cbd5e1;">Tải xuống</a>
    </div>
  </div>
  <div class="vb-title-block">
    <div class="vb-title-type">VĂN BẢN ĐIỀU HÀNH</div>
    <div class="vb-subject">{html.escape(base_name)}</div>
  </div>
  <div class="vb-content">
    {paragraphs_html}
  </div>
  {pdf_embed_html}
</div>
"""
        )
        imported_items.append(obj.to_dict())

    return JsonResponse({
        'thanh_cong': True,
        'thong_bao': f'Đã nạp thành công {len(imported_items)} tệp văn bản vào kho lưu trữ.',
        'du_lieu': imported_items,
        'tong_so': MauVanBan.objects.count()
    })
