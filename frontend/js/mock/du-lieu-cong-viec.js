/**
 * DU-LIEU-CONG-VIEC.JS - DỮ LIỆU MẪU QUẢN LÝ GIAO VIỆC & XỬ LÝ NHIỆM VỤ
 * 
 * TODO(nhóm): Sau khi thành viên nhánh feature/cong-viec hoàn thiện API,
 * thay các hàm trong congViecService bằng api.get / api.post tương ứng.
 */

(function (window) {
  const MOCK_CONG_VIEC = [
    {
      id: 1,
      ten_cong_viec: 'Tổng hợp số liệu dự kiến tuyển sinh lớp 10 THPT công lập năm 2026',
      nguoi_giao: 'Lê Thị Bích Thuận (Giám đốc Sở)',
      nguoi_xu_ly: 'Trần Văn Nam (Phòng GD Trung học)',
      phong_ban: 'Phòng Giáo dục Trung học',
      ngay_giao: '2026-10-28',
      han_hoan_thanh: '2026-11-04',
      do_uu_tien: 'CAO',
      tien_do: 85,
      trang_thai: 'DANG_THUC_HIEN',
      noi_dung: 'Thu thập bảng khảo sát nguyện vọng lớp 9 từ các trường THCS và năng lực tiếp nhận của 21 trường THPT công lập trên địa bàn.',
      ket_qua_bao_cao: 'Đã hoàn thành thu thập 19/21 trường, đang chờ số liệu 2 trường cuối cùng.',
      danh_gia_lanh_dao: ''
    },
    {
      id: 2,
      ten_cong_viec: 'Xây dựng dự thảo Kế hoạch bồi dưỡng giáo viên Tin học và Ngoại ngữ hè 2026',
      nguoi_giao: 'Mai Tấn Linh (Phó Giám đốc Sở)',
      nguoi_xu_ly: 'Hoàng Minh Tuấn (Phòng GD Tiểu học)',
      phong_ban: 'Phòng Giáo dục Tiểu học',
      ngay_giao: '2026-10-25',
      han_hoan_thanh: '2026-11-08',
      do_uu_tien: 'TRUNG_BINH',
      tien_do: 50,
      trang_thai: 'DANG_THUC_HIEN',
      noi_dung: 'Liên hệ trường Đại học Sư phạm - ĐH Đà Nẵng để thống nhất khung chương trình tập huấn.',
      ket_qua_bao_cao: 'Đã hoàn thành dự thảo khung đề cương và liên hệ báo cáo viên.',
      danh_gia_lanh_dao: ''
    },
    {
      id: 3,
      ten_cong_viec: 'Thẩm định hồ sơ công nhận trường chuẩn Quốc gia mức độ 2 THCS Nguyễn Khuyến',
      nguoi_giao: 'Phùng Văn Cường (Phó Giám đốc Sở)',
      nguoi_xu_ly: 'Lê Thị Thảo (Phòng Kế hoạch - Tài chính)',
      phong_ban: 'Phòng Kế hoạch - Tài chính',
      ngay_giao: '2026-10-15',
      han_hoan_thanh: '2026-10-30',
      do_uu_tien: 'CAO',
      tien_do: 100,
      trang_thai: 'CHO_DANH_GIA',
      noi_dung: 'Kiểm tra thực tế các tiêu chuẩn phòng thí nghiệm, sân chơi bãi tập và tỷ lệ máy tính/học sinh.',
      ket_qua_bao_cao: 'Đã hoàn thành biên bản nghiệm thu đạt 5/5 tiêu chuẩn theo Thông tư 18 của Bộ GD&ĐT.',
      danh_gia_lanh_dao: ''
    },
    {
      id: 4,
      ten_cong_viec: 'Rà soát quy hoạch đất giáo dục tại khu đô thị Tây Bắc',
      nguoi_giao: 'Lê Thị Bích Thuận (Giám đốc Sở)',
      nguoi_xu_ly: 'Nguyễn Văn Nam (Văn phòng Sở)',
      phong_ban: 'Văn phòng Sở',
      ngay_giao: '2026-10-01',
      han_hoan_thanh: '2026-10-20',
      do_uu_tien: 'TRUNG_BINH',
      tien_do: 100,
      trang_thai: 'HOAN_THANH',
      noi_dung: 'Phối hợp Sở Xây dựng thẩm tra 3 vị trí dự kiến xây dựng trường liên cấp.',
      ket_qua_bao_cao: 'Đã trình UBND TP bản đồ quy hoạch chi tiết 1/500.',
      danh_gia_lanh_dao: 'Hoàn thành xuất sắc, đúng tiến độ.'
    }
  ];

  const congViecService = {
    // TODO(nhóm): thay bằng api.get('/api/cong-viec', filters)
    getAll: async function (filters = {}) {
      let result = [...MOCK_CONG_VIEC];
      if (filters.q) {
        const q = filters.q.toLowerCase();
        result = result.filter(cv =>
          cv.ten_cong_viec.toLowerCase().includes(q) ||
          cv.nguoi_xu_ly.toLowerCase().includes(q)
        );
      }
      if (filters.trang_thai) {
        result = result.filter(cv => cv.trang_thai === filters.trang_thai);
      }
      return result;
    },

    // TODO(nhóm): thay bằng api.get(`/api/cong-viec/${id}`)
    getById: async function (id) {
      const cv = MOCK_CONG_VIEC.find(c => c.id === parseInt(id));
      if (!cv) throw new Error('Không tìm thấy công việc.');
      return { ...cv };
    },

    // TODO(nhóm): thay bằng api.post('/api/cong-viec', data)
    create: async function (data) {
      const newId = MOCK_CONG_VIEC.length ? Math.max(...MOCK_CONG_VIEC.map(c => c.id)) + 1 : 1;
      const newCv = {
        id: newId,
        ten_cong_viec: data.ten_cong_viec,
        nguoi_giao: data.nguoi_giao || 'Lãnh đạo Sở GD&ĐT',
        nguoi_xu_ly: data.nguoi_xu_ly,
        phong_ban: data.phong_ban || 'Phòng chuyên môn',
        ngay_giao: new Date().toISOString().split('T')[0],
        han_hoan_thanh: data.han_hoan_thanh,
        do_uu_tien: data.do_uu_tien || 'TRUNG_BINH',
        tien_do: 0,
        trang_thai: 'CHUA_THUC_HIEN',
        noi_dung: data.noi_dung || '',
        ket_qua_bao_cao: '',
        danh_gia_lanh_dao: ''
      };
      MOCK_CONG_VIEC.unshift(newCv);
      return newCv;
    },

    // TODO(nhóm): thay bằng api.post(`/api/cong-viec/${id}/tien-do`, { tien_do, bao_cao })
    updateProgress: async function (id, progress, note) {
      const cv = MOCK_CONG_VIEC.find(c => c.id === parseInt(id));
      if (!cv) throw new Error('Không tìm thấy công việc.');
      cv.tien_do = parseInt(progress);
      if (note) cv.ket_qua_bao_cao = note;
      if (cv.tien_do >= 100) {
        cv.trang_thai = 'CHO_DANH_GIA';
      } else {
        cv.trang_thai = 'DANG_THUC_HIEN';
      }
      return cv;
    },

    // TODO(nhóm): thay bằng api.post(`/api/cong-viec/${id}/danh-gia`, { ket_luan, nhan_xet })
    evaluate: async function (id, conclusion, comment) {
      const cv = MOCK_CONG_VIEC.find(c => c.id === parseInt(id));
      if (!cv) throw new Error('Không tìm thấy công việc.');
      cv.trang_thai = conclusion === 'DAT' ? 'HOAN_THANH' : 'DANG_THUC_HIEN';
      cv.danh_gia_lanh_dao = comment || 'Đã nghiệm thu kết quả công việc.';
      return cv;
    }
  };

  window.congViecService = congViecService;
})(window);
