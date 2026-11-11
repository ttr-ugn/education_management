document.addEventListener('DOMContentLoaded', async () => {

      const user = await window.AuthGuard.check();

      if (!user) return;



      // Cập nhật số thông báo chưa đọc trên topbar

      if (window.thongBaoService) {

        window.thongBaoService.getUnreadCount().then(c => {

          const b = document.querySelector('.topbar-icon-badge');

          if (b && c > 0) {

            b.style.display = 'block';

            b.textContent = c > 99 ? '99+' : c;

          }

        });

      }



      // Cập nhật thông tin chào mừng

      const greetingEl = document.getElementById('welcomeGreeting');

      const subtextEl = document.getElementById('welcomeSubtext');

      const quickActionsEl = document.getElementById('quickActionButtons');



      const hour = new Date().getHours();

      const timeGreeting = hour < 12 ? 'Chào buổi sáng' : (hour < 18 ? 'Chào buổi chiều' : 'Chào buổi tối');

      greetingEl.textContent = `${timeGreeting}, đồng chí ${user.ho_va_ten}!`;



      // Cấu hình nút tác vụ nhanh và card thống kê theo vai trò

      const statRoleSpec = document.getElementById('statRoleSpec');

      const statRoleLabel = document.getElementById('statRoleLabel');



      if (user.vai_tro === 'VAN_THU') {

        subtextEl.textContent = 'Vai trò: Văn thư cơ quan & Quản trị hệ thống. Tiếp nhận dự thảo từ Chuyên viên, chuyển Lãnh đạo ký số và ban hành văn bản chính thức.';

        statRoleLabel.textContent = 'Dự thảo chờ kiểm tra';

        

        let draftCount = 0;

        try {

          const vbRes = await window.api.get('/api/van-ban-di?trang_thai=CHO_VAN_THU_KIEM_TRA');

          if (vbRes.du_lieu) {

            draftCount = vbRes.du_lieu.length;

            statRoleSpec.textContent = draftCount;

          }

        } catch (e) {}



        quickActionsEl.innerHTML = `

          <a href="van-ban-di/kiem-tra.html" class="btn btn-warning">

            📥 Kiểm tra dự thảo Chuyên viên (${draftCount})

          </a>

          <a href="van-ban-di/ban-hanh.html" class="btn btn-outline-primary" style="background: rgba(255,255,255,0.15); color: #fff; border-color: rgba(255,255,255,0.3);">

            Cấp số & Ban hành

          </a>

          <a href="cong-viec/giao-viec.html" class="btn btn-outline-primary" style="background: rgba(255,255,255,0.15); color: #fff; border-color: rgba(255,255,255,0.3);">

            + Giao việc mới

          </a>

          <a href="admin/duyet-tai-khoan.html" class="btn btn-outline-primary" style="background: rgba(255,255,255,0.15); color: #fff; border-color: rgba(255,255,255,0.3);">

            Duyệt tài khoản

          </a>

        `;

      } else if (user.vai_tro === 'LANH_DAO') {

        subtextEl.textContent = 'Vai trò: Lãnh đạo Sở. Xem xét phê duyệt, ký số điện tử văn bản nội bộ, xem hồ sơ lưu trữ và theo dõi báo cáo thống kê.';

        statRoleLabel.textContent = 'Văn bản chờ duyệt';

        statRoleSpec.textContent = '0';

        quickActionsEl.innerHTML = `

          <a href="van-ban-di/phe-duyet.html" class="btn btn-warning">

            ✍ Ký số & Phê duyệt VB

          </a>

          <a href="ho-so/danh-sach.html" class="btn btn-primary">

            📁 Xem Hồ sơ tài liệu

          </a>

          <a href="thong-ke.html" class="btn btn-secondary">

            📊 Xem Báo cáo thống kê

          </a>

          <a href="van-ban-di/danh-sach.html" class="btn btn-outline-primary" style="background: rgba(255,255,255,0.15); color: #fff; border-color: rgba(255,255,255,0.3);">

            Sổ theo dõi văn bản

          </a>

        `;

      } else {

        // CHUYEN_VIEN

        subtextEl.textContent = 'Vai trò: Chuyên viên xử lý nghiệp vụ. Soạn thảo văn bản đi, theo dõi tiến độ phê duyệt và thực hiện nhiệm vụ được giao.';

        statRoleLabel.textContent = 'Văn bản của tôi';

        statRoleSpec.textContent = '0';

        quickActionsEl.innerHTML = `

          <a href="van-ban-di/soan-thao.html" class="btn btn-primary">

            + Soạn thảo dự thảo mới

          </a>

          <a href="van-ban-di/danh-sach.html" class="btn btn-outline-primary" style="background: rgba(255,255,255,0.15); color: #fff; border-color: rgba(255,255,255,0.3);">

            Văn bản của tôi

          </a>

          <a href="cong-viec/xu-ly.html" class="btn btn-warning">

            Báo cáo tiến độ CV

          </a>

        `;

      }



      // Nạp danh sách dự thảo nội bộ thật vào bảng
      try {
        const vbAll = await window.api.get('/api/van-ban-di');
        if (vbAll && vbAll.du_lieu && vbAll.du_lieu.length > 0) {
          const list = vbAll.du_lieu.slice(0, 5);
          const statEl = document.getElementById('statVBDen');
          if (statEl) statEl.textContent = vbAll.du_lieu.length;

          const statusConfig = {
            'CHO_LANH_DAO_KY': {
              label: 'Chờ LĐ ký',
              icon: '✍️',
              bg: '#eff6ff',
              color: '#1d4ed8',
              border: '#bfdbfe',
              dot: '#2563eb'
            },
            'CHO_LANH_DAO_DUYET': {
              label: 'Chờ LĐ duyệt',
              icon: '✍️',
              bg: '#eff6ff',
              color: '#1d4ed8',
              border: '#bfdbfe',
              dot: '#2563eb'
            },
            'CHO_VAN_THU_KIEM_TRA': {
              label: 'Chờ VT kiểm tra',
              icon: '⏳',
              bg: '#fffbeb',
              color: '#b45309',
              border: '#fde68a',
              dot: '#f59e0b'
            },
            'DA_KY_CHO_BAN_HANH': {
              label: 'Chờ ban hành',
              icon: '📝',
              bg: '#f0fdf4',
              color: '#15803d',
              border: '#bbf7d0',
              dot: '#22c55e'
            },
            'DA_DUYET': {
              label: 'Chờ ban hành',
              icon: '📝',
              bg: '#f0fdf4',
              color: '#15803d',
              border: '#bbf7d0',
              dot: '#22c55e'
            },
            'DA_BAN_HANH': {
              label: 'Đã ban hành',
              icon: '✅',
              bg: '#ecfdf5',
              color: '#047857',
              border: '#a7f3d0',
              dot: '#10b981'
            },
            'VAN_THU_TRA_LAI': {
              label: 'VT trả lại',
              icon: '↩️',
              bg: '#fef2f2',
              color: '#b91c1c',
              border: '#fecaca',
              dot: '#ef4444'
            },
            'LANH_DAO_TRA_LAI': {
              label: 'LĐ trả lại',
              icon: '↩️',
              bg: '#fef2f2',
              color: '#b91c1c',
              border: '#fecaca',
              dot: '#ef4444'
            }
          };

          const escapeHtml = (str) => {
            if (!str) return '';
            return String(str)
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;');
          };

          const tbody = document.getElementById('recentVBDenList');
          if (tbody) {
            tbody.innerHTML = list.map(d => {
              // 1. Tên người soạn & initials avatar
              const author = (d.nguoi_soan_ten || d.nguoi_soan_thao || 'Lê Thị Thảo').trim();
              const words = author.split(/\s+/).filter(Boolean);
              const initials = words.length >= 2
                ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
                : author.slice(0, 2).toUpperCase();
              const donVi = d.don_vi_soan_thao || 'Phòng GD&ĐT';

              // 2. Huy hiệu trạng thái cao cấp
              const cfg = statusConfig[d.trang_thai] || {
                label: d.trang_thai || 'Đang xử lý',
                icon: '📌',
                bg: '#f1f5f9',
                color: '#475569',
                border: '#cbd5e1',
                dot: '#64748b'
              };

              const badgeHtml = `
                <span class="badge" style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; font-size: 12px; font-weight: 600; border-radius: 20px; background: ${cfg.bg}; color: ${cfg.color}; border: 1px solid ${cfg.border}; box-shadow: 0 1px 2px rgba(0,0,0,0.04); white-space: nowrap;">
                  <span style="width: 7px; height: 7px; border-radius: 50%; background: ${cfg.dot}; display: inline-block;"></span>
                  <span>${cfg.icon} ${cfg.label}</span>
                </span>
              `;

              // 3. Mã số dạng pill monospace xanh
              const codeHtml = `
                <div class="doc-code-pill" style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 6px; font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, Menlo, monospace; font-size: 12px; font-weight: 600; color: #0284c7; white-space: nowrap;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                  <span>${escapeHtml(d.so_ky_hieu || 'Dự thảo')}</span>
                </div>
              `;

              // 4. Chip người soạn có avatar & phòng ban
              const authorHtml = `
                <div class="user-chip" style="display: flex; align-items: center; gap: 10px; min-width: 170px;">
                  <div class="user-chip-avatar" style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: 700; font-size: 11.5px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 1px 3px rgba(2, 132, 199, 0.3);">
                    ${initials}
                  </div>
                  <div>
                    <div class="user-chip-name" style="font-weight: 600; color: #1e293b; font-size: 13px; line-height: 1.2;">${escapeHtml(author)}</div>
                    <div class="user-chip-dept" style="font-size: 11px; color: #64748b; margin-top: 2px;">${escapeHtml(donVi)}</div>
                  </div>
                </div>
              `;

              // 5. Trích yếu nội dung kèm tag loại văn bản và độ khẩn
              const trichYeuHtml = `
                <div style="max-width: 340px;">
                  <a href="van-ban-di/danh-sach.html?id=${d.van_ban_id || ''}" style="color: #0f172a; font-weight: 600; font-size: 13.5px; line-height: 1.45; text-decoration: none; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${escapeHtml(d.trich_yeu)}">
                    ${escapeHtml(d.trich_yeu)}
                  </a>
                  <div style="display: flex; align-items: center; gap: 6px; margin-top: 4px; flex-wrap: wrap;">
                    ${d.loai_van_ban ? `<span style="font-size: 11px; padding: 1px 7px; background: #f1f5f9; color: #475569; border-radius: 4px; border: 1px solid #e2e8f0; font-weight: 500;">${escapeHtml(d.loai_van_ban)}</span>` : ''}
                    ${d.do_khan && d.do_khan === 'Khẩn' ? `<span style="font-size: 10.5px; padding: 1px 6px; background: #fef2f2; color: #dc2626; border-radius: 4px; border: 1px solid #fecaca; font-weight: 600;">⚡ Khẩn</span>` : ''}
                  </div>
                </div>
              `;

              return `
                <tr style="transition: background-color 0.15s ease;">
                  <td style="vertical-align: middle; padding: 12px 16px;">${codeHtml}</td>
                  <td style="vertical-align: middle; padding: 12px 16px;">${trichYeuHtml}</td>
                  <td style="vertical-align: middle; padding: 12px 16px;">${authorHtml}</td>
                  <td style="vertical-align: middle; padding: 12px 16px;">${badgeHtml}</td>
                </tr>
              `;
            }).join('');
          }
        }
      } catch (e) {
        console.error('Lỗi nạp danh sách dự thảo:', e);
      }
    });
