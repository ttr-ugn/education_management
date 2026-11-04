-- ============================================================================
-- CƠ SỞ DỮ LIỆU TOÀN DIỆN HỆ THỐNG QUẢN LÝ VĂN BẢN & ĐIỀU HÀNH NỘI BỘ
-- SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG
-- Tích hợp đầy đủ 5 phân hệ (MVC Architecture):
-- 1. Người dùng & Xác thực (Auth & Users)
-- 2. Quản lý văn bản đi (Document Management - 5 bước & Ký số)
-- 3. Kho lưu trữ văn bản & Hồ sơ cơ quan (Document Storage)
-- 4. Thông báo & Nhắc nhở điều hành (Notifications & Reminders)
-- 5. Theo dõi công việc & Báo cáo thống kê (Task Management)
-- 6. Trợ lý ảo AI Chatbox & Kho mẫu văn bản (Chatbot Assistant)
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- 1. PHÂN HỆ: NGƯỜI DÙNG & TÀI KHOẢN HỆ THỐNG
-- ============================================================================

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

CREATE INDEX IF NOT EXISTS idx_nguoi_dung_ten_dang_nhap ON nguoi_dung(ten_dang_nhap);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_email ON nguoi_dung(email);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_trang_thai ON nguoi_dung(trang_thai);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_vai_tro ON nguoi_dung(vai_tro);

-- ============================================================================
-- 2. PHÂN HỆ: QUẢN LÝ VĂN BẢN ĐI (VÒNG ĐỜI 5 BƯỚC & KÝ SỐ ĐIỆN TỬ)
-- Chuyên viên -> Văn thư -> Lãnh đạo (Ký số) -> Văn thư (Ban hành) -> Chuyên viên
-- ============================================================================

CREATE TABLE IF NOT EXISTS van_ban_di (
    van_ban_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    so_ky_hieu             TEXT,
    trich_yeu              TEXT NOT NULL,
    loai_van_ban           TEXT NOT NULL,
    do_khan                TEXT DEFAULT 'Bình thường',
    don_vi_soan_thao       TEXT NOT NULL,
    noi_nhan               TEXT NOT NULL,
    noi_dung_tom_tat       TEXT,
    file_goc_path          TEXT NOT NULL,
    file_goc_ten           TEXT NOT NULL,
    file_goc_dung_luong    TEXT,
    file_da_ky_path        TEXT,
    file_da_ky_ten         TEXT,
    nguoi_soan_id          INTEGER NOT NULL,
    van_thu_id             INTEGER,
    lanh_dao_ky_id         INTEGER,
    lanh_dao_ky_ten        TEXT,
    trang_thai             TEXT NOT NULL CHECK (trang_thai IN (
                               'CHO_VAN_THU_KIEM_TRA',
                               'VAN_THU_TRA_LAI',
                               'CHO_LANH_DAO_KY',
                               'LANH_DAO_TRA_LAI',
                               'DA_KY_CHO_BAN_HANH',
                               'DA_BAN_HANH'
                           )) DEFAULT 'CHO_VAN_THU_KIEM_TRA',
    y_kien_van_thu         TEXT,
    y_kien_lanh_dao        TEXT,
    ky_so_trang            INTEGER,
    ky_so_x                REAL,
    ky_so_y                REAL,
    thoi_gian_ky           TEXT,
    ngay_tao               TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_trinh_van_thu     TEXT,
    ngay_trinh_lanh_dao    TEXT,
    ngay_ban_hanh          TEXT,
    FOREIGN KEY (nguoi_soan_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE RESTRICT,
    FOREIGN KEY (van_thu_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL,
    FOREIGN KEY (lanh_dao_ky_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS lich_su_xu_ly_van_ban (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    van_ban_id             INTEGER NOT NULL,
    nguoi_thuc_hien_id     INTEGER NOT NULL,
    hanh_dong              TEXT NOT NULL,
    trang_thai_truoc       TEXT,
    trang_thai_sau         TEXT NOT NULL,
    noi_dung               TEXT,
    thoi_gian              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (van_ban_id) REFERENCES van_ban_di(van_ban_id) ON DELETE CASCADE,
    FOREIGN KEY (nguoi_thuc_hien_id) REFERENCES nguoi_dung(nguoi_dung_id)
);

CREATE INDEX IF NOT EXISTS idx_van_ban_di_trang_thai ON van_ban_di(trang_thai);
CREATE INDEX IF NOT EXISTS idx_van_ban_di_nguoi_soan ON van_ban_di(nguoi_soan_id);
CREATE INDEX IF NOT EXISTS idx_van_ban_di_lanh_dao ON van_ban_di(lanh_dao_ky_id);
CREATE INDEX IF NOT EXISTS idx_van_ban_di_ngay_tao ON van_ban_di(ngay_tao);
CREATE INDEX IF NOT EXISTS idx_lich_su_van_ban_id ON lich_su_xu_ly_van_ban(van_ban_id);

-- ============================================================================
-- 3. PHÂN HỆ: KHO LƯU TRỮ VĂN BẢN & HỒ SƠ TÀI LIỆU
-- ============================================================================

CREATE TABLE IF NOT EXISTS ho_so_luu_tru (
    ho_so_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_ho_so          TEXT NOT NULL UNIQUE COLLATE NOCASE,
    tieu_de           TEXT NOT NULL,
    nguoi_lap_id      INTEGER,
    nguoi_lap         TEXT NOT NULL,
    don_vi            TEXT NOT NULL,
    nam_tai_lieu      INTEGER NOT NULL DEFAULT 2026,
    thoi_han_bao_quan TEXT NOT NULL DEFAULT '10 năm',
    so_luong_van_ban  INTEGER NOT NULL DEFAULT 0,
    tinh_trang        TEXT NOT NULL CHECK (tinh_trang IN ('DANG_THU_THAP', 'DA_NOP_LUU_TRU', 'DA_DONG')) DEFAULT 'DANG_THU_THAP',
    mo_ta             TEXT,
    ngay_tao          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nguoi_lap_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_ho_so_ma_ho_so ON ho_so_luu_tru(ma_ho_so);
CREATE INDEX IF NOT EXISTS idx_ho_so_tinh_trang ON ho_so_luu_tru(tinh_trang);
CREATE INDEX IF NOT EXISTS idx_ho_so_nam_tai_lieu ON ho_so_luu_tru(nam_tai_lieu);

CREATE TABLE IF NOT EXISTS van_ban_ban_hanh (
    van_ban_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    so_ky_hieu           TEXT NOT NULL UNIQUE COLLATE NOCASE,
    trich_yeu            TEXT NOT NULL,
    loai_van_ban         TEXT NOT NULL,
    co_quan_ban_hanh     TEXT NOT NULL DEFAULT 'Sở Giáo dục và Đào tạo TP. Đà Nẵng',
    don_vi_soan_thao     TEXT,
    nguoi_ky             TEXT NOT NULL,
    chuc_vu_nguoi_ky     TEXT NOT NULL,
    ngay_ky              TEXT NOT NULL,
    ngay_ban_hanh        TEXT NOT NULL,
    nam_luu_tru          INTEGER NOT NULL,
    thang_luu_tru        INTEGER NOT NULL,
    quy_luu_tru          INTEGER NOT NULL,
    thoi_han_bao_quan    TEXT NOT NULL DEFAULT '10 năm',
    nam_het_han_bao_quan INTEGER,
    muc_do_mat           TEXT NOT NULL CHECK (muc_do_mat IN ('THUONG', 'MAT', 'TOI_MAT')) DEFAULT 'THUONG',
    do_khan              TEXT NOT NULL CHECK (do_khan IN ('THUONG', 'HOA_TOC', 'THUONG_KHAN')) DEFAULT 'THUONG',
    so_to_so_trang       INTEGER DEFAULT 1,
    ho_so_id             INTEGER,
    tep_dinh_kem         TEXT,
    dinh_dang_tep        TEXT DEFAULT 'pdf',
    dung_luong_kb        INTEGER DEFAULT 0,
    ma_xac_thuc_so       TEXT,
    tu_khoa              TEXT,
    ghi_chu              TEXT,
    nguoi_luu_id         INTEGER,
    ngay_tao             TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ho_so_id) REFERENCES ho_so_luu_tru(ho_so_id) ON DELETE SET NULL,
    FOREIGN KEY (nguoi_luu_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_vbbh_so_ky_hieu ON van_ban_ban_hanh(so_ky_hieu);
CREATE INDEX IF NOT EXISTS idx_vbbh_ngay_ban_hanh ON van_ban_ban_hanh(ngay_ban_hanh);
CREATE INDEX IF NOT EXISTS idx_vbbh_nam_thang ON van_ban_ban_hanh(nam_luu_tru, thang_luu_tru);
CREATE INDEX IF NOT EXISTS idx_vbbh_loai_van_ban ON van_ban_ban_hanh(loai_van_ban);

CREATE TABLE IF NOT EXISTS van_ban_mau (
    bieu_mau_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_bieu_mau          TEXT NOT NULL UNIQUE COLLATE NOCASE,
    ten_bieu_mau         TEXT NOT NULL,
    loai_van_ban         TEXT NOT NULL,
    linh_vuc             TEXT NOT NULL,
    phien_ban            TEXT NOT NULL DEFAULT '1.0',
    ngay_ap_dung         TEXT NOT NULL,
    trang_thai           TEXT NOT NULL CHECK (trang_thai IN ('DANG_AP_DUNG', 'HET_HIEU_LUC')) DEFAULT 'DANG_AP_DUNG',
    tep_mau              TEXT NOT NULL,
    dinh_dang_tep        TEXT NOT NULL DEFAULT 'docx',
    dung_luong_kb        INTEGER DEFAULT 0,
    luot_tai             INTEGER NOT NULL DEFAULT 0,
    huong_dan_dien       TEXT,
    nguoi_tao_id         INTEGER,
    ngay_tao             TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nguoi_tao_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_vbm_ma_bieu_mau ON van_ban_mau(ma_bieu_mau);
CREATE INDEX IF NOT EXISTS idx_vbm_loai_van_ban ON van_ban_mau(loai_van_ban);
CREATE INDEX IF NOT EXISTS idx_vbm_linh_vuc ON van_ban_mau(linh_vuc);

-- ============================================================================
-- 4. PHÂN HỆ: THÔNG BÁO & NHẮC NHỞ ĐIỀU HÀNH
-- ============================================================================

CREATE TABLE IF NOT EXISTS thong_bao (
    thong_bao_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    tieu_de                TEXT NOT NULL,
    noi_dung               TEXT NOT NULL,
    loai                   TEXT NOT NULL DEFAULT 'Hệ thống' CHECK (loai IN ('Cuộc họp', 'Hệ thống', 'Khen thưởng', 'Văn bản', 'Công việc', 'Nhắc nhở', 'Khác')),
    muc_do                 TEXT NOT NULL DEFAULT 'Bình thường' CHECK (muc_do IN ('Bình thường', 'Quan trọng', 'Khẩn cấp')),
    nguoi_gui_id           INTEGER,
    nguoi_nhan_id          INTEGER,
    ngay_hen_gio           TEXT,
    lien_ket               TEXT,
    ngay_tao               TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nguoi_gui_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL,
    FOREIGN KEY (nguoi_nhan_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS thong_bao_da_doc (
    thong_bao_id           INTEGER NOT NULL,
    nguoi_dung_id          INTEGER NOT NULL,
    ngay_doc               TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (thong_bao_id, nguoi_dung_id),
    FOREIGN KEY (thong_bao_id) REFERENCES thong_bao(thong_bao_id) ON DELETE CASCADE,
    FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_thong_bao_nguoi_nhan ON thong_bao(nguoi_nhan_id);
CREATE INDEX IF NOT EXISTS idx_thong_bao_loai ON thong_bao(loai);
CREATE INDEX IF NOT EXISTS idx_thong_bao_ngay_tao ON thong_bao(ngay_tao);

-- ============================================================================
-- 5. PHÂN HỆ: QUẢN LÝ CÔNG VIỆC & THEO DÕI TIẾN ĐỘ
-- ============================================================================

CREATE TABLE IF NOT EXISTS cong_viec (
    cong_viec_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_cong_viec         TEXT NOT NULL,
    noi_dung              TEXT,
    nguoi_giao_id         INTEGER,
    nguoi_xu_ly_id        INTEGER,
    nguoi_giao_ten        TEXT,
    nguoi_xu_ly_ten       TEXT,
    phong_ban             TEXT NOT NULL,
    ngay_giao             TEXT NOT NULL DEFAULT (DATE('now', 'localtime')),
    han_hoan_thanh        TEXT NOT NULL,
    do_uu_tien            TEXT NOT NULL CHECK (do_uu_tien IN ('THAP', 'TRUNG_BINH', 'CAO', 'KHAN_CAP')) DEFAULT 'TRUNG_BINH',
    tien_do               INTEGER NOT NULL DEFAULT 0 CHECK (tien_do >= 0 AND tien_do <= 100),
    trang_thai            TEXT NOT NULL CHECK (trang_thai IN ('CHUA_THUC_HIEN', 'DANG_THUC_HIEN', 'CHO_DANH_GIA', 'HOAN_THANH', 'QUA_HAN')) DEFAULT 'CHUA_THUC_HIEN',
    ket_qua_bao_cao       TEXT,
    danh_gia_lanh_dao     TEXT,
    tep_dinh_kem_ket_qua  TEXT,
    so_ky_hieu_vb         TEXT,
    trich_yeu_vb          TEXT,
    ngay_van_ban          TEXT,
    tep_dinh_kem_vb       TEXT,
    ngay_tao              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nguoi_giao_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL,
    FOREIGN KEY (nguoi_xu_ly_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_cong_viec_nguoi_xu_ly ON cong_viec(nguoi_xu_ly_id);
CREATE INDEX IF NOT EXISTS idx_cong_viec_nguoi_giao ON cong_viec(nguoi_giao_id);
CREATE INDEX IF NOT EXISTS idx_cong_viec_trang_thai ON cong_viec(trang_thai);
CREATE INDEX IF NOT EXISTS idx_cong_viec_phong_ban ON cong_viec(phong_ban);
CREATE INDEX IF NOT EXISTS idx_cong_viec_han_hoan_thanh ON cong_viec(han_hoan_thanh);

CREATE TABLE IF NOT EXISTS nhat_ky_cong_viec (
    nhat_ky_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    cong_viec_id         INTEGER NOT NULL,
    nguoi_cap_nhat_id    INTEGER,
    nguoi_cap_nhat_ten   TEXT,
    tien_do_cu           INTEGER DEFAULT 0,
    tien_do_moi          INTEGER NOT NULL,
    noi_dung_ghi_chu     TEXT NOT NULL,
    tep_dinh_kem         TEXT,
    thoi_gian            TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cong_viec_id) REFERENCES cong_viec(cong_viec_id) ON DELETE CASCADE,
    FOREIGN KEY (nguoi_cap_nhat_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_nhat_ky_cong_viec_id ON nhat_ky_cong_viec(cong_viec_id);

-- ============================================================================
-- 6. PHÂN HỆ: TRỢ LÝ ẢO AI CHATBOX & KHO BIỂU MẪU
-- ============================================================================

CREATE TABLE IF NOT EXISTS mau_van_ban (
    mau_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_mau            TEXT NOT NULL UNIQUE COLLATE NOCASE,
    ten_mau           TEXT NOT NULL,
    loai_van_ban      TEXT NOT NULL,
    linh_vuc          TEXT NOT NULL,
    co_quan_ban_hanh  TEXT NOT NULL DEFAULT 'SỞ GIÁO DỤC VÀ ĐÀO TẠO TP. ĐÀ NẴNG',
    tham_quyen_ky     TEXT,
    mo_ta             TEXT,
    can_cu_phap_ly    TEXT,
    tu_khoa           TEXT,
    noi_dung_html     TEXT NOT NULL,
    noi_dung_text     TEXT NOT NULL,
    ten_tep           TEXT,
    luot_xem          INTEGER NOT NULL DEFAULT 0,
    luot_tai          INTEGER NOT NULL DEFAULT 0,
    ngay_tao          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mau_van_ban_loai ON mau_van_ban(loai_van_ban);
CREATE INDEX IF NOT EXISTS idx_mau_van_ban_linh_vuc ON mau_van_ban(linh_vuc);
CREATE INDEX IF NOT EXISTS idx_mau_van_ban_ma_mau ON mau_van_ban(ma_mau);

CREATE TABLE IF NOT EXISTS lich_su_chat (
    tin_nhan_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nguoi_dung_id     INTEGER,
    cau_hoi           TEXT NOT NULL,
    cau_tra_loi       TEXT NOT NULL,
    mau_de_xuat_ids   TEXT,
    thoi_gian         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(nguoi_dung_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_lich_su_chat_user ON lich_su_chat(nguoi_dung_id);
