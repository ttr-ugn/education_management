"""Tests for Ho So Luu Tru archival document APIs, preview, and download endpoints."""

import json
import tempfile
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

from django.test import Client, TestCase, override_settings

from authentication.models import NguoiDung
from common.constants import ThoiHanBaoQuan, TrangThaiHoSo, VaiTroNguoiDung
from ho_so.models import HoSoLuuTru, VanBanBanHanh
from ho_so.services import ArchivalDocumentService


class _TagBalanceParser(HTMLParser):
    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img",
        "input", "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.parent_map = {}

    def handle_starttag(self, tag, attrs):
        attr_map = dict(attrs)
        elem_id = attr_map.get("id")
        if elem_id:
            self.parent_map[elem_id] = [item[1] for item in self.stack if item[1]]
        if tag not in self.VOID_TAGS:
            self.stack.append((tag, elem_id))

    def handle_endtag(self, tag):
        if tag in self.VOID_TAGS:
            return
        if not self.stack:
            self.errors.append(f"Unexpected </{tag}>")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        self.errors.append(f"Mismatched </{tag}> (expected </{self.stack[-1][0]}>)")
        for idx in range(len(self.stack) - 1, -1, -1):
            if self.stack[idx][0] == tag:
                del self.stack[idx:]
                break


class HoSoDocumentAPITestCase(TestCase):
    """Kiểm thử API văn bản trong hồ sơ, xem trước A4/PDF và tải về."""

    def setUp(self):
        self.client = Client()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.media_root = Path(self.temp_dir.name)
        pdf_dir = self.media_root / "van_ban_dieu_hanh"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        (pdf_dir / "sample.pdf").write_bytes(b"%PDF-1.4\n%MockPDFContent\n")

        self.creator = NguoiDung.objects.create(
            ten_dang_nhap="vanthu_test_api",
            mat_khau_hash="hashed_pw",
            ho_va_ten="Nguyễn Thị Văn Thư",
            vai_tro=VaiTroNguoiDung.VAN_THU,
            phong_ban="Văn phòng Sở GD&ĐT",
        )
        self.dossier = HoSoLuuTru.objects.create(
            ma_ho_so="HS-2026-GDTrH-901",
            tieu_de="Hồ sơ kiểm thử chỉ đạo chuyên môn",
            don_vi="Phòng Giáo dục Trung học",
            nguoi_lap=self.creator,
            nam_tai_lieu=2026,
            thoi_han_bao_quan=ThoiHanBaoQuan.MUOI_NAM,
            so_luong_van_ban=2,
            tinh_trang=TrangThaiHoSo.DANG_THU_THAP,
        )
        self.pdf_doc = VanBanBanHanh.objects.create(
            so_ky_hieu="1752/QĐ-SGDĐT",
            trich_yeu="Quyết định phê duyệt chỉ tiêu tuyển sinh lớp 10",
            loai_van_ban="Quyết định",
            co_quan_ban_hanh="Sở Giáo dục và Đào tạo TP. Đà Nẵng",
            nguoi_ky="Lê Thị Bích Thuận",
            chuc_vu_nguoi_ky="Giám đốc Sở GD&ĐT",
            ngay_ky=date(2026, 8, 12),
            ngay_ban_hanh=date(2026, 8, 12),
            ho_so=self.dossier,
            tep_dinh_kem="van_ban_dieu_hanh/sample.pdf",
        )
        self.html_doc = VanBanBanHanh.objects.create(
            so_ky_hieu="125/SGDĐT-GDTrH",
            trich_yeu="Hướng dẫn thi học sinh giỏi <script>alert(1)</script>",
            loai_van_ban="Hướng dẫn",
            co_quan_ban_hanh="Phòng Giáo dục Trung học - Sở GD&ĐT TP. Đà Nẵng",
            nguoi_ky="Mai Tấn Linh",
            chuc_vu_nguoi_ky="Phó Giám đốc Sở GD&ĐT",
            ngay_ky=date(2026, 9, 8),
            ngay_ban_hanh=date(2026, 9, 8),
            ho_so=self.dossier,
            tep_dinh_kem=None,
        )
        self.available_doc = VanBanBanHanh.objects.create(
            so_ky_hieu="89/TTr-SGDĐT",
            trich_yeu="Tờ trình phê duyệt Đề án Chuyển đổi số",
            loai_van_ban="Tờ trình",
            co_quan_ban_hanh="Phòng Kế hoạch - Tài chính",
            nguoi_ky="Lê Thị Bích Thuận",
            chuc_vu_nguoi_ky="Giám đốc Sở GD&ĐT",
            ngay_ky=date(2026, 10, 20),
            ngay_ban_hanh=date(2026, 10, 20),
            ho_so=None,
            tep_dinh_kem=None,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_list_and_available_documents_include_preview_and_download_urls(self):
        with override_settings(MEDIA_ROOT=str(self.media_root), MEDIA_URL="/media/"):
            res = self.client.get(f"/api/ho-so/{self.dossier.ho_so_id}/van-ban")
            self.assertEqual(res.status_code, 200)
            payload = json.loads(res.content.decode("utf-8"))
            self.assertTrue(payload["thanh_cong"])
            self.assertEqual(payload["tong_so"], 2)

            by_code = {item["so_ky_hieu"]: item for item in payload["du_lieu"]}
            pdf_item = by_code["1752/QĐ-SGDĐT"]
            html_item = by_code["125/SGDĐT-GDTrH"]

            self.assertEqual(pdf_item["preview_url"], "/media/van_ban_dieu_hanh/sample.pdf")
            self.assertEqual(pdf_item["nguon"], "PDF gốc lưu trữ")
            self.assertEqual(
                html_item["preview_url"],
                f"/api/ho-so/van-ban/{self.html_doc.van_ban_id}/xem-truoc",
            )
            self.assertEqual(html_item["nguon"], "Văn bản ban hành điện tử")
            self.assertEqual(
                html_item["don_vi_soan_thao"],
                "Phòng Giáo dục Trung học - Sở GD&ĐT TP. Đà Nẵng",
            )

            avail_res = self.client.get(
                f"/api/ho-so/{self.dossier.ho_so_id}/van-ban-kha-dung"
            )
            self.assertEqual(avail_res.status_code, 200)
            avail_payload = json.loads(avail_res.content.decode("utf-8"))
            self.assertEqual(avail_payload["tong_so"], 1)
            self.assertEqual(avail_payload["du_lieu"][0]["so_ky_hieu"], "89/TTr-SGDĐT")

    def test_html_preview_and_word_download(self):
        res_preview = self.client.get(
            f"/api/ho-so/van-ban/{self.html_doc.van_ban_id}/xem-truoc"
        )
        self.assertEqual(res_preview.status_code, 200)
        body = res_preview.content.decode("utf-8")
        self.assertIn("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", body)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", body)
        self.assertNotIn("<script>alert(1)</script>", body)

        res_download = self.client.get(
            f"/api/ho-so/van-ban/{self.html_doc.van_ban_id}/tai-ve"
        )
        self.assertEqual(res_download.status_code, 200)
        self.assertIn("application/msword", res_download["Content-Type"])
        self.assertIn('attachment; filename="', res_download["Content-Disposition"])
        self.assertTrue(res_download["Content-Disposition"].endswith('.doc"'))

    def test_pdf_preview_download_and_path_traversal_guard(self):
        with override_settings(MEDIA_ROOT=str(self.media_root), MEDIA_URL="/media/"):
            res_preview = self.client.get(
                f"/api/ho-so/van-ban/{self.pdf_doc.van_ban_id}/xem-truoc"
            )
            self.assertEqual(res_preview.status_code, 200)
            self.assertEqual(res_preview["Content-Type"], "application/pdf")
            preview_bytes = b"".join(res_preview.streaming_content)
            res_preview.close()
            self.assertTrue(preview_bytes.startswith(b"%PDF-1.4"))

            res_dl = self.client.get(
                f"/api/ho-so/van-ban/{self.pdf_doc.van_ban_id}/tai-ve"
            )
            self.assertEqual(res_dl.status_code, 200)
            self.assertIn("attachment;", res_dl["Content-Disposition"])
            self.assertIn("sample.pdf", res_dl["Content-Disposition"])
            b"".join(res_dl.streaming_content)
            res_dl.close()

            url, disk_path, is_pdf = ArchivalDocumentService.resolve_attachment(
                "../../education_management/settings.py"
            )
            self.assertIsNone(url)
            self.assertIsNone(disk_path)
            self.assertFalse(is_pdf)

    def test_chi_tiet_html_has_balanced_modals_and_missing_doc_returns_404(self):
        res_page = self.client.get("/pages/ho-so/chi-tiet.html")
        self.assertEqual(res_page.status_code, 200)
        parser = _TagBalanceParser()
        parser.feed(res_page.content.decode("utf-8"))
        self.assertEqual(parser.errors, [])
        self.assertEqual(parser.stack, [])
        self.assertNotIn("modalAddDoc", parser.parent_map.get("previewModal", []))

        res_404 = self.client.get("/api/ho-so/van-ban/999999/xem-truoc")
        self.assertEqual(res_404.status_code, 404)
