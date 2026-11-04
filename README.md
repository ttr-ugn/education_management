# HỆ THỐNG QUẢN LÝ VĂN BẢN ĐIỀU HÀNH
## SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG
**Môn học:** Lập trình Web | **Phiên bản:** 1.0.0 (Nhánh `main` - Leader)

---

## 1. GIỚI THIỆU DỰ ÁN
Dự án phục vụ công tác tin học hóa quản lý văn bản đi, văn bản đến, hồ sơ lưu trữ, phân công giao việc và điều hành nội bộ tại Sở Giáo dục và Đào tạo TP. Đà Nẵng.

### Công nghệ sử dụng:
- **Backend:** Python 3.10+, Flask, SQLite 3 (thư viện chuẩn `sqlite3`), Werkzeug Security.
- **Frontend:** HTML5, CSS3 hiện đại, Vanilla JavaScript (ES6+ fetch API, kiến trúc Module).
- **Cơ sở dữ liệu:** SQLite (`database/qlvb.db`), trực quan hóa qua công cụ **DB Browser for SQLite**.

---

## 2. PHẠM VI NHÁNH `main` CỦA LEADER
1. **Toàn bộ giao diện người dùng (Frontend):** Đã xây dựng đầy đủ tất cả màn hình chức năng theo đặc tả, dùng dữ liệu mẫu (mock data) được đóng gói qua các Service JS.
2. **Backend & CSDL thật cho phân hệ Xác thực & Phân quyền:**
   - Đăng ký tài khoản Chuyên viên (chờ duyệt) và Văn thư (cần mã nội bộ).
   - Đăng nhập (tạo session bảo mật, chống Brute-force khóa tạm 15 phút).
   - Đổi mật khẩu (bắt buộc đổi ở lần đầu đối với Lãnh đạo và Văn thư mặc định).
   - Văn thư duyệt / từ chối tài khoản Chuyên viên có lý do.
   - Văn thư tạo tài khoản Lãnh đạo (sinh mật khẩu tạm 1 lần).
   - Khóa / mở khóa và đặt lại mật khẩu cho người dùng.
   - Phân quyền truy cập đa tầng (Frontend Auth Guard + Backend Decorator `@login_required`, `@role_required`).

---

## 3. HƯỚNG DẪN CÀI ĐẶT & CHẠY TRÊN PYCHARM

### Bước 1: Mở dự án trong PyCharm
- Khởi động PyCharm -> chọn **Open** -> duyệt tới thư mục `D:\education_management`.

### Bước 2: Thiết lập môi trường ảo (Python Virtual Environment)
- Vào **File** -> **Settings** (hoặc `Ctrl + Alt + S`).
- Chọn **Project: education_management** -> **Python Interpreter**.
- Nhấp **Add Interpreter** -> **Add Local Interpreter...**
- Chọn **Existing**, trỏ tới file: `D:\education_management\venv\Scripts\python.exe`.
- Nếu chưa có venv, chọn **New** với Python 3.10+.

### Bước 3: Cài đặt thư viện
Mở Terminal trong PyCharm (`Alt + F12`) và chạy:
```bash
pip install -r requirements.txt
```

### Bước 4: Tạo file cấu hình môi trường `.env`
Sao chép từ `.env.example`:
```bash
cp .env.example .env
```
*(Trên Windows PowerShell có thể chạy `Copy-Item .env.example .env`)*.

Nội dung `.env`:
- `SECRET_KEY`: Khóa bí mật bảo vệ session.
- `DATABASE_PATH`: `database/qlvb.db`.
- `INTERNAL_CODE`: Mã nội bộ để đăng ký Văn thư (`DANANG_SGD_VT2026`).
- `DEFAULT_ADMIN_USERNAME`: `admin_vanthu`
- `DEFAULT_ADMIN_PASSWORD`: `Admin@123`

### Bước 5: Khởi tạo Cơ sở dữ liệu
Trong Terminal PyCharm, chạy lệnh:
```bash
python database/init_db.py
```
Lệnh này sẽ tạo bảng `nguoi_dung` và tự động seed tài khoản Văn thư mặc định.

### Bước 6: Cấu hình Run Configuration và Chạy ứng dụng
1. Trên thanh công cụ PyCharm, nhấp **Add Configuration...** (hoặc **Current File** -> **Edit Configurations**).
2. Nhấp dấu **+** -> chọn **Python**.
3. Đặt tên: `Run App`.
4. Mục **Script path**: Trỏ tới `D:\education_management\app.py`.
5. Mục **Python interpreter**: Chọn venv của dự án.
6. Mục **Working directory**: `D:\education_management`.
7. Nhấn **Apply** -> **OK**.
8. Nhấn nút **Play (Run)** màu xanh (hoặc `Shift + F10`).
9. Mở trình duyệt web và truy cập: [http://localhost:5000](http://localhost:5000)

---

## 4. TÀI KHOẢN MẪU ĐỂ KIỂM THỬ HỆ THỐNG

| Vai trò | Tên đăng nhập | Mật khẩu ban đầu | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Văn thư (Admin)** | `admin_vanthu` | `Admin@123` | Hệ thống yêu cầu đổi mật khẩu ở lần đăng nhập đầu tiên |
| **Đăng ký Văn thư mới** | Form đăng ký | Tự đặt (>=8 ký tự) | Cần nhập đúng mã xác nhận: `DANANG_SGD_VT2026` |
| **Đăng ký Chuyên viên** | Form đăng ký | Tự đặt (>=8 ký tự) | Sẽ vào trạng thái `CHO_DUYET`. Dùng `admin_vanthu` để duyệt |
| **Lãnh đạo** | Văn thư tạo | Hệ thống sinh ngẫu nhiên | Văn thư tạo tại trang Quản trị, mật khẩu tạm hiển thị 1 lần |

---

## 5. QUY ƯỚC CHIA NHÁNH GIT CHO THÀNH VIÊN TRONG NHÓM (5 NGƯỜI)

Leader đã chuẩn bị khung kiến trúc hoàn chỉnh. Các thành viên nhận nhiệm vụ sẽ tạo nhánh riêng từ `main`, triển khai backend cho phân hệ của mình theo quy ước sau:

### Phân công đề xuất:
- **Thành viên 1 (Leader):** Hoàn thiện Core, Auth, Users, Layout chung, Mock Frontend.
- **Thành viên 2:** Nhánh `feature/van-ban-den` (Backend + CSDL Văn bản đến).
- **Thành viên 3:** Nhánh `feature/van-ban-di` (Backend + CSDL Văn bản đi).
- **Thành viên 4:** Nhánh `feature/cong-viec` (Backend + CSDL Giao việc & Xử lý công việc).
- **Thành viên 5:** Nhánh `feature/ho-so-thong-ke` (Backend + CSDL Hồ sơ lưu trữ, Thông báo, Thống kê, Chatbot).

### Các bước thành viên làm việc trên nhánh:
1. **Lấy code mới nhất từ main:**
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Tạo nhánh chức năng riêng:**
   ```bash
   git checkout -b feature/van-ban-den
   ```
3. **Thêm bảng CSDL vào `database/schema.sql`:**
   Mỗi thành viên viết câu lệnh `CREATE TABLE ...` của chức năng mình vào cuối file `schema.sql` (tuân thủ khóa ngoại liên kết tới `nguoi_dung(nguoi_dung_id)`).
4. **Tạo Blueprint Backend trong thư mục `backend/<tên-module>/`:**
   Ví dụ `backend/van_ban_den/`:
   ```
   backend/van_ban_den/
   ├── __init__.py
   ├── routes.py
   └── services.py
   ```
5. **Đăng ký Blueprint trong `app.py`:**
   ```python
   from backend.van_ban_den.routes import van_ban_den_bp
   app.register_blueprint(van_ban_den_bp, url_prefix='/api/van-ban-den')
   ```
6. **Chuyển đổi Frontend từ Mock Data sang API thật:**
   Trong thư mục `frontend/js/mock/du-lieu-van-ban.js`:
   - Chỉ cần thay nội dung bên trong hàm (ví dụ `vanBanDenService.getList()`) từ việc trả về mảng mẫu thành gọi `api.get('/api/van-ban-den')`.
   - **Giao diện HTML/CSS không cần phải viết lại!**

---

## 6. KIỂM TRA CƠ SỞ DỮ LIỆU
1. Tải và cài đặt phần mềm miễn phí: [DB Browser for SQLite](https://sqlitebrowser.org/).
2. Mở file `database/qlvb.db` để trực tiếp xem và kiểm tra dữ liệu bảng `nguoi_dung`.
