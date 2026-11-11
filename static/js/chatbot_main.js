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

      // Các phần tử modal kho lưu trữ
      const repoModal = document.getElementById('repoModal');
      const btnOpenRepo = document.getElementById('btnOpenRepo');
      const btnCloseRepo = document.getElementById('btnCloseRepo');
      const repoGrid = document.getElementById('repoGrid');
      const repoSearchInput = document.getElementById('repoSearchInput');
      const repoTypeSelect = document.getElementById('repoTypeSelect');
      const repoFieldSelect = document.getElementById('repoFieldSelect');
      const btnRefreshRepo = document.getElementById('btnRefreshRepo');

      let currentZoom = 1.0;
      let currentLoadedMau = null;

      // Hàm lấy class màu cho loại văn bản
      function getBadgeClass(loai) {
        switch (loai) {
          case 'Tờ trình': return 'badge-to-trinh';
          case 'Quyết định': return 'badge-quyet-dinh';
          case 'Công văn': return 'badge-cong-van';
          case 'Kế hoạch': return 'badge-ke-hoach';
          case 'Thông báo': return 'badge-thong-bao';
          case 'Biên bản': return 'badge-bien-ban';
          case 'Báo cáo': return 'badge-bao-cao';
          default: return 'badge-cong-van';
        }
      }

      // Render danh sách card mẫu văn bản trong khung chat
      function renderTemplateCards(templates) {
        if (!templates || templates.length === 0) return '';

        let html = '<div class="template-card-deck">';
        templates.forEach(t => {
          const badgeClass = getBadgeClass(t.loai_van_ban);
          const downloadUrl = `/api/chatbot/mau-van-ban/${t.mau_id}/tai-ve`;

          html += `
            <div class="template-card">
              <div>
                <div class="template-card-header">
                  <span class="template-badge ${badgeClass}">${t.loai_van_ban}</span>
                  <span class="template-code">${t.ma_mau}</span>
                </div>
                <div class="template-title">${t.ten_mau}</div>
                <div class="template-field">📂 ${t.linh_vuc} | ✍️ ${t.tham_quyen_ky || 'Lãnh đạo Sở'}</div>
                <div class="template-desc">${t.mo_ta || ''}</div>
              </div>
              <div class="template-actions">
                <button type="button" class="btn-preview" onclick="window.showPreviewModal(${t.mau_id})">
                  <span>👁️ Xem trước (Preview)</span>
                </button>
                <a href="${downloadUrl}" class="btn-download-doc" download title="Tải file Word mẫu">
                  <span>📥 Tải Word (.doc)</span>
                </a>
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

        let content = isUser ? text : `<b>${sender}:</b><br>${text}`;
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
          html += `<button class="chip-btn" data-query="${c}">${c}</button>`;
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
            appendMessage('Trợ lý ảo', res.cau_tra_loi, false, res.mau_de_xuat);
            if (res.goi_y_tiep_theo) {
              updateQuickChips(res.goi_y_tiep_theo);
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
      window.showPreviewModal = async function(mauId) {
        printableArea.innerHTML = '<div style="text-align:center; padding: 40px; color: #64748b;">Đang tải nội dung văn bản...</div>';
        previewModalTitle.textContent = 'Đang tải...';
        previewModal.classList.add('active');
        currentZoom = 1.0;
        printableArea.style.transform = `scale(${currentZoom})`;

        try {
          const res = await window.api.get(`/api/chatbot/mau-van-ban/${mauId}`);
          if (res.thanh_cong && res.mau) {
            currentLoadedMau = res.mau;
            previewModalTitle.textContent = `${res.mau.ma_mau} - ${res.mau.ten_mau}`;
            printableArea.innerHTML = res.mau.noi_dung_html;
            btnDownloadFromPreview.href = `/api/chatbot/mau-van-ban/${mauId}/tai-ve`;
          } else {
            printableArea.innerHTML = '<div style="color:red; text-align:center; padding: 30px;">Không thể tải dữ liệu mẫu văn bản này.</div>';
          }
        } catch (err) {
          printableArea.innerHTML = `<div style="color:red; text-align:center; padding: 30px;">Lỗi: ${err.message}</div>`;
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
        printableArea.style.transform = `scale(1.0)`;
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
      // XỬ LÝ KHÁM PHÁ TOÀN BỘ KHO LƯU TRỮ (MODAL REPO)
      // ===================================================================
      async function loadRepository() {
        repoGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">Đang tải danh sách biểu mẫu...</div>';

        const keyword = repoSearchInput.value.trim();
        const loai = repoTypeSelect.value;
        const linh_vuc = repoFieldSelect.value;

        try {
          const res = await window.api.get('/api/chatbot/kho-mau', { keyword, loai, linh_vuc });
          if (res.thanh_cong) {
            renderRepoGrid(res.danh_sach_mau);
          } else {
            repoGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: red;">${res.thong_bao}</div>`;
          }
        } catch (err) {
          repoGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: red;">Lỗi tải kho mẫu: ${err.message}</div>`;
        }
      }

      function renderRepoGrid(list) {
        if (!list || list.length === 0) {
          repoGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">Không tìm thấy mẫu văn bản nào phù hợp với bộ lọc.</div>';
          return;
        }

        let html = '';
        list.forEach(t => {
          const badgeClass = getBadgeClass(t.loai_van_ban);
          const downloadUrl = `/api/chatbot/mau-van-ban/${t.mau_id}/tai-ve`;

          html += `
            <div class="template-card">
              <div>
                <div class="template-card-header">
                  <span class="template-badge ${badgeClass}">${t.loai_van_ban}</span>
                  <span class="template-code">${t.ma_mau}</span>
                </div>
                <div class="template-title">${t.ten_mau}</div>
                <div class="template-field">📂 ${t.linh_vuc} | ✍️ ${t.tham_quyen_ky || 'Lãnh đạo Sở'}</div>
                <div class="template-desc">${t.mo_ta || ''}</div>
              </div>
              <div class="template-actions">
                <button type="button" class="btn-preview" onclick="window.showPreviewModal(${t.mau_id})">
                  <span>👁️ Xem trước</span>
                </button>
                <a href="${downloadUrl}" class="btn-download-doc" download title="Tải file Word mẫu">
                  <span>📥 Tải Word</span>
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
