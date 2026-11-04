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
│                       CONTROLLER (Bộ điều khiển - controllers/)            │
│  - app.py: Dispatcher trung tâm điều hướng request                          │
│  - controllers/auth_controller.py: Quản lý phiên, đăng nhập, đổi mật khẩu   │
│  - controllers/users_controller.py: Quản trị tài khoản, duyệt chuyên viên    │
│  - controllers/documents_controller.py: Vòng đời văn bản đi 5 bước & ký số  │
│  - controllers/ho_so_controller.py: Quản lý hồ sơ lưu trữ & đồng bộ tài liệu│
│  - controllers/cong_viec_controller.py: Giao việc & nhật ký tiến độ         │
│  - controllers/thong_bao_controller.py: Thông báo & nhắc nhở real-time 2s   │
│  - controllers/kho_van_ban_controller.py: Cây niên đại & kho ban hành       │
│  - controllers/chatbot_controller.py: Trợ lý ảo AI & biểu mẫu hành chính    │
│  - backend/auth/decorators.py: Guards phân quyền (@login_required, @role)   │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
               Gọi nghiệp vụ & truy xuất dữ liệu
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MODEL (Dữ liệu & Nghiệp vụ - models/)              │
│  - models/base_model.py: BaseModel kết nối SQLite và tiện ích mapping       │
│  - models/user_model.py: Thực thể người dùng (UserModel)                    │
│  - models/document_model.py: Thực thể văn bản đi (DocumentModel)            │
│  - models/dossier_model.py: Thực thể hồ sơ lưu trữ (DossierModel)           │
│  - models/task_model.py: Thực thể công việc điều hành (TaskModel)           │
│  - models/notification_model.py: Thực thể thông báo & nhắc nhở              │
│  - models/repository_model.py: Thực thể kho lưu trữ số hóa                  │
│  - models/chatbot_model.py: Thực thể trợ lý ảo & mẫu văn bản                │
│  - database/schema.sql: 10 bảng CSDL SQLite quan hệ chặt chẽ               │
│  - database/db.py: Connection Pool (sqlite3.Row, PRAGMA foreign_keys = ON) │
│  - backend/documents/pdf_sign.py: Đóng dấu chữ ký số điện tử chuẩn NĐ 30   │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
                  Trả về dữ liệu JSON / File Stream
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VIEW (Giao diện hiển thị - views/ & frontend/)     │
│  - views/__init__.py: Module ánh xạ và phục vụ View Engine                  │
│  - frontend/pages/: Màn hình giao diện nghiệp vụ theo vai trò cán bộ:       │
│      + van-ban-di/: Soạn thảo, Ký số duyệt, Cấp số ban hành, Xem trước A4   │
│      + van-ban-den/: Tiếp nhận ngoài Sở, Phân công chỉ đạo, Xử lý           │
│      + cong-viec/: Giao nhiệm vụ, Báo cáo xử lý tiến độ, Đánh giá           │
│      + ho-so/: Danh mục hồ sơ, Chi tiết hồ sơ, Thêm/Gỡ văn bản              │
│      + thong-bao.html: Trung tâm thông báo điều hành & Lời nhắc real-time   │
│      + thong-ke.html: Báo cáo & Thống kê trực quan hóa (Chart.js)           │
│      + chatbot.html: Trợ lý ảo hỏi đáp và gợi ý mẫu công văn                │
│      + dashboard.html: Bảng điều khiển phân quyền đa tầng                   │
│  - frontend/css/: Hệ thống định dạng giao diện hành chính chuẩn mực         │
│  - frontend/js/core/: api.js, menu.js, auth-guard.js, notification-bell.js  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. CẤU TRÚC THƯ MỤC CHUẨN MVC

```
education_management/
├── controllers/                  # CONTROLLERS LAYER
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── chatbot_controller.py
│   ├── cong_viec_controller.py
│   ├── documents_controller.py
│   ├── ho_so_controller.py
│   ├── kho_van_ban_controller.py
│   ├── thong_bao_controller.py
│   └── users_controller.py
│
├── models/                       # MODELS LAYER
│   ├── __init__.py
│   ├── base_model.py
│   ├── chatbot_model.py
│   ├── document_model.py
│   ├── dossier_model.py
│   ├── notification_model.py
│   ├── repository_model.py
│   ├── task_model.py
│   └── user_model.py
│
├── views/                        # VIEWS LAYER WRAPPER
│   ├── __init__.py
│   └── README.md
│
├── frontend/                     # VIEWS IMPLEMENTATION
│   ├── assets/                   # Logo, icons, tài nguyên tĩnh
│   ├── css/                      # base.css, layout.css, components.css
│   ├── js/
│   │   ├── core/                 # api.js, auth-guard.js, menu.js, notification-bell.js, toast.js
│   │   └── mock/                 # du-lieu-ho-so.js, du-lieu-van-ban.js, du-lieu-thong-ke.js...
│   └── pages/                    # Toàn bộ view HTML nghiệp vụ
│
├── database/                     # DATABASE & PERSISTENCE
│   ├── schema.sql                # Cấu trúc CSDL SQLite quan hệ
│   ├── db.py                     # Quản lý kết nối SQLite
│   ├── init_db.py                # Khởi tạo CSDL & Seed tài khoản
│   └── qlvb.db                   # File CSDL SQLite thực tế
│
├── app.py                        # Central Application Dispatcher
├── config.py                     # Cấu hình hệ thống & biến môi trường
└── requirements.txt              # Thư viện phụ thuộc
```
