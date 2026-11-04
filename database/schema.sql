-- Bảng người dùng trong hệ thống Quản lý văn bản điều hành
-- Sở Giáo dục và Đào tạo TP. Đà Nẵng
-- Lưu ý: Chỉ duy nhất bảng này được khởi tạo trên nhánh main của Leader.

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

-- Chỉ mục tối ưu hóa tốc độ truy vấn
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_ten_dang_nhap ON nguoi_dung(ten_dang_nhap);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_email ON nguoi_dung(email);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_trang_thai ON nguoi_dung(trang_thai);
CREATE INDEX IF NOT EXISTS idx_nguoi_dung_vai_tro ON nguoi_dung(vai_tro);

-- ============================================================
-- PHÂN HỆ: KHO LƯU TRỮ VĂN BẢN & HỒ SƠ CƠ QUAN
-- Nhánh: document-storage | Phụ trách: trungkien11oppo-creator
-- ============================================================

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

-- ============================================================
-- PHÂN HỆ: KHO LƯU TRỮ VĂN BẢN (DATE-TIME & BIỂU MẪU)
-- Nhánh: document-storage | Phụ trách: trungkien11oppo-creator
-- Gồm 2 kho chính:
-- 1. van_ban_ban_hanh: Văn bản đã ký ban hành (Quản lý theo trục thời gian Date-Time)
-- 2. van_ban_mau: Biểu mẫu hành chính chuẩn Sở GD&ĐT
-- ============================================================

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
CREATE INDEX IF NOT EXISTS idx_vbbh_nam_het_han ON van_ban_ban_hanh(nam_het_han_bao_quan);

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
CREATE INDEX IF NOT EXISTS idx_vbm_trang_thai ON van_ban_mau(trang_thai);
