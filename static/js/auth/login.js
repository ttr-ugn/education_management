/**
 * LOGIN.JS - XỬ LÝ ĐĂNG NHẬP VÀ HIỂN THỊ TRẠNG THÁI TÀI KHOẢN
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  const alertBox = document.getElementById('loginAlert');
  const alertIcon = document.getElementById('alertIcon');
  const alertMsg = document.getElementById('alertMessage');
  const submitBtn = document.getElementById('submitBtn');
  const btnSpinner = document.getElementById('btnSpinner');
  const btnText = document.getElementById('btnText');
  const togglePasswordBtn = document.getElementById('togglePasswordBtn');
  const passwordInput = document.getElementById('mat_khau');
  const usernameInput = document.getElementById('ten_dang_nhap');

  // 1. Kiểm tra nếu đã có phiên làm việc thì tự động chuyển vào Dashboard
  (async function checkExistingSession() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('redirect')) {
      // Nếu có redirect từ trang khác tới, không tự chuyển hướng để tránh vòng lặp
      return;
    }
    try {
      const res = await window.api.get('/api/auth/toi');
      if (res && res.thanh_cong && res.du_lieu) {
        if (res.du_lieu.bat_buoc_doi_mat_khau) {
          window.location.replace('doi-mat-khau.html?required=1');
        } else {
          window.location.replace('dashboard.html');
        }
      }
    } catch (e) {
      // Chưa đăng nhập, tiếp tục ở lại trang
    }
  })();

  // 2. Ẩn/Hiện mật khẩu
  if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener('click', () => {
      const isPassword = passwordInput.getAttribute('type') === 'password';
      passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
      togglePasswordBtn.innerHTML = isPassword
        ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
            <line x1="1" y1="1" x2="23" y2="23"></line>
          </svg>`
        : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>`;
    });
  }

  // 3. Hàm hiển thị thông báo
  function showAlert(message, type = 'danger', icon = '⚠') {
    alertBox.className = `auth-alert auth-alert-${type} show`;
    alertIcon.textContent = icon;
    alertMsg.textContent = message;
  }

  function hideAlert() {
    alertBox.className = 'auth-alert';
    alertMsg.textContent = '';
  }

  // 4. Xử lý submit form
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert();

    const ten_dang_nhap = usernameInput.value.trim();
    const mat_khau = passwordInput.value;

    if (!ten_dang_nhap) {
      showAlert('Vui lòng nhập tên đăng nhập.', 'warning', '⚠');
      usernameInput.focus();
      return;
    }

    if (!mat_khau) {
      showAlert('Vui lòng nhập mật khẩu.', 'warning', '⚠');
      passwordInput.focus();
      return;
    }

    // Trạng thái đang gửi request
    submitBtn.disabled = true;
    btnSpinner.classList.remove('d-none');
    btnText.textContent = 'Đang xác thực...';

    try {
      const response = await window.api.post('/api/auth/dang-nhap', {
        ten_dang_nhap: ten_dang_nhap,
        mat_khau: mat_khau
      });

      window.Toast.success('Đăng nhập thành công! Đang chuyển hướng...', 'Chào mừng');

      const user = response.du_lieu;
      const urlParams = new URLSearchParams(window.location.search);
      const redirectUrl = urlParams.get('redirect');

      setTimeout(() => {
        if (user.bat_buoc_doi_mat_khau) {
          window.location.replace('doi-mat-khau.html?required=1');
        } else if (redirectUrl && !redirectUrl.includes('login.html')) {
          window.location.replace(redirectUrl);
        } else {
          window.location.replace('dashboard.html');
        }
      }, 600);

    } catch (err) {
      const errorMsg = err.message || 'Đăng nhập không thành công.';
      const status = err.status;

      // Xử lý thông báo theo từng trạng thái cụ thể
      if (status === 423) {
        showAlert(errorMsg, 'warning', '🔒');
      } else if (status === 403) {
        if (errorMsg.includes('chờ Văn thư')) {
          showAlert('Tài khoản của bạn đang ở trạng thái CHỜ DUYỆT. Vui lòng liên hệ Văn thư Sở để được phê duyệt trước khi đăng nhập.', 'info', '⏳');
        } else if (errorMsg.includes('từ chối')) {
          showAlert(errorMsg, 'danger', '🚫');
        } else if (errorMsg.includes('đã bị khóa')) {
          showAlert('Tài khoản của bạn đã bị KHÓA bởi Quản trị viên. Vui lòng liên hệ bộ phận Văn thư Sở để được hỗ trợ mở khóa.', 'danger', '⛔');
        } else {
          showAlert(errorMsg, 'danger', '⚠');
        }
      } else if (errorMsg.includes('Failed to fetch') || err.name === 'TypeError') {
        showAlert('Không thể kết nối đến máy chủ Django backend. Hãy truy cập đúng http://127.0.0.1:8000 và bấm Ctrl + F5 để làm mới bộ nhớ đệm.', 'danger', '⚠');
      } else {
        showAlert(errorMsg, 'danger', '⚠');
      }
    } finally {
      submitBtn.disabled = false;
      btnSpinner.classList.add('d-none');
      btnText.textContent = 'Đăng nhập';
    }
  });
});
