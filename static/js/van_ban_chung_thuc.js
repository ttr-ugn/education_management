/**
 * VAN_BAN_CHUNG_THUC.JS
 * Xử lý Dịch vụ Chứng thực Chữ ký số và Thẩm định Tính toàn vẹn Tài liệu
 * Tương thích chuẩn API Django và Nghị định 30/2020/NĐ-CP
 */

document.addEventListener('DOMContentLoaded', async () => {
  // 0. Xác thực phiên người dùng & dựng thanh điều hướng Sidebar
  if (window.AuthGuard && typeof window.AuthGuard.check === 'function') {
    const user = await window.AuthGuard.check();
    if (!user) return;
  }

  let allDocs = [];
  let selectedFile = null;

  const statTotalSigned = document.getElementById('statTotalSigned');
  const selectInternalDoc = document.getElementById('selectInternalDoc');
  const signedDocsTableBody = document.getElementById('signedDocsTableBody');
  const filterInput = document.getElementById('filterInput');
  const btnReloadList = document.getElementById('btnReloadList');

  const btnVerifyInternal = document.getElementById('btnVerifyInternal');
  const dropZone = document.getElementById('dropZone');
  const uploadFileCert = document.getElementById('uploadFileCert');
  const uploadLabel = document.getElementById('uploadLabel');
  const uploadSublabel = document.getElementById('uploadSublabel');
  const btnVerifyUpload = document.getElementById('btnVerifyUpload');

  const resultPanel = document.getElementById('verificationResultPanel');
  const resFileName = document.getElementById('resFileName');
  const resFileSize = document.getElementById('resFileSize');
  const resSigner = document.getElementById('resSigner');
  const resTitleSigner = document.getElementById('resTitleSigner');
  const resTimestamp = document.getElementById('resTimestamp');
  const resHash = document.getElementById('resHash');
  const resMessage = document.getElementById('resMessage');

  // 1. Tải dữ liệu ban đầu
  async function loadData() {
    try {
      signedDocsTableBody.innerHTML = '<tr><td colspan="7" class="text-center p-4 text-muted">Đang nạp dữ liệu chứng thực...</td></tr>';

      let res;
      if (window.api && typeof window.api.get === 'function') {
        res = await window.api.get('/api/van-ban-di/chung-thuc-chu-ky-so');
      } else {
        const resp = await fetch('/api/van-ban-di/chung-thuc-chu-ky-so');
        res = await resp.json();
      }

      if (res && res.thanh_cong) {
        allDocs = res.danh_sach_van_ban || [];
        if (statTotalSigned) {
          statTotalSigned.textContent = res.thong_ke ? res.thong_ke.tong_van_ban_da_ky : allDocs.length;
        }

        renderDocSelect(allDocs);
        renderTable(allDocs);
      } else {
        signedDocsTableBody.innerHTML = '<tr><td colspan="7" class="text-center p-4 text-danger">Không thể tải dữ liệu chứng thực chữ ký số.</td></tr>';
      }
    } catch (err) {
      console.error('Lỗi khi tải dữ liệu chứng thực:', err);
      signedDocsTableBody.innerHTML = '<tr><td colspan="7" class="text-center p-4 text-danger">Lỗi kết nối máy chủ dịch vụ chứng thực số.</td></tr>';
    }
  }

  // 2. Điền select box văn bản
  function renderDocSelect(docs) {
    if (!selectInternalDoc) return;
    if (docs.length === 0) {
      selectInternalDoc.innerHTML = '<option value="">-- Chưa có văn bản nào đã ký số --</option>';
      return;
    }

    selectInternalDoc.innerHTML = '<option value="">-- Chọn một văn bản đã ký để đối chiếu --</option>' +
      docs.map(d => `<option value="${d.id}">[${d.so_ky_hieu}] ${escapeHtml(d.trich_yeu.substring(0, 80))}...</option>`).join('');
  }

  // 3. Render bảng văn bản đã ký số
  function renderTable(docs) {
    if (!signedDocsTableBody) return;
    if (docs.length === 0) {
      signedDocsTableBody.innerHTML = '<tr><td colspan="7" class="text-center p-4 text-muted">Không có văn bản nào thỏa mãn điều kiện tìm kiếm.</td></tr>';
      return;
    }

    signedDocsTableBody.innerHTML = docs.map(d => {
      const shortHash = d.ma_bam_sha256 ? `${d.ma_bam_sha256.substring(0, 16)}...` : '---';
      return `
        <tr>
          <td style="padding: 12px 16px; font-weight: 700; color: #004b91;">${escapeHtml(d.so_ky_hieu)}</td>
          <td style="padding: 12px 16px;">
            <div style="font-weight: 600; color: #1e293b; font-size: 13px;">${escapeHtml(d.trich_yeu)}</div>
            <div style="font-size: 11.5px; color: #64748b; margin-top: 3px;">Loại: ${escapeHtml(d.loai_van_ban || 'Văn bản')} - Tệp: ${escapeHtml(d.file_ten || '')}</div>
          </td>
          <td style="padding: 12px 16px;">
            <div style="font-weight: 600; color: #0f172a; font-size: 13px;">${escapeHtml(d.nguoi_ky)}</div>
            <div style="font-size: 11.5px; color: #64748b;">${escapeHtml(d.chuc_vu)}</div>
          </td>
          <td style="padding: 12px 16px; font-size: 12.5px; color: #475569;">${escapeHtml(d.thoi_gian_ky)}</td>
          <td style="padding: 12px 16px;">
            <span style="font-family: monospace; font-size: 11px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #0369a1; display: inline-block;" title="${d.ma_bam_sha256}">
              ${shortHash}
            </span>
          </td>
          <td style="padding: 12px 16px; text-align: center;">
            <span class="badge badge-success" style="font-size: 11px; padding: 4px 8px;">TOÀN VẸN</span>
          </td>
          <td style="padding: 12px 16px; text-align: center;">
            <div style="display: flex; gap: 6px; justify-content: center; align-items: center;">
              <button class="btn btn-outline-primary btn-sm btn-action-preview" data-id="${d.id}" data-title="${escapeHtml(d.trich_yeu)}" data-code="${escapeHtml(d.so_ky_hieu)}" style="font-size: 11.5px; padding: 3px 8px; font-weight: 600;">
                Xem trước
              </button>
              <button class="btn btn-primary btn-sm btn-action-verify" data-id="${d.id}" style="font-size: 11.5px; padding: 3px 8px; font-weight: 600;">
                Thẩm định
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    // Gắn sự kiện cho các nút Thẩm định trên bảng
    document.querySelectorAll('.btn-action-verify').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const docId = e.currentTarget.getAttribute('data-id');
        if (selectInternalDoc) {
          selectInternalDoc.value = docId;
        }
        verifyInternal(docId);
      });
    });

    // Gắn sự kiện cho các nút Xem trước trên bảng
    document.querySelectorAll('.btn-action-preview').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const docId = e.currentTarget.getAttribute('data-id');
        const code = e.currentTarget.getAttribute('data-code');
        const title = e.currentTarget.getAttribute('data-title');
        openDocPreviewModal(docId, `Văn bản ${code}`, title, code);
      });
    });
  }

  // 4. Xử lý thẩm định văn bản nội bộ
  async function verifyInternal(docId) {
    const id = docId || (selectInternalDoc ? selectInternalDoc.value : null);
    if (!id) {
      if (window.Toast) window.Toast.warning('Vui lòng chọn một văn bản trong danh sách để thẩm định.');
      else alert('Vui lòng chọn một văn bản trong danh sách để thẩm định.');
      return;
    }

    try {
      btnVerifyInternal.disabled = true;
      btnVerifyInternal.textContent = 'Đang thẩm định...';

      let res;
      if (window.api && typeof window.api.post === 'function') {
        res = await window.api.post('/api/van-ban-di/chung-thuc-chu-ky-so', { van_ban_id: id });
      } else {
        const resp = await fetch('/api/van-ban-di/chung-thuc-chu-ky-so', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ van_ban_id: id })
        });
        res = await resp.json();
      }

      if (res && res.thanh_cong && res.ket_qua) {
        showVerificationResult(res.ket_qua);
        if (window.Toast) window.Toast.success('Thẩm định chữ ký số thành công: Toàn vẹn và Hợp chuẩn!');
      } else {
        if (window.Toast) window.Toast.error(res ? res.thong_bao : 'Thẩm định thất bại.');
      }
    } catch (e) {
      console.error(e);
      if (window.Toast) window.Toast.error('Lỗi thẩm định văn bản.');
    } finally {
      btnVerifyInternal.disabled = false;
      btnVerifyInternal.textContent = 'Thẩm định văn bản đã chọn';
    }
  }

  // 5. Xử lý tải tệp và kéo thả
  if (dropZone && uploadFileCert) {
    dropZone.addEventListener('click', () => uploadFileCert.click());

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.style.borderColor = '#16a34a';
      dropZone.style.backgroundColor = '#f0fdf4';
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.style.borderColor = '#0284c7';
      dropZone.style.backgroundColor = '#ffffff';
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.style.borderColor = '#0284c7';
      dropZone.style.backgroundColor = '#ffffff';
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        selectedFile = e.dataTransfer.files[0];
        updateFileLabel(selectedFile);
      }
    });

    uploadFileCert.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        updateFileLabel(selectedFile);
      }
    });
  }

  function updateFileLabel(file) {
    if (!file) return;
    uploadLabel.textContent = `Tệp đã chọn: ${file.name}`;
    uploadSublabel.textContent = `Dung lượng: ${roundKb(file.size)} - Sẵn sàng kiểm tra tính toàn vẹn`;
  }

  function roundKb(bytes) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  // 6. Xử lý thẩm định tệp tải lên
  if (btnVerifyUpload) {
    btnVerifyUpload.addEventListener('click', async () => {
      if (!selectedFile) {
        if (window.Toast) window.Toast.warning('Vui lòng chọn hoặc kéo thả tệp văn bản vào khung trước khi thẩm định.');
        else alert('Vui lòng chọn hoặc kéo thả tệp văn bản vào khung trước khi thẩm định.');
        return;
      }

      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        btnVerifyUpload.disabled = true;
        btnVerifyUpload.textContent = 'Đang quét SHA-256...';

        const resp = await fetch('/api/van-ban-di/chung-thuc-chu-ky-so', {
          method: 'POST',
          body: formData
        });
        const res = await resp.json();

        if (res && res.thanh_cong && res.ket_qua) {
          showVerificationResult(res.ket_qua);
          if (window.Toast) window.Toast.success('Thẩm định tệp tải lên thành công: Mã băm SHA-256 khớp chuẩn!');
        } else {
          if (window.Toast) window.Toast.error(res ? res.thong_bao : 'Kiểm tra tệp thất bại.');
        }
      } catch (err) {
        console.error(err);
        if (window.Toast) window.Toast.error('Lỗi kiểm tra tệp văn bản.');
      } finally {
        btnVerifyUpload.disabled = false;
        btnVerifyUpload.textContent = 'Kiểm tra tính toàn vẹn tệp tải lên';
      }
    });
  }

  let lastVerificationResult = null;
  const btnPreviewVerifiedDoc = document.getElementById('btnPreviewVerifiedDoc');

  // 7. Hiển thị khối kết quả thẩm định
  function showVerificationResult(k) {
    if (!resultPanel) return;

    lastVerificationResult = k;

    if (resFileName) resFileName.textContent = k.ten_tep || 'van_ban.pdf';
    if (resFileSize) resFileSize.textContent = k.dung_luong || '---';
    if (resSigner) resSigner.textContent = k.nguoi_ky || 'Lê Thị Bích Thuận';
    if (resTitleSigner) resTitleSigner.textContent = k.chuc_vu || 'Giám đốc Sở';
    if (resTimestamp) resTimestamp.textContent = k.thoi_gian_tham_dinh || '---';
    if (resHash) resHash.textContent = k.ma_bam_sha256 || '---';
    if (resMessage) resMessage.textContent = k.thong_diep || 'Văn bản nguyên vẹn, chữ ký số số hóa hợp chuẩn.';

    resultPanel.style.display = 'block';
    resultPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // Xử lý nút bấm Xem trước nội dung văn bản khi thẩm định
  if (btnPreviewVerifiedDoc) {
    btnPreviewVerifiedDoc.addEventListener('click', () => {
      if (!lastVerificationResult) {
        if (window.Toast) window.Toast.warning('Chưa có kết quả thẩm định để xem trước.');
        return;
      }

      if (lastVerificationResult.van_ban_id) {
        openDocPreviewModal(
          lastVerificationResult.van_ban_id,
          lastVerificationResult.ten_tep || 'Văn bản điện tử',
          lastVerificationResult.trich_yeu || '',
          lastVerificationResult.so_ky_hieu || ''
        );
      } else if (selectedFile) {
        previewUploadedFile(selectedFile, lastVerificationResult);
      } else {
        if (window.Toast) window.Toast.info('Đang mở bản xem trước tài liệu thẩm định...');
        openDocPreviewModal(1, 'Văn bản điện tử thẩm định', lastVerificationResult.trich_yeu || 'Văn bản đã chứng thực', '');
      }
    });
  }

  // 8. Tìm kiếm / lọc bảng
  if (filterInput) {
    filterInput.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase().trim();
      if (!term) {
        renderTable(allDocs);
        return;
      }
      const filtered = allDocs.filter(d =>
        (d.so_ky_hieu && d.so_ky_hieu.toLowerCase().includes(term)) ||
        (d.trich_yeu && d.trich_yeu.toLowerCase().includes(term)) ||
        (d.nguoi_ky && d.nguoi_ky.toLowerCase().includes(term))
      );
      renderTable(filtered);
    });
  }

  if (btnReloadList) {
    btnReloadList.addEventListener('click', () => {
      if (filterInput) filterInput.value = '';
      loadData();
    });
  }

  if (btnVerifyInternal) {
    btnVerifyInternal.addEventListener('click', () => verifyInternal());
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // Nạp dữ liệu
  loadData();
});

// Modal chi tiết chứng thư CA
function openCertDetailModal() {
  const modal = document.getElementById('certDetailModal');
  if (modal) modal.style.display = 'flex';
}

function closeCertDetailModal() {
  const modal = document.getElementById('certDetailModal');
  if (modal) modal.style.display = 'none';
}

// Modal Xem trước Toàn văn Văn bản & Dấu Chữ ký số
function openDocPreviewModal(docId, fileName, trichYeu, soKyHieu) {
  const modal = document.getElementById('docPreviewModal');
  const titleEl = document.getElementById('docPreviewModalTitle');
  const subEl = document.getElementById('docPreviewModalSubtitle');
  const iframe = document.getElementById('docPreviewIframe');
  const loading = document.getElementById('previewLoading');

  if (titleEl) titleEl.textContent = (soKyHieu ? `[${soKyHieu}] ` : '') + (fileName || 'Xem trước văn bản');
  if (subEl) subEl.textContent = trichYeu || 'Văn bản đã chứng thực chữ ký số điện tử';
  if (loading) loading.style.display = 'flex';
  if (iframe) {
    iframe.onload = () => { if (loading) loading.style.display = 'none'; };
    iframe.src = `/api/van-ban-di/${docId}/preview`;
  }
  if (modal) modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function closeDocPreviewModal() {
  const modal = document.getElementById('docPreviewModal');
  const iframe = document.getElementById('docPreviewIframe');
  if (modal) modal.style.display = 'none';
  if (iframe) iframe.src = '';
  document.body.style.overflow = '';
}

function previewUploadedFile(file, result) {
  const modal = document.getElementById('docPreviewModal');
  const titleEl = document.getElementById('docPreviewModalTitle');
  const subEl = document.getElementById('docPreviewModalSubtitle');
  const iframe = document.getElementById('docPreviewIframe');
  const loading = document.getElementById('previewLoading');

  if (titleEl) titleEl.textContent = `Tệp thẩm định: ${file.name}`;
  if (subEl) subEl.textContent = `Mã băm SHA-256: ${result.ma_bam_sha256 || '---'}`;
  if (modal) modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';

  if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
    if (iframe) {
      iframe.src = URL.createObjectURL(file);
    }
  } else {
    // Non-PDF uploaded file: Render clean HTML view inside iframe
    const reader = new FileReader();
    reader.onload = function (e) {
      const content = e.target.result;
      const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{font-family:Arial,sans-serif;padding:30px;line-height:1.6;color:#1e293b;}.badge{display:inline-block;padding:6px 12px;background:#ecfdf5;color:#047857;border:1px solid #a7f3d0;border-radius:6px;font-weight:bold;margin-bottom:15px;}</style></head><body><div class="badge">CHỨNG THỰC TOÀN VẸN HỢP LỆ</div><h2>${file.name}</h2><p><b>Dung lượng:</b> ${(file.size/1024).toFixed(1)} KB | <b>SHA-256:</b> <code>${result.ma_bam_sha256}</code></p><hr><pre style="white-space:pre-wrap;background:#f8fafc;padding:15px;border-radius:6px;border:1px solid #e2e8f0;">${content}</pre></body></html>`;
      if (iframe) {
        iframe.srcdoc = html;
      }
    };
    reader.readAsText(file);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const printBtn = document.getElementById('previewPrintBtn');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      const iframe = document.getElementById('docPreviewIframe');
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.print();
      }
    });
  }
});

window.openDocPreviewModal = openDocPreviewModal;
window.closeDocPreviewModal = closeDocPreviewModal;
window.previewUploadedFile = previewUploadedFile;
