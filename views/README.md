# TẦNG VIEW (KIẾN TRÚC MVC)
Hệ thống Quản lý Văn bản và Điều hành Sở GD&ĐT Đà Nẵng

Tầng View chịu trách nhiệm hiển thị giao diện người dùng và tương tác trực quan với cán bộ:
- **`frontend/pages/`**: Các màn hình giao diện người dùng theo phân hệ (Văn bản đi, Văn bản đến, Hồ sơ lưu trữ, Công việc, Thống kê, Thông báo, Chatbot).
- **`frontend/css/`**: Hệ thống định dạng giao diện hành chính nhà nước chuẩn mực (`base.css`, `layout.css`, `components.css`).
- **`frontend/js/core/`**: Xử lý logic hiển thị, bảo vệ phân quyền trang (`auth-guard.js`), menu động (`menu.js`), chuông thông báo thời gian thực (`notification-bell.js`), thông báo nổi (`toast.js`).
