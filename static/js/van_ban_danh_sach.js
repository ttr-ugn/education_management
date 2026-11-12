function openPreviewModal(docId, fileType, fileName, trichYeu, soKyHieu) {
      const modal = document.getElementById('previewModal');
      const modalTitle = document.getElementById('previewModalTitle');
      const modalSubtitle = document.getElementById('previewModalSubtitle');
      const downloadBtn = document.getElementById('previewDownloadBtn');
      const iframe = document.getElementById('previewIframe');
      const loading = document.getElementById('previewLoading');

      modalTitle.textContent = fileName || 'Xem trước văn bản';
      modalSubtitle.textContent = (soKyHieu ? `[${soKyHieu}] ` : '') + (trichYeu || '');
      downloadBtn.href = `/api/van-ban-di/${docId}/download?type=${fileType || 'goc'}`;
      downloadBtn.download = fileName || 'van_ban';

      loading.style.display = 'flex';
      iframe.src = `/api/van-ban-di/${docId}/preview?type=${fileType || 'goc'}`;
      modal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }

    function onPreviewLoaded() {
      const loading = document.getElementById('previewLoading');
      if (loading) loading.style.display = 'none';
    }

    function closePreviewModal() {
      const modal = document.getElementById('previewModal');
      const iframe = document.getElementById('previewIframe');
      if (modal) modal.style.display = 'none';
      if (iframe) iframe.src = '';
      document.body.style.overflow = '';
    }

    function printPreviewFrame() {
      const iframe = document.getElementById('previewIframe');
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.print();
      }
    }

    window.openPreviewModal = openPreviewModal;
    window.closePreviewModal = closePreviewModal;
    window.onPreviewLoaded = onPreviewLoaded;
    window.printPreviewFrame = printPreviewFrame;

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closePreviewModal();
    });

    document.addEventListener('DOMContentLoaded', async () => {
      const user = await window.AuthGuard.check();
      if (!user) return;

      const headerActions = document.getElementById('headerActionButtons');
      if (user.vai_tro === 'VAN_THU') {
        headerActions.innerHTML = `
          <a href="kiem-tra.html" class="btn btn-warning">
            Tiếp nhận dự thảo Chuyên viên gửi
          </a>
          <a href="ban-hanh.html" class="btn btn-success">
            Cấp số & Ban hành
          </a>
          <a href="soan-thao.html" class="btn btn-primary">
            + Soạn thảo mới
          </a>
        `;
      } else if (user.vai_tro === 'LANH_DAO') {
        headerActions.innerHTML = `
          <a href="phe-duyet.html" class="btn btn-warning">
            Ký số & Duyệt văn bản
          </a>
        `;
      } else {
        headerActions.innerHTML = `
          <a href="soan-thao.html" class="btn btn-primary">
            + Soạn thảo dự thảo mới
          </a>
        `;
      }

      const tbody = document.getElementById('vbDiTableBody');
      const searchInput = document.getElementById('searchInput');
      const filterStatus = document.getElementById('filterStatus');
      const reloadBtn = document.getElementById('reloadBtn');

      const STATUS_LABELS = {
        'CHO_VAN_THU_KIEM_TRA': '<span class="badge" style="background: #fef3c7; color: #b45309; border: 1px solid #fde68a; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px;">Chờ VT kiểm tra</span>',
        'VAN_THU_TRA_LAI': '<span class="badge" style="background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px;">VT trả lại</span>',
        'CHO_LANH_DAO_KY': '<span class="badge" style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px;">Chờ LĐ ký</span>',
        'CHO_LANH_DAO_DUYET': '<span class="badge" style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px;">Chờ LĐ ký</span>',
        'LANH_DAO_TRA_LAI': '<span class="badge" style="background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px;">LĐ trả lại</span>',
        'DA_KY_CHO_BAN_HANH': '<span class="badge" style="background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px;">Chờ ban hành</span>',
        'DA_DUYET': '<span class="badge" style="background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px;">Chờ ban hành</span>',
        'DA_BAN_HANH': '<span class="badge" style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px;">Đã ban hành</span>',
        'YEU_CAU_CHINH_SUA': '<span class="badge" style="background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px;">Cần sửa</span>'
      };

      async function loadData() {
        try {
          const filters = {
            q: searchInput.value.trim(),
            trang_thai: filterStatus.value
          };
          tbody.innerHTML = '<tr><td colspan="8" class="text-center p-4 text-muted"><div class="spinner-border spinner-border-sm text-primary" role="status" style="margin-right: 6px;"></div>Đang nạp dữ liệu văn bản...</td></tr>';

          const list = await window.vanBanDiService.getAll(filters);

          if (!list || list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center p-4 text-muted">Không có văn bản đi nào phù hợp.</td></tr>';
            return;
          }

          tbody.innerHTML = list.map(item => {
            const docId = item.id || item.van_ban_id;
            let quickBtn = '';
            if (user.vai_tro === 'VAN_THU' && item.trang_thai === 'CHO_VAN_THU_KIEM_TRA') {
              quickBtn = `
                <a href="kiem-tra.html" class="btn-action-primary btn-amber" title="Tiếp nhận và kiểm tra thể thức dự thảo">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
                  <span>Kiểm tra</span>
                </a>
              `;
            } else if (user.vai_tro === 'LANH_DAO' && (item.trang_thai === 'CHO_LANH_DAO_KY' || item.trang_thai === 'CHO_LANH_DAO_DUYET')) {
              quickBtn = `
                <a href="phe-duyet.html" class="btn-action-primary btn-blue" title="Ký số điện tử và phê duyệt văn bản">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                  <span>Ký số</span>
                </a>
              `;
            } else if (user.vai_tro === 'VAN_THU' && (item.trang_thai === 'DA_KY_CHO_BAN_HANH' || item.trang_thai === 'DA_DUYET')) {
              quickBtn = `
                <a href="ban-hanh.html" class="btn-action-primary btn-emerald" title="Cấp số và ban hành văn bản">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                  <span>Ban hành</span>
                </a>
              `;
            } else if (item.trang_thai === 'DA_BAN_HANH' && item.co_file_da_ky) {
              quickBtn = `
                <a href="/api/van-ban-di/${docId}/download?type=da_ky" target="_blank" class="btn-action-primary btn-pdf" title="Tải văn bản đã ký số">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                  <span>Tải PDF</span>
                </a>
              `;
            }

            // 1. Mã số dạng pill monospace
            const codeHtml = `
              <div class="doc-code-pill" style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 6px; font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, Menlo, monospace; font-size: 12px; font-weight: 600; color: #0284c7; white-space: nowrap;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                <span>${item.so_ky_hieu || 'Dự thảo'}</span>
              </div>
            `;

            // 2. Trích yếu
            const safeTrichYeu = (item.trich_yeu || '').replace(/"/g, '&quot;');
            const safeFileName = (item.file_da_ky_ten || item.file_goc_ten || 'van_ban').replace(/'/g, "\\'");
            const safeSoKyHieu = (item.so_ky_hieu || '').replace(/'/g, "\\'");
            const safeJsTrichYeu = (item.trich_yeu || '').replace(/'/g, "\\'");

            const trichYeuHtml = `
              <div style="max-width: 280px;">
                <a href="chi-tiet.html?id=${docId}" style="color: #0f172a; font-weight: 600; font-size: 13.5px; line-height: 1.45; text-decoration: none; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${safeTrichYeu}">
                  ${item.trich_yeu || ''}
                </a>
                ${item.ly_do_chinh_sua ? `<div style="font-size: 11.5px; color: #dc2626; background: #fef2f2; border: 1px solid #fecaca; padding: 2px 8px; border-radius: 4px; margin-top: 5px; display: inline-flex; align-items: center; gap: 4px;">Ý kiến: ${item.ly_do_chinh_sua}</div>` : ''}
              </div>
            `;

            // 3. Loại văn bản
            const loaiHtml = `
              <span style="display: inline-flex; align-items: center; padding: 3px 8px; background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 11.5px; font-weight: 600; white-space: nowrap;">
                ${item.loai_van_ban || 'Văn bản'}
              </span>
            `;

            // 4. Avatar chip người soạn
            const author = (item.nguoi_soan_ten || item.nguoi_soan_thao || 'Lê Thị Thảo').trim();
            const words = author.split(/\s+/).filter(Boolean);
            const initials = words.length >= 2
              ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
              : author.slice(0, 2).toUpperCase();
            const donVi = item.don_vi_soan_thao || 'Phòng GD&ĐT';

            const authorHtml = `
              <div class="user-chip" style="display: flex; align-items: center; gap: 10px; min-width: 180px;">
                <div class="user-chip-avatar" style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: 700; font-size: 11.5px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 1px 3px rgba(2, 132, 199, 0.3);">
                  ${initials}
                </div>
                <div>
                  <div class="user-chip-name" style="font-weight: 600; color: #1e293b; font-size: 13px; line-height: 1.2;">${author}</div>
                  <div class="user-chip-dept" style="font-size: 11px; color: #64748b; margin-top: 2px;">${donVi}</div>
                </div>
              </div>
            `;

            // 5. Lãnh đạo ký chip
            const leaderName = item.lanh_dao_ky || item.lanh_dao_ky_ten || 'Lãnh đạo Sở';
            const lanhDaoHtml = `
              <span style="display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap;">
                
                <span>${leaderName}</span>
              </span>
            `;

            // 6. Ngày soạn
            const dateStr = (item.ngay_soan || item.ngay_tao || '').split(' ');
            const datePart = dateStr[0] || '2026-11-10';
            const timePart = dateStr[1] || '';
            const ngaySoanHtml = `
              <div style="white-space: nowrap;">
                <span style="display: inline-flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 600; color: #334155;">
                  ${datePart}
                </span>
                ${timePart ? `<div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">${timePart}</div>` : ''}
              </div>
            `;

            return `
              <tr style="transition: background-color 0.15s ease;">
                <td style="vertical-align: middle; padding: 12px 16px;">${codeHtml}</td>
                <td style="vertical-align: middle; padding: 12px 16px;">${trichYeuHtml}</td>
                <td style="vertical-align: middle; padding: 12px 16px;">${loaiHtml}</td>
                <td style="vertical-align: middle; padding: 12px 16px;">${authorHtml}</td>
                <td style="vertical-align: middle; padding: 12px 16px;">${lanhDaoHtml}</td>
                <td style="vertical-align: middle; padding: 12px 16px;">${ngaySoanHtml}</td>
                <td style="vertical-align: middle; padding: 12px 16px;">${STATUS_LABELS[item.trang_thai] || item.trang_thai}</td>
                <td style="vertical-align: middle; padding: 10px 12px; text-align: center;">
                  <div class="action-card-group" style="width: 155px; margin: 0 auto; display: flex; flex-direction: column; gap: 5px;">
                    ${quickBtn}
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; width: 100%;">
                      <button type="button" class="btn-action-preview" onclick="openPreviewModal(${docId}, '${item.co_file_da_ky ? 'da_ky' : 'goc'}', '${safeFileName}', '${safeJsTrichYeu}', '${safeSoKyHieu}')" title="Xem trước tài liệu trực tiếp">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                        <span>Xem</span>
                      </button>
                      <a href="chi-tiet.html?id=${docId}" class="btn-action-detail" title="Xem toàn bộ hồ sơ chi tiết">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M15 3h6v6"></path><path d="M10 14L21 3"></path><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path></svg>
                        <span>Chi tiết</span>
                      </a>
                    </div>
                  </div>
                </td>
              </tr>
            `;
          }).join('');
        } catch (err) {
          console.error('Lỗi khi tải dữ liệu văn bản đi:', err);
          tbody.innerHTML = `<tr><td colspan="8" class="text-center p-4 text-danger">Đã xảy ra lỗi khi tải danh sách: ${err.message}</td></tr>`;
        }
      }

      searchInput.addEventListener('input', loadData);
      filterStatus.addEventListener('change', loadData);
      reloadBtn.addEventListener('click', loadData);

      loadData();
    });
