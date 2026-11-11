document.addEventListener('DOMContentLoaded', async () => {
      const user = await window.AuthGuard.check();
      if (!user) return;

      const data = await window.thongKeService.getOverview();
      if (!data) return;

      // Cập nhật số liệu KPI tóm tắt nếu có
      if (data.summary) {
        if (document.getElementById('kpiTongVB')) document.getElementById('kpiTongVB').innerText = data.summary.tong_van_ban.toLocaleString();
        if (document.getElementById('kpiVbDen')) document.getElementById('kpiVbDen').innerText = data.summary.vb_den.toLocaleString();
        if (document.getElementById('kpiVbDi')) document.getElementById('kpiVbDi').innerText = data.summary.vb_di.toLocaleString();
        if (document.getElementById('kpiTyLeDungHan')) document.getElementById('kpiTyLeDungHan').innerText = `${data.summary.ty_le_dung_han}%`;
      }

      // Kiểm tra thư viện Chart.js đã sẵn sàng chưa
      if (typeof Chart === 'undefined') {
        console.warn('Thư viện Chart.js chưa sẵn sàng.');
        return;
      }

      // Font chung và tùy chọn bảng màu
      Chart.defaults.font.family = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
      Chart.defaults.color = "#64748b";

      // 1. Biểu đồ lưu lượng tháng (Bar kết hợp hiện đại)
      new Chart(document.getElementById('chartLuuLuong'), {
        type: 'bar',
        data: {
          labels: data.van_ban_theo_thang.labels,
          datasets: [
            {
              label: 'Văn bản đến',
              data: data.van_ban_theo_thang.vb_den,
              backgroundColor: '#0284c7',
              borderRadius: 6,
              barPercentage: 0.65,
              categoryPercentage: 0.75
            },
            {
              label: 'Văn bản đi',
              data: data.van_ban_theo_thang.vb_di,
              backgroundColor: '#10b981',
              borderRadius: 6,
              barPercentage: 0.65,
              categoryPercentage: 0.75
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
          plugins: {
            legend: {
              position: 'top',
              align: 'end',
              labels: {
                usePointStyle: true,
                pointStyle: 'circle',
                boxWidth: 8,
                boxHeight: 8,
                padding: 16,
                font: { size: 12, weight: '500' }
              }
            },
            tooltip: {
              backgroundColor: '#1e293b',
              titleFont: { size: 12.5, weight: '600' },
              bodyFont: { size: 12 },
              padding: 10,
              cornerRadius: 8
            }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { font: { size: 11.5 } }
            },
            y: {
              beginAtZero: true,
              grid: { color: '#f1f5f9', drawBorder: false },
              ticks: { font: { size: 11 }, precision: 0 }
            }
          }
        }
      });

      // 2. Biểu đồ Doughnut công việc (Tỷ lệ hoàn thành với Center Text)
      const pctValue = data.tinh_hinh_xu_ly_cong_viec.percent || '89%';
      new Chart(document.getElementById('chartCongViec'), {
        type: 'doughnut',
        data: {
          labels: data.tinh_hinh_xu_ly_cong_viec.labels,
          datasets: [{
            data: data.tinh_hinh_xu_ly_cong_viec.data,
            backgroundColor: ['#10b981', '#0284c7', '#f43f5e'],
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
                usePointStyle: true,
                pointStyle: 'circle',
                boxWidth: 8,
                boxHeight: 8,
                padding: 14,
                font: { size: 11.5, weight: '500' }
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
          id: 'centerTextTask',
          beforeDraw(chart) {
            const { width, height, ctx } = chart;
            ctx.restore();
            ctx.font = '700 24px system-ui, -apple-system, sans-serif';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#0f172a';
            const text = String(pctValue);
            const textX = Math.round((width - ctx.measureText(text).width) / 2);
            const textY = height / 2 - 10;
            ctx.fillText(text, textX, textY);

            ctx.font = '600 10.5px system-ui, -apple-system, sans-serif';
            ctx.fillStyle = '#64748b';
            const subText = 'ĐÚNG HẠN';
            const subX = Math.round((width - ctx.measureText(subText).width) / 2);
            const subY = height / 2 + 14;
            ctx.fillText(subText, subX, subY);
            ctx.save();
          }
        }]
      });

      // 3. Biểu đồ Doughnut phân bổ loại văn bản (Không bị cắt xén, có Center Text)
      new Chart(document.getElementById('chartLoaiVB'), {
        type: 'doughnut',
        data: {
          labels: data.co_cau_loai_van_ban.labels,
          datasets: [{
            data: data.co_cau_loai_van_ban.data,
            backgroundColor: ['#0284c7', '#6366f1', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'],
            borderWidth: 2,
            borderColor: '#ffffff',
            borderRadius: 4,
            hoverOffset: 5
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '62%',
          plugins: {
            legend: {
              position: 'right',
              labels: {
                usePointStyle: true,
                pointStyle: 'circle',
                boxWidth: 8,
                boxHeight: 8,
                padding: 12,
                font: { size: 11.5, weight: '500' }
              }
            },
            tooltip: {
              backgroundColor: '#1e293b',
              titleFont: { size: 12.5, weight: '600' },
              bodyFont: { size: 12 },
              padding: 10,
              cornerRadius: 8,
              callbacks: {
                label: function (ctx) {
                  return ` ${ctx.label}: ${ctx.raw}%`;
                }
              }
            }
          }
        },
        plugins: [{
          id: 'centerTextDocTypes',
          beforeDraw(chart) {
            const chartArea = chart.chartArea;
            if (!chartArea) return;
            const centerX = (chartArea.left + chartArea.right) / 2;
            const centerY = (chartArea.top + chartArea.bottom) / 2;
            const { ctx } = chart;
            ctx.restore();
            ctx.font = '700 18px system-ui, -apple-system, sans-serif';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#0f172a';
            const text = '100%';
            const textX = Math.round(centerX - (ctx.measureText(text).width / 2));
            const textY = centerY - 8;
            ctx.fillText(text, textX, textY);

            ctx.font = '600 10px system-ui, -apple-system, sans-serif';
            ctx.fillStyle = '#64748b';
            const subText = 'CƠ CẤU';
            const subX = Math.round(centerX - (ctx.measureText(subText).width / 2));
            const subY = centerY + 12;
            ctx.fillText(subText, subX, subY);
            ctx.save();
          }
        }]
      });

      // 4. Biểu đồ ngang phòng ban (Horizontal Bar thanh mảnh, bo tròn)
      new Chart(document.getElementById('chartPhongBan'), {
        type: 'bar',
        data: {
          labels: data.van_ban_theo_phong_ban.labels,
          datasets: [{
            label: 'Số văn bản phụ trách',
            data: data.van_ban_theo_phong_ban.data,
            backgroundColor: '#3b82f6',
            hoverBackgroundColor: '#2563eb',
            borderRadius: 6,
            barPercentage: 0.65,
            categoryPercentage: 0.8
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#1e293b',
              titleFont: { size: 12.5, weight: '600' },
              bodyFont: { size: 12 },
              padding: 10,
              cornerRadius: 8
            }
          },
          scales: {
            x: {
              beginAtZero: true,
              grid: { color: '#f1f5f9', drawBorder: false },
              ticks: { font: { size: 11 }, precision: 0 }
            },
            y: {
              grid: { display: false },
              ticks: { font: { size: 12, weight: '500' }, color: '#334155' }
            }
          }
        }
      });
    });
