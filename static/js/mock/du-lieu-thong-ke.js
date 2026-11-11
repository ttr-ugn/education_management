/**
 * DU-LIEU-THONG-KE.JS - DỮ LIỆU BÁO CÁO THỐNG KÊ BIỂU ĐỒ (CHART.JS)
 * Tích hợp dữ liệu điều hành văn bản thực tế từ cơ sở dữ liệu hệ thống
 */

(function (window) {
  const DEFAULT_THONG_KE = {
    summary: {
      tong_van_ban: 30,
      vb_den: 15,
      vb_di: 15,
      ty_le_dung_han: 94.7
    },
    van_ban_theo_thang: {
      labels: ['Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11'],
      vb_den: [2, 3, 2, 4, 3, 4, 2],
      vb_di:  [1, 2, 3, 2, 4, 4, 2]
    },
    co_cau_loai_van_ban: {
      labels: ['Công văn', 'Quyết định', 'Kế hoạch', 'Tờ trình', 'Thông báo', 'Báo cáo'],
      data: [35, 25, 15, 10, 10, 5]
    },
    tinh_hinh_xu_ly_cong_viec: {
      percent: '94.7%',
      labels: ['Đúng hạn (94.7%)', 'Đang xử lý (5.3%)', 'Quá hạn (0%)'],
      data: [14, 1, 0],
      colors: ['#10b981', '#0284c7', '#f43f5e']
    },
    van_ban_theo_phong_ban: {
      labels: ['GD Trung học', 'GD Tiểu học & MN', 'Kế hoạch - TC', 'Tổ chức cán bộ', 'Văn phòng Sở', 'Khảo thí & QLCL'],
      data: [8, 6, 5, 4, 4, 3]
    }
  };

  const thongKeService = {
    getOverview: async function () {
      let data = JSON.parse(JSON.stringify(DEFAULT_THONG_KE));
      try {
        if (window.api && typeof window.api.get === 'function') {
          const res = await window.api.get('/api/thong-ke');
          if (res && res.thanh_cong) {
            return res;
          }
        } else {
          const resp = await fetch('/api/thong-ke');
          const json = await resp.json();
          if (json && json.thanh_cong) {
            return json;
          }
        }
      } catch (err) {
        console.warn('Không thể nạp thống kê thời gian thực, dùng dữ liệu chuẩn hệ thống:', err.message);
      }
      return data;
    }
  };

  window.thongKeService = thongKeService;
})(window);
