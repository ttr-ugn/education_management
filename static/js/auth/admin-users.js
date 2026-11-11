/**
 * ADMIN-USERS.JS - CÁC HÀM XỬ LÝ QUẢN TRỊ TÀI KHOẢN (VĂN THƯ)
 * Kết nối API Backend thật: Duyệt, Từ chối, Tạo lãnh đạo, Khóa, Mở khóa, Đặt lại MK.
 */

window.AdminUserModule = (function () {
  const ROLE_BADGES = {
    'VAN_THU': '<span class="badge" style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">⚡ Văn thư (Admin)</span>',
    'LANH_DAO': '<span class="badge" style="background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">🏛️ Lãnh đạo</span>',
    'CHUYEN_VIEN': '<span class="badge" style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">💼 Chuyên viên</span>'
  };

  const STATUS_BADGES = {
    'CHO_DUYET': '<span class="badge" style="background: #fef3c7; color: #b45309; border: 1px solid #fde68a; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">⏳ Chờ duyệt</span>',
    'HOAT_DONG': '<span class="badge" style="background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">● Hoạt động</span>',
    'TU_CHOI': '<span class="badge" style="background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">❌ Bị từ chối</span>',
    'BI_KHOA': '<span class="badge" style="background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">🔒 Bị khóa</span>'
  };

  /**
   * Lấy danh sách người dùng từ API
   */
  async function loadUsers(filters = {}) {
    try {
      const res = await window.api.get('/api/users', filters);
      return res.du_lieu || [];
    } catch (err) {
      window.Toast.error(err.message || 'Không thể tải danh sách người dùng.');
      return [];
    }
  }

  /**
   * Duyệt tài khoản
   */
  async function approve(userId, userName, onDone) {
    if (!confirm(`Đồng chí có chắc chắn muốn phê duyệt tài khoản cho cán bộ: "${userName}"?`)) {
      return;
    }
    try {
      const res = await window.api.post(`/api/users/${userId}/duyet`);
      window.Toast.success(res.thong_bao || 'Đã duyệt tài khoản thành công.');
      if (typeof onDone === 'function') onDone();
    } catch (err) {
      window.Toast.error(err.message || 'Không thể phê duyệt tài khoản.');
    }
  }

  /**
   * Mở modal từ chối tài khoản với lý do
   */
  function promptReject(userId, userName, onDone) {
    const modalId = 'rejectReasonModal';
    let modal = document.getElementById(modalId);
    if (!modal) {
      modal = document.createElement('div');
      modal.id = modalId;
      modal.className = 'modal-backdrop';
      modal.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-header">
            <h3 class="modal-title" style="color: var(--danger-color);">Từ chối phê duyệt tài khoản</h3>
            <button class="modal-close-btn" id="rejectCloseBtn">&times;</button>
          </div>
          <div class="modal-body">
            <p style="margin-bottom: 12px; font-size: 13.5px;">
              Đang từ chối tài khoản của cán bộ: <b id="rejectTargetName"></b>.<br>
              Vui lòng nhập lý do từ chối (lý do này sẽ hiển thị khi cán bộ thử đăng nhập):
            </p>
            <div class="form-group">
              <label class="form-label required">Lý do từ chối</label>
              <textarea id="rejectReasonInput" class="form-control" rows="3" placeholder="Ví dụ: Thông tin phòng ban không chính xác, vui lòng đăng ký lại..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" id="rejectCancelBtn">Hủy bỏ</button>
            <button class="btn btn-danger" id="rejectConfirmBtn">Xác nhận từ chối</button>
          </div>
        </div>
      `;
      document.body.appendChild(modal);
    }

    const targetNameEl = modal.querySelector('#rejectTargetName');
    const reasonInput = modal.querySelector('#rejectReasonInput');
    const closeBtn = modal.querySelector('#rejectCloseBtn');
    const cancelBtn = modal.querySelector('#rejectCancelBtn');
    const confirmBtn = modal.querySelector('#rejectConfirmBtn');

    targetNameEl.textContent = userName;
    reasonInput.value = '';
    modal.classList.remove('d-none');
    reasonInput.focus();

    const closeModal = () => {
      modal.classList.add('d-none');
    };

    closeBtn.onclick = closeModal;
    cancelBtn.onclick = closeModal;

    confirmBtn.onclick = async () => {
      const reason = reasonInput.value.trim();
      if (!reason) {
        alert('Vui lòng nhập lý do từ chối tài khoản.');
        reasonInput.focus();
        return;
      }

      confirmBtn.disabled = true;
      confirmBtn.textContent = 'Đang xử lý...';

      try {
        const res = await window.api.post(`/api/users/${userId}/tu-choi`, { ly_do: reason });
        window.Toast.success(res.thong_bao || 'Đã từ chối tài khoản thành công.');
        closeModal();
        if (typeof onDone === 'function') onDone();
      } catch (err) {
        window.Toast.error(err.message || 'Lỗi khi từ chối tài khoản.');
      } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Xác nhận từ chối';
      }
    };
  }

  /**
   * Khóa tài khoản
   */
  async function lock(userId, userName, onDone) {
    if (!confirm(`Đồng chí có chắc chắn muốn KHÓA tài khoản của cán bộ: "${userName}"? Cán bộ này sẽ không thể đăng nhập vào hệ thống.`)) {
      return;
    }
    try {
      const res = await window.api.post(`/api/users/${userId}/khoa`);
      window.Toast.success(res.thong_bao || 'Đã khóa tài khoản thành công.');
      if (typeof onDone === 'function') onDone();
    } catch (err) {
      window.Toast.error(err.message || 'Không thể khóa tài khoản.');
    }
  }

  /**
   * Mở khóa tài khoản
   */
  async function unlock(userId, userName, onDone) {
    if (!confirm(`Đồng chí có chắc chắn muốn MỞ KHÓA tài khoản của cán bộ: "${userName}"?`)) {
      return;
    }
    try {
      const res = await window.api.post(`/api/users/${userId}/mo-khoa`);
      window.Toast.success(res.thong_bao || 'Đã mở khóa tài khoản thành công.');
      if (typeof onDone === 'function') onDone();
    } catch (err) {
      window.Toast.error(err.message || 'Không thể mở khóa tài khoản.');
    }
  }

  /**
   * Đặt lại mật khẩu
   */
  async function resetPassword(userId, userName, onDone) {
    if (!confirm(`Đồng chí có chắc chắn muốn ĐẶT LẠI MẬT KHẨU cho cán bộ: "${userName}"? Hệ thống sẽ sinh mật khẩu ngẫu nhiên mới và yêu cầu cán bộ đổi mật khẩu ở lần đăng nhập tiếp theo.`)) {
      return;
    }
    try {
      const res = await window.api.post(`/api/users/${userId}/dat-lai-mat-khau`);
      const newPassword = res.mat_khau_moi;
      showPasswordModal('MẬT KHẨU MỚI ĐÃ THIẾT LẬP', `Đã đặt lại mật khẩu thành công cho cán bộ <b>${userName}</b>. Vui lòng gửi mật khẩu mới này cho cán bộ:`, newPassword);
      if (typeof onDone === 'function') onDone();
    } catch (err) {
      window.Toast.error(err.message || 'Không thể đặt lại mật khẩu.');
    }
  }

  /**
   * Modal hiển thị mật khẩu tạm thời kèm nút Copy
   */
  function showPasswordModal(title, messageHtml, password) {
    let modal = document.getElementById('tempPasswordModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'tempPasswordModal';
      modal.className = 'modal-backdrop';
      modal.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-header" style="background-color: var(--primary-subtle);">
            <h3 class="modal-title" id="pwdModalTitle" style="color: var(--primary-dark);">MẬT KHẨU TẠM THỜI</h3>
            <button class="modal-close-btn" id="pwdModalClose">&times;</button>
          </div>
          <div class="modal-body">
            <div id="pwdModalMsg" style="font-size: 13.5px; margin-bottom: 16px;"></div>
            <div style="background-color: #f8fafc; border: 2px dashed #004b91; padding: 16px; border-radius: 8px; text-align: center; margin-bottom: 16px;">
              <span style="font-size: 12px; color: #64748b; display: block; margin-bottom: 4px;">MẬT KHẨU TẠM:</span>
              <span id="tempPasswordDisplay" style="font-size: 22px; font-weight: bold; font-family: monospace; letter-spacing: 2px; color: #b91c1c;"></span>
            </div>
            <div style="display: flex; gap: 10px;">
              <button class="btn btn-outline-primary w-100" id="copyPasswordBtn">
                📋 Sao chép mật khẩu
              </button>
            </div>
            <p style="font-size: 12px; color: #b45309; margin-top: 14px; background-color: #fffbeb; padding: 8px 12px; border-radius: 4px;">
              ⚠ <b>Lưu ý:</b> Mật khẩu tạm này chỉ hiển thị duy nhất một lần. Hệ thống đã đặt cờ bắt buộc đổi mật khẩu ở lần đăng nhập đầu tiên.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-primary" id="pwdModalDone">Đã hoàn tất lưu trữ</button>
          </div>
        </div>
      `;
      document.body.appendChild(modal);
    }

    const titleEl = modal.querySelector('#pwdModalTitle');
    const msgEl = modal.querySelector('#pwdModalMsg');
    const pwdEl = modal.querySelector('#tempPasswordDisplay');
    const copyBtn = modal.querySelector('#copyPasswordBtn');
    const closeBtn = modal.querySelector('#pwdModalClose');
    const doneBtn = modal.querySelector('#pwdModalDone');

    titleEl.textContent = title;
    msgEl.innerHTML = messageHtml;
    pwdEl.textContent = password;
    modal.classList.remove('d-none');

    const closeModal = () => modal.classList.add('d-none');
    closeBtn.onclick = closeModal;
    doneBtn.onclick = closeModal;

    copyBtn.onclick = () => {
      navigator.clipboard.writeText(password).then(() => {
        window.Toast.success('Đã sao chép mật khẩu vào bộ nhớ tạm (Clipboard)!');
        copyBtn.textContent = '✓ Đã sao chép thành công';
        setTimeout(() => { copyBtn.textContent = '📋 Sao chép mật khẩu'; }, 2000);
      }).catch(() => {
        window.Toast.info('Không thể tự động sao chép. Vui lòng bôi đen và nhấn Ctrl+C.');
      });
    };
  }

  return {
    ROLE_BADGES,
    STATUS_BADGES,
    loadUsers,
    approve,
    promptReject,
    lock,
    unlock,
    resetPassword,
    showPasswordModal
  };
})();
