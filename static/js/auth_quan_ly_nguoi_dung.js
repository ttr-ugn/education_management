document.addEventListener('DOMContentLoaded', async () => {
      const user = await window.AuthGuard.check({ requiredRoles: ['VAN_THU'] });
      if (!user) return;

      const tbody = document.getElementById('usersTableBody');
      const searchInput = document.getElementById('searchInput');
      const filterRole = document.getElementById('filterRole');
      const filterStatus = document.getElementById('filterStatus');
      const reloadBtn = document.getElementById('reloadBtn');

      let allUsers = [];

      async function fetchUsers() {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center p-4 text-muted">Đang nạp dữ liệu người dùng...</td></tr>';
        const params = {};
        if (filterRole.value) params.vai_tro = filterRole.value;
        if (filterStatus.value) params.trang_thai = filterStatus.value;
        if (searchInput.value.trim()) params.q = searchInput.value.trim();

        allUsers = await window.AdminUserModule.loadUsers(params);
        renderTable();
      }

      function renderTable() {
        // Cập nhật thống kê nhanh
        if (allUsers) {
          const total = allUsers.length;
          const leaders = allUsers.filter(u => u.vai_tro === 'LANH_DAO').length;
          const specialists = allUsers.filter(u => u.vai_tro === 'CHUYEN_VIEN').length;
          const active = allUsers.filter(u => u.trang_thai === 'HOAT_DONG').length;
          const activePct = total > 0 ? Math.round((active / total) * 100) : 100;
          if (document.getElementById('statTotalUsers')) document.getElementById('statTotalUsers').innerText = total;
          if (document.getElementById('statLeaders')) document.getElementById('statLeaders').innerText = leaders;
          if (document.getElementById('statSpecialists')) document.getElementById('statSpecialists').innerText = specialists;
          if (document.getElementById('statActiveRatio')) document.getElementById('statActiveRatio').innerText = `${activePct}%`;
        }

        if (!allUsers || allUsers.length === 0) {
          tbody.innerHTML = '<tr><td colspan="9" class="text-center p-4 text-muted">Không tìm thấy người dùng nào phù hợp.</td></tr>';
          return;
        }

        tbody.innerHTML = allUsers.map((u, i) => {
          const isSelf = u.nguoi_dung_id === user.nguoi_dung_id;

          // 1. Avatar chip
          const author = (u.ho_va_ten || 'Cán bộ').trim();
          const words = author.split(/\s+/).filter(Boolean);
          const initials = words.length >= 2
            ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
            : author.slice(0, 2).toUpperCase();

          const avatarGrad = u.vai_tro === 'LANH_DAO' 
            ? 'linear-gradient(135deg, #7e22ce 0%, #6b21a8 100%)' 
            : (u.vai_tro === 'VAN_THU' ? 'linear-gradient(135deg, #059669 0%, #047857 100%)' : 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)');

          const nameHtml = `
            <div style="display: flex; align-items: center; gap: 10px; min-width: 175px;">
              <div style="width: 34px; height: 34px; border-radius: 50%; background: ${avatarGrad}; color: #ffffff; font-weight: 700; font-size: 11.5px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.15);">
                ${initials}
              </div>
              <div>
                <div style="font-weight: 700; color: #0f172a; font-size: 13.5px; line-height: 1.3;">
                  ${u.ho_va_ten}
                  ${isSelf ? '<span style="background: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd; font-size: 10px; font-weight: 700; border-radius: 12px; padding: 1px 6px; margin-left: 5px;">Bạn</span>' : ''}
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 1px;">${u.chuc_vu || 'Cán bộ'}</div>
              </div>
            </div>
          `;

          // 2. Monospace pill username
          const usernameHtml = `
            <div style="display: inline-flex; align-items: center; gap: 5px; padding: 3px 8px; background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 6px; font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; font-size: 12px; font-weight: 600; color: #0284c7;">
              <span>${u.ten_dang_nhap}</span>
            </div>
          `;

          // 3. Email
          const emailHtml = `
            <div style="display: inline-flex; align-items: center; gap: 5px; color: #475569; font-size: 12px;">
              <span>${u.email}</span>
            </div>
          `;

          // 4. Phòng ban
          const deptHtml = `
            <div style="min-width: 180px;">
              <div style="font-weight: 600; color: #1e293b; font-size: 13px;">${u.phong_ban || 'Văn phòng Sở'}</div>
              <div style="font-size: 11px; color: #64748b; margin-top: 1px;">${u.chuc_vu || 'Cán bộ'}</div>
            </div>
          `;

          // 5. Đăng nhập cuối
          const lastLoginHtml = u.lan_dang_nhap_cuoi ? `
            <span style="display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: #334155; font-weight: 500;">
              <span>${u.lan_dang_nhap_cuoi}</span>
            </span>
          ` : `
            <span style="display: inline-flex; align-items: center; gap: 4px; font-size: 11.5px; color: #94a3b8; background: #f8fafc; border: 1px solid #e2e8f0; padding: 2px 8px; border-radius: 6px;">
              <span>Chưa đăng nhập</span>
            </span>
          `;

          // 6. Action buttons
          let actionBtns = '';
          if (u.trang_thai === 'CHO_DUYET') {
            actionBtns += `
              <button class="btn-action-soft btn-action-unlock btn-approve" data-id="${u.nguoi_dung_id}" data-name="${u.ho_va_ten}">Duyệt</button>
              <button class="btn-action-soft btn-action-lock btn-reject" data-id="${u.nguoi_dung_id}" data-name="${u.ho_va_ten}">Từ chối</button>
            `;
          } else {
            if (u.trang_thai === 'HOAT_DONG') {
              if (isSelf) {
                actionBtns += `<span style="border: 1px solid #e2e8f0; background: #f8fafc; color: #64748b; padding: 5px 12px; border-radius: 6px; font-size: 11.5px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">Bạn</span>`;
              } else {
                actionBtns += `<button class="btn-action-soft btn-action-lock btn-lock" data-id="${u.nguoi_dung_id}" data-name="${u.ho_va_ten}" title="Khóa tài khoản cán bộ này">Khóa</button>`;
              }
            } else if (u.trang_thai === 'BI_KHOA') {
              actionBtns += `<button class="btn-action-soft btn-action-unlock btn-unlock" data-id="${u.nguoi_dung_id}" data-name="${u.ho_va_ten}" title="Mở khóa tài khoản">Mở khóa</button>`;
            }

            if (u.trang_thai !== 'TU_CHOI' && !isSelf) {
              actionBtns += `<button class="btn-action-soft btn-action-reset btn-reset-pwd" data-id="${u.nguoi_dung_id}" data-name="${u.ho_va_ten}" title="Cấp lại mật khẩu mới cho cán bộ">Đặt lại MK</button>`;
            }
          }

          return `
            <tr style="transition: background-color 0.15s ease;">
              <td style="vertical-align: middle; text-align: center; font-weight: 600; color: #64748b; font-size: 12px;">${i + 1}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${nameHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${usernameHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${emailHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${deptHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${window.AdminUserModule.ROLE_BADGES[u.vai_tro] || u.vai_tro}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">
                ${window.AdminUserModule.STATUS_BADGES[u.trang_thai] || u.trang_thai}
                ${u.ly_do_tu_choi ? `<div style="font-size: 11px; color: #dc2626; margin-top: 3px;" title="${u.ly_do_tu_choi}">Lý do: ${u.ly_do_tu_choi.substring(0, 20)}...</div>` : ''}
              </td>
              <td style="vertical-align: middle; padding: 12px 14px;">${lastLoginHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px; text-align: center;">
                <div class="d-flex justify-content-center gap-1">
                  ${actionBtns}
                </div>
              </td>
            </tr>
          `;
        }).join('');

        // Gắn sự kiện
        tbody.querySelectorAll('.btn-approve').forEach(btn => {
          btn.addEventListener('click', () => {
            window.AdminUserModule.approve(btn.dataset.id, btn.dataset.name, fetchUsers);
          });
        });

        tbody.querySelectorAll('.btn-reject').forEach(btn => {
          btn.addEventListener('click', () => {
            window.AdminUserModule.promptReject(btn.dataset.id, btn.dataset.name, fetchUsers);
          });
        });

        tbody.querySelectorAll('.btn-lock').forEach(btn => {
          btn.addEventListener('click', () => {
            window.AdminUserModule.lock(btn.dataset.id, btn.dataset.name, fetchUsers);
          });
        });

        tbody.querySelectorAll('.btn-unlock').forEach(btn => {
          btn.addEventListener('click', () => {
            window.AdminUserModule.unlock(btn.dataset.id, btn.dataset.name, fetchUsers);
          });
        });

        tbody.querySelectorAll('.btn-reset-pwd').forEach(btn => {
          btn.addEventListener('click', () => {
            window.AdminUserModule.resetPassword(btn.dataset.id, btn.dataset.name, fetchUsers);
          });
        });
      }

      filterRole.addEventListener('change', fetchUsers);
      filterStatus.addEventListener('change', fetchUsers);
      reloadBtn.addEventListener('click', fetchUsers);

      let debounceTimer;
      searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(fetchUsers, 300);
      });

      fetchUsers();
    });
