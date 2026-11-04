/**
 * DU-LIEU-THONG-BAO.JS - DỮ LIỆU MẪU THÔNG BÁO ĐIỀU HÀNH NỘI BỘ
 */

(function (window) {
  const MOCK_THONG_BAO = [
    {
      id: 1,
      tieu_de: 'Thông báo lịch họp giao ban công tác tháng 11/2026 của Ban Giám đốc Sở',
      nguoi_gui: 'Văn phòng Sở GD&ĐT',
      thoi_gian: '2026-11-03 08:30',
      loai: 'Cuộc họp',
      muc_do: 'Quan trọng',
      da_doc: false,
      noi_dung: 'Kính mời Trưởng các Phòng chuyên môn dự buổi họp giao ban định kỳ vào lúc 08h00 ngày 06/11/2026 tại Hội trường A - Sở GD&ĐT Đà Nẵng. Các phòng chuẩn bị báo cáo tiến độ các đề án trọng điểm.'
    },
    {
      id: 2,
      tieu_de: 'Triển khai lịch bảo trì hệ thống máy chủ thư điện tử nội bộ cuối tuần',
      nguoi_gui: 'Tổ CNTT - Văn phòng Sở',
      thoi_gian: '2026-11-02 14:15',
      loai: 'Hệ thống',
      muc_do: 'Bình thường',
      da_doc: true,
      noi_dung: 'Hệ thống mail @danang.edu.vn sẽ tạm dừng phục vụ trong khoảng thời gian từ 22h00 thứ Bảy đến 04h00 Chủ nhật tuần này để nâng cấp đường truyền cáp quang.'
    },
    {
      id: 3,
      tieu_de: 'Chúc mừng đồng chí đạt danh hiệu Chiến sĩ thi đua cấp Thành phố',
      nguoi_gui: 'Hội đồng Thi đua - Khen thưởng Sở',
      thoi_gian: '2026-10-30 09:00',
      loai: 'Khen thưởng',
      muc_do: 'Bình thường',
      da_doc: true,
      noi_dung: 'Sở GD&ĐT chúc mừng 05 đồng chí cán bộ, chuyên viên các phòng ban đã vinh dự được Chủ tịch UBND TP. Đà Nẵng trao tặng danh hiệu thi đua xuất sắc năm học 2025-2026.'
    }
  ];

  const thongBaoService = {
    // TODO(nhóm): thay bằng api.get('/api/thong-bao')
    getAll: async function () {
      return [...MOCK_THONG_BAO];
    },

    // TODO(nhóm): thay bằng api.post(`/api/thong-bao/${id}/da-doc`)
    markAsRead: async function (id) {
      const tb = MOCK_THONG_BAO.find(t => t.id === parseInt(id));
      if (tb) tb.da_doc = true;
      return tb;
    }
  };

  window.thongBaoService = thongBaoService;
})(window);
