/**
 * TOAST.JS - THÔNG BÁO NỔI TỰ ĐỘNG
 * Quản lý thông báo toast nhẹ nhàng, không cần thư viện ngoài.
 */

(function (window) {
  let toastContainer = null;

  function ensureContainer() {
    if (!toastContainer) {
      toastContainer = document.getElementById('toast-container');
      if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
      }
    }
    return toastContainer;
  }

  const Toast = {
    show: function (message, type = 'info', title = null, duration = 3500) {
      const container = ensureContainer();
      const toast = document.createElement('div');
      toast.className = `toast toast-${type}`;

      const iconMap = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
      };

      const titleMap = {
        success: title || 'Thành công',
        error: title || 'Lỗi xử lý',
        warning: title || 'Cảnh báo',
        info: title || 'Thông báo'
      };

      toast.innerHTML = `
        <div style="font-size: 16px; font-weight: bold;">${iconMap[type] || 'ℹ'}</div>
        <div class="toast-content">
          <div class="toast-title">${titleMap[type]}</div>
          <div>${message}</div>
        </div>
        <button class="toast-close" aria-label="Đóng">&times;</button>
      `;

      const closeBtn = toast.querySelector('.toast-close');
      const removeToast = () => {
        toast.style.animation = 'slideInRight 0.25s ease reverse forwards';
        setTimeout(() => {
          if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
          }
        }, 250);
      };

      closeBtn.addEventListener('click', removeToast);
      container.appendChild(toast);

      if (duration > 0) {
        setTimeout(removeToast, duration);
      }
    },

    success: function (message, title, duration) {
      this.show(message, 'success', title, duration);
    },

    error: function (message, title, duration) {
      this.show(message, 'error', title, duration);
    },

    warning: function (message, title, duration) {
      this.show(message, 'warning', title, duration);
    },

    info: function (message, title, duration) {
      this.show(message, 'info', title, duration);
    }
  };

  window.Toast = Toast;
})(window);
