document.addEventListener('DOMContentLoaded', async () => {
      // 1. Kiểm tra xác thực cán bộ/chuyên viên
      const user = await window.AuthGuard.check();
      if (!user) return;

      const chatMessages = document.getElementById('chatMessages');
      const chatForm = document.getElementById('chatForm');
      const chatInput = document.getElementById('chatInput');
      const btnSend = document.getElementById('btnSend');

      // Các phần tử modal xem trước
      const previewModal = document.getElementById('previewModal');
      const btnClosePreview = document.getElementById('btnClosePreview');
      const printableArea = document.getElementById('printableArea');
      const previewModalTitle = document.getElementById('previewModalTitle');
      const btnDownloadFromPreview = document.getElementById('btnDownloadFromPreview');
      const btnCopyContent = document.getElementById('btnCopyContent');
      const btnPrintDoc = document.getElementById('btnPrintDoc');
      const btnZoomIn = document.getElementById('btnZoomIn');
      const btnZoomOut = document.getElementById('btnZoomOut');
      const btnZoomReset = document.getElementById('btnZoomReset');

      // Các phần tử modal kho lưu trữ & tải lên
      const repoModal = document.getElementById('repoModal');
      const btnOpenRepo = document.getElementById('btnOpenRepo');
      const btnCloseRepo = document.getElementById('btnCloseRepo');
      const repoGrid = document.getElementById('repoGrid');
      const repoSearchInput = document.getElementById('repoSearchInput');
      const repoTypeSelect = document.getElementById('repoTypeSelect');
      const repoFieldSelect = document.getElementById('repoFieldSelect');
      const btnRefreshRepo = document.getElementById('btnRefreshRepo');
      const uploadRepoInput = document.getElementById('uploadRepoInput');
      const repoCountBtn = document.getElementById('repoCountBtn');

      let currentZoom = 1.0;
      let currentLoadedMau = null;

      function escapeHtml(str) {
        if (str === null || str === undefined) return '';
        return String(str)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#39;');
      }

      function formatBotText(text) {
        return escapeHtml(text)
          .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
          .replace(/\*(.+?)\*/g, '<i>$1</i>')
          .replace(/\n/g, '<br>');
      }

      // Hàm lấy class màu cho loại văn bản
      function getBadgeClass(loai) {
        switch (loai) {
          case 'Tờ trình': return 'badge-to-trinh';
          case 'Quyết định': return 'badge-quyet-dinh';
          case 'Nghị định': return 'badge-nghi-dinh';
          case 'Thông tư': return 'badge-thong-tu';
          case 'Công văn': return 'badge-cong-van';
          case 'Kế hoạch': return 'badge-ke-hoach';
          case 'Thông báo': return 'badge-thong-bao';
          case 'Biên bản': return 'badge-bien-ban';
          case 'Báo cáo': return 'badge-bao-cao';
          case 'Văn bản điều hành': return 'badge-cong-van';
          default: return 'badge-cong-van';
        }
      }

      // Render danh sách card mẫu văn bản / tài liệu trong khung chat
      function renderTemplateCards(templates) {
        if (!templates || templates.length === 0) return '';

        let html = '<div class="template-card-deck">';
        templates.forEach(t => {
          const badgeClass = getBadgeClass(t.loai_van_ban);
          const loaiTep = t.loai_tep || 'mau';
          const isMau = (loaiTep === 'mau' || loaiTep === 'mau_van_ban');
          const downloadUrl = `/api/chatbot/mau-van-ban/${t.mau_id}/tai-ve`;

          html += `
            <div class="template-card" style="cursor: pointer;" onclick="if (!event.target.closest('a, button')) window.showPreviewModal(${Number(t.mau_id)}, '${escapeHtml(loaiTep)}')" title="Nhấn vào thẻ để xem trước file">
              <div>
                <div class="template-card-header">
                  <span class="template-badge ${badgeClass}">${escapeHtml(t.loai_van_ban)}</span>
                  <span class="template-code">${escapeHtml(t.ma_mau || '')}</span>
                </div>
                <div class="template-title">${escapeHtml(t.ten_mau)}</div>
                <div class="template-field">${escapeHtml(t.linh_vuc || 'Sở GD&ĐT')} | ${escapeHtml(t.tham_quyen_ky || 'Lãnh đạo Sở')}</div>
                <div class="template-desc">${escapeHtml(t.mo_ta || '')}</div>
              </div>
              <div class="template-actions">
                <button type="button" class="btn-preview" onclick="event.stopPropagation(); window.showPreviewModal(${Number(t.mau_id)}, '${escapeHtml(loaiTep)}')">
                  <span>Xem trước (Preview)</span>
                </button>
                ${isMau ? `
                <a href="${downloadUrl}" class="btn-download-doc" download title="Tải file Word mẫu" onclick="event.stopPropagation();">
                  <span>Tải Word (.doc)</span>
                </a>` : ''}
              </div>
            </div>
          `;
        });
        html += '</div>';
        return html;
      }

      // Thêm tin nhắn vào khung chat
      function appendMessage(sender, text, isUser = false, templates = []) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${isUser ? 'bubble-user' : 'bubble-bot'}`;

        let content = isUser ? escapeHtml(text) : `<b>${escapeHtml(sender)}:</b><br>${formatBotText(text)}`;
        if (templates && templates.length > 0) {
          content += renderTemplateCards(templates);
        }

        bubble.innerHTML = content;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }

      // Cập nhật thanh câu hỏi gợi ý nhanh tiếp theo
      function updateQuickChips(chips) {
        if (!chips || chips.length === 0) return;
        const container = document.getElementById('quickChips');
        let html = `
          <span class="chip-label">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            Gợi ý tiếp theo:
          </span>
        `;
        chips.forEach(c => {
          html += `<button class="chip-btn" data-query="${escapeHtml(c)}">${escapeHtml(c)}</button>`;
        });
        container.innerHTML = html;
        attachChipEvents();
      }

      // Gửi câu hỏi đến Backend API `/api/chatbot`
      async function handleSend(text) {
        if (!text || !text.trim()) return;

        appendMessage('Bạn', text, true);
        chatInput.value = '';
        btnSend.disabled = true;

        // Trạng thái đang soạn
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'chat-bubble bubble-bot';
        typingIndicator.id = 'typingIndicator';
        typingIndicator.innerHTML = '<i>Trợ lý ảo đang tra cứu kho lưu trữ biểu mẫu Sở GD&ĐT...</i>';
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
          const res = await window.api.post('/api/chatbot', { message: text });
          const indicator = document.getElementById('typingIndicator');
          if (indicator) indicator.remove();

          if (res.thanh_cong) {
            const data = res.du_lieu || res;
            const answer = data.cau_tra_loi || data.tra_loi || res.cau_tra_loi || res.tra_loi || '';
            const templates = data.mau_de_xuat || res.mau_de_xuat || [];
            appendMessage('Trợ lý ảo', answer, false, templates);
            const chips = data.goi_y_tiep_theo || res.goi_y_tiep_theo;
            if (chips && chips.length > 0) {
              updateQuickChips(chips);
            }
          } else {
            appendMessage('Trợ lý ảo', res.thong_bao || 'Rất tiếc, đã có lỗi xảy ra.', false);
          }
        } catch (err) {
          const indicator = document.getElementById('typingIndicator');
          if (indicator) indicator.remove();
          appendMessage('Trợ lý ảo', `Không thể kết nối đến máy chủ: ${err.message}`, false);
          if (window.Toast) window.Toast.error('Lỗi kết nối máy chủ');
        } finally {
          btnSend.disabled = false;
          chatInput.focus();
        }
      }

      // ===================================================================
      // XỬ LÝ XEM TRƯỚC VĂN BẢN (MODAL PREVIEW A4)
      // ===================================================================
      window.showPreviewModal = async function(itemId, loaiTep = 'mau') {
        printableArea.innerHTML = '<div style="text-align:center; padding: 40px; color: #64748b;">Đang tải bản xem trước văn bản...</div>';
        previewModalTitle.textContent = 'Đang tải...';
        previewModal.classList.add('active');
        currentZoom = 1.0;
        printableArea.style.transform = 'scale(1)';
        btnZoomReset.textContent = '100%';
        const modalBody = previewModal.querySelector('.preview-modal-body');
        if (modalBody) modalBody.scrollTop = 0;

        try {
          let res;
          if (loaiTep && loaiTep !== 'mau' && loaiTep !== 'mau_van_ban') {
            res = await window.api.get(`/api/chatbot/xem-truoc/${loaiTep}/${itemId}`);
            if (res.thanh_cong) {
              previewModalTitle.textContent = res.tieu_de || 'Xem trước văn bản';
              printableArea.innerHTML = res.noi_dung_html;
              if (res.download_url) {
                btnDownloadFromPreview.href = res.download_url;
                btnDownloadFromPreview.style.display = 'inline-flex';
              } else {
                btnDownloadFromPreview.style.display = 'none';
              }
              currentLoadedMau = { noi_dung_text: printableArea.innerText };
              return;
            }
          }

          res = await window.api.get(`/api/chatbot/mau-van-ban/${itemId}`);
          if (res.thanh_cong && (res.mau || res.du_lieu)) {
            const mau = res.mau || res.du_lieu;
            currentLoadedMau = mau;
            previewModalTitle.textContent = `${mau.ma_mau} - ${mau.ten_mau}`;
            printableArea.innerHTML = mau.noi_dung_html;
            btnDownloadFromPreview.href = `/api/chatbot/mau-van-ban/${itemId}/tai-ve`;
            btnDownloadFromPreview.style.display = 'inline-flex';
          } else {
            printableArea.innerHTML = '<div style="color:red; text-align:center; padding: 30px;">Không thể tải dữ liệu mẫu văn bản này.</div>';
          }
        } catch (err) {
          printableArea.innerHTML = `<div style="color:red; text-align:center; padding: 30px;">Lỗi: ${escapeHtml(err.message)}</div>`;
        }
      };

      function closePreviewModal() {
        previewModal.classList.remove('active');
        printableArea.innerHTML = '';
        currentLoadedMau = null;
      }

      btnClosePreview.addEventListener('click', closePreviewModal);
      previewModal.addEventListener('click', (e) => {
        if (e.target === previewModal) closePreviewModal();
      });

      // Thu phóng văn bản
      btnZoomIn.addEventListener('click', () => {
        if (currentZoom < 1.4) {
          currentZoom += 0.1;
          printableArea.style.transform = `scale(${currentZoom})`;
          btnZoomReset.textContent = `${Math.round(currentZoom * 100)}%`;
        }
      });
      btnZoomOut.addEventListener('click', () => {
        if (currentZoom > 0.6) {
          currentZoom -= 0.1;
          printableArea.style.transform = `scale(${currentZoom})`;
          btnZoomReset.textContent = `${Math.round(currentZoom * 100)}%`;
        }
      });
      btnZoomReset.addEventListener('click', () => {
        currentZoom = 1.0;
        printableArea.style.transform = 'scale(1.0)';
        btnZoomReset.textContent = '100%';
      });

      // In văn bản trực tiếp
      btnPrintDoc.addEventListener('click', () => {
        window.print();
      });

      // Sao chép nội dung text
      btnCopyContent.addEventListener('click', () => {
        if (!currentLoadedMau) return;
        const textToCopy = currentLoadedMau.noi_dung_text || printableArea.innerText;
        navigator.clipboard.writeText(textToCopy).then(() => {
          if (window.Toast) window.Toast.success('Đã sao chép toàn bộ nội dung văn bản vào Clipboard!');
        }).catch(() => {
          if (window.Toast) window.Toast.warning('Không thể tự động sao chép, vui lòng bôi đen văn bản.');
        });
      });

      // ===================================================================
      // XỬ LÝ TẢI LÊN VĂN BẢN VÀO KHO LƯU TRỮ (/api/chatbot/upload)
      // ===================================================================
      if (uploadRepoInput) {
        uploadRepoInput.addEventListener('change', async (e) => {
          const files = e.target.files;
          if (!files || files.length === 0) return;

          const formData = new FormData();
          for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
          }

          if (window.Toast) window.Toast.info(`Đang đọc và nạp ${files.length} tệp vào kho lưu trữ...`);

          try {
            const res = await window.api.post('/api/chatbot/upload', formData);
            if (res.thanh_cong) {
              if (window.Toast) window.Toast.success(res.thong_bao);
              if (repoCountBtn && typeof res.tong_so === 'number') {
                repoCountBtn.textContent = `Kho lưu trữ văn bản (${res.tong_so})`;
              }
              if (repoModal.classList.contains('active')) {
                loadRepository();
              }
              const uploadedDocs = res.du_lieu || [];
              if (uploadedDocs.length > 0) {
                appendMessage(
                  'Trợ lý ảo',
                  `Tôi đã tiếp nhận và trích xuất nội dung **${uploadedDocs.length} tài liệu mới** vào kho lưu trữ để phục vụ tra cứu AI. Đồng chí có thể nhấn vào tài liệu bên dưới để xem trước ngay:`,
                  false,
                  uploadedDocs
                );
              }
            } else {
              if (window.Toast) window.Toast.error(res.thong_bao || 'Không thể tải tệp lên kho lưu trữ.');
            }
          } catch (err) {
            if (window.Toast) window.Toast.error('Lỗi tải tệp: ' + err.message);
          } finally {
            uploadRepoInput.value = '';
          }
        });
      }

      // ===================================================================
      // XỬ LÝ KHÁM PHÁ TOÀN BỘ KHO LƯU TRỮ (MODAL REPO)
      // ===================================================================
      async function loadRepository() {
        repoGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">Đang tải danh sách văn bản & biểu mẫu...</div>';

        const keyword = repoSearchInput.value.trim();
        const loai = repoTypeSelect.value;
        const linh_vuc = repoFieldSelect.value;

        try {
          const res = await window.api.get('/api/chatbot/kho-mau', { keyword, loai, linh_vuc });
          if (res.thanh_cong) {
            renderRepoGrid(res.danh_sach_mau);
            if (!keyword && !loai && !linh_vuc && repoCountBtn && typeof res.tong_so === 'number') {
              repoCountBtn.textContent = `Kho lưu trữ văn bản (${res.tong_so})`;
            }
          } else {
            repoGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: red;">${escapeHtml(res.thong_bao)}</div>`;
          }
        } catch (err) {
          repoGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: red;">Lỗi tải kho mẫu: ${escapeHtml(err.message)}</div>`;
        }
      }

      function renderRepoGrid(list) {
        if (!list || list.length === 0) {
          repoGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">Không tìm thấy văn bản nào phù hợp với bộ lọc.</div>';
          return;
        }

        let html = '';
        list.forEach(t => {
          const badgeClass = getBadgeClass(t.loai_van_ban);
          const downloadUrl = `/api/chatbot/mau-van-ban/${t.mau_id}/tai-ve`;

          html += `
            <div class="template-card" style="cursor: pointer;" onclick="if (!event.target.closest('a, button')) window.showPreviewModal(${Number(t.mau_id)}, 'mau')" title="Nhấn vào thẻ để xem trước file">
              <div>
                <div class="template-card-header">
                  <span class="template-badge ${badgeClass}">${escapeHtml(t.loai_van_ban)}</span>
                  <span class="template-code">${escapeHtml(t.ma_mau)}</span>
                </div>
                <div class="template-title">${escapeHtml(t.ten_mau)}</div>
                <div class="template-field">${escapeHtml(t.linh_vuc)} | ${escapeHtml(t.tham_quyen_ky || 'Lãnh đạo Sở')}</div>
                <div class="template-desc">${escapeHtml(t.mo_ta || '')}</div>
              </div>
              <div class="template-actions">
                <button type="button" class="btn-preview" onclick="event.stopPropagation(); window.showPreviewModal(${Number(t.mau_id)}, 'mau')">
                  <span>Xem trước</span>
                </button>
                <a href="${downloadUrl}" class="btn-download-doc" download title="Tải file Word mẫu" onclick="event.stopPropagation();">
                  <span>Tải Word</span>
                </a>
              </div>
            </div>
          `;
        });
        repoGrid.innerHTML = html;
      }

      btnOpenRepo.addEventListener('click', () => {
        repoModal.classList.add('active');
        loadRepository();
      });

      btnCloseRepo.addEventListener('click', () => {
        repoModal.classList.remove('active');
      });

      repoModal.addEventListener('click', (e) => {
        if (e.target === repoModal) repoModal.classList.remove('active');
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          if (previewModal.classList.contains('active')) {
            closePreviewModal();
          } else if (repoModal.classList.contains('active')) {
            repoModal.classList.remove('active');
          }
        }
      });

      repoSearchInput.addEventListener('input', () => {
        clearTimeout(window._searchTimer);
        window._searchTimer = setTimeout(loadRepository, 300);
      });
      repoTypeSelect.addEventListener('change', loadRepository);
      repoFieldSelect.addEventListener('change', loadRepository);
      btnRefreshRepo.addEventListener('click', loadRepository);

      // Submit chat form
      chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSend(chatInput.value);
      });

      function attachChipEvents() {
        document.querySelectorAll('.chip-btn').forEach(btn => {
          btn.onclick = () => {
            const query = btn.dataset.query;
            if (query === 'Xem toàn bộ kho mẫu văn bản') {
              btnOpenRepo.click();
            } else {
              handleSend(query);
            }
          };
        });
      }

      attachChipEvents();
    });
