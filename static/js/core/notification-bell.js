/**
 * NOTIFICATION-BELL.JS - QUẢN LÝ CHUÔNG THÔNG BÁO & TỰ ĐỘNG NHẮC NHỞ ĐẾN HẠN
 * Nhánh: notifications-reminders
 * 
 * Tính năng:
 * 1. Tự động gắn dropdown menu nhanh vào icon chuông ở topbar (cạnh avatar profile).
 * 2. Hiển thị badge số lượng thông báo chưa đọc & nhắc nhở đến hạn.
 * 3. Hiệu ứng chuông lắc (bell-ringing) khi có nhắc nhở đến hạn.
 * 4. Tự động kiểm tra định kỳ (Auto polling mỗi 30s) và bắn Toast cảnh báo khi đến giờ hẹn.
 * 5. Phát âm thanh bíp nhẹ (Web Audio API) khi có nhắc nhở đến hạn.
 */

(function (window) {
  // Bộ nhớ đệm các nhắc nhở đã cảnh báo âm thanh/toast trong phiên
  const alertedIds = new Set();

  function playAlertBeep() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc.frequency.setValueAtTime(880, ctx.currentTime + 0.15); // A5
      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.4);
    } catch (e) {
      // Bỏ qua nếu trình duyệt chặn autoplay audio
    }
  }

  function getRootPath() {
    if (window.AuthGuard && typeof window.AuthGuard.getRootPath === 'function') {
      return window.AuthGuard.getRootPath();
    }
    return window.location.pathname.includes('/pages/') ? '' : 'pages/';
  }

  async function initNotificationBell() {
    // Tìm nút chuông trên topbar
    const bellBtn = document.querySelector('.topbar-icon-btn[title*="Thông báo"]') || document.querySelector('.topbar-right .topbar-icon-btn');
    if (!bellBtn) return;

    // Ngăn chặn tạo lại nếu đã khởi tạo
    if (bellBtn.dataset.bellInitialized === 'true') return;
    bellBtn.dataset.bellInitialized = 'true';

    // Bọc trong topbar-bell-wrapper
    let wrapper = bellBtn.parentElement;
    if (!wrapper.classList.contains('topbar-bell-wrapper')) {
      wrapper = document.createElement('div');
      wrapper.className = 'topbar-bell-wrapper';
      bellBtn.parentNode.insertBefore(wrapper, bellBtn);
      wrapper.appendChild(bellBtn);
    }

    // Biến thẻ <a> thành nút mở dropdown (ngăn chặn chuyển trang ngay lập tức khi click)
    bellBtn.setAttribute('href', 'javascript:void(0)');

    // Đảm bảo có thẻ badge
    let badge = bellBtn.querySelector('.topbar-icon-badge');
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'topbar-icon-badge';
      badge.style.display = 'none';
      bellBtn.appendChild(badge);
    }

    // Tạo HTML cho Dropdown
    const rootPath = getRootPath();
    const thongBaoUrl = rootPath ? `${rootPath}thong-bao.html` : 'thong-bao.html';

    const dropdown = document.createElement('div');
    dropdown.className = 'notif-dropdown';
    dropdown.id = 'topbarNotifDropdown';
    dropdown.innerHTML = `
      <div class="notif-dropdown-header">
        <div class="notif-dropdown-title">
          <span>🔔</span>
          <span>Thông báo & Lời nhắc</span>
        </div>
        <button type="button" class="btn btn-outline-secondary btn-sm" id="btnQuickMarkAll" style="font-size: 11px; padding: 2px 8px;">
          ✓ Đọc tất cả
        </button>
      </div>
      <div class="notif-dropdown-tabs">
        <button class="notif-tab-btn active" data-tab="all">Tất cả</button>
        <button class="notif-tab-btn" data-tab="due">⏰ Đến hạn (<span id="notifDueCount">0</span>)</button>
      </div>
      <div class="notif-dropdown-list" id="notifDropdownList">
        <div class="text-center text-muted" style="padding: 24px; font-size: 13px;">
          Đang nạp thông báo...
        </div>
      </div>
      <div class="notif-dropdown-footer">
        <a href="${thongBaoUrl}">Xem tất cả & Quản lý thông báo điều hành &rarr;</a>
      </div>
    `;
    wrapper.appendChild(dropdown);

    let activeTab = 'all';
    let cachedList = [];

    // Toggle Dropdown khi bấm vào chuông
    bellBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isShowing = dropdown.classList.contains('show');
      if (isShowing) {
        dropdown.classList.remove('show');
      } else {
        dropdown.classList.add('show');
        loadDropdownData();
      }
    });

    // Đóng dropdown khi click ra ngoài
    document.addEventListener('click', (e) => {
      if (!wrapper.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });

    // Xử lý chuyển tab trong dropdown
    dropdown.querySelectorAll('.notif-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.querySelectorAll('.notif-tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeTab = btn.dataset.tab;
        renderDropdownItems();
      });
    });

    // Nút đọc tất cả
    const btnQuickMarkAll = dropdown.querySelector('#btnQuickMarkAll');
    if (btnQuickMarkAll) {
      btnQuickMarkAll.addEventListener('click', async (e) => {
        e.stopPropagation();
        if (window.thongBaoService) {
          await window.thongBaoService.markAllAsRead();
          if (window.Toast) window.Toast.success('Đã đánh dấu tất cả thông báo là đã đọc.');
          await updateBellStats();
          loadDropdownData();
        }
      });
    }

    async function loadDropdownData() {
      const listEl = dropdown.querySelector('#notifDropdownList');
      try {
        if (window.thongBaoService && typeof window.thongBaoService.getAll === 'function') {
          cachedList = await window.thongBaoService.getAll();
        } else if (window.api && typeof window.api.get === 'function') {
          const res = await window.api.get('/api/thong-bao');
          cachedList = (res && res.thanh_cong) ? (res.du_lieu || []) : [];
        } else {
          const resp = await fetch('/api/thong-bao');
          const json = await resp.json();
          cachedList = (json && json.thanh_cong) ? (json.du_lieu || []) : [];
        }
        renderDropdownItems();
      } catch (err) {
        listEl.innerHTML = `
          <div class="text-center text-muted" style="padding: 24px; font-size: 13px;">
            <div style="font-size: 24px; margin-bottom: 4px;">📭</div>
            Không có thông báo mới nào.
          </div>
        `;
      }
    }

    function renderDropdownItems() {
      const listEl = dropdown.querySelector('#notifDropdownList');
      let displayItems = [...cachedList];

      if (activeTab === 'due') {
        displayItems = displayItems.filter(item => item.da_den_han || (item.loai === 'Nhắc nhở' && item.ngay_hen_gio));
      }

      if (displayItems.length === 0) {
        listEl.innerHTML = `
          <div class="text-center text-muted" style="padding: 30px 16px; font-size: 13px;">
            <div style="font-size: 24px; margin-bottom: 4px;">📭</div>
            Không có ${activeTab === 'due' ? 'nhắc nhở nào đến hạn' : 'thông báo nào'}.
          </div>
        `;
        return;
      }

      listEl.innerHTML = displayItems.slice(0, 8).map(item => {
        let badgeHtml = '';
        if (item.da_den_han) {
          badgeHtml = '<span class="badge badge-danger">⏰ ĐẾN HẠN</span>';
        } else if (item.muc_do === 'Khẩn cấp') {
          badgeHtml = '<span class="badge badge-danger">Hỏa tốc</span>';
        } else if (item.muc_do === 'Quan trọng') {
          badgeHtml = '<span class="badge badge-warning">Quan trọng</span>';
        } else {
          badgeHtml = `<span class="badge badge-secondary">${item.loai}</span>`;
        }

        const isUnread = !item.da_doc;
        const itemClass = `notif-dropdown-item ${isUnread ? 'unread' : ''} ${item.da_den_han ? 'is-due' : ''}`;

        return `
          <div class="${itemClass}" data-id="${item.id}">
            <div class="notif-item-top">
              <div>
                ${badgeHtml}
                ${isUnread ? '<span class="badge badge-info ml-1" style="font-size: 10px;">Mới</span>' : ''}
              </div>
              <span class="text-muted" style="font-size: 11px;">${item.thoi_gian ? item.thoi_gian.substring(5, 16) : ''}</span>
            </div>
            <div class="notif-item-title">${item.tieu_de}</div>
            <div class="notif-item-desc">${item.noi_dung}</div>
            ${item.ngay_hen_gio ? `
              <div style="font-size: 11px; color: #dc2626; font-weight: 600; margin-top: 2px;">
                ⏰ Hạn xử lý: ${item.ngay_hen_gio}
              </div>
            ` : ''}
          </div>
        `;
      }).join('');

      // Gán sự kiện click vào item
      listEl.querySelectorAll('.notif-dropdown-item').forEach(el => {
        el.addEventListener('click', async (e) => {
          e.stopPropagation();
          const id = el.dataset.id;
          if (window.thongBaoService) {
            await window.thongBaoService.markAsRead(id);
            await updateBellStats();
            // Nếu đang ở trang thong-bao.html thì reload trang, nếu không thì chuyển hướng
            if (window.location.pathname.includes('thong-bao.html')) {
              if (typeof window.loadNotificationsData === 'function') {
                window.loadNotificationsData();
              }
            } else {
              window.location.href = thongBaoUrl;
            }
          }
        });
      });
    }

    async function updateBellStats() {
      try {
        let stats = { chua_doc: 0, den_han: 0 };
        if (window.thongBaoService && typeof window.thongBaoService.getStats === 'function') {
          stats = await window.thongBaoService.getStats();
        } else if (window.api && typeof window.api.get === 'function') {
          const res = await window.api.get('/api/thong-bao/dem-chua-doc');
          if (res && res.thanh_cong) {
            stats = { chua_doc: res.chua_doc || 0, den_han: res.den_han || 0 };
          }
        } else {
          const resp = await fetch('/api/thong-bao/dem-chua-doc');
          const res = await resp.json();
          if (res && res.thanh_cong) {
            stats = { chua_doc: res.chua_doc || 0, den_han: res.den_han || 0 };
          }
        }

        const dueEl = dropdown.querySelector('#notifDueCount');
        if (dueEl) dueEl.textContent = stats.den_han || 0;

        const totalBadgeCount = stats.chua_doc;

        if (totalBadgeCount > 0) {
          badge.style.display = 'flex';
          badge.textContent = totalBadgeCount > 99 ? '99+' : totalBadgeCount;
          badge.style.backgroundColor = '#ef4444';
          badge.style.color = '#ffffff';
          badge.style.minWidth = '18px';
          badge.style.height = '18px';
          badge.style.fontSize = '10.5px';
          badge.style.fontWeight = '700';
          badge.style.borderRadius = '9px';
          badge.style.border = '2px solid #ffffff';
        } else {
          badge.style.display = 'none';
          badge.textContent = '0';
        }

        // Nếu có nhắc nhở đến hạn -> kích hoạt hiệu ứng chuông rung lắc
        if (stats.den_han > 0) {
          bellBtn.classList.add('bell-ringing');
        } else {
          bellBtn.classList.remove('bell-ringing');
        }
      } catch (err) {
        // im lặng nếu có lỗi mạng
      }
    }

    // Tự động kiểm tra nhắc nhở đến hạn (Auto Reminder Checker)
    async function checkAutoReminders() {
      if (!window.thongBaoService) return;
      try {
        const dueList = await window.thongBaoService.getDueReminders();
        let hasNewDue = false;

        dueList.forEach(item => {
          if (!alertedIds.has(item.id)) {
            alertedIds.add(item.id);
            hasNewDue = true;
            if (window.Toast) {
              window.Toast.warning(`⏰ [NHẮC NHỞ ĐẾN HẠN] ${item.tieu_de}\nNội dung: ${item.noi_dung.substring(0, 80)}...`);
            }
          }
        });

        if (hasNewDue) {
          playAlertBeep();
        }

        await updateBellStats();
      } catch (e) {
        // im lặng
      }
    }

    // Nạp dữ liệu lần đầu
    await updateBellStats();
    await checkAutoReminders();

    // Thiết lập tự động quét mỗi 30 giây (30,000 ms)
    // Thiết lập tự động quét thời gian thực mỗi 2 giây (2000 ms) theo đúng yêu cầu
    setInterval(async () => {
      await updateBellStats();
      await checkAutoReminders();
    }, 2000);
  }

  // Khởi chạy khi DOM sẵn sàng
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNotificationBell);
  } else {
    initNotificationBell();
  }

  window.NotificationBell = {
    init: initNotificationBell
  };
})(window);
