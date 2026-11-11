document.addEventListener('DOMContentLoaded', async () => {
      const user = await window.AuthGuard.check();
      if (!user) return;

      const container = document.getElementById('notificationsContainer');
      const countStats = document.getElementById('countStats');
      const filterTabs = document.getElementById('filterTabs');
      const btnMarkAllRead = document.getElementById('btnMarkAllRead');

      // Modal elements
      const modal = document.getElementById('createNotificationModal');
      const btnOpenCreateModal = document.getElementById('btnOpenCreateModal');
      const btnCloseCreateModal = document.getElementById('btnCloseCreateModal');
      const btnCancelCreate = document.getElementById('btnCancelCreate');
      const form = document.getElementById('createNotificationForm');
      const modalTitleText = document.getElementById('modalTitleText');
      const btnSubmitNotification = document.getElementById('btnSubmitNotification');
      const tbPhamVi = document.getElementById('tbPhamVi');

      // Tùy biến giao diện theo vai trò người dùng
      if (user.vai_tro === 'VAN_THU') {
        btnOpenCreateModal.innerHTML = '📢 Phát hành thông báo (Văn thư)';
        modalTitleText.textContent = 'PHÁT HÀNH THÔNG BÁO ĐIỀU HÀNH NỘI BỘ (VĂN THƯ)';
        btnSubmitNotification.textContent = 'Phát hành thông báo';
      } else {
        btnOpenCreateModal.innerHTML = '⏰ Tạo lời nhắc cá nhân (Hẹn giờ)';
        modalTitleText.textContent = 'TẠO LỜI NHẮC CÔNG VIỆC CÁ NHÂN';
        btnSubmitNotification.textContent = 'Lưu lời nhắc';
        if (tbPhamVi) {
          tbPhamVi.value = 'me';
          document.getElementById('groupPhamVi').style.display = 'none';
        }
      }

      let currentFilter = 'all';
      let allNotifications = [];

      async function loadData() {
        try {
          allNotifications = await window.thongBaoService.getAll();
          renderList();
        } catch (err) {
          container.innerHTML = `
            <div class="card p-4 text-center text-danger">
              Không thể tải danh sách thông báo. Vui lòng thử lại sau.
            </div>
          `;
        }
      }

      window.loadNotificationsData = loadData;

      function renderList() {
        let filtered = [...allNotifications];
        if (currentFilter === 'unread') {
          filtered = filtered.filter(item => !item.da_doc);
        } else if (currentFilter === 'due') {
          filtered = filtered.filter(item => item.da_den_han || (item.loai === 'Nhắc nhở' && item.ngay_hen_gio));
        } else if (currentFilter !== 'all') {
          filtered = filtered.filter(item => item.loai === currentFilter);
        }

        const unreadTotal = allNotifications.filter(item => !item.da_doc).length;
        const dueTotal = allNotifications.filter(item => item.da_den_han).length;
        countStats.textContent = `Tổng số: ${allNotifications.length} | Chưa đọc: ${unreadTotal} | ⏰ Đến hạn: ${dueTotal}`;

        if (filtered.length === 0) {
          container.innerHTML = `
            <div class="card" style="padding: 40px; text-align: center; color: #64748b;">
              <div style="font-size: 36px; margin-bottom: 8px;">📭</div>
              <b>Không có thông báo hoặc lời nhắc nào trong mục này.</b>
            </div>
          `;
          return;
        }

        container.innerHTML = filtered.map(item => {
          let badgeColor = 'badge-info';
          if (item.muc_do === 'Khẩn cấp') badgeColor = 'badge-danger';
          else if (item.muc_do === 'Quan trọng') badgeColor = 'badge-warning';

          let borderColor = item.da_doc ? '#cbd5e1' : 'var(--primary-color)';
          if (item.da_den_han) borderColor = '#ef4444';
          else if (item.muc_do === 'Khẩn cấp') borderColor = '#ef4444';

          return `
            <div class="card notification-item mb-3" style="border-left: 4px solid ${borderColor};">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <div>
                    ${item.da_den_han ? '<span class="badge badge-due-alert mr-1">⏰ ĐÃ ĐẾN HẠN!</span>' : ''}
                    <span class="badge ${badgeColor}">${item.muc_do}</span>
                    <span class="badge badge-secondary ml-1">${item.loai}</span>
                    ${!item.da_doc ? '<span class="badge badge-warning ml-1">Mới</span>' : ''}
                    ${item.nguoi_nhan_id ? '<span class="badge badge-info ml-1">🔒 Lời nhắc riêng</span>' : '<span class="badge badge-secondary ml-1">🌐 Toàn cơ quan</span>'}
                  </div>
                  <small class="text-muted">${item.thoi_gian}</small>
                </div>
                <h3 style="font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 8px;">
                  ${item.tieu_de}
                </h3>
                <p style="font-size: 13.5px; color: #475569; line-height: 1.5; margin-bottom: 12px; white-space: pre-line;">
                  ${item.noi_dung}
                </p>
                ${item.ngay_hen_gio ? `
                  <div style="font-size: 12.5px; color: ${item.da_den_han ? '#dc2626' : '#2563eb'}; font-weight: 600; margin-bottom: 10px; background: #f8fafc; padding: 6px 10px; border-radius: 6px; display: inline-block;">
                    ⏰ Lịch hẹn / Hạn hoàn thành: <b>${item.ngay_hen_gio}</b>
                  </div>
                ` : ''}
                <div class="d-flex justify-content-between align-items-center text-muted" style="font-size: 12px; border-top: 1px solid var(--border-color); padding-top: 8px;">
                  <span>Nguồn phát hành: <b>${item.nguoi_gui}</b></span>
                  <div class="d-flex align-items-center gap-2">
                    ${!item.da_doc ? `
                      <button class="btn btn-outline-primary btn-sm btn-mark-read" data-id="${item.id}">
                        ✓ Đánh dấu đã đọc
                      </button>
                    ` : '<span class="text-muted" style="font-size: 12px;">✓ Đã đọc</span>'}
                    ${(user.vai_tro === 'VAN_THU' || user.ho_va_ten === item.nguoi_gui) ? `
                      <button class="btn-delete-tb" data-id="${item.id}" title="Xóa thông báo này">🗑 Xóa</button>
                    ` : ''}
                  </div>
                </div>
              </div>
            </div>
          `;
        }).join('');

        // Gán sự kiện đánh dấu đã đọc
        container.querySelectorAll('.btn-mark-read').forEach(btn => {
          btn.addEventListener('click', async () => {
            try {
              await window.thongBaoService.markAsRead(btn.dataset.id);
              window.Toast.success('Đã đánh dấu thông báo là đã đọc.');
              loadData();
              if (window.NotificationBell) window.NotificationBell.init();
            } catch (err) {
              window.Toast.error(err.message || 'Lỗi xử lý');
            }
          });
        });

        // Gán sự kiện xóa thông báo
        container.querySelectorAll('.btn-delete-tb').forEach(btn => {
          btn.addEventListener('click', async () => {
            if (!confirm('Đồng chí có chắc chắn muốn xóa mục này khỏi hệ thống?')) return;
            try {
              await window.thongBaoService.delete(btn.dataset.id);
              window.Toast.success('Đã xóa thành công.');
              loadData();
              if (window.NotificationBell) window.NotificationBell.init();
            } catch (err) {
              window.Toast.error(err.message || 'Lỗi khi xóa');
            }
          });
        });
      }

      // Xử lý chuyển tab lọc
      filterTabs.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          filterTabs.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          currentFilter = btn.dataset.filter;
          renderList();
        });
      });

      // Đánh dấu tất cả đã đọc
      btnMarkAllRead.addEventListener('click', async () => {
        try {
          await window.thongBaoService.markAllAsRead();
          window.Toast.success('Đã đánh dấu toàn bộ thông báo là đã đọc.');
          loadData();
          if (window.NotificationBell) window.NotificationBell.init();
        } catch (err) {
          window.Toast.error('Không thể cập nhật trạng thái đã đọc');
        }
      });

      // Mở modal tạo thông báo
      btnOpenCreateModal.addEventListener('click', () => {
        form.reset();
        modal.classList.remove('d-none');
      });

      function closeModal() {
        modal.classList.add('d-none');
      }

      btnCloseCreateModal.addEventListener('click', closeModal);
      btnCancelCreate.addEventListener('click', closeModal);

      // Submit form tạo thông báo
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phamVi = tbPhamVi ? tbPhamVi.value : 'all';
        const rawDate = document.getElementById('tbNgayHenGio').value;

        const payload = {
          tieu_de: document.getElementById('tbTieuDe').value.trim(),
          loai: document.getElementById('tbLoai').value,
          muc_do: document.getElementById('tbMucDo').value,
          ngay_hen_gio: rawDate ? rawDate.replace('T', ' ') + ':00' : null,
          noi_dung: document.getElementById('tbNoiDung').value.trim(),
          nguoi_nhan_id: phamVi === 'me' ? user.nguoi_dung_id : null
        };

        try {
          await window.thongBaoService.create(payload);
          window.Toast.success(phamVi === 'me' ? 'Đã lưu lời nhắc cá nhân thành công!' : 'Đã phát hành thông báo điều hành thành công!');
          closeModal();
          loadData();
          if (window.NotificationBell) window.NotificationBell.init();
        } catch (err) {
          window.Toast.error(err.message || 'Không thể tạo thông báo');
        }
      });

      // Nạp dữ liệu lần đầu
      loadData();

      // Cài đặt hàm thời gian thực tự động load lại danh sách mỗi 2 giây (2000 ms)
      setInterval(loadData, 2000);
    });
