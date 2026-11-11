let currentHsId = 1;
    let currentUserRole = 'CAN_BO';
    let isDossierClosed = false;
    let selectedAddDoc = null;

    function openPreviewModal(url, soKyHieu, trichYeu) {
      const modal = document.getElementById('previewModal');
      const title = document.getElementById('previewModalTitle');
      const subtitle = document.getElementById('previewModalSubtitle');
      const iframe = document.getElementById('previewIframe');
      const downloadBtn = document.getElementById('previewDownloadBtn');
      const loader = document.getElementById('previewLoading');

      title.textContent = soKyHieu || 'Xem trước văn bản';
      subtitle.textContent = trichYeu || '';
      downloadBtn.href = url;
      loader.style.display = 'flex';
      iframe.src = url;
      modal.style.display = 'flex';
    }

    function onPreviewLoaded() {
      const loader = document.getElementById('previewLoading');
      if (loader) loader.style.display = 'none';
    }

    function closePreviewModal() {
      const modal = document.getElementById('previewModal');
      const iframe = document.getElementById('previewIframe');
      iframe.src = '';
      modal.style.display = 'none';
    }

    function printPreviewFrame() {
      const iframe = document.getElementById('previewIframe');
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      }
    }

    function openAddDocModal() {
      const modal = document.getElementById('modalAddDoc');
      const loading = document.getElementById('availableDocsLoading');
      const listEl = document.getElementById('availableDocsList');
      const confirmBtn = document.getElementById('btnConfirmAddDoc');

      selectedAddDoc = null;
      confirmBtn.disabled = true;
      loading.style.display = 'block';
      listEl.style.display = 'none';
      listEl.innerHTML = '';
      modal.style.display = 'flex';

      window.hoSoService.getAvailableVanBan(currentHsId).then(docs => {
        loading.style.display = 'none';
        if (!docs || docs.length === 0) {
          listEl.innerHTML = '<div style="padding: 24px; text-align: center; color: #64748b;">Hiện không có văn bản đã ban hành nào khả dụng để bổ sung.</div>';
          listEl.style.display = 'flex';
          return;
        }

        listEl.innerHTML = docs.map(d => `
          <div class="doc-choice-item" data-id="${d.van_ban_id}" data-source="${d.nguon}">
            <input type="radio" name="docChoice" value="${d.van_ban_id}" style="margin-top: 3px;">
            <div style="flex: 1;">
              <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <strong style="color: #003366; font-size: 14px;">${d.so_ky_hieu}</strong>
                <span style="font-size: 12px; color: #64748b;">${d.ngay_ban_hanh || '2026-11-04'}</span>
              </div>
              <div style="font-size: 13px; font-weight: 500; margin: 3px 0; color: #1e293b;">
                ${d.trich_yeu}
              </div>
              <div style="font-size: 12px; color: #64748b;">
                Người ký: <b>${d.nguoi_ky}</b> | Đơn vị: ${d.don_vi_soan_thao}
              </div>
            </div>
          </div>
        `).join('');

        listEl.style.display = 'flex';

        listEl.querySelectorAll('.doc-choice-item').forEach(item => {
          item.addEventListener('click', () => {
            listEl.querySelectorAll('.doc-choice-item').forEach(x => x.classList.remove('selected'));
            item.classList.add('selected');
            const radio = item.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
            selectedAddDoc = {
              id: item.dataset.id,
              nguon: item.dataset.source
            };
            confirmBtn.disabled = false;
          });
        });
      }).catch(err => {
        loading.style.display = 'none';
        listEl.innerHTML = `<div style="color: #ef4444; padding: 12px;">Lỗi: ${err.message}</div>`;
        listEl.style.display = 'flex';
      });
    }

    function closeAddDocModal() {
      document.getElementById('modalAddDoc').style.display = 'none';
      selectedAddDoc = null;
    }

    async function reloadDossierDocuments() {
      const tbody = document.getElementById('vbHoSoTableBody');
      const badgeCount = document.getElementById('hsSoLuongVB');
      tbody.innerHTML = '<tr><td colspan="7" class="text-center p-4 text-muted">Đang cập nhật danh sách...</td></tr>';

      try {
        const docs = await window.hoSoService.getVanBanInHoSo(currentHsId);
        badgeCount.textContent = `${docs.length} VB`;

        if (docs.length === 0) {
          tbody.innerHTML = '<tr><td colspan="7" class="text-center p-4 text-muted">Chưa có văn bản nào trong hồ sơ lưu trữ này. Bấm <b>"+ Thêm văn bản vào hồ sơ"</b> để bổ sung.</td></tr>';
          return;
        }

        tbody.innerHTML = docs.map((d, idx) => {
          const stt = String(idx + 1).padStart(2, '0');
          const canDelete = (currentUserRole !== 'LANH_DAO' && !isDossierClosed);
          const previewBtn = `
            <button class="btn btn-outline-primary btn-sm btn-doc-preview" 
                    data-url="${d.preview_url}" 
                    data-so="${d.so_ky_hieu}" 
                    data-trich="${encodeURIComponent(d.trich_yeu)}"
                    style="padding: 2px 8px; font-size: 11.5px; border-radius: 4px; display: inline-flex; align-items: center; gap: 3px;" 
                    title="Xem nội dung trực tiếp">
              👁 ${d.tep_dinh_kem || 'Xem file'}
            </button>
          `;

          const deleteBtn = canDelete ? `
            <button class="btn btn-outline-danger btn-sm btn-doc-delete" 
                    data-id="${d.van_ban_id}" 
                    data-nguon="${d.nguon}"
                    style="padding: 2px 7px; font-size: 11.5px;" 
                    title="Gỡ văn bản khỏi hồ sơ">
              🗑 Gỡ
            </button>
          ` : '<span class="text-muted" style="font-size: 11.5px;">-</span>';

          return `
            <tr>
              <td style="text-align: center; font-weight: 600; color: #64748b;">${stt}</td>
              <td><strong style="color: #003366;">${d.so_ky_hieu}</strong></td>
              <td><small>${d.ngay_ban_hanh}</small></td>
              <td style="max-width: 320px;">
                <div style="font-weight: 500; line-height: 1.4;">${d.trich_yeu}</div>
              </td>
              <td>
                <div style="font-weight: 500;">${d.nguoi_ky}</div>
                <small class="text-muted">${d.don_vi_soan_thao}</small>
              </td>
              <td>
                <div style="display: flex; flex-direction: column; gap: 4px; align-items: flex-start;">
                  ${previewBtn}
                  <a href="${d.download_url}" download style="font-size: 11px; color: #64748b; text-decoration: none;">📥 Tải về máy</a>
                </div>
              </td>
              <td style="text-align: center;">${deleteBtn}</td>
            </tr>
          `;
        }).join('');

        // Gắn sự kiện xem trước
        tbody.querySelectorAll('.btn-doc-preview').forEach(btn => {
          btn.addEventListener('click', () => {
            const url = btn.dataset.url;
            const so = btn.dataset.so;
            const trich = decodeURIComponent(btn.dataset.trich);
            openPreviewModal(url, so, trich);
          });
        });

        // Gắn sự kiện xóa
        tbody.querySelectorAll('.btn-doc-delete').forEach(btn => {
          btn.addEventListener('click', async () => {
            const vbId = btn.dataset.id;
            const nguon = btn.dataset.nguon;
            if (confirm('Đồng chí có chắc chắn muốn gỡ văn bản này ra khỏi hồ sơ lưu trữ?')) {
              try {
                await window.hoSoService.removeVanBan(currentHsId, vbId, nguon);
                window.Toast.success('Đã gỡ văn bản khỏi hồ sơ thành công!');
                reloadDossierDocuments();
              } catch (err) {
                window.Toast.error(err.message || 'Lỗi gỡ văn bản');
              }
            }
          });
        });

      } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center p-4 text-danger">Lỗi tải văn bản: ${err.message}</td></tr>`;
      }
    }

    document.addEventListener('DOMContentLoaded', async () => {
      const user = await window.AuthGuard.check();
      if (!user) return;
      currentUserRole = user.vai_tro;

      if (user.vai_tro === 'LANH_DAO') {
        const btnNop = document.getElementById('btnNopLuuTru');
        if (btnNop) btnNop.style.display = 'none';
        const btnAdd = document.getElementById('btnAddDocToHs');
        if (btnAdd) btnAdd.style.display = 'none';
      }

      const urlParams = new URLSearchParams(window.location.search);
      currentHsId = parseInt(urlParams.get('id') || '1');

      // Sự kiện nút Thêm văn bản
      const btnAdd = document.getElementById('btnAddDocToHs');
      if (btnAdd) {
        btnAdd.addEventListener('click', openAddDocModal);
      }

      const btnConfirmAdd = document.getElementById('btnConfirmAddDoc');
      if (btnConfirmAdd) {
        btnConfirmAdd.addEventListener('click', async () => {
          if (!selectedAddDoc) return;
          try {
            await window.hoSoService.addVanBan(currentHsId, selectedAddDoc.id, selectedAddDoc.nguon);
            window.Toast.success('Đã bổ sung văn bản vào hồ sơ thành công!');
            closeAddDocModal();
            reloadDossierDocuments();
          } catch (err) {
            window.Toast.error(err.message || 'Lỗi bổ sung văn bản');
          }
        });
      }

      try {
        const hs = await window.hoSoService.getById(currentHsId);
        if (!hs) {
          window.Toast.error('Không tìm thấy hồ sơ lưu trữ.');
          return;
        }

        document.getElementById('hsTitle').textContent = hs.tieu_de;
        document.getElementById('hsMa').textContent = `Mã hồ sơ: ${hs.ma_ho_so}`;
        document.getElementById('hsDonVi').textContent = hs.don_vi || 'Sở GD&ĐT';
        document.getElementById('hsNguoiLap').textContent = hs.nguoi_lap || 'Cán bộ';
        document.getElementById('hsNam').textContent = hs.nam_tai_lieu || '2026';
        document.getElementById('hsThoiHan').textContent = hs.thoi_han_bao_quan || 'Vĩnh viễn';

        const isNop = (hs.tinh_trang === 'DA_NOP_LUU_TRU' || hs.tinh_trang === 'DA_LUU_TRU');
        isDossierClosed = (hs.tinh_trang === 'DA_DONG');

        document.getElementById('hsStatus').textContent = isNop ? 'Đã nộp lưu trữ' : (isDossierClosed ? 'Đã đóng' : 'Đang thu thập');
        document.getElementById('hsStatus').className = isNop ? 'badge badge-success' : (isDossierClosed ? 'badge badge-secondary' : 'badge badge-warning');
        document.getElementById('hsMoTa').textContent = hs.mo_ta || 'Không có ghi chú thêm.';

        const btnNopLuuTru = document.getElementById('btnNopLuuTru');
        if ((isNop || isDossierClosed) && btnNopLuuTru) {
          btnNopLuuTru.style.display = 'none';
        }
        if (isDossierClosed && btnAdd) {
          btnAdd.style.display = 'none';
        }

        if (btnNopLuuTru) {
          btnNopLuuTru.addEventListener('click', async () => {
            if (confirm('Đồng chí có chắc chắn muốn đóng hồ sơ và nộp vào Kho lưu trữ cơ quan Sở GD&ĐT?')) {
              try {
                await window.hoSoService.submitToArchive(currentHsId);
                window.Toast.success('Đã nộp hồ sơ vào Kho lưu trữ cơ quan thành công!');
                document.getElementById('hsStatus').textContent = 'Đã nộp lưu trữ';
                document.getElementById('hsStatus').className = 'badge badge-success';
                btnNopLuuTru.style.display = 'none';
              } catch (err) {
                window.Toast.error(err.message || 'Lỗi khi nộp lưu trữ');
              }
            }
          });
        }

        // Tải danh sách văn bản thực tế
        await reloadDossierDocuments();

      } catch (err) {
        window.Toast.error(err.message || 'Lỗi nạp chi tiết hồ sơ');
      }

      // Đóng modal bằng phím ESC
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          closePreviewModal();
          closeAddDocModal();
        }
      });
    });
