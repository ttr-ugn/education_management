let currentFilterStatus = 'CHO_LANH_DAO_KY';
    let allDrafts = [];
    let activeDoc = null;

    function openPreviewModal(docId, fileName, trichYeu, soKyHieu, status) {
      activeDoc = { id: docId, fileName, trichYeu, soKyHieu, status };

      const modal = document.getElementById('previewModal');
      const modalTitle = document.getElementById('previewModalTitle');
      const modalSubtitle = document.getElementById('previewModalSubtitle');
      const downloadBtn = document.getElementById('previewDownloadBtn');
      const iframe = document.getElementById('previewIframe');
      const loading = document.getElementById('previewLoading');
      const signBtn = document.getElementById('modalSignBtn');
      const rejectBtn = document.getElementById('modalRejectBtn');

      modalTitle.textContent = fileName || 'Xem trước văn bản';
      modalSubtitle.textContent = (soKyHieu ? `[${soKyHieu}] ` : '') + (trichYeu || '');

      const isPending = (status === 'CHO_LANH_DAO_KY' || status === 'CHO_LANH_DAO_DUYET');
      signBtn.style.display = isPending ? 'inline-flex' : 'none';
      rejectBtn.style.display = isPending ? 'inline-flex' : 'none';

      const fileType = (status === 'DA_KY_CHO_BAN_HANH' || status === 'DA_BAN_HANH') ? 'da_ky' : 'goc';
      downloadBtn.href = `/api/van-ban-di/${docId}/download?type=${fileType}`;
      downloadBtn.download = fileName || 'van_ban';

      loading.style.display = 'flex';
      iframe.src = `/api/van-ban-di/${docId}/preview?type=${fileType}`;
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
      activeDoc = null;
    }

    function printPreviewFrame() {
      const iframe = document.getElementById('previewIframe');
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.print();
      }
    }

    async function executeSign(docId, trichYeu) {
      if (!confirm(`Đồng chí xác nhận KÝ SỐ ĐIỆN TỬ và PHÊ DUYỆT dự thảo:\n"${trichYeu || 'Văn bản'}"?`)) {
        return;
      }
      try {
        const res = await window.api.post(`/api/van-ban-di/${docId}/ky-so`, { page: 1, x: 60, y: 70 });
        window.Toast.success(res.thong_bao || 'Đã ký số điện tử thành công! Dự thảo đã chuyển về Văn thư để cấp số và ban hành.');
        closePreviewModal();
        fetchData();
      } catch (err) {
        window.Toast.error(err.message || 'Lỗi khi ký số văn bản');
      }
    }

    async function executeReject(docId) {
      const reason = prompt('Vui lòng nhập ý kiến chỉ đạo / lý do yêu cầu chỉnh sửa lại dự thảo:');
      if (reason && reason.trim()) {
        try {
          await window.api.post(`/api/van-ban-di/${docId}/tu-choi`, { ly_do: reason.trim() });
          window.Toast.info('Đã trả lại dự thảo kèm ý kiến chỉ đạo cho Chuyên viên và Văn thư.');
          closePreviewModal();
          fetchData();
        } catch (err) {
          window.Toast.error(err.message || 'Lỗi khi trả lại văn bản');
        }
      }
    }

    function signActiveDoc() {
      if (activeDoc) executeSign(activeDoc.id, activeDoc.trichYeu);
    }

    function rejectActiveDoc() {
      if (activeDoc) executeReject(activeDoc.id);
    }

    window.openPreviewModal = openPreviewModal;
    window.closePreviewModal = closePreviewModal;
    window.onPreviewLoaded = onPreviewLoaded;
    window.printPreviewFrame = printPreviewFrame;
    window.signActiveDoc = signActiveDoc;
    window.rejectActiveDoc = rejectActiveDoc;

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closePreviewModal();
    });

    document.addEventListener('DOMContentLoaded', async () => {
      // Xác thực vai trò Lãnh đạo
      const user = await window.AuthGuard.check({ requiredRoles: ['LANH_DAO'] });
      if (!user) return;

      const tbody = document.getElementById('pendingDraftsTable');
      const searchInput = document.getElementById('searchInput');
      const reloadBtn = document.getElementById('reloadBtn');
      const countPendingEl = document.getElementById('countPending');
      const filterTabs = document.querySelectorAll('.filter-tab');

      // Sự kiện chuyển Tab
      filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
          filterTabs.forEach(t => {
            t.classList.remove('btn-primary', 'active');
            t.classList.add('btn-outline-primary');
          });
          tab.classList.remove('btn-outline-primary');
          tab.classList.add('btn-primary', 'active');
          currentFilterStatus = tab.dataset.status;
          renderTable();
        });
      });

      window.fetchData = async function() {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center p-4 text-muted">Đang tải danh sách dự thảo...</td></tr>';
        try {
          const res = await window.api.get('/api/van-ban-di');
          allDrafts = res.du_lieu || [];

          // Đếm số lượng chờ ký duyệt
          const pendingCount = allDrafts.filter(d => d.trang_thai === 'CHO_LANH_DAO_KY' || d.trang_thai === 'CHO_LANH_DAO_DUYET').length;
          countPendingEl.textContent = pendingCount;

          renderTable();
        } catch (err) {
          tbody.innerHTML = `<tr><td colspan="7" class="text-center p-4 text-danger">Lỗi tải dữ liệu: ${err.message}</td></tr>`;
        }
      };

      function renderTable() {
        const kw = searchInput.value.toLowerCase().trim();
        const filtered = allDrafts.filter(d => {
          let matchStatus = false;
          if (currentFilterStatus === 'CHO_LANH_DAO_KY') {
            matchStatus = (d.trang_thai === 'CHO_LANH_DAO_KY' || d.trang_thai === 'CHO_LANH_DAO_DUYET');
          } else {
            matchStatus = (d.trang_thai === currentFilterStatus);
          }

          const matchKw = !kw ||
            (d.trich_yeu && d.trich_yeu.toLowerCase().includes(kw)) ||
            (d.so_ky_hieu && d.so_ky_hieu.toLowerCase().includes(kw)) ||
            (d.nguoi_soan_thao && d.nguoi_soan_thao.toLowerCase().includes(kw)) ||
            (d.nguoi_soan_ten && d.nguoi_soan_ten.toLowerCase().includes(kw)) ||
            (d.don_vi_soan_thao && d.don_vi_soan_thao.toLowerCase().includes(kw));
          return matchStatus && matchKw;
        });

        if (filtered.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" class="text-center p-4 text-muted">Không có văn bản nào trong mục này.</td></tr>`;
          return;
        }

        tbody.innerHTML = filtered.map(d => {
          const fileInfo = (d.tep_dinh_kem && d.tep_dinh_kem[0]) || { ten_tep: d.file_goc_ten || 'DuThao.docx' };
          const downloadUrl = fileInfo.download_url || `/api/van-ban-di/${d.id}/download?type=goc`;
          const fileName = (d.file_goc_ten || fileInfo.ten_tep || 'DuThao.docx');
          const cleanFileName = fileName.replace(/'/g, "\\'");
          const cleanTrichYeu = (d.trich_yeu || '').replace(/'/g, "\\'");
          const cleanSo = (d.so_ky_hieu || '').replace(/'/g, "\\'");

          // 1. Mã dự thảo
          const codeHtml = `
            <div class="doc-code-pill" style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 6px; font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, Menlo, monospace; font-size: 12px; font-weight: 600; color: #0284c7; white-space: nowrap;">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
              <span>${d.so_ky_hieu || 'Dự thảo'}</span>
            </div>
          `;

          // 2. Trích yếu
          const trichYeuHtml = `
            <div style="max-width: 280px;">
              <a href="chi-tiet.html?id=${d.id}" style="color: #0f172a; font-weight: 600; font-size: 13.5px; line-height: 1.45; text-decoration: none; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${d.trich_yeu || ''}">
                ${d.trich_yeu || ''}
              </a>
              ${d.ly_do_chinh_sua ? `<div style="font-size: 11.5px; color: #dc2626; background: #fef2f2; border: 1px solid #fecaca; padding: 2px 8px; border-radius: 4px; margin-top: 5px; display: inline-flex; align-items: center; gap: 4px;">⚠️ Ý kiến chỉ đạo: ${d.ly_do_chinh_sua}</div>` : ''}
            </div>
          `;

          // 3. Loại văn bản
          const loaiHtml = `
            <span style="display: inline-flex; align-items: center; padding: 3px 8px; background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 11.5px; font-weight: 600; white-space: nowrap;">
              ${d.loai_van_ban || 'Văn bản'}
            </span>
          `;

          // 4. Avatar chip người soạn
          const author = (d.nguoi_soan_ten || d.nguoi_soan_thao || 'Lê Thị Thảo').trim();
          const words = author.split(/\s+/).filter(Boolean);
          const initials = words.length >= 2
            ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
            : author.slice(0, 2).toUpperCase();
          const donVi = d.don_vi_soan_thao || 'Phòng GD&ĐT';

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

          // 5. Tệp đính kèm
          const fileHtml = `
            <div style="display: inline-flex; align-items: center; gap: 4px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 2px 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
              <button type="button" class="btn btn-sm btn-preview-file" onclick="openPreviewModal(${d.id}, '${cleanFileName}', '${cleanTrichYeu}', '${cleanSo}', '${d.trang_thai}')" style="display: inline-flex; align-items: center; gap: 5px; padding: 4px 8px; border: none; background: transparent; color: #0284c7; font-weight: 600; font-size: 12px; cursor: pointer;" title="Xem trước nội dung văn bản">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <span style="max-width: 90px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${fileName}</span>
              </button>
              <a href="${downloadUrl}" class="btn-download-icon" style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 4px; background: #f1f5f9; color: #475569; text-decoration: none;" title="Tải tệp về máy" download="${fileName}">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              </a>
            </div>
          `;

          // 6. Thời gian gửi
          const dateStr = (d.ngay_trinh_lanh_dao || d.ngay_soan || d.ngay_tao || '').split(' ');
          const datePart = dateStr[0] || '2026-11-10';
          const timePart = dateStr[1] || '';
          const ngayGuiHtml = `
            <div style="white-space: nowrap;">
              <span style="display: inline-flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 600; color: #334155;">
                📅 ${datePart}
              </span>
              ${timePart ? `<div style="font-size: 11px; color: #94a3b8; margin-top: 2px; padding-left: 18px;">${timePart}</div>` : ''}
            </div>
          `;

          // 7. Thao tác phê duyệt (Ký số & Duyệt, Trả lại)
          let actionsHtml = '';
          if (d.trang_thai === 'CHO_LANH_DAO_KY' || d.trang_thai === 'CHO_LANH_DAO_DUYET') {
            actionsHtml = `
              <div class="d-flex gap-2 justify-content-center" style="display: flex; gap: 6px; align-items: center;">
                <button class="btn btn-sign" data-id="${d.id}" data-title="${cleanTrichYeu}" style="display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; font-size: 12px; font-weight: 600; color: #ffffff; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border: none; border-radius: 6px; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.25); cursor: pointer; transition: all 0.15s ease;" title="Ký số điện tử & Phê duyệt">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                  <span>Ký số & Duyệt</span>
                </button>
                <button class="btn btn-reject" data-id="${d.id}" style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 10px; font-size: 12px; font-weight: 600; color: #dc2626; background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; cursor: pointer; transition: all 0.15s ease;" title="Yêu cầu Chuyên viên sửa đổi">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 14 4 9 9 4"></polyline><path d="M20 20v-7a4 4 0 0 0-4-4H4"></path></svg>
                  <span>Sửa</span>
                </button>
              </div>
            `;
          } else if (d.trang_thai === 'DA_KY_CHO_BAN_HANH') {
            actionsHtml = `
              <div class="d-flex flex-column align-items-center gap-1">
                <span class="badge" style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; font-size: 12px; font-weight: 600; border-radius: 20px; background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; box-shadow: 0 1px 2px rgba(4, 120, 87, 0.05); white-space: nowrap;">
                  <span style="width: 6px; height: 6px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
                  <span>✓ Đã ký số</span>
                </span>
                <span style="font-size: 11px; color: #64748b; margin-top: 2px;">Chờ Văn thư ban hành</span>
              </div>
            `;
          } else if (d.trang_thai === 'LANH_DAO_TRA_LAI') {
            actionsHtml = `
              <span class="badge" style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; font-size: 12px; font-weight: 600; border-radius: 20px; background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; box-shadow: 0 1px 2px rgba(185, 28, 28, 0.05); white-space: nowrap;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #ef4444; display: inline-block;"></span>
                <span>↩️ Đã yêu cầu chỉnh sửa</span>
              </span>
            `;
          } else if (d.trang_thai === 'DA_BAN_HANH') {
            actionsHtml = `
              <span class="badge" style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; font-size: 12px; font-weight: 600; border-radius: 20px; background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; box-shadow: 0 1px 2px rgba(4, 120, 87, 0.05); white-space: nowrap;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
                <span>✅ Đã ban hành</span>
              </span>
            `;
          } else {
            actionsHtml = `<span class="badge badge-secondary" style="font-size: 11.5px; padding: 4px 10px; border-radius: 20px;">${d.trang_thai || 'Đang xử lý'}</span>`;
          }

          return `
            <tr style="transition: background-color 0.15s ease;">
              <td style="vertical-align: middle; padding: 12px 16px;">${codeHtml}</td>
              <td style="vertical-align: middle; padding: 12px 16px;">${trichYeuHtml}</td>
              <td style="vertical-align: middle; padding: 12px 16px;">${loaiHtml}</td>
              <td style="vertical-align: middle; padding: 12px 16px;">${authorHtml}</td>
              <td style="vertical-align: middle; padding: 12px 16px;">${fileHtml}</td>
              <td style="vertical-align: middle; padding: 12px 16px;">${ngayGuiHtml}</td>
              <td style="vertical-align: middle; padding: 12px 16px; text-align: center;">${actionsHtml}</td>
            </tr>
          `;
        }).join('');

        // Gắn sự kiện các nút trên bảng
        tbody.querySelectorAll('.btn-sign').forEach(btn => {
          btn.addEventListener('click', () => {
            executeSign(btn.dataset.id, btn.dataset.title);
          });
        });

        tbody.querySelectorAll('.btn-reject').forEach(btn => {
          btn.addEventListener('click', () => {
            executeReject(btn.dataset.id);
          });
        });
      }

      searchInput.addEventListener('input', renderTable);
      reloadBtn.addEventListener('click', fetchData);

      fetchData();
    });
