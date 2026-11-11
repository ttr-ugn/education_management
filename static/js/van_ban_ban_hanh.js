let currentPublishDocId = null;

    function closePublishModal() {
      document.getElementById('publishModal').style.display = 'none';
      currentPublishDocId = null;
    }

    async function openPublishModal(doc) {
      currentPublishDocId = doc.id;
      document.getElementById('modalTrichYeu').textContent = doc.trich_yeu;
      
      const type = doc.loai_van_ban;
      const vietTat = type === 'Kế hoạch' ? 'KH' : (type === 'Quyết định' ? 'QĐ' : 'VP');
      document.getElementById('modalSoKyHieu').value = `1225/SGDĐT-${vietTat}`;
      document.getElementById('modalNgayBanHanh').value = new Date().toISOString().split('T')[0];

      // Nạp danh mục hồ sơ để chọn
      const hoSoSelect = document.getElementById('modalHoSoSelect');
      hoSoSelect.innerHTML = '<option value="">-- Không lưu vào hồ sơ (để sau) --</option>';
      try {
        const hsRes = await window.api.get('/api/ho-so');
        if (hsRes && hsRes.du_lieu) {
          hsRes.du_lieu.forEach(hs => {
            const opt = document.createElement('option');
            opt.value = hs.ho_so_id || hs.id;
            opt.textContent = `${hs.ma_ho_so}: ${hs.tieu_de}`;
            hoSoSelect.appendChild(opt);
          });
        }
      } catch (e) {}

      document.getElementById('publishModal').style.display = 'flex';
    }

    document.addEventListener('DOMContentLoaded', async () => {
      const user = await window.AuthGuard.check({ requiredRoles: ['VAN_THU'] });
      if (!user) return;

      const tbody = document.getElementById('approvedDraftsTable');

      async function loadData() {
        try {
          tbody.innerHTML = '<tr><td colspan="5" class="text-center p-4 text-muted"><div class="spinner-border spinner-border-sm text-primary" role="status" style="margin-right: 6px;"></div>Đang tải danh sách...</td></tr>';
          
          const list = await window.vanBanDiService.getAll({ trang_thai: 'DA_KY_CHO_BAN_HANH' });
          if (!list || list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center p-4 text-muted">Không có văn bản nào đang chờ cấp số phát hành.</td></tr>';
            return;
          }

          tbody.innerHTML = list.map(d => {
            const docId = d.id || d.van_ban_id;
            const docData = JSON.stringify({ id: docId, trich_yeu: d.trich_yeu, loai_van_ban: d.loai_van_ban }).replace(/"/g, '&quot;');
            return `
            <tr style="transition: background-color 0.15s ease;">
              <td style="vertical-align: middle; padding: 12px 16px;">
                <div class="doc-code-pill" style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 6px; font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, Menlo, monospace; font-size: 12px; font-weight: 600; color: #0284c7; white-space: nowrap;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                  <span>${d.so_ky_hieu || 'Dự thảo'}</span>
                </div>
              </td>
              <td style="vertical-align: middle; padding: 12px 16px; max-width: 380px;">
                <div style="font-weight: 600; color: #0f172a; font-size: 13.5px; line-height: 1.45;">${d.trich_yeu}</div>
                <div style="font-size: 11.5px; color: #059669; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 2px 8px; border-radius: 4px; margin-top: 5px; display: inline-flex; align-items: center; gap: 4px;">
                  ✓ Đã phê duyệt bởi: ${d.lanh_dao_ky || 'Lãnh đạo Sở'}
                </div>
              </td>
              <td style="vertical-align: middle; padding: 12px 16px;">
                <span style="display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap;">
                  <span>🏛️</span>
                  <span>${d.lanh_dao_ky || 'Lãnh đạo Sở'}</span>
                </span>
              </td>
              <td style="vertical-align: middle; padding: 12px 16px;">
                <span style="font-weight: 600; color: #1e293b; font-size: 13px;">${d.don_vi_soan_thao || 'Văn phòng Sở'}</span>
              </td>
              <td style="vertical-align: middle; padding: 12px 16px; text-align: center;">
                <button class="btn btn-publish" data-doc="${docData}" style="display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 7px 14px; font-size: 12.5px; font-weight: 600; color: #ffffff; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border: none; border-radius: 6px; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.25); cursor: pointer; transition: all 0.15s ease; white-space: nowrap;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                  <span>Cấp số & Ban hành</span>
                </button>
              </td>
            </tr>
          `;
          }).join('');

          tbody.querySelectorAll('.btn-publish').forEach(btn => {
            btn.addEventListener('click', () => {
              const doc = JSON.parse(btn.dataset.doc);
              openPublishModal(doc);
            });
          });
        } catch (err) {
          console.error('Lỗi nạp dữ liệu văn bản chờ ban hành:', err);
          tbody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-danger">⚠️ Lỗi nạp dữ liệu: ${err.message}</td></tr>`;
        }
      }

      document.getElementById('btnConfirmPublish').addEventListener('click', async () => {
        if (!currentPublishDocId) return;
        const soKyHieu = document.getElementById('modalSoKyHieu').value.trim();
        const ngayBanHanh = document.getElementById('modalNgayBanHanh').value;
        const hoSoId = document.getElementById('modalHoSoSelect').value;

        if (!soKyHieu) {
          window.Toast.error('Vui lòng nhập số ký hiệu chính thức.');
          return;
        }

        try {
          await window.vanBanDiService.publish(currentPublishDocId, {
            so_ky_hieu: soKyHieu,
            ngay_ban_hanh: ngayBanHanh,
            ho_so_id: hoSoId ? parseInt(hoSoId) : null
          });
          window.Toast.success(`Đã ban hành văn bản chính thức với số: ${soKyHieu}!`);
          closePublishModal();
          loadData();
        } catch (err) {
          window.Toast.error(err.message || 'Lỗi ban hành văn bản');
        }
      });

      // Phím ESC đóng modal
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closePublishModal();
      });

      loadData();
    });
