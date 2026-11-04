/**
 * DU-LIEU-THONG-KE.JS - DỮ LIỆU MẪU BÁO CÁO THỐNG KÊ BIỂU ĐỒ (CHART.JS)
 */

(function (window) {
  const MOCK_THONG_KE = {
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
      labels: ['Đúng hạn (82%)', 'Đang xử lý (12%)', 'Quá hạn (6%)'],
      data: [82, 12, 6],
      colors: ['#10b981', '#0284c7', '#ef4444']
    },
    van_ban_theo_phong_ban: {
      labels: ['GD Trung học', 'GD Tiểu học', 'Kế hoạch - TC', 'Tổ chức CB', 'Văn phòng Sở', 'Thanh tra'],
      data: [28, 22, 19, 14, 12, 8]
    }
  };

  const thongKeService = {
    // TODO(nhóm): thay bằng api.get('/api/thong-ke')
    getOverview: async function () {
      return JSON.parse(JSON.stringify(MOCK_THONG_KE));
    }
  };

  window.thongKeService = thongKeService;
})(window);
