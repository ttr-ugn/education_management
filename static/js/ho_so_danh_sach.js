document.addEventListener('DOMContentLoaded', async () => {
      const user = await window.AuthGuard.check();
      if (!user) return;

      // Nếu là Lãnh đạo -> Ẩn nút tạo hồ sơ (Lãnh đạo chỉ xem)
      if (user.vai_tro === 'LANH_DAO') {
        const btnThem = document.getElementById('btnThemHoSo');
        if (btnThem) btnThem.style.display = 'none';
      }

      const tbody = document.getElementById('hoSoTableBody');
      const searchInput = document.getElementById('searchInput');
      const filterStatus = document.getElementById('filterStatus');
      const filterYear = document.getElementById('filterYear');
      const reloadBtn = document.getElementById('reloadBtn');

      const escapeHtml = (str) => {
        if (!str) return '';
        return String(str)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;');
      };

      const statusConfig = {
        'DA_LUU_TRU': {
          label: 'Đã lưu trữ',
          bg: '#ecfdf5',
          color: '#047857',
          border: '#a7f3d0',
          dot: '#10b981'
        },
        'DA_NOP_LUU_TRU': {
          label: 'Đã lưu trữ',
          bg: '#ecfdf5',
          color: '#047857',
          border: '#a7f3d0',
          dot: '#10b981'
        },
        'DANG_THU_THAP': {
          label: 'Đang thu thập',
          bg: '#fffbeb',
          color: '#b45309',
          border: '#fde68a',
          dot: '#f59e0b'
        },
        'DA_DONG': {
          label: 'Đã đóng hồ sơ',
          bg: '#f1f5f9',
          color: '#475569',
          border: '#cbd5e1',
          dot: '#64748b'
        }
      };

      async function loadData() {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center p-4 text-muted">Đang tải dữ liệu hồ sơ...</td></tr>';
        const filters = {
          q: searchInput.value.trim(),
          tinh_trang: filterStatus.value,
          nam_tai_lieu: filterYear.value
        };

        try {
          const list = await window.hoSoService.getAll(filters);

          if (!list || list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center p-4 text-muted">Không tìm thấy hồ sơ lưu trữ nào phù hợp.</td></tr>';
            return;
          }

          tbody.innerHTML = list.map(item => {
            // Tên người lập & avatar chip
            const author = (item.nguoi_lap || 'Nguyễn Thị Thu Hằng').trim();
            const words = author.split(/\s+/).filter(Boolean);
            const initials = words.length >= 2
              ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
              : author.slice(0, 2).toUpperCase();

            // Tình trạng badge
            const cfg = statusConfig[item.tinh_trang] || {
              label: item.tinh_trang || 'Đang xử lý',
              bg: '#f1f5f9',
              color: '#475569',
              border: '#cbd5e1',
              dot: '#64748b'
            };

            const badgeHtml = `
              <span class="badge" style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; font-size: 12px; font-weight: 600; border-radius: 20px; background: ${cfg.bg}; color: ${cfg.color}; border: 1px solid ${cfg.border}; box-shadow: 0 1px 2px rgba(0,0,0,0.04); white-space: nowrap;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: ${cfg.dot}; display: inline-block;"></span>
                <span>${cfg.label}</span>
              </span>
            `;

            const codeHtml = `
              <div class="doc-code-pill" style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 6px; font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, Menlo, monospace; font-size: 12px; font-weight: 600; color: #0284c7; white-space: nowrap;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2.2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                <span>${escapeHtml(item.ma_ho_so)}</span>
              </div>
            `;

            const authorHtml = `
              <div class="user-chip" style="display: flex; align-items: center; gap: 9px; white-space: nowrap;">
                <div class="user-chip-avatar" style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: 700; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 1px 3px rgba(2, 132, 199, 0.25);">
                  ${initials}
                </div>
                <div class="user-chip-name" style="font-weight: 600; color: #1e293b; font-size: 13px;">${escapeHtml(author)}</div>
              </div>
            `;

            return `
              <tr style="transition: background-color 0.15s ease;">
                <td style="vertical-align: middle; padding: 12px 16px;">${codeHtml}</td>
                <td style="vertical-align: middle; padding: 12px 16px; max-width: 300px;">
                  <a href="chi-tiet.html?id=${item.id}" style="color: #0f172a; font-weight: 600; font-size: 13.5px; line-height: 1.45; text-decoration: none; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${escapeHtml(item.tieu_de)}">
                    ${escapeHtml(item.tieu_de)}
                  </a>
                  ${item.mo_ta ? `<div style="font-size: 11.5px; color: #64748b; margin-top: 3px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden;">${escapeHtml(item.mo_ta)}</div>` : ''}
                </td>
                <td style="vertical-align: middle; padding: 12px 16px;">
                  <span style="font-weight: 600; color: #1e293b; font-size: 13px;">${escapeHtml(item.don_vi || 'Sở GD&ĐT')}</span>
                </td>
                <td style="vertical-align: middle; padding: 12px 16px;">${authorHtml}</td>
                <td style="vertical-align: middle; padding: 12px 16px; text-align: center;">
                  <span style="display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 12px; font-weight: 600; color: #475569;">
                    ${escapeHtml(item.nam_tai_lieu || '2026')}
                  </span>
                </td>
                <td style="vertical-align: middle; padding: 12px 16px; text-align: center;">
                  <span class="badge" style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; font-size: 11.5px; font-weight: 600; border-radius: 20px; background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; white-space: nowrap;">
                    ${escapeHtml(item.thoi_han_bao_quan || 'Vĩnh viễn')}
                  </span>
                </td>
                <td style="vertical-align: middle; padding: 12px 16px; text-align: center;">
                  <span style="display: inline-flex; align-items: center; gap: 5px; padding: 3px 9px; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 14px; font-size: 12px; font-weight: 700; color: #1e293b; white-space: nowrap;">
                    ${item.so_luong_van_ban || 0} VB
                  </span>
                </td>
                <td style="vertical-align: middle; padding: 12px 16px;">${badgeHtml}</td>
                <td style="vertical-align: middle; padding: 12px 16px; text-align: center;">
                  <a href="chi-tiet.html?id=${item.id}" class="btn btn-outline-primary btn-sm" style="display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; border-radius: 6px; font-weight: 600; text-decoration: none;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    <span>Xem chi tiết</span>
                  </a>
                </td>
              </tr>
            `;
          }).join('');
        } catch (err) {
          tbody.innerHTML = `<tr><td colspan="9" class="text-center p-4 text-danger">Lỗi nạp dữ liệu hồ sơ: ${err.message}</td></tr>`;
        }
      }

      searchInput.addEventListener('input', loadData);
      filterStatus.addEventListener('change', loadData);
      filterYear.addEventListener('change', loadData);
      reloadBtn.addEventListener('click', loadData);

      loadData();
    });
