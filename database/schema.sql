-- Bảng người dùng trong hệ thống Quản lý văn bản điều hành
-- Sở Giáo dục và Đào tạo TP. Đà Nẵng

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nguoi_dung (
    nguoi_dung_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_dang_nhap          TEXT NOT NULL UNIQUE COLLATE BINARY,
    mat_khau_hash          TEXT NOT NULL,
    ho_va_ten              TEXT NOT NULL,
    email                  TEXT NOT NULL UNIQUE COLLATE NOCASE,
    sdt                    TEXT,
    phong_ban              TEXT,
    chuc_vu                TEXT,
    vai_tro                TEXT NOT NULL CHECK (vai_tro IN ('VAN_THU', 'CHUYEN_VIEN', 'LANH_DAO')),
    trang_thai             TEXT NOT NULL CHECK (trang_thai IN ('CHO_DUYET', 'HOAT_DONG', 'TU_CHOI', 'BI_KHOA')),
    ly_do_tu_choi          TEXT,
    bat_buoc_doi_mat_khau  INTEGER NOT NULL DEFAULT 0,
    so_lan_dang_nhap_sai   INTEGER NOT NULL DEFAULT 0,
    khoa_den               TEXT,
    nguoi_tao_id           INTEGER,
    ngay_tao               TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_duyet             TEXT,
    lan_dang_nhap_cuoi     TEXT,
    FOREIGN KEY (nguoi_tao_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL
);

-- Chỉ mục người dùng
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_ten_dang_nhap ON nguoi_dung(ten_dang_nhap);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_email ON nguoi_dung(email);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_trang_thai ON nguoi_dung(trang_thai);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_vai_tro ON nguoi_dung(vai_tro);

-- ========================================================
-- PHÂN HỆ QUẢN LÝ VĂN BẢN ĐI (VÒNG ĐỜI 5 BƯỚC)
-- Chuyên viên -> Văn thư -> Lãnh đạo -> Văn thư -> Chuyên viên
-- ========================================================

CREATE TABLE IF NOT EXISTS van_ban_di (
    van_ban_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    so_ky_hieu             TEXT,                                  -- Số dự thảo hoặc số chính thức khi ban hành
    trich_yeu              TEXT NOT NULL,                         -- Trích yếu nội dung
    loai_van_ban           TEXT NOT NULL,                         -- Công văn, Kế hoạch, Tờ trình, Thông báo...
    do_khan                TEXT DEFAULT 'Bình thường',            -- Bình thường, Khẩn, Thượng khẩn, Hỏa tốc
    don_vi_soan_thao       TEXT NOT NULL,                         -- Tên đơn vị / phòng ban soạn thảo
    noi_nhan               TEXT NOT NULL,                         -- Nơi nhận văn bản
    noi_dung_tom_tat       TEXT,                                  -- Tóm tắt nội dung chi tiết

    -- Tệp đính kèm văn bản
    file_goc_path          TEXT NOT NULL,                         -- Đường dẫn lưu trữ file gốc upload (.pdf, .docx)
    file_goc_ten           TEXT NOT NULL,                         -- Tên file hiển thị ban đầu
    file_goc_dung_luong    TEXT,                                  -- Dung lượng file (ví dụ: '1.2 MB')
    file_da_ky_path        TEXT,                                  -- Đường dẫn file PDF sau khi Lãnh đạo đã gán chữ ký số
    file_da_ky_ten         TEXT,                                  -- Tên file PDF đã ký

    -- Các bên tham gia xử lý
    nguoi_soan_id          INTEGER NOT NULL,                      -- ID Chuyên viên soạn thảo
    van_thu_id             INTEGER,                               -- ID Văn thư tiếp nhận / thẩm định / ban hành
    lanh_dao_ky_id         INTEGER,                               -- ID Lãnh đạo phụ trách ký duyệt
    lanh_dao_ky_ten        TEXT,                                  -- Tên lãnh đạo hiển thị

    -- Trạng thái vòng đời 5 bước
    trang_thai             TEXT NOT NULL CHECK (trang_thai IN (
                               'CHO_VAN_THU_KIEM_TRA',            -- Bước 1: Chuyên viên soạn xong gửi Văn thư
                               'VAN_THU_TRA_LAI',                 -- Bước 2a: Văn thư yêu cầu Chuyên viên sửa
                               'CHO_LANH_DAO_KY',                 -- Bước 2b: Văn thư duyệt gửi Lãnh đạo
                               'LANH_DAO_TRA_LAI',                -- Bước 3a: Lãnh đạo yêu cầu chỉnh sửa
                               'DA_KY_CHO_BAN_HANH',              -- Bước 3b: Lãnh đạo đã ký số bằng click chuột
                               'DA_BAN_HANH'                      -- Bước 4: Văn thư cấp số, đóng dấu, ban hành
                           )) DEFAULT 'CHO_VAN_THU_KIEM_TRA',

    -- Ý kiến phản hồi / Lý do trả lại
    y_kien_van_thu         TEXT,                                  -- Nhận xét hoặc lý do trả lại của Văn thư
    y_kien_lanh_dao        TEXT,                                  -- Ý kiến chỉ đạo hoặc lý do trả lại của Lãnh đạo

    -- Tọa độ chữ ký số trên PDF
    ky_so_trang            INTEGER,                               -- Trang PDF được ký (1-indexed)
    ky_so_x                REAL,                                  -- Tọa độ X trên trang
    ky_so_y                REAL,                                  -- Tọa độ Y trên trang
    thoi_gian_ky           TEXT,                                  -- Timestamp thời điểm ký

    -- Mốc thời gian quy trình
    ngay_tao               TEXT DEFAULT CURRENT_TIMESTAMP,
    ngay_trinh_van_thu     TEXT,
    ngay_trinh_lanh_dao    TEXT,
    ngay_ban_hanh          TEXT,

    FOREIGN KEY (nguoi_soan_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE RESTRICT,
    FOREIGN KEY (van_thu_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL,
    FOREIGN KEY (lanh_dao_ky_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL
);

-- Bảng nhật ký xử lý tiến trình văn bản (Audit Trail)
CREATE TABLE IF NOT EXISTS lich_su_xu_ly_van_ban (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    van_ban_id             INTEGER NOT NULL,
    nguoi_thuc_hien_id     INTEGER NOT NULL,
    hanh_dong              TEXT NOT NULL,                         -- KHOI_TAO, VAN_THU_CHINH_SUA, VAN_THU_TRA_LAI, TRINH_LANH_DAO, LANH_DAO_TRA_LAI, KY_SO, BAN_HANH
    trang_thai_truoc       TEXT,
    trang_thai_sau         TEXT NOT NULL,
    noi_dung               TEXT,
    thoi_gian              TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (van_ban_id) REFERENCES van_ban_di(van_ban_id) ON DELETE CASCADE,
    FOREIGN KEY (nguoi_thuc_hien_id) REFERENCES nguoi_dung(nguoi_dung_id)
);

-- Chỉ mục tối ưu tra cứu văn bản đi
CREATE INDEX IF NOT EXISTS idx_van_ban_di_trang_thai ON van_ban_di(trang_thai);
CREATE INDEX IF NOT EXISTS idx_van_ban_di_nguoi_soan ON van_ban_di(nguoi_soan_id);
CREATE INDEX IF NOT EXISTS idx_van_ban_di_lanh_dao ON van_ban_di(lanh_dao_ky_id);
CREATE INDEX IF NOT EXISTS idx_van_ban_di_ngay_tao ON van_ban_di(ngay_tao);
CREATE INDEX IF NOT EXISTS idx_lich_su_van_ban_id ON lich_su_xu_ly_van_ban(van_ban_id);
