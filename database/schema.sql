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

-- ============================================================================
-- PHÂN HỆ: KHO LƯU TRỮ MẪU VĂN BẢN & TRỢ LÝ ẢO CHATBOX
-- Nhánh: chatbox (Thành viên phụ trách Chatbox gợi ý & tra cứu mẫu văn bản)
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
