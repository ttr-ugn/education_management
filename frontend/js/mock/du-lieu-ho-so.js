/**
 * DU-LIEU-HO-SO.JS - DỮ LIỆU MẪU QUẢN LÝ HỒ SƠ LƯU TRỮ CƠ QUAN
 * 
 * TODO(nhóm): Sau khi thành viên hoàn thiện backend phân hệ hồ sơ,
 * thay các hàm trong hoSoService bằng api.get / api.post tương ứng.
 */

(function (window) {
  const MOCK_HO_SO = [
    {
      id: 1,
      ma_ho_so: 'HS-2026-VP-01',
      tieu_de: 'Hồ sơ chỉ đạo, điều hành công tác văn thư, lưu trữ năm 2026',
      nguoi_lap: 'Trần Thị Thu Thảo',
      don_vi: 'Văn phòng Sở GD&ĐT',
      nam_tai_lieu: 2026,
      thoi_han_bao_quan: 'Vĩnh viễn',
      so_luong_van_ban: 14,
      tinh_trang: 'DANG_THU_THAP',
      mo_ta: 'Tập hợp toàn bộ các quyết định, kế hoạch, thông tri về công tác lưu trữ số và bảo mật văn bản.'
    },
    {
      id: 2,
      ma_ho_so: 'HS-2026-GDTrH-03',
      tieu_de: 'Hồ sơ tổ chức Hội thi giáo viên dạy giỏi cấp THPT toàn thành phố năm học 2025-2026',
      nguoi_lap: 'Trần Văn Nam',
      don_vi: 'Phòng Giáo dục Trung học',
      nam_tai_lieu: 2026,
      thoi_han_bao_quan: '20 năm',
      so_luong_van_ban: 28,
      tinh_trang: 'DA_NOP_LUU_TRU',
      mo_ta: 'Kế hoạch tổ chức, danh sách ban giám khảo, bảng điểm chấm thi và quyết định công nhận giải thưởng.'
    },
    {
      id: 3,
      ma_ho_so: 'HS-2025-KHTC-05',
      tieu_de: 'Hồ sơ quyết toán tài chính ngân sách sự nghiệp giáo dục năm 2025',
      nguoi_lap: 'Lê Thị Thảo',
      don_vi: 'Phòng Kế hoạch - Tài chính',
      nam_tai_lieu: 2025,
      thoi_han_bao_quan: '10 năm',
      so_luong_van_ban: 45,
      tinh_trang: 'DA_DONG',
      mo_ta: 'Báo cáo tài chính, biên bản đối chiếu kho bạc và thẩm định của Sở Tài chính TP. Đà Nẵng.'
    }
  ];

  const hoSoService = {
    // TODO(nhóm): thay bằng api.get('/api/ho-so', filters)
    getAll: async function (filters = {}) {
      let result = [...MOCK_HO_SO];
      if (filters.q) {
        const q = filters.q.toLowerCase();
        result = result.filter(hs =>
          hs.ma_ho_so.toLowerCase().includes(q) ||
          hs.tieu_de.toLowerCase().includes(q) ||
          hs.don_vi.toLowerCase().includes(q)
        );
      }
      if (filters.tinh_trang) {
        result = result.filter(hs => hs.tinh_trang === filters.tinh_trang);
      }
      return result;
    },

    // TODO(nhóm): thay bằng api.get(`/api/ho-so/${id}`)
    getById: async function (id) {
      const hs = MOCK_HO_SO.find(h => h.id === parseInt(id));
      if (!hs) throw new Error('Không tìm thấy hồ sơ lưu trữ.');
      return { ...hs };
    },

    // TODO(nhóm): thay bằng api.post('/api/ho-so', data)
    create: async function (data) {
      const newId = MOCK_HO_SO.length ? Math.max(...MOCK_HO_SO.map(h => h.id)) + 1 : 1;
      const newHs = {
        id: newId,
        ma_ho_so: data.ma_ho_so || `HS-2026-${newId}`,
        tieu_de: data.tieu_de,
        nguoi_lap: data.nguoi_lap || 'Cán bộ lập hồ sơ',
        don_vi: data.don_vi || 'Phòng ban chuyên môn',
        nam_tai_lieu: data.nam_tai_lieu || 2026,
        thoi_han_bao_quan: data.thoi_han_bao_quan || '10 năm',
        so_luong_van_ban: 0,
        tinh_trang: 'DANG_THU_THAP',
        mo_ta: data.mo_ta || ''
      };
      MOCK_HO_SO.unshift(newHs);
      return newHs;
    },

    // TODO(nhóm): thay bằng api.post(`/api/ho-so/${id}/nop-luu-tru`)
    submitToArchive: async function (id) {
      const hs = MOCK_HO_SO.find(h => h.id === parseInt(id));
      if (!hs) throw new Error('Không tìm thấy hồ sơ.');
      hs.tinh_trang = 'DA_NOP_LUU_TRU';
      return hs;
    }
  };

  window.hoSoService = hoSoService;
})(window);
