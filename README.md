# Hệ thống Quản lý Văn bản và Điều hành — Sở GD&ĐT TP. Đà Nẵng

Dự án xây dựng bằng **Django** nhằm tin học hóa quy trình quản lý văn bản đi, văn bản đến, hồ sơ lưu trữ, giao việc điều hành, thông báo và trợ lý ảo tra cứu kho văn bản tại **Sở Giáo dục và Đào tạo Thành phố Đà Nẵng**.  
Hệ thống được nâng cấp từ giao diện frontend tĩnh sang kiến trúc **Django Backend + Template Rendering**, kết hợp API JSON nội bộ phục vụ thao tác dữ liệu theo thời gian thực.

## Mục tiêu dự án

- Quản lý tập trung văn bản đi và văn bản đến theo quy trình xử lý cơ quan nhà nước
- Quản lý hồ sơ lưu trữ điện tử, danh mục văn bản ban hành và thời hạn bảo quản
- Hỗ trợ giao việc, đính kèm văn bản căn cứ, phân công phòng ban/chuyên viên và theo dõi tiến độ xử lý
- Tăng khả năng tra cứu, tổng hợp số liệu điều hành, thống kê KPI và gửi thông báo nhắc việc
- Chuẩn hóa luồng xử lý, kiểm duyệt, ký số và hỗ trợ Trợ lý ảo AI tra cứu nhanh kho văn bản lưu trữ

## Module chính

### 1. Quản lý văn bản đi
- Thêm mới, soạn thảo và cập nhật dự thảo văn bản đi (hỗ trợ gắn từ công việc được giao)
- Kiểm tra thể thức bởi Văn thư, trình Lãnh đạo Sở ký số
- Xem danh sách, lọc tìm kiếm và xem chi tiết văn bản đi
- Duyệt ký, hoàn trả chỉnh sửa và ban hành văn bản chính thức
- Theo dõi lịch sử và trạng thái xử lý văn bản đi

### 2. Quản lý văn bản đến
- Tiếp nhận, đăng ký số đến và cập nhật thông tin văn bản đến
- Xem danh sách, lọc theo trạng thái/độ khẩn và xem chi tiết văn bản đến
- Chỉ đạo phân công phòng ban/chuyên viên chủ trì xử lý
- Theo dõi tiến độ và hạn xử lý văn bản đến

### 3. Hồ sơ lưu trữ
- Tạo lập và cập nhật hồ sơ lưu trữ theo đơn vị, năm tài liệu và thời hạn bảo quản
- Quản lý danh sách hồ sơ và xem chi tiết danh mục văn bản trong hồ sơ
- Liên kết bổ sung hoặc gỡ văn bản ban hành khỏi hồ sơ, nộp lưu trữ và đóng hồ sơ
- Xem trước văn bản trực tiếp (PDF gốc hoặc bản chuẩn A4 Nghị định 30/2020/NĐ-CP) và tải về (`.pdf` / `.doc`)

### 4. Quản lý công việc
- Giao nhiệm vụ mới kèm thông tin căn cứ pháp lý và **văn bản đính kèm** (tải tệp lên hoặc chọn nhanh từ kho văn bản hệ thống)
- Phân công chuyên viên, phòng ban phụ trách và điều chuyển công việc
- Chuyên viên xem/tải văn bản đính kèm, cập nhật tỷ lệ `%` tiến độ và nộp báo cáo kết quả
- Lãnh đạo / Văn thư nghiệm thu, phê duyệt đạt yêu cầu hoặc hoàn trả làm lại
- Theo dõi biểu đồ KPI, tình trạng quá hạn và quản lý tệp liên quan đến công việc

### 5. Xác thực & Phân quyền người dùng
- Đăng ký tài khoản Chuyên viên / Văn thư và quy trình Văn thư phê duyệt tài khoản
- Đăng nhập bảo mật phiên (session), giới hạn số lần đăng nhập sai
- Tạo tài khoản Lãnh đạo, đổi mật khẩu, đặt lại mật khẩu và khóa/mở khóa tài khoản
- Kiểm soát quyền truy cập đa tầng theo vai trò (`VAN_THU`, `LANH_DAO`, `CHUYEN_VIEN`)

### 6. Dashboard, Thông báo & Trợ lý ảo AI
- Dashboard tổng hợp số liệu văn bản, công việc, tỷ lệ hoàn thành đúng hạn và biểu đồ theo phòng ban
- Tạo và gửi thông báo toàn đơn vị, nhắc nhở hạn xử lý công việc/văn bản
- Trợ lý ảo AI tra cứu kho lưu trữ & kho mẫu văn bản: tìm theo từ khóa hoặc số ký hiệu, đề xuất danh sách tệp liên quan, xem trước trực tiếp (A4/PDF) và tải lên bổ sung văn bản vào kho dữ liệu

## Công nghệ sử dụng

- **Backend:** Python 3.10+, Django 6.1 (`Django>=5.0`), Pillow, pypdf, ReportLab, Mammoth
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+ Fetch API), Chart.js
- **Database:** SQLite (`db.sqlite3`)
- **Template Engine:** Django Templates (`templates/base.html`)
- **Quản lý file tĩnh:** Django Static Files (`static/`)
- **Quản lý media:** Django Media Files (`media/`)
- **Kiểm thử:** Django Test Framework (`tests/`)
- **Version Control:** Git, GitHub

## Cấu trúc dự án

```bash
education_management/
│
├── manage.py
├── requirements.txt
├── db.sqlite3
├── seed_django_data.py
├── seed_mau_van_ban.py
│
├── education_management/
│   ├── settings.py
│   ├── urls.py
│   ├── middleware.py
│   ├── asgi.py
│   └── wsgi.py
│
├── authentication/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── authentication/
│
├── van_ban/
│   ├── models.py
│   ├── services.py
│   ├── reports.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── van_ban/
│
├── ho_so/
│   ├── models.py
│   ├── services.py
│   ├── reports.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── ho_so/
│
├── cong_viec/
│   ├── models.py
│   ├── services.py
│   ├── reports.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── cong_viec/
│
├── dashboard/
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── dashboard/
│
├── thong_bao/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── thong_bao/
│
├── chatbot/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── chatbot/
│
├── common/
│   ├── audit.py
│   ├── constants.py
│   ├── excel_exporter.py
│   ├── pagination.py
│   ├── pdf_signer.py
│   ├── security.py
│   ├── serializers.py
│   └── validators.py
│
├── templates/
│   ├── base.html
│   └── index.html
│
├── static/
│   ├── css/
│   ├── js/
│   ├── libs/
│   └── assets/
│
├── media/
│   ├── cong_viec_dinh_kem/
│   └── van_ban_dieu_hanh/
│
└── tests/
```

## Hướng dẫn cài đặt & chạy dự án

1. **Tạo / kích hoạt môi trường ảo và cài đặt thư viện:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Khởi tạo cơ sở dữ liệu & dữ liệu mẫu (nếu chạy mới):**
   ```bash
   python manage.py migrate
   python seed_django_data.py
   python seed_mau_van_ban.py
   ```

3. **Chạy máy chủ phát triển Django:**
   ```bash
   python manage.py runserver 8000
   ```
   Truy cập ứng dụng tại: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

4. **Kiểm tra cấu hình và chạy bộ test:**
   ```bash
   python manage.py check
   python manage.py test tests
   ```

## Tài khoản mẫu

| Vai trò | Tên đăng nhập | Mật khẩu | Đơn vị |
| :--- | :--- | :--- | :--- |
| **Văn thư (Admin)** | `admin_vanthu` | `Admin@123` | Văn phòng Sở GD&ĐT |
| **Giám đốc Sở** | `giamdoc_so` | `GiamDoc@123` | Ban Giám đốc Sở |
| **Phó Giám đốc Sở** | `phogiamdoc_so` | `LanhDao@123` | Ban Giám đốc Sở |
| **Chuyên viên** | `minhcv` | `ChuyenVien@123` | Phòng Giáo dục Trung học |
