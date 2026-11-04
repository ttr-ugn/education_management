/**
 * DU-LIEU-THONG-KE.JS - DỮ LIỆU BÁO CÁO THỐNG KÊ BIỂU ĐỒ (CHART.JS)
 * Tích hợp dữ liệu công việc thực tế từ /api/cong-viec/thong-ke
 */

(function (window) {
  const DEFAULT_THONG_KE = {
    van_ban_theo_thang: {
      labels: ['Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11'],
      vb_den: [45, 52, 38, 70, 85, 92, 24],
      vb_di:  [30, 42, 25, 55, 68, 74, 18]
    },
    co_cau_loai_van_ban: {
      labels: ['Công văn', 'Quyết định', 'Kế hoạch', 'Tờ trình', 'Thông báo', 'Báo cáo'],
      data: [42, 18, 15, 10, 8, 7]
    },
    tinh_hinh_xu_ly_cong_viec: {
      labels: ['Đúng hạn (75%)', 'Đang xử lý (15%)', 'Quá hạn (10%)'],
      data: [75, 15, 10],
      colors: ['#10b981', '#0284c7', '#ef4444']
    },
    van_ban_theo_phong_ban: {
      labels: ['GD Trung học', 'GD Tiểu học', 'Kế hoạch - TC', 'Tổ chức CB', 'Văn phòng Sở', 'Thanh tra'],
      data: [28, 22, 19, 14, 12, 8]
    }
  };

  const thongKeService = {
    getOverview: async function () {
      const data = JSON.parse(JSON.stringify(DEFAULT_THONG_KE));
      try {
        if (window.api) {
          const cvRes = await window.api.get('/api/cong-viec/thong-ke');
          if (cvRes && cvRes.du_lieu) {
            const st = cvRes.du_lieu.theo_trang_thai;
            const tong = cvRes.du_lieu.tong_so || 1;
            const pctDone = Math.round((st.HOAN_THANH / tong) * 100);
            const pctDoing = Math.round(((st.DANG_THUC_HIEN + st.CHO_DANH_GIA + st.CHUA_THUC_HIEN) / tong) * 100);
            const pctOver = Math.round((st.QUA_HAN / tong) * 100);

            data.tinh_hinh_xu_ly_cong_viec = {
              labels: [
                `Đúng hạn (${pctDone}%)`,
                `Đang xử lý (${pctDoing}%)`,
                `Quá hạn (${pctOver}%)`
              ],
              data: [st.HOAN_THANH, st.DANG_THUC_HIEN + st.CHO_DANH_GIA + st.CHUA_THUC_HIEN, st.QUA_HAN],
              colors: ['#10b981', '#0284c7', '#ef4444']
            };
          }
        }
      } catch (err) {
        console.warn('Không thể nạp thống kê công việc thời gian thực, dùng dữ liệu mặc định.');
      }
      return data;
    }
  };

  window.thongKeService = thongKeService;
})(window);
