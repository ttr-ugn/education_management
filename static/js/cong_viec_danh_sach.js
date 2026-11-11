document.addEventListener('DOMContentLoaded', async () => {

      const user = await window.AuthGuard.check();

      if (!user) return;



      const role = user.vai_tro;

      const isSpecialist = role === 'CHUYEN_VIEN';

      const isLeader = role === 'LANH_DAO';

      const isClerk = role === 'VAN_THU';



      const btnGiaoViec = document.getElementById('btnGiaoViec');

      const btnBaoCao = document.getElementById('btnBaoCao');

      const btnNghiemThu = document.getElementById('btnNghiemThu');



      // Điều chỉnh giao diện theo phân quyền chuẩn:

      if (isLeader) {

        document.getElementById('pageSubtitle').innerText = 'Theo dõi tiến độ thực hiện công việc của các phòng ban trực thuộc Sở';

        if (btnGiaoViec) btnGiaoViec.style.display = 'none';

        if (btnBaoCao) btnBaoCao.style.display = 'none';

        if (btnNghiemThu) btnNghiemThu.style.display = 'none';

      } else if (isSpecialist) {

        document.getElementById('pageSubtitle').innerText = 'Danh sách nhiệm vụ cá nhân được phân công và báo cáo tiến độ';

        document.getElementById('chartRoleScope').innerText = 'Việc cá nhân';

        if (btnGiaoViec) btnGiaoViec.style.display = 'none';

        if (btnNghiemThu) btnNghiemThu.style.display = 'none';

        if (btnBaoCao) btnBaoCao.style.display = 'inline-flex';

      } else if (isClerk) {

        document.getElementById('pageSubtitle').innerText = 'Quản lý giao nhiệm vụ và điều hành công việc cơ quan';

        if (btnGiaoViec) btnGiaoViec.style.display = 'inline-flex';

        if (btnNghiemThu) btnNghiemThu.style.display = 'inline-flex';

        if (btnBaoCao) btnBaoCao.style.display = 'none';

      }



      const tbody = document.getElementById('congViecTableBody');

      const searchInput = document.getElementById('searchInput');

      const filterStatus = document.getElementById('filterStatus');

      const filterPriority = document.getElementById('filterPriority');

      const reloadBtn = document.getElementById('reloadBtn');



      let doughnutChart = null;

      let barChart = null;



      const STATUS_LABELS = {
        'DANG_THUC_HIEN': '<span class="badge" style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">⚙️ Đang thực hiện</span>',
        'CHO_DANH_GIA': '<span class="badge" style="background: #fef3c7; color: #b45309; border: 1px solid #fde68a; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">⏳ Chờ nghiệm thu</span>',
        'HOAN_THANH': '<span class="badge" style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">✅ Đã hoàn thành</span>',
        'QUA_HAN': '<span class="badge" style="background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; animation: pulse 2s infinite;">⚠️ Quá hạn</span>',
        'CHUA_THUC_HIEN': '<span class="badge" style="background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">⏸️ Chưa thực hiện</span>'
      };

      const PRIORITY_LABELS = {
        'KHAN_CAP': '<span class="badge" style="background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; padding: 3px 8px; border-radius: 20px; font-weight: 700; font-size: 11px; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">🔥 Khẩn cấp</span>',
        'KHAM_CAP': '<span class="badge" style="background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; padding: 3px 8px; border-radius: 20px; font-weight: 700; font-size: 11px; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">🔥 Khẩn cấp</span>',
        'Khẩn cấp': '<span class="badge" style="background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; padding: 3px 8px; border-radius: 20px; font-weight: 700; font-size: 11px; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">🔥 Khẩn cấp</span>',
        'CAO': '<span class="badge" style="background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; padding: 3px 8px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">⚡ Cao</span>',
        'Cao': '<span class="badge" style="background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; padding: 3px 8px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">⚡ Cao</span>',
        'TRUNG_BINH': '<span class="badge" style="background: #fef3c7; color: #b45309; border: 1px solid #fde68a; padding: 3px 8px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">🟡 Trung bình</span>',
        'Trung bình': '<span class="badge" style="background: #fef3c7; color: #b45309; border: 1px solid #fde68a; padding: 3px 8px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">🟡 Trung bình</span>',
        'THAP': '<span class="badge" style="background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; padding: 3px 8px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">⚪ Thấp</span>',
        'Thấp': '<span class="badge" style="background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; padding: 3px 8px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">⚪ Thấp</span>'
      };

      // Tải và vẽ Biểu đồ & KPI
      async function loadStatistics() {
        try {
          const stats = await window.congViecService.getStatistics();
          if (!stats) return;

          document.getElementById('statTongSo').innerText = stats.tong_so || 0;
          document.getElementById('statDangLam').innerText = stats.theo_trang_thai?.DANG_THUC_HIEN || 0;
          document.getElementById('statChoDuyet').innerText = stats.theo_trang_thai?.CHO_DANH_GIA || 0;
          document.getElementById('statQuaHan').innerText = stats.theo_trang_thai?.QUA_HAN || 0;
          const elHoanThanh = document.getElementById('statHoanThanh');
          if (elHoanThanh) {
            elHoanThanh.innerText = stats.theo_trang_thai?.HOAN_THANH ?? stats.da_hoan_thanh ?? 0;
          } else if (document.getElementById('statTyLeDungHan')) {
            document.getElementById('statTyLeDungHan').innerText = `${stats.ty_le_dung_han !== undefined ? stats.ty_le_dung_han : 0}%`;
          }

          // Render Biểu đồ tròn (Doughnut) hiện đại
          if (typeof Chart !== 'undefined' && stats.chart_doughnut && stats.chart_doughnut.labels) {
            const ctxDoughnut = document.getElementById('statusDoughnutChart').getContext('2d');
            if (doughnutChart) doughnutChart.destroy();
            doughnutChart = new Chart(ctxDoughnut, {
              type: 'doughnut',
              data: {
                labels: stats.chart_doughnut.labels,
                datasets: [{
                  data: stats.chart_doughnut.data,
                  backgroundColor: ['#0284c7', '#f59e0b', '#10b981', '#f43f5e', '#94a3b8'],
                  borderWidth: 3,
                  borderColor: '#ffffff',
                  borderRadius: 6,
                  hoverOffset: 6
                }]
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                  legend: {
                    position: 'bottom',
                    labels: {
                      boxWidth: 10,
                      boxHeight: 10,
                      usePointStyle: true,
                      pointStyle: 'circle',
                      font: { size: 11.5, weight: '500' },
                      padding: 12
                    }
                  },
                  tooltip: {
                    backgroundColor: '#1e293b',
                    titleFont: { size: 12.5, weight: '600' },
                    bodyFont: { size: 12 },
                    padding: 10,
                    cornerRadius: 8
                  }
                }
              },
              plugins: [{
                id: 'centerText',
                beforeDraw(chart) {
                  const { width, height, ctx } = chart;
                  ctx.restore();
                  ctx.font = '700 24px system-ui, -apple-system, sans-serif';
                  ctx.textBaseline = 'middle';
                  ctx.fillStyle = '#0f172a';
                  const text = String(stats.tong_so || 0);
                  const textX = Math.round((width - ctx.measureText(text).width) / 2);
                  const textY = height / 2 - 10;
                  ctx.fillText(text, textX, textY);

                  ctx.font = '600 10.5px system-ui, -apple-system, sans-serif';
                  ctx.fillStyle = '#64748b';
                  const subText = 'NHIỆM VỤ';
                  const subX = Math.round((width - ctx.measureText(subText).width) / 2);
                  const subY = height / 2 + 14;
                  ctx.fillText(subText, subX, subY);
                  ctx.save();
                }
              }]
            });
          }

          // Render Biểu đồ cột (Bar) hiện đại
          if (typeof Chart !== 'undefined' && stats.chart_bar && stats.chart_bar.labels) {
            const ctxBar = document.getElementById('deptBarChart').getContext('2d');
            if (barChart) barChart.destroy();
            barChart = new Chart(ctxBar, {
              type: 'bar',
              data: {
                labels: stats.chart_bar.labels,
                datasets: [
                  {
                    label: 'Được giao',
                    data: stats.chart_bar.duoc_giao,
                    backgroundColor: '#3b82f6',
                    borderRadius: 6,
                    barPercentage: 0.7,
                    categoryPercentage: 0.8
                  },
                  {
                    label: 'Đã xong',
                    data: stats.chart_bar.da_xong,
                    backgroundColor: '#10b981',
                    borderRadius: 6,
                    barPercentage: 0.7,
                    categoryPercentage: 0.8
                  },
                  {
                    label: 'Trễ hạn',
                    data: stats.chart_bar.qua_han,
                    backgroundColor: '#f43f5e',
                    borderRadius: 6,
                    barPercentage: 0.7,
                    categoryPercentage: 0.8
                  }
                ]
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                  mode: 'index',
                  intersect: false
                },
                scales: {
                  x: {
                    grid: { display: false },
                    ticks: {
                      font: { size: 11.5, weight: '500' },
                      color: '#475569',
                      maxRotation: 0,
                      minRotation: 0
                    }
                  },
                  y: {
                    beginAtZero: true,
                    grid: {
                      color: '#f1f5f9',
                      drawBorder: false
                    },
                    ticks: {
                      precision: 0,
                      font: { size: 11 },
                      color: '#64748b'
                    }
                  }
                },
                plugins: {
                  legend: {
                    position: 'bottom',
                    labels: {
                      boxWidth: 10,
                      boxHeight: 10,
                      usePointStyle: true,
                      pointStyle: 'circle',
                      font: { size: 11.5, weight: '500' },
                      padding: 14
                    }
                  },
                  tooltip: {
                    backgroundColor: '#1e293b',
                    titleFont: { size: 12.5, weight: '600' },
                    bodyFont: { size: 12 },
                    padding: 10,
                    cornerRadius: 8
                  }
                }
              }
            });
          }
        } catch (err) {
          console.error('Lỗi khi tải biểu đồ thống kê:', err);
        }
      }

      // Tải bảng danh sách
      async function loadData() {
        const filters = {
          q: searchInput.value.trim(),
          trang_thai: filterStatus.value,
          do_uu_tien: filterPriority.value
        };
        const list = await window.congViecService.getAll(filters);

        if (!list || list.length === 0) {
          tbody.innerHTML = '<tr><td colspan="10" class="text-center p-4 text-muted">Không tìm thấy công việc nào phù hợp.</td></tr>';
          return;
        }

        tbody.innerHTML = list.map((item, index) => {
          // 1. Văn bản liên kết dạng pill monospace
          const docHtml = item.so_ky_hieu_vb ? `
            <div style="min-width: 175px; max-width: 220px;">
              <div style="display: inline-flex; align-items: center; gap: 5px; padding: 3px 8px; background: #f0f7ff; border: 1px solid #bae6fd; border-radius: 6px; font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; font-size: 11.5px; font-weight: 600; color: #0284c7;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                <span>${item.so_ky_hieu_vb}</span>
              </div>
              <div style="font-size: 11px; color: #64748b; margin-top: 3px; line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${(item.trich_yeu_vb || '').replace(/"/g, '&quot;')}">
                ${item.trich_yeu_vb || 'Văn bản chỉ đạo giao ban'}
              </div>
            </div>
          ` : `
            <span style="display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 11.5px; color: #64748b;">
              <span>📌</span>
              <span>Chỉ đạo trực tiếp</span>
            </span>
          `;

          // 2. Chip Lãnh đạo giao việc
          const leaderName = item.nguoi_giao || item.nguoi_giao_ten || 'Lãnh đạo Sở';
          const leaderHtml = `
            <span style="display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap;">
              <span>🏛️</span>
              <span>${leaderName}</span>
            </span>
          `;

          // 3. Avatar chip Cán bộ xử lý (Đồng bộ sổ văn bản đi)
          const officer = (item.nguoi_xu_ly || item.nguoi_xu_ly_ten || 'Cán bộ').trim();
          const words = officer.split(/\s+/).filter(Boolean);
          const initials = words.length >= 2
            ? (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase()
            : officer.slice(0, 2).toUpperCase();
          const deptName = item.phong_ban || 'Văn phòng Sở';

          const officerHtml = `
            <div class="user-chip" style="display: flex; align-items: center; gap: 10px; min-width: 175px;">
              <div class="user-chip-avatar" style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: 700; font-size: 11.5px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 1px 3px rgba(2, 132, 199, 0.3);">
                ${initials}
              </div>
              <div>
                <div class="user-chip-name" style="font-weight: 600; color: #1e293b; font-size: 13px; line-height: 1.25;">${officer}</div>
                <div class="user-chip-dept" style="font-size: 11px; color: #64748b; margin-top: 2px;">${deptName}</div>
              </div>
            </div>
          `;

          // 4. Hạn chót có icon lịch
          const isOverdue = item.trang_thai === 'QUA_HAN';
          const deadlineHtml = `
            <div style="white-space: nowrap;">
              <span style="display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; color: ${isOverdue ? '#dc2626' : '#334155'}; ${isOverdue ? 'background: #fef2f2; border: 1px solid #fecaca; padding: 2px 7px; border-radius: 4px;' : ''}">
                <span>📅</span>
                <span>${item.han_hoan_thanh || '---'}</span>
              </span>
              ${isOverdue ? '<div style="font-size: 10.5px; color: #dc2626; font-weight: 600; margin-top: 2px;">Quá hạn!</div>' : ''}
            </div>
          `;

          // 5. Thanh tiến độ hiện đại
          const progressVal = item.tien_do || 0;
          const progressColor = progressVal >= 100 ? '#10b981' : (isOverdue ? '#f43f5e' : '#0284c7');
          const progressGradient = progressVal >= 100 
            ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)' 
            : (isOverdue ? 'linear-gradient(90deg, #f43f5e 0%, #e11d48 100%)' : 'linear-gradient(90deg, #0284c7 0%, #0ea5e9 100%)');
          
          const progressHtml = `
            <div style="min-width: 95px;">
              <div style="font-size: 12px; margin-bottom: 3px; font-weight: 700; color: ${progressColor}; display: flex; justify-content: space-between; align-items: center;">
                <span>${progressVal}%</span>
                ${progressVal >= 100 ? '<span style="font-size: 10px; color: #10b981;">Xong</span>' : ''}
              </div>
              <div style="width: 100%; height: 7px; background-color: #f1f5f9; border-radius: 4px; overflow: hidden; border: 1px solid #e2e8f0;">
                <div style="width: ${progressVal}%; height: 100%; background: ${progressGradient}; border-radius: 4px; transition: width 0.3s ease;"></div>
              </div>
            </div>
          `;

          // 6. Tên nhiệm vụ / Mô tả
          const taskTitleHtml = `
            <div style="max-width: 270px;">
              <a href="javascript:void(0)" onclick="viewTaskDetail(${item.id})" style="color: #0f172a; font-weight: 600; font-size: 13.5px; line-height: 1.45; text-decoration: none; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${(item.ten_cong_viec || '').replace(/"/g, '&quot;')}">
                ${item.ten_cong_viec}
              </a>
              <div style="font-size: 11.5px; color: #64748b; margin-top: 3px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden;" title="${(item.noi_dung || '').replace(/"/g, '&quot;')}">
                ${item.noi_dung || ''}
              </div>
            </div>
          `;

          // 7. Thao tác / Chi tiết
          const actionHtml = `
            <div class="d-flex justify-content-center gap-1">
              <button type="button" class="btn btn-outline-primary btn-sm" onclick="viewTaskDetail(${item.id})" title="Xem chi tiết & Căn cứ văn bản" style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; font-weight: 600; font-size: 12px; border-radius: 6px;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <span>Xem</span>
              </button>
              ${isSpecialist ? `
                <a href="../van-ban-di/soan-thao.html?cong_viec_id=${item.id}&ten_cong_viec=${encodeURIComponent(item.ten_cong_viec)}" class="btn btn-outline-success btn-sm" title="Soạn văn bản xử lý nhiệm vụ này" style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; font-weight: 600; font-size: 12px; border-radius: 6px;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                  <span>Soạn VB</span>
                </a>
              ` : ''}
            </div>
          `;

          return `
            <tr style="transition: background-color 0.15s ease;">
              <td style="vertical-align: middle; text-align: center; font-weight: 600; color: #64748b; font-size: 12px;">${index + 1}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${taskTitleHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${docHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${leaderHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${officerHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${deadlineHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${PRIORITY_LABELS[item.do_uu_tien] || item.do_uu_tien}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${progressHtml}</td>
              <td style="vertical-align: middle; padding: 12px 14px;">${STATUS_LABELS[item.trang_thai] || item.trang_thai}</td>
              <td style="vertical-align: middle; padding: 12px 14px; text-align: center;">${actionHtml}</td>
            </tr>
          `;
        }).join('');
      }

      // Xử lý modal chi tiết

      window.viewTaskDetail = async function (id) {

        try {

          const task = await window.congViecService.getById(id);

          if (!task) return;



          document.getElementById('modalTaskTitle').innerText = task.ten_cong_viec;

          document.getElementById('modalDocNumber').innerText = task.so_ky_hieu_vb ? `Số ký hiệu: ${task.so_ky_hieu_vb}` : 'Không có số hiệu văn bản';

          document.getElementById('modalDocSummary').innerText = task.trich_yeu_vb || 'Căn cứ nhiệm vụ theo chỉ đạo nội bộ';

          document.getElementById('modalDocDate').innerText = task.ngay_van_ban ? `Ngày văn bản: ${task.ngay_van_ban}` : '';

          document.getElementById('modalAssigner').innerText = task.nguoi_giao || 'Lãnh đạo';

          document.getElementById('modalAssignee').innerText = `${task.nguoi_xu_ly} (${task.phong_ban})`;

          document.getElementById('modalDept').innerText = task.phong_ban;

          document.getElementById('modalDeadline').innerText = task.han_hoan_thanh;

          document.getElementById('modalPriority').innerHTML = PRIORITY_LABELS[task.do_uu_tien] || task.do_uu_tien;

          document.getElementById('modalStatus').innerHTML = STATUS_LABELS[task.trang_thai] || task.trang_thai;

          document.getElementById('modalContent').innerText = task.noi_dung || 'Không có mô tả chi tiết.';

          document.getElementById('modalResult').innerText = task.ket_qua_bao_cao || 'Chưa nộp báo cáo kết quả.';



          const feedbackBox = document.getElementById('modalFeedbackBox');

          if (task.danh_gia_lanh_dao) {

            feedbackBox.style.display = 'block';

            document.getElementById('modalFeedback').innerText = task.danh_gia_lanh_dao;

          } else {

            feedbackBox.style.display = 'none';

          }



          // Lịch sử tiến độ

          const timelineEl = document.getElementById('modalTimeline');

          if (task.nhat_ky && task.nhat_ky.length > 0) {

            timelineEl.innerHTML = task.nhat_ky.map(log => `

              <div class="timeline-item">

                <div style="font-size: 11.5px; color: #64748b;">${log.thoi_gian} - <b>${log.nguoi_cap_nhat_ten || 'Cán bộ'}</b></div>

                <div style="font-size: 13px; margin-top: 2px;">${log.noi_dung_ghi_chu}</div>

                <div style="font-size: 11.5px; color: #0284c7; font-weight: 600;">Tiến độ ghi nhận: ${log.tien_do_moi}%</div>

              </div>

            `).join('');

          } else {

            timelineEl.innerHTML = '<div style="font-size: 12.5px; color: #94a3b8;">Chưa có cập nhật tiến độ nào.</div>';

          }



          const btnDraft = document.getElementById('btnTaskActionDraft');

          if (btnDraft) {

            if (role === 'CHUYEN_VIEN') {

              btnDraft.style.display = 'inline-flex';

              btnDraft.href = `../van-ban-di/soan-thao.html?cong_viec_id=${task.id}&ten_cong_viec=${encodeURIComponent(task.ten_cong_viec)}&noi_dung=${encodeURIComponent(task.noi_dung || '')}&so_vb=${encodeURIComponent(task.so_ky_hieu_vb || '')}`;

            } else {

              btnDraft.style.display = 'none';

            }

          }



          document.getElementById('detailModal').style.display = 'flex';

        } catch (e) {

          window.Toast.error('Không thể tải chi tiết công việc.');

        }

      };



      const closeModal = () => { document.getElementById('detailModal').style.display = 'none'; };

      document.getElementById('closeModalBtn').addEventListener('click', closeModal);

      document.getElementById('closeModalBtn2').addEventListener('click', closeModal);



      searchInput.addEventListener('input', loadData);

      filterStatus.addEventListener('change', loadData);

      filterPriority.addEventListener('change', loadData);

      reloadBtn.addEventListener('click', () => {

        loadStatistics();

        loadData();

      });



            // Khởi tạo ban đầu
      try { await loadStatistics(); } catch (e) { console.error('Init stat error:', e); }
      try { await loadData(); } catch (e) { console.error('Init data error:', e); }
    });
