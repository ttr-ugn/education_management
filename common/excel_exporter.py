"""
Education Management - Tabular Data Exporter (CSV & Excel)
Module trích xuất báo cáo thống kê văn bản, công việc, hồ sơ dạng bảng tương thích Microsoft Excel.
"""

import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional


class ExcelExporter:
    """
    Công cụ xuất báo cáo dữ liệu định dạng CSV chuẩn UTF-8 BOM (tự động nhận diện tiếng Việt trong MS Excel).
    """

    @staticmethod
    def export_to_csv_bom(
        headers: List[str],
        data_rows: List[List[Any]],
        title: Optional[str] = None
    ) -> str:
        """
        Tạo nội dung file CSV có tiền tố UTF-8 BOM (\\ufeff) để Excel không bị lỗi font tiếng Việt.
        """
        output = io.StringIO()
        # Ghi UTF-8 BOM
        output.write('\ufeff')
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        if title:
            writer.writerow([title.upper()])
            writer.writerow([f"Ngày trích xuất: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"])
            writer.writerow([])  # Dòng trống phân cách

        writer.writerow(headers)
        for row in data_rows:
            formatted_row = []
            for item in row:
                if item is None:
                    formatted_row.append('')
                elif isinstance(item, datetime):
                    formatted_row.append(item.strftime('%d/%m/%Y %H:%M'))
                else:
                    formatted_row.append(str(item))
            writer.writerow(formatted_row)

        return output.getvalue()

    @classmethod
    def export_van_ban_list(cls, van_ban_list: List[Dict[str, Any]]) -> str:
        """
        Xuất danh sách Sổ theo dõi văn bản đi ra bảng biểu.
        """
        headers = [
            'STT',
            'Số ký hiệu',
            'Trích yếu nội dung',
            'Loại văn bản',
            'Độ khẩn',
            'Đơn vị soạn thảo',
            'Người soạn',
            'Lãnh đạo ký',
            'Ngày tạo',
            'Trạng thái'
        ]
        rows = []
        for idx, vb in enumerate(van_ban_list, 1):
            rows.append([
                idx,
                vb.get('so_ky_hieu') or 'Chưa cấp số',
                vb.get('trich_yeu', ''),
                vb.get('loai_van_ban', ''),
                vb.get('do_khan', ''),
                vb.get('don_vi_soan_thao', ''),
                vb.get('nguoi_soan_ten', ''),
                vb.get('lanh_dao_ky_ten', ''),
                vb.get('ngay_tao', ''),
                vb.get('trang_thai', '')
            ])
        return cls.export_to_csv_bom(headers, rows, title="SỔ THEO DÕI VĂN BẢN ĐI - SỞ GD&ĐT TP. ĐÀ NẴNG")

    @classmethod
    def export_cong_viec_list(cls, cong_viec_list: List[Dict[str, Any]]) -> str:
        """
        Xuất danh sách Theo dõi tiến độ công việc ra bảng biểu.
        """
        headers = [
            'STT',
            'Tên nhiệm vụ / công việc',
            'Người giao việc',
            'Cán bộ phụ trách',
            'Phòng ban',
            'Hạn hoàn thành',
            'Độ ưu tiên',
            'Tiến độ (%)',
            'Trạng thái xử lý'
        ]
        rows = []
        for idx, cv in enumerate(cong_viec_list, 1):
            rows.append([
                idx,
                cv.get('ten_cong_viec', ''),
                cv.get('nguoi_giao', ''),
                cv.get('nguoi_xu_ly', ''),
                cv.get('phong_ban', ''),
                cv.get('han_hoan_thanh', ''),
                cv.get('do_uu_tien', ''),
                f"{cv.get('tien_do', 0)}%",
                cv.get('trang_thai', '')
            ])
        return cls.export_to_csv_bom(headers, rows, title="BÁO CÁO TIẾN ĐỘ THỰC HIỆN NHIỆM VỤ CÔNG TÁC")

    @classmethod
    def export_ho_so_list(cls, ho_so_list: List[Dict[str, Any]]) -> str:
        """
        Xuất Danh mục hồ sơ lưu trữ cơ quan ra bảng biểu.
        """
        headers = [
            'STT',
            'Mã hồ sơ',
            'Tiêu đề hồ sơ',
            'Đơn vị lập hồ sơ',
            'Người lập',
            'Năm tài liệu',
            'Thời hạn bảo quản',
            'Số lượng VB',
            'Tình trạng'
        ]
        rows = []
        for idx, hs in enumerate(ho_so_list, 1):
            rows.append([
                idx,
                hs.get('ma_ho_so', ''),
                hs.get('tieu_de', ''),
                hs.get('don_vi', ''),
                hs.get('nguoi_lap', ''),
                hs.get('nam_tai_lieu', ''),
                hs.get('thoi_han_bao_quan', ''),
                hs.get('so_luong_van_ban', 0),
                hs.get('tinh_trang', '')
            ])
        return cls.export_to_csv_bom(headers, rows, title="DANH MỤC HỒ SƠ LƯU TRỮ CƠ QUAN")
