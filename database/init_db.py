import sys
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# Đảm bảo console trên Windows hỗ trợ utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config

def init_database():
    """Khởi tạo file CSDL SQLite và nạp bảng dữ liệu đầy đủ."""
    db_path = Path(Config.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    schema_path = Path(__file__).resolve().parent / 'schema.sql'
    if not schema_path.exists():
        print(f"[LỖI] Không tìm thấy file schema tại: {schema_path}")
        return False

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.execute('PRAGMA foreign_keys = ON;')
    cursor = conn.cursor()

    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"[OK] Đã khởi tạo schema CSDL thành công tại: {Config.DATABASE_PATH}")
    except Exception as e:
        print(f"[LỖI] Khởi tạo schema thất bại: {e}")
        conn.close()
        return False

    default_hash = generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD)

    # 1. Seed danh sách người dùng mẫu (Văn thư, Lãnh đạo, Chuyên viên)
    users_to_seed = [
        {
            'ten_dang_nhap': Config.DEFAULT_ADMIN_USERNAME,
            'mat_khau_hash': default_hash,
            'ho_va_ten': Config.DEFAULT_ADMIN_NAME,
            'email': Config.DEFAULT_ADMIN_EMAIL,
            'sdt': '0236.3822.456',
            'phong_ban': 'Văn phòng Sở GD&ĐT',
            'chuc_vu': 'Văn thư cơ quan',
            'vai_tro': 'VAN_THU',
            'trang_thai': 'HOAT_DONG',
            'bat_buoc_doi_mat_khau': 1
        },
        {
            'ten_dang_nhap': 'lanhdao_thuan',
            'mat_khau_hash': default_hash,
            'ho_va_ten': 'Lê Thị Bích Thuận',
            'email': 'thuanltb@danang.edu.vn',
            'sdt': '0905.123.789',
            'phong_ban': 'Ban Giám đốc Sở',
            'chuc_vu': 'Giám đốc Sở',
            'vai_tro': 'LANH_DAO',
            'trang_thai': 'HOAT_DONG',
            'bat_buoc_doi_mat_khau': 0
        },
        {
            'ten_dang_nhap': 'chuyenvien_nam',
            'mat_khau_hash': default_hash,
            'ho_va_ten': 'Trần Văn Nam',
            'email': 'namtv@danang.edu.vn',
            'sdt': '0913.456.789',
            'phong_ban': 'Phòng Giáo dục Trung học',
            'chuc_vu': 'Chuyên viên chính',
            'vai_tro': 'CHUYEN_VIEN',
            'trang_thai': 'HOAT_DONG',
            'bat_buoc_doi_mat_khau': 0
        },
        {
            'ten_dang_nhap': 'chuyenvien_tuan',
            'mat_khau_hash': default_hash,
            'ho_va_ten': 'Hoàng Minh Tuấn',
            'email': 'tuanhm@danang.edu.vn',
            'sdt': '0988.567.890',
            'phong_ban': 'Phòng Giáo dục Tiểu học',
            'chuc_vu': 'Chuyên viên',
            'vai_tro': 'CHUYEN_VIEN',
            'trang_thai': 'HOAT_DONG',
            'bat_buoc_doi_mat_khau': 0
        },
        {
            'ten_dang_nhap': 'chuyenvien_thao',
            'mat_khau_hash': default_hash,
            'ho_va_ten': 'Lê Thị Thảo',
            'email': 'thaolt@danang.edu.vn',
            'sdt': '0977.345.678',
            'phong_ban': 'Phòng Kế hoạch - Tài chính',
            'chuc_vu': 'Chuyên viên kế hoạch',
            'vai_tro': 'CHUYEN_VIEN',
            'trang_thai': 'HOAT_DONG',
            'bat_buoc_doi_mat_khau': 0
        }
    ]

    for u in users_to_seed:
        cursor.execute('SELECT nguoi_dung_id FROM nguoi_dung WHERE ten_dang_nhap = ?', (u['ten_dang_nhap'],))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO nguoi_dung (
                    ten_dang_nhap, mat_khau_hash, ho_va_ten, email,
                    sdt, phong_ban, chuc_vu, vai_tro, trang_thai,
                    bat_buoc_doi_mat_khau, so_lan_dang_nhap_sai
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                u['ten_dang_nhap'], u['mat_khau_hash'], u['ho_va_ten'], u['email'],
                u['sdt'], u['phong_ban'], u['chuc_vu'], u['vai_tro'], u['trang_thai'],
                u['bat_buoc_doi_mat_khau'], 0
            ))
    conn.commit()
    print("[OK] Đã seed danh sách người dùng mẫu (Văn thư, Lãnh đạo, Chuyên viên).")

    # Lấy ID của các cán bộ để liên kết khóa ngoại
    cursor.execute("SELECT nguoi_dung_id, ho_va_ten, vai_tro FROM nguoi_dung")
    user_map = {row[1]: row[0] for row in cursor.fetchall()}
    cursor.execute("SELECT nguoi_dung_id FROM nguoi_dung WHERE vai_tro = 'LANH_DAO' LIMIT 1")
    lanh_dao_row = cursor.fetchone()
    lanh_dao_id = lanh_dao_row[0] if lanh_dao_row else 1

    cursor.execute("SELECT nguoi_dung_id FROM nguoi_dung WHERE vai_tro = 'VAN_THU' LIMIT 1")
    van_thu_row = cursor.fetchone()
    van_thu_id = van_thu_row[0] if van_thu_row else 1

    # 2. Seed danh sách công việc điều hành mẫu (có gắn văn bản liên kết)
    tasks_to_seed = [
        {
            'ten_cong_viec': 'Tổng hợp số liệu dự kiến tuyển sinh lớp 10 THPT công lập năm 2026',
            'noi_dung': 'Thu thập bảng khảo sát nguyện vọng học sinh lớp 9 từ các trường THCS và năng lực tiếp nhận của 21 trường THPT công lập trên địa bàn thành phố Đà Nẵng.',
            'nguoi_giao_id': lanh_dao_id,
            'nguoi_giao_ten': 'Lê Thị Bích Thuận (Giám đốc Sở)',
            'nguoi_xu_ly_id': user_map.get('Trần Văn Nam', 3),
            'nguoi_xu_ly_ten': 'Trần Văn Nam',
            'phong_ban': 'Phòng Giáo dục Trung học',
            'ngay_giao': '2026-10-28',
            'han_hoan_thanh': '2026-11-10',
            'do_uu_tien': 'CAO',
            'tien_do': 85,
            'trang_thai': 'DANG_THUC_HIEN',
            'ket_qua_bao_cao': 'Đã hoàn thành thu thập số liệu 19/21 trường THPT, đang hoàn thiện báo cáo phân tích tỷ lệ chọi.',
            'danh_gia_lanh_dao': '',
            'so_ky_hieu_vb': '452/BGDĐT-GDTrH',
            'trich_yeu_vb': 'Hướng dẫn công tác tổ chức tuyển sinh các lớp đầu cấp năm học 2026-2027',
            'ngay_van_ban': '2026-10-20'
        },
        {
            'ten_cong_viec': 'Xây dựng dự thảo Kế hoạch bồi dưỡng giáo viên Tin học và Ngoại ngữ hè 2026',
            'noi_dung': 'Liên hệ Trường Đại học Sư phạm - Đại học Đà Nẵng để thống nhất khung chương trình tập huấn nâng cao năng lực chuyển đổi số.',
            'nguoi_giao_id': lanh_dao_id,
            'nguoi_giao_ten': 'Lê Thị Bích Thuận (Giám đốc Sở)',
            'nguoi_xu_ly_id': user_map.get('Hoàng Minh Tuấn', 4),
            'nguoi_xu_ly_ten': 'Hoàng Minh Tuấn',
            'phong_ban': 'Phòng Giáo dục Tiểu học',
            'ngay_giao': '2026-10-25',
            'han_hoan_thanh': '2026-11-15',
            'do_uu_tien': 'TRUNG_BINH',
            'tien_do': 50,
            'trang_thai': 'DANG_THUC_HIEN',
            'ket_qua_bao_cao': 'Đã hoàn thành đề cương khung và danh sách báo cáo viên dự kiến.',
            'danh_gia_lanh_dao': '',
            'so_ky_hieu_vb': '890/UBND-VX',
            'trich_yeu_vb': 'Chỉ đạo nâng cao năng lực ứng dụng CNTT và Ngoại ngữ cho đội ngũ giáo viên tiểu học',
            'ngay_van_ban': '2026-10-18'
        },
        {
            'ten_cong_viec': 'Thẩm định hồ sơ công nhận trường chuẩn Quốc gia mức độ 2 THCS Nguyễn Khuyến',
            'noi_dung': 'Kiểm tra thực tế các tiêu chuẩn phòng thí nghiệm, sân chơi bài tập, tỷ lệ máy tính/học sinh theo Thông tư số 18/2018/TT-BGDĐT.',
            'nguoi_giao_id': lanh_dao_id,
            'nguoi_giao_ten': 'Lê Thị Bích Thuận (Giám đốc Sở)',
            'nguoi_xu_ly_id': user_map.get('Lê Thị Thảo', 5),
            'nguoi_xu_ly_ten': 'Lê Thị Thảo',
            'phong_ban': 'Phòng Kế hoạch - Tài chính',
            'ngay_giao': '2026-10-15',
            'han_hoan_thanh': '2026-11-05',
            'do_uu_tien': 'CAO',
            'tien_do': 100,
            'trang_thai': 'CHO_DANH_GIA',
            'ket_qua_bao_cao': 'Đã hoàn thành biên bản nghiệm thu đạt 5/5 tiêu chuẩn chuẩn Quốc gia mức độ 2. Kính trình Lãnh đạo Sở phê duyệt.',
            'danh_gia_lanh_dao': '',
            'so_ky_hieu_vb': '89/TTr-THCSNK',
            'trich_yeu_vb': 'Tờ trình đề nghị thẩm định công nhận đạt chuẩn Quốc gia mức độ 2 trường THCS Nguyễn Khuyến',
            'ngay_van_ban': '2026-10-12'
        },
        {
            'ten_cong_viec': 'Rà soát quy hoạch quỹ đất giáo dục tại khu đô thị Tây Bắc',
            'noi_dung': 'Phối hợp Sở Xây dựng thẩm tra 3 vị trí dự kiến xây dựng trường liên cấp phục vụ con em khu công nghệ cao.',
            'nguoi_giao_id': lanh_dao_id,
            'nguoi_giao_ten': 'Lê Thị Bích Thuận (Giám đốc Sở)',
            'nguoi_xu_ly_id': user_map.get('Trần Văn Nam', 3),
            'nguoi_xu_ly_ten': 'Trần Văn Nam',
            'phong_ban': 'Văn phòng Sở GD&ĐT',
            'ngay_giao': '2026-10-01',
            'han_hoan_thanh': '2026-10-25',
            'do_uu_tien': 'TRUNG_BINH',
            'tien_do': 100,
            'trang_thai': 'HOAN_THANH',
            'ket_qua_bao_cao': 'Đã trình UBND TP bản đồ quy hoạch chi tiết 1/500 và thống nhất vị trí cắm mốc.',
            'danh_gia_lanh_dao': 'Hoàn thành xuất sắc, đúng tiến độ và đầy đủ hồ sơ pháp lý.',
            'so_ky_hieu_vb': '204/TB-UBND',
            'trich_yeu_vb': 'Thông báo kết luận của Chủ tịch UBND TP về quy hoạch mạng lưới trường học khu vực Tây Bắc',
            'ngay_van_ban': '2026-10-01'
        },
        {
            'ten_cong_viec': 'Khẩn trương kiểm tra cơ sở vật chất phòng chống bão lũ tại các trường ven sông',
            'noi_dung': 'Kiểm tra hệ thống thoát nước, chằng chống cây xanh và an toàn điện lưới tại các trường mầm non, tiểu học vùng trũng huyện Hòa Vang.',
            'nguoi_giao_id': lanh_dao_id,
            'nguoi_giao_ten': 'Lê Thị Bích Thuận (Giám đốc Sở)',
            'nguoi_xu_ly_id': user_map.get('Hoàng Minh Tuấn', 4),
            'nguoi_xu_ly_ten': 'Hoàng Minh Tuấn',
            'phong_ban': 'Phòng Giáo dục Tiểu học',
            'ngay_giao': '2026-10-20',
            'han_hoan_thanh': '2026-11-01',
            'do_uu_tien': 'KHAN_CAP',
            'tien_do': 40,
            'trang_thai': 'QUA_HAN',
            'ket_qua_bao_cao': 'Đã kiểm tra 8/14 điểm trường, 6 điểm trường còn lại đang tiếp tục tổng hợp phương án di dời trang thiết bị.',
            'danh_gia_lanh_dao': '',
            'so_ky_hieu_vb': '15/CĐ-PCTT',
            'trich_yeu_vb': 'Công điện khẩn về ứng phó mưa lớn kéo dài và lũ cục bộ trên địa bàn TP. Đà Nẵng',
            'ngay_van_ban': '2026-10-20'
        },
        {
            'ten_cong_viec': 'Tổ chức Hội nghị tập huấn Quy chế Quản lý văn bản điều hành điện tử năm 2026',
            'noi_dung': 'Xây dựng tài liệu hướng dẫn và tổ chức tập huấn trực tuyến cho văn thư, cán bộ CNTT của tất cả các trường THPT trực thuộc.',
            'nguoi_giao_id': van_thu_id,
            'nguoi_giao_ten': 'Văn thư Sở GD&ĐT Đà Nẵng',
            'nguoi_xu_ly_id': user_map.get('Lê Thị Thảo', 5),
            'nguoi_xu_ly_ten': 'Lê Thị Thảo',
            'phong_ban': 'Phòng Kế hoạch - Tài chính',
            'ngay_giao': '2026-11-01',
            'han_hoan_thanh': '2026-11-20',
            'do_uu_tien': 'TRUNG_BINH',
            'tien_do': 0,
            'trang_thai': 'CHUA_THUC_HIEN',
            'ket_qua_bao_cao': '',
            'danh_gia_lanh_dao': '',
            'so_ky_hieu_vb': '12/KH-SGDĐT',
            'trich_yeu_vb': 'Kế hoạch chuyển đổi số và số hóa công tác hành chính văn phòng Sở GD&ĐT năm 2026',
            'ngay_van_ban': '2026-11-01'
        }
    ]

    cursor.execute("SELECT COUNT(*) FROM cong_viec")
    if cursor.fetchone()[0] == 0:
        for t in tasks_to_seed:
            cursor.execute('''
                INSERT INTO cong_viec (
                    ten_cong_viec, noi_dung, nguoi_giao_id, nguoi_giao_ten,
                    nguoi_xu_ly_id, nguoi_xu_ly_ten, phong_ban, ngay_giao,
                    han_hoan_thanh, do_uu_tien, tien_do, trang_thai,
                    ket_qua_bao_cao, danh_gia_lanh_dao,
                    so_ky_hieu_vb, trich_yeu_vb, ngay_van_ban
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                t['ten_cong_viec'], t['noi_dung'], t['nguoi_giao_id'], t['nguoi_giao_ten'],
                t['nguoi_xu_ly_id'], t['nguoi_xu_ly_ten'], t['phong_ban'], t['ngay_giao'],
                t['han_hoan_thanh'], t['do_uu_tien'], t['tien_do'], t['trang_thai'],
                t['ket_qua_bao_cao'], t['danh_gia_lanh_dao'],
                t['so_ky_hieu_vb'], t['trich_yeu_vb'], t['ngay_van_ban']
            ))
            task_id = cursor.lastrowid
            # Thêm nhật ký khởi tạo
            cursor.execute('''
                INSERT INTO nhat_ky_cong_viec (
                    cong_viec_id, nguoi_cap_nhat_id, nguoi_cap_nhat_ten,
                    tien_do_cu, tien_do_moi, noi_dung_ghi_chu
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                task_id, t['nguoi_giao_id'], t['nguoi_giao_ten'],
                0, t['tien_do'], f"Khởi tạo nhiệm vụ: {t['ten_cong_viec']}"
            ))
        conn.commit()
        print(f"[OK] Đã seed thành công {len(tasks_to_seed)} nhiệm vụ công việc mẫu kèm thông tin văn bản.")
    else:
        print("[INFO] Bảng cong_viec đã có dữ liệu, bỏ qua bước seed công việc.")

    conn.close()
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("KHỞI TẠO CƠ SỞ DỮ LIỆU QLVB - SỞ GD&ĐT TP. ĐÀ NẴNG")
    print("=" * 60)
    init_database()
