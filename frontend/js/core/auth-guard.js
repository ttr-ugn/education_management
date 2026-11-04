/**
 * AUTH-GUARD.JS - BẢO VỆ ĐỊNH TUYẾN & PHÂN QUYỀN TRANG PHÍA FRONTEND
 * Kiểm tra session qua API /api/auth/toi, chặn truy cập trái phép và điều hướng.
 */

(function (window) {
  let currentUser = null;

  const ROLE_NAMES = {
    'VAN_THU': 'Văn thư (Admin)',
    'LANH_DAO': 'Lãnh đạo Sở',
    'CHUYEN_VIEN': 'Chuyên viên'
  };

  /**
   * Tính toán đường dẫn gốc tới thư mục frontend từ trang hiện tại.
   */
  function getRootPath() {
    const path = window.location.pathname;
    if (path.includes('/pages/admin/') ||
        path.includes('/pages/van-ban-den/') ||
        path.includes('/pages/van-ban-di/') ||
        path.includes('/pages/ho-so/') ||
        path.includes('/pages/cong-viec/')) {
      return '../../';
    }
    if (path.includes('/pages/')) {
      return '../';
    }
    return './';
  }

  /**
   * Kiểm tra quyền truy cập của trang hiện tại.
   * @param {Object} options { requiredRoles: ['VAN_THU'], allowGuest: false }
   */
  async function checkAuth(options = {}) {
    const currentPath = window.location.pathname;
    const isAuthPage = currentPath.endsWith('login.html') ||
                       currentPath.endsWith('register.html') ||
                       currentPath.endsWith('index.html') ||
                       currentPath === '/' ||
                       currentPath === '';

    try {
      const response = await window.api.get('/api/auth/toi');
      currentUser = response.du_lieu;

      // 1. Nếu đang ở trang đăng nhập / đăng ký mà đã có phiên -> chuyển về Dashboard
      if (currentPath.endsWith('login.html') || currentPath.endsWith('register.html')) {
        window.location.replace(`${getRootPath()}pages/dashboard.html`);
        return currentUser;
      }

      // 2. Kiểm tra cờ bắt buộc đổi mật khẩu
      if (currentUser.bat_buoc_doi_mat_khau) {
        if (!currentPath.endsWith('doi-mat-khau.html')) {
          window.location.replace(`${getRootPath()}pages/doi-mat-khau.html?required=1`);
          return currentUser;
        }
      }

      // 3. Kiểm tra vai trò nếu trang yêu cầu vai trò cụ thể (VD: trang /pages/admin/...)
      if (options.requiredRoles && Array.isArray(options.requiredRoles)) {
        if (!options.requiredRoles.includes(currentUser.vai_tro)) {
          showForbiddenPage(options.requiredRoles);
          return null;
        }
      }

      // Tự động bảo vệ tất cả trang trong thư mục /pages/admin/ chỉ cho VAN_THU
      if (currentPath.includes('/pages/admin/') && currentUser.vai_tro !== 'VAN_THU') {
        showForbiddenPage(['VAN_THU']);
        return null;
      }

      // Cập nhật thông tin người dùng lên thanh topbar
      renderUserProfile(currentUser);

      // Dựng menu theo vai trò nếu có hàm renderMenu
      if (window.MenuBuilder && typeof window.MenuBuilder.render === 'function') {
        window.MenuBuilder.render(currentUser.vai_tro);
      }

      return currentUser;

    } catch (err) {
      currentUser = null;

      // Nếu chưa đăng nhập mà đang ở trang cần bảo vệ -> chuyển về login
      if (!isAuthPage) {
        window.location.replace(`${getRootPath()}pages/login.html?redirect=${encodeURIComponent(window.location.href)}`);
      }
      return null;
    }
  }

  /**
   * Cập nhật thông tin người dùng lên widget trên Topbar.
   */
  function renderUserProfile(user) {
    if (!user) return;

    // Họ tên
    const nameEls = document.querySelectorAll('.user-name, #currentUserName');
    nameEls.forEach(el => { el.textContent = user.ho_va_ten; });

    // Vai trò
    const roleEls = document.querySelectorAll('.user-role-badge, #currentUserRole');
    roleEls.forEach(el => { el.textContent = ROLE_NAMES[user.vai_tro] || user.vai_tro; });

    // Avatar chữ cái đầu
    const avatarEls = document.querySelectorAll('.user-avatar, #currentUserAvatar');
    if (user.ho_va_ten) {
      const parts = user.ho_va_ten.trim().split(' ');
      const initials = parts.length > 1
        ? (parts[parts.length - 2][0] + parts[parts.length - 1][0]).toUpperCase()
        : user.ho_va_ten.substring(0, 2).toUpperCase();
      avatarEls.forEach(el => { el.textContent = initials; });
    }

    // Đăng ký sự kiện nút Đăng xuất
    const logoutBtns = document.querySelectorAll('#logoutBtn, .btn-logout');
    logoutBtns.forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        if (confirm('Đồng chí có chắc chắn muốn đăng xuất khỏi hệ thống?')) {
          try {
            await window.api.post('/api/auth/dang-xuat');
          } catch (e) {
            // bỏ qua
          }
          window.location.replace(`${getRootPath()}pages/login.html`);
        }
      });
    });
  }

  /**
   * Hiển thị giao diện 403 Forbidden nếu không đủ quyền.
   */
  function showForbiddenPage(requiredRoles) {
    const content = document.querySelector('.content-wrapper') || document.body;
    content.innerHTML = `
      <div style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 64px; color: #ef4444; font-weight: bold;">403</div>
        <h2 style="font-size: 22px; color: #003366; margin: 12px 0;">TRUY CẬP BỊ TỪ CHỐI (FORBIDDEN)</h2>
        <p style="color: #64748b; max-width: 500px; margin: 0 auto 24px;">
          Tài khoản của bạn (${ROLE_NAMES[currentUser?.vai_tro] || 'Không xác định'}) không có quyền truy cập trang quản trị này.
          Chức năng này chỉ dành riêng cho: <b>${requiredRoles.map(r => ROLE_NAMES[r] || r).join(', ')}</b>.
        </p>
        <a href="${getRootPath()}pages/dashboard.html" class="btn btn-primary">
          Quay lại Bảng điều khiển
        </a>
      </div>
    `;
  }

  window.AuthGuard = {
    check: checkAuth,
    getUser: () => currentUser,
    getRootPath: getRootPath
  };
})(window);
