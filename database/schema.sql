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

-- Chỉ mục tối ưu hóa tốc độ truy vấn cho người dùng
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_ten_dang_nhap ON nguoi_dung(ten_dang_nhap);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_email ON nguoi_dung(email);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_trang_thai ON nguoi_dung(trang_thai);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_vai_tro ON nguoi_dung(vai_tro);


-- ====================================================================
-- PHÂN HỆ QUẢN LÝ CÔNG VIỆC ĐIỀU HÀNH & BÁO CÁO THỐNG KÊ (TASK MANAGEMENT)
-- Nhánh: task-management
-- Phân quyền cho: VĂN THƯ, CHUYÊN VIÊN, LÃNH ĐẠO
-- ====================================================================

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
    -- Thông tin văn bản liên kết (Căn cứ pháp lý / chỉ đạo điều hành)
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

-- Bảng nhật ký tiến độ & trao đổi công việc
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
