/**
 * DU-LIEU-THONG-KE.JS - DỮ LIỆU BÁO CÁO THỐNG KÊ BIỂU ĐỒ (CHART.JS)
 * Tích hợp dữ liệu công việc thực tế từ /api/cong-viec/thong-ke
 */

(function (window) {
  const DEFAULT_THONG_KE = {
    summary: {
      tong_van_ban: 1285,
      vb_den: 742,
      vb_di: 543,
      ty_le_dung_han: 96.8
    },
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
      percent: '89.3%',
      labels: ['Đúng hạn (89.3%)', 'Đang xử lý (7.1%)', 'Quá hạn (3.6%)'],
      data: [25, 2, 1],
      colors: ['#10b981', '#0284c7', '#f43f5e']
    },
    van_ban_theo_phong_ban: {
      labels: ['GD Trung học', 'GD Tiểu học & MN', 'Kế hoạch - TC', 'Tổ chức cán bộ', 'Văn phòng Sở', 'Khảo thí & QLCL'],
      data: [28, 22, 19, 14, 12, 9]
    }
  };

  const thongKeService = {
    getOverview: async function () {
      const data = JSON.parse(JSON.stringify(DEFAULT_THONG_KE));
      try {
        if (window.api) {
          const cvRes = await window.api.get('/api/cong-viec/thong-ke');
          if (cvRes && cvRes.du_lieu) {
            const dl = cvRes.du_lieu;
            const st = dl.theo_trang_thai;
            const tong = dl.tong_so || 1;
            const tyLe = dl.ty_le_dung_han !== undefined ? dl.ty_le_dung_han : 89.3;
            const quaHan = st ? (st.QUA_HAN || 0) : 3;
            const dungHan = tong - quaHan;
            const dangXuLy = st ? (st.DANG_THUC_HIEN || 0) : 16;

            data.tinh_hinh_xu_ly_cong_viec = {
              percent: `${tyLe}%`,
              labels: [
                `Đúng hạn (${tyLe}%)`,
                `Đang thực hiện (${Math.round((dangXuLy / tong) * 100)}%)`,
                `Quá hạn (${Math.round((quaHan / tong) * 100)}%)`
              ],
              data: [dungHan, dangXuLy, quaHan],
              colors: ['#10b981', '#0284c7', '#f43f5e']
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
