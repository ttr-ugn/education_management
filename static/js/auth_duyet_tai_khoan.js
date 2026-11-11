document.addEventListener('DOMContentLoaded', async () => {
      // 1. Phân quyền: Chỉ cho phép VAN_THU
      const user = await window.AuthGuard.check({ requiredRoles: ['VAN_THU'] });
      if (!user) return;

      const tbody = document.getElementById('pendingTableBody');
      const counterEl = document.getElementById('pendingCounter');
      const searchInput = document.getElementById('searchInput');
      const refreshBtn = document.getElementById('refreshBtn');

      let allPendingUsers = [];

      async function loadData() {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center p-4 text-muted">Đang tải dữ liệu...</td></tr>';
        allPendingUsers = await window.AdminUserModule.loadUsers({ trang_thai: 'CHO_DUYET' });
        renderTable();
      }

      function renderTable() {
        const query = searchInput.value.toLowerCase().trim();
        const filtered = allPendingUsers.filter(u =>
          (u.ho_va_ten && u.ho_va_ten.toLowerCase().includes(query)) ||
          (u.ten_dang_nhap && u.ten_dang_nhap.toLowerCase().includes(query)) ||
          (u.email && u.email.toLowerCase().includes(query)) ||
          (u.phong_ban && u.phong_ban.toLowerCase().includes(query))
        );

        counterEl.innerHTML = `⏳ Đang chờ duyệt: <b>${filtered.length}</b>`;

        if (filtered.length === 0) {
          tbody.innerHTML = `
            <tr>
              <td colspan="8" class="text-center p-4 text-muted">
                ${allPendingUsers.length === 0 ? 'Hiện tại không có tài khoản nào đang chờ duyệt.' : 'Không tìm thấy kết quả phù hợp.'}
              </td>
            </tr>
          `;
          return;
        }

        tbody.innerHTML = filtered.map((u, index) => {
          const author = (u.ho_va_ten || 'Cán bộ').trim();
          const words = author.split(/\s+/).filter(Boolean);
          const initials = words.length >= 2
            ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
            : author.slice(0, 2).toUpperCase();

          return `
            <tr>
              <td style="text-align: center; font-weight: 600; color: #64748b; font-size: 12px;">${index + 1}</td>
              <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                  <div style="width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: 700; font-size: 11.5px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.15);">
                    ${initials}
                  </div>
                  <div>
                    <div style="font-weight: 700; color: #0f172a; font-size: 13.5px;">${u.ho_va_ten}</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 1px;">${u.chuc_vu || 'Chuyên viên'}</div>
                  </div>
                </div>
              </td>
              <td>
                <div style="display: inline-flex; align-items: center; padding: 3px 8px; background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 6px; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px; font-weight: 600; color: #0284c7;">
                  ${u.ten_dang_nhap}
                </div>
              </td>
              <td>
                <span style="display: inline-flex; align-items: center; gap: 5px; color: #475569; font-size: 12px;">
                  <span>✉️</span>
                  <span>${u.email}</span>
                </span>
              </td>
              <td>
                ${u.sdt ? `
                  <span style="display: inline-flex; align-items: center; gap: 4px; color: #475569; font-size: 12px;">
                    <span>📱</span>
                    <span>${u.sdt}</span>
                  </span>
                ` : '<span style="color: #94a3b8; font-size: 12px; font-style: italic;">Chưa có</span>'}
              </td>
              <td>
                <div>
                  <div style="font-weight: 600; color: #1e293b; font-size: 13px;">${u.phong_ban || 'Chưa cập nhật'}</div>
                  <div style="font-size: 11px; color: #64748b; margin-top: 1px;">${u.chuc_vu || ''}</div>
                </div>
              </td>
              <td>
                <span style="font-size: 12px; color: #334155; font-weight: 500;">
                  📅 ${u.ngay_tao || 'Hôm nay'}
                </span>
              </td>
              <td style="text-align: center;">
                <div class="d-flex justify-content-center gap-1">
                  <button class="btn-action-soft btn-action-approve btn-approve" data-id="${u.nguoi_dung_id}" data-name="${u.ho_va_ten}">
                    ✓ Phê duyệt
                  </button>
                  <button class="btn-action-soft btn-action-reject btn-reject" data-id="${u.nguoi_dung_id}" data-name="${u.ho_va_ten}">
                    ✕ Từ chối
                  </button>
                </div>
              </td>
            </tr>
          `;
        }).join('');

        // Gắn sự kiện các nút
        tbody.querySelectorAll('.btn-approve').forEach(btn => {
          btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            const name = btn.getAttribute('data-name');
            window.AdminUserModule.approve(id, name, loadData);
          });
        });

        tbody.querySelectorAll('.btn-reject').forEach(btn => {
          btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            const name = btn.getAttribute('data-name');
            window.AdminUserModule.promptReject(id, name, loadData);
          });
        });
      }

      searchInput.addEventListener('input', renderTable);
      refreshBtn.addEventListener('click', loadData);

      // Tải dữ liệu ban đầu
      loadData();
    });
