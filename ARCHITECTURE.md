# KIẾN TRÚC HỆ THỐNG THEO MÔ HÌNH MVC (MODEL - VIEW - CONTROLLER)
## Đề tài: Quản lý văn bản điều hành Sở GD&ĐT TP. Đà Nẵng

---

### 1. SƠ ĐỒ TỔNG THỂ KIẾN TRÚC MVC

```
                        [ NGƯỜI DÙNG / TRÌNH DUYỆT WEB ]
                                      │
                         HTTP Requests (GET/POST/PUT)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CONTROLLER (Bộ điều khiển)                           │
│  - app.py: Dispatcher trung tâm điều hướng request                          │
│  - backend/*/routes.py: 8 Flask Blueprints RESTful API                      │
│  - backend/auth/decorators.py: Guards phân quyền (@login_required, @role)   │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
               Gọi nghiệp vụ & truy xuất dữ liệu
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MODEL (Dữ liệu & Nghiệp vụ)                         │
│  - database/schema.sql: 10 bảng CSDL SQLite quan hệ chặt chẽ               │
│  - database/db.py: Connection Pool (sqlite3.Row, PRAGMA foreign_keys = ON) │
│  - backend/*/services.py: Xử lý Business Logic, tính toán, mã hóa mật khẩu  │
│  - backend/documents/pdf_sign.py: Đóng dấu chữ ký số điện tử chuẩn NĐ 30   │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
                  Trả về dữ liệu JSON / File Stream
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VIEW (Giao diện hiển thị)                          │
│  - frontend/pages/: Các trang HTML ngữ cảnh theo vai trò cán bộ              │
│  - frontend/css/: Hệ thống giao diện chuẩn cơ quan hành chính Nhà nước      │
│  - frontend/js/core/: api.js (Fetch wrapper), menu.js (Sidebar role-based), │
│                       auth-guard.js (Bảo vệ tuyến đường), toast.js          │
│  - frontend/js/mock/: Service Adapter trung gian kết nối Controller         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. PHÂN TÁCH CHI TIẾT CÁC THÀNH PHẦN

#### A. MODEL (Tầng dữ liệu & Logic nghiệp vụ)
1. **Cơ sở dữ liệu SQLite (`database/`):**
   * `schema.sql`: Định nghĩa toàn bộ 10 bảng dữ liệu (`nguoi_dung`, `van_ban_di`, `lich_su_xu_ly_van_ban`, `ho_so_luu_tru`, `van_ban_ban_hanh`, `van_ban_mau`, `thong_bao`, `thong_bao_da_doc`, `cong_viec`, `nhat_ky_cong_viec`, `mau_van_ban`, `lich_su_chat`).
   * `db.py`: Cung cấp hàm `get_db()` theo vòng đời request của Flask, quản lý kết nối và đóng kết nối an toàn.
   * `init_db.py`: Nạp schema và seed dữ liệu mẫu đầy đủ cho tất cả các phân hệ.
2. **Services (`backend/*/services.py`):**
   * Xử lý xác thực, hash mật khẩu `scrypt/pbkdf2` qua Werkzeug.
   * Xử lý kiểm tra điều kiện chuyển trạng thái văn bản theo quy trình 5 bước.
   * `pdf_sign.py`: Nhúng chữ ký số và con dấu đỏ điện tử vào file PDF tại tọa độ click chuột của Lãnh đạo.

#### B. CONTROLLER (Tầng điều khiển & Điều phối)
1. **Dispatcher (`app.py`):**
   * Khởi tạo ứng dụng Flask, nạp cấu hình `Config`.
   * Đăng ký 8 Blueprints điều khiển tương ứng với 8 phân hệ con.
   * Phục vụ static frontend và bắt lỗi toàn cục (`404`, `500`).
2. **Blueprints (`backend/*/routes.py`):**
   * `backend/auth/routes.py`: Tiếp nhận đăng nhập, đăng ký, đổi mật khẩu, phiên làm việc (`/api/auth/*`).
   * `backend/users/routes.py`: Duyệt tài khoản, phân quyền, quản lý cán bộ (`/api/users/*`).
   * `backend/documents/routes.py`: Tiếp nhận soạn thảo, chuyển văn thư, lãnh đạo ký số, ban hành (`/api/van-ban-di/*`).
   * `backend/ho_so/routes.py`: Quản lý hồ sơ cơ quan (`/api/ho-so/*`).
   * `backend/kho_van_ban/routes.py`: Tra cứu văn bản theo trục thời gian niên đại và biểu mẫu (`/api/kho-van-ban/*`).
   * `backend/thong_bao/routes.py`: Thông báo điều hành, nhắc nhở tự động theo lịch hẹn (`/api/thong-bao/*`).
   * `backend/cong_viec/routes.py`: Giao việc, cập nhật tiến độ, đánh giá nhiệm vụ (`/api/cong-viec/*`).
   * `backend/chatbot/routes.py`: Trợ lý ảo AI gợi ý mẫu văn bản và tra cứu pháp quy (`/api/chatbot/*`).
3. **Guards & Middleware (`backend/auth/decorators.py`):**
   * `@login_required`: Kiểm tra Session Cookie xác thực.
   * `@role_required`: Phân quyền RBAC (`VAN_THU`, `LANH_DAO`, `CHUYEN_VIEN`).

#### C. VIEW (Tầng giao diện & Trình diễn)
1. **Templates / Pages (`frontend/pages/`):**
   * `van-ban-di/`: Soạn thảo, Ký số, Ban hành, Chi tiết, Danh sách.
   * `van-ban-den/`: Tiếp nhận, Phân công, Xử lý.
   * `cong-viec/`: Giao việc, Danh sách nhiệm vụ, Báo cáo kết quả, Phê duyệt.
   * `ho-so/`: Lưu trữ hồ sơ, Xem danh mục tài liệu.
   * `thong-bao.html`: Trung tâm thông báo & nhắc nhở.
   * `chatbot.html`: Giao diện tương tác với trợ lý ảo và xem trước mẫu A4.
   * `dashboard.html`: Bảng điều khiển phân quyền theo từng vai trò.
2. **Presentation Logic (`frontend/js/core/`):**
   * `api.js`: Wrapper chuẩn giao tiếp RESTful với Controllers.
   * `menu.js`: Render menu sidebar động theo vai trò người dùng đăng nhập.
   * `notification-bell.js`: Chuông thông báo trên topbar hiển thị số lượng và danh sách nhắc nhở.
