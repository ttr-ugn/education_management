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
