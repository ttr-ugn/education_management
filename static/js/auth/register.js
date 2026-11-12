/**
 * REGISTER.JS - XỬ LÝ ĐĂNG KÝ TÀI KHOẢN VĂN THƯ / CHUYÊN VIÊN
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registerForm');
  const alertBox = document.getElementById('registerAlert');
  const alertIcon = document.getElementById('alertIcon');
  const alertMsg = document.getElementById('alertMessage');
  const submitBtn = document.getElementById('submitBtn');
  const btnSpinner = document.getElementById('btnSpinner');
  const btnText = document.getElementById('btnText');
  const vaiTroInput = document.getElementById('vai_tro');

  const tabChuyenVien = document.getElementById('tabChuyenVien');
  const tabVanThu = document.getElementById('tabVanThu');
  const maNoiBoGroup = document.getElementById('maNoiBoGroup');
  const maNoiBoInput = document.getElementById('ma_noi_bo');
  const chucVuInput = document.getElementById('chuc_vu');
  const phongBanSelect = document.getElementById('phong_ban');

  const pendingModal = document.getElementById('pendingSuccessModal');
  const successUserName = document.getElementById('successUserName');

  // 1. Chuyển đổi qua lại giữa 2 vai trò
  tabChuyenVien.addEventListener('click', () => {
    tabChuyenVien.classList.add('active');
    tabVanThu.classList.remove('active');
    vaiTroInput.value = 'CHUYEN_VIEN';
    maNoiBoGroup.classList.add('d-none');
    maNoiBoInput.removeAttribute('required');
    chucVuInput.value = 'Chuyên viên';
    hideAlert();
  });

  tabVanThu.addEventListener('click', () => {
    tabVanThu.classList.add('active');
    tabChuyenVien.classList.remove('active');
    vaiTroInput.value = 'VAN_THU';
    maNoiBoGroup.classList.remove('d-none');
    maNoiBoInput.setAttribute('required', 'required');
    chucVuInput.value = 'Văn thư cơ quan';
    phongBanSelect.value = 'Văn phòng Sở';
    hideAlert();
  });

  function showAlert(message, type = 'danger', icon = '') {
    alertBox.className = `auth-alert auth-alert-${type} show`;
    alertIcon.textContent = '';
    alertMsg.textContent = message;
    alertBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function hideAlert() {
    alertBox.className = 'auth-alert';
    alertMsg.textContent = '';
  }

  // 2. Validate FE
  function validateForm() {
    const ho_va_ten = document.getElementById('ho_va_ten').value.trim();
    const email = document.getElementById('email').value.trim();
    const ten_dang_nhap = document.getElementById('ten_dang_nhap').value.trim();
    const mat_khau = document.getElementById('mat_khau').value;
    const xac_nhan = document.getElementById('xac_nhan_mat_khau').value;
    const phong_ban = phongBanSelect.value;
    const vai_tro = vaiTroInput.value;
    const ma_noi_bo = maNoiBoInput.value.trim();

    if (!ho_va_ten) {
      showAlert('Vui lòng nhập họ và tên cán bộ.');
      return false;
    }

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showAlert('Vui lòng nhập email hợp lệ (ví dụ: canbo@danang.edu.vn).');
      return false;
    }

    if (!phong_ban) {
      showAlert('Vui lòng chọn Phòng ban / Đơn vị công tác.');
      return false;
    }

    if (!ten_dang_nhap || !/^[a-zA-Z0-9._]{4,30}$/.test(ten_dang_nhap)) {
      showAlert('Tên đăng nhập phải từ 4-30 ký tự, chỉ gồm chữ cái, chữ số, dấu chấm (.) và gạch dưới (_).');
      return false;
    }

    if (!mat_khau || mat_khau.length < 8) {
      showAlert('Mật khẩu phải có độ dài tối thiểu 8 ký tự.');
      return false;
    }

    const hasLetter = /[a-zA-Z]/.test(mat_khau);
    const hasDigit = /[0-9]/.test(mat_khau);
    if (!hasLetter || !hasDigit) {
      showAlert('Mật khẩu phải chứa ít nhất một chữ cái và một chữ số.');
      return false;
    }

    if (mat_khau !== xac_nhan) {
      showAlert('Mật khẩu xác nhận không trùng khớp.');
      return false;
    }

    if (vai_tro === 'VAN_THU' && !ma_noi_bo) {
      showAlert('Vui lòng nhập Mã xác nhận nội bộ của Sở GD&ĐT để đăng ký vai trò Văn thư.');
      return false;
    }

    return true;
  }

  // 3. Submit form
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert();

    if (!validateForm()) return;

    submitBtn.disabled = true;
    btnSpinner.classList.remove('d-none');
    btnText.textContent = 'Đang xử lý đăng ký...';

    const payload = {
      ho_va_ten: document.getElementById('ho_va_ten').value.trim(),
      email: document.getElementById('email').value.trim(),
      sdt: document.getElementById('sdt').value.trim(),
      phong_ban: phongBanSelect.value,
      chuc_vu: chucVuInput.value.trim(),
      ten_dang_nhap: document.getElementById('ten_dang_nhap').value.trim(),
      mat_khau: document.getElementById('mat_khau').value,
      vai_tro: vaiTroInput.value,
      ma_noi_bo: maNoiBoInput.value.trim()
    };

    try {
      const response = await window.api.post('/api/auth/dang-ky', payload);

      if (payload.vai_tro === 'CHUYEN_VIEN') {
        // Hiển thị modal chờ duyệt
        successUserName.textContent = payload.ho_va_ten;
        pendingModal.classList.remove('d-none');
      } else {
        // Văn thư đăng ký thành công -> chuyển về login
        window.Toast.success('Đăng ký tài khoản Văn thư thành công! Đang chuyển đến trang đăng nhập...', 'Thành công');
        setTimeout(() => {
          window.location.replace('login.html');
        }, 1500);
      }

    } catch (err) {
      showAlert(err.message || 'Đăng ký không thành công. Vui lòng kiểm tra lại thông tin.', 'danger', '');
    } finally {
      submitBtn.disabled = false;
      btnSpinner.classList.add('d-none');
      btnText.textContent = 'Đăng ký tài khoản';
    }
  });
});
