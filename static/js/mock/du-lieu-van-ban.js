/**
 * DU-LIEU-VAN-BAN.JS - DỮ LIỆU MẪU VĂN BẢN ĐẾN & VĂN BẢN ĐI
 * Cung cấp Service bao bọc để các trang giao diện gọi dữ liệu.
 * 
 * TODO(nhóm): Khi thành viên nhánh feature/van-ban-den hoặc feature/van-ban-di
 * hoàn thiện API, chỉ cần thay đổi phần thân các hàm service dưới đây
 * từ việc đọc mảng cục bộ sang gọi `window.api.get(...)` / `window.api.post(...)`.
 * GIAO DIỆN HTML/CSS HOÀN TOÀN KHÔNG CẦN CHỈNH SỬA.
 */

window.ENABLE_MOCK_BANNER = true; // Biến cấu hình hiển thị banner cảnh báo mock data

(function (window) {
  // Dữ liệu mẫu Văn bản đến
  const MOCK_VAN_BAN_DEN = [
    {
      id: 1,
      so_den: '01/VBD',
      so_ky_hieu: '142/BGDĐT-GDTrH',
      ngay_ban_hanh: '2026-10-25',
      ngay_den: '2026-10-27',
      co_quan_gui: 'Bộ Giáo dục và Đào tạo',
      trich_yeu: 'V/v hướng dẫn tổ chức Kỳ thi tốt nghiệp Trung học phổ thông năm 2026',
      loai_van_ban: 'Công văn',
      do_khan: 'Khẩn',
      do_mat: 'Bình thường',
      han_xu_ly: '2026-11-10',
      nguoi_ky: 'Thứ trưởng Nguyễn Văn Phúc',
      nguoi_phan_cong: 'Lê Thị Bích Thuận (Giám đốc Sở)',
      chuyen_vien_xu_ly: 'Trần Văn Nam (Phòng GD Trung học)',
      trang_thai: 'DANG_XU_LY',
      noi_dung_chi_dao: 'Giao Phòng GD Trung học chủ trì nghiên cứu, lập kế hoạch chi tiết tập huấn cho các trường THPT.',
      tep_dinh_kem: [
        { ten_tep: '142_BGDDT_HuongDanThi2026.pdf', dung_luong: '2.4 MB' }
      ]
    },
    {
      id: 2,
      so_den: '02/VBD',
      so_ky_hieu: '88/UBND-VX',
      ngay_ban_hanh: '2026-10-28',
      ngay_den: '2026-10-29',
      co_quan_gui: 'Ủy ban nhân dân thành phố Đà Nẵng',
      trich_yeu: 'Về việc phân bổ kinh phí đầu tư cơ sở vật chất trường chuẩn quốc gia năm học 2026-2027',
      loai_van_ban: 'Quyết định',
      do_khan: 'Thượng khẩn',
      do_mat: 'Bình thường',
      han_xu_ly: '2026-11-05',
      nguoi_ky: 'Chủ tịch UBND TP. Đà Nẵng',
      nguoi_phan_cong: 'Mai Tấn Linh (Phó Giám đốc Sở)',
      chuyen_vien_xu_ly: 'Lê Thị Thảo (Phòng Kế hoạch - Tài chính)',
      trang_thai: 'DANG_XU_LY',
      noi_dung_chi_dao: 'Phòng KHTC rà soát danh mục trường cần bổ sung phòng máy tính và thư viện thông minh.',
      tep_dinh_kem: [
        { ten_tep: 'QD_88_PhanBoKinhPhi_UBND.pdf', dung_luong: '1.8 MB' },
        { ten_tep: 'PhuLuc_DanhSachTruong.xlsx', dung_luong: '540 KB' }
      ]
    },
    {
      id: 3,
      so_den: '03/VBD',
      so_ky_hieu: '45/STTTT-CNTT',
      ngay_ban_hanh: '2026-10-30',
      ngay_den: '2026-11-01',
      co_quan_gui: 'Sở Thông tin và Truyền thông TP. Đà Nẵng',
      trich_yeu: 'Hướng dẫn bảo đảm an toàn thông tin mạng trong các cơ quan hành chính nhà nước dịp cuối năm 2026',
      loai_van_ban: 'Công văn',
      do_khan: 'Bình thường',
      do_mat: 'Bình thường',
      han_xu_ly: '2026-11-15',
      nguoi_ky: 'Giám đốc Sở TTTT',
      nguoi_phan_cong: null,
      chuyen_vien_xu_ly: null,
      trang_thai: 'CHUA_PHAN_CONG',
      noi_dung_chi_dao: '',
      tep_dinh_kem: [
        { ten_tep: 'CV_45_AnToanThongTin_STTTT.pdf', dung_luong: '950 KB' }
      ]
    },
    {
      id: 4,
      so_den: '04/VBD',
      so_ky_hieu: '310/SGDĐT-GDTH',
      ngay_ban_hanh: '2026-10-15',
      ngay_den: '2026-10-16',
      co_quan_gui: 'Phòng GD&ĐT Quận Hải Châu',
      trich_yeu: 'Báo cáo sơ kết triển khai đổi mới chương trình Giáo dục phổ thông 2018 cấp Tiểu học',
      loai_van_ban: 'Báo cáo',
      do_khan: 'Bình thường',
      do_mat: 'Bình thường',
      han_xu_ly: '2026-10-30',
      nguoi_ky: 'Trưởng phòng GD&ĐT Quận Hải Châu',
      nguoi_phan_cong: 'Phùng Văn Cường (Phó Giám đốc Sở)',
      chuyen_vien_xu_ly: 'Hoàng Minh Tuấn (Phòng GD Tiểu học)',
      trang_thai: 'DA_XU_LY',
      noi_dung_chi_dao: 'Đã tổng hợp vào báo cáo chung toàn thành phố ngày 28/10.',
      tep_dinh_kem: [
        { ten_tep: 'BC_SoKet_TieuHoc_HaiChau.pdf', dung_luong: '3.1 MB' }
      ]
    }
  ];

  // Dữ liệu mẫu Văn bản đi
  const MOCK_VAN_BAN_DI = [
    {
      id: 101,
      so_ky_hieu: '1205/SGDĐT-VP',
      trich_yeu: 'Kế hoạch tổ chức Tuần lễ hưởng ứng học tập suốt đời năm 2026 trên địa bàn TP. Đà Nẵng',
      loai_van_ban: 'Kế hoạch',
      don_vi_soan_thao: 'Văn phòng Sở',
      nguoi_soan_thao: 'Nguyễn Văn Nam (Chuyên viên)',
      lanh_dao_ky: 'Lê Thị Bích Thuận (Giám đốc Sở)',
      ngay_soan: '2026-10-20',
      ngay_ban_hanh: '2026-10-24',
      do_khan: 'Bình thường',
      trang_thai: 'DA_BAN_HANH',
      noi_dung_tom_tat: 'Phát động phong trào học tập suốt đời từ ngày 01/10 đến 07/10/2026 trong toàn ngành GD&ĐT Đà Nẵng.',
      noi_nhan: 'UBND các quận/huyện, các trường THPT, trung tâm GDTX',
      tep_dinh_kem: [{ ten_tep: 'KH_1205_SGDDT_HocTapSuotDoi.pdf', dung_luong: '1.2 MB' }]
    },
    {
      id: 102,
      so_ky_hieu: 'Dự thảo-08/SGDĐT-GDTrH',
      trich_yeu: 'Tờ trình UBND thành phố về việc thành lập Hội đồng xét chọn Nhà giáo Ưu tú lần thứ 17',
      loai_van_ban: 'Tờ trình',
      don_vi_soan_thao: 'Phòng Tổ chức cán bộ',
      nguoi_soan_thao: 'Phạm Thị Thùy Dung',
      lanh_dao_ky: 'Lê Thị Bích Thuận (Giám đốc Sở)',
      ngay_soan: '2026-11-01',
      ngay_ban_hanh: null,
      do_khan: 'Khẩn',
      trang_thai: 'CHO_LANH_DAO_DUYET',
      noi_dung_tom_tat: 'Đề xuất danh sách thành viên Hội đồng cấp thành phố gồm 15 đồng chí.',
      noi_nhan: 'UBND TP. Đà Nẵng, Sở Nội vụ',
      tep_dinh_kem: [{ ten_tep: 'ToTrinh_HoiDong_NhaGiaoUuTu.docx', dung_luong: '450 KB' }]
    },
    {
      id: 103,
      so_ky_hieu: 'Dự thảo-12/SGDĐT-KHTC',
      trich_yeu: 'Thông báo dự toán ngân sách và định mức chi cho các đơn vị sự nghiệp công lập năm 2027',
      loai_van_ban: 'Thông báo',
      don_vi_soan_thao: 'Phòng Kế hoạch - Tài chính',
      nguoi_soan_thao: 'Đặng Quốc Bảo',
      lanh_dao_ky: 'Mai Tấn Linh (Phó Giám đốc Sở)',
      ngay_soan: '2026-10-28',
      ngay_ban_hanh: null,
      do_khan: 'Bình thường',
      trang_thai: 'YEU_CAU_CHINH_SUA',
      ly_do_chinh_sua: 'Cần bổ sung chi tiết biểu mẫu phụ lục 02 về định mức chi công nghệ thông tin theo công văn mới của Bộ Tài chính.',
      noi_dung_tom_tat: 'Hướng dẫn lập dự toán chi thường xuyên năm 2027.',
      noi_nhan: 'Các đơn vị trực thuộc Sở',
      tep_dinh_kem: [{ ten_tep: 'TB_DuToan_KHTC_2027.docx', dung_luong: '680 KB' }]
    },
    {
      id: 104,
      so_ky_hieu: '1210/SGDĐT-GDTrH',
      trich_yeu: 'Công văn triệu tập Hội nghị tập huấn xây dựng đề kiểm tra đánh giá theo định hướng phát triển năng lực',
      loai_van_ban: 'Công văn',
      don_vi_soan_thao: 'Phòng Giáo dục Trung học',
      nguoi_soan_thao: 'Trần Văn Nam',
      lanh_dao_ky: 'Phùng Văn Cường (Phó Giám đốc Sở)',
      ngay_soan: '2026-11-02',
      ngay_ban_hanh: null,
      do_khan: 'Bình thường',
      trang_thai: 'DA_DUYET', // Lãnh đạo đã duyệt, chờ Văn thư ban hành cấp số
      noi_dung_tom_tat: 'Triệu tập 120 giáo viên cốt cán các bộ môn Toán, Ngữ văn, Tiếng Anh.',
      noi_nhan: 'Các trường THPT, THCS trên địa bàn',
      tep_dinh_kem: [{ ten_tep: 'CV_TapHuan_KiemTraDanhGia.pdf', dung_luong: '1.5 MB' }]
    }
  ];

  // ==========================================
  // SERVICE VĂN BẢN ĐẾN
  // ==========================================
  const vanBanDenService = {
    // TODO(nhóm): thay bằng api.get('/api/van-ban-den', filters)
    getAll: async function (filters = {}) {
      let result = [...MOCK_VAN_BAN_DEN];
      if (filters.q) {
        const q = filters.q.toLowerCase();
        result = result.filter(item =>
          item.so_ky_hieu.toLowerCase().includes(q) ||
          item.trich_yeu.toLowerCase().includes(q) ||
          item.co_quan_gui.toLowerCase().includes(q)
        );
      }
      if (filters.trang_thai) {
        result = result.filter(item => item.trang_thai === filters.trang_thai);
      }
      if (filters.do_khan) {
        result = result.filter(item => item.do_khan === filters.do_khan);
      }
      return result;
    },

    // TODO(nhóm): thay bằng api.get(`/api/van-ban-den/${id}`)
    getById: async function (id) {
      const item = MOCK_VAN_BAN_DEN.find(doc => doc.id === parseInt(id));
      if (!item) throw new Error('Không tìm thấy văn bản đến.');
      return { ...item };
    },

    // TODO(nhóm): thay bằng api.post('/api/van-ban-den', data)
    create: async function (data) {
      const newId = MOCK_VAN_BAN_DEN.length ? Math.max(...MOCK_VAN_BAN_DEN.map(d => d.id)) + 1 : 1;
      const newDoc = {
        id: newId,
        so_den: `${String(newId).padStart(2, '0')}/VBD`,
        so_ky_hieu: data.so_ky_hieu,
        ngay_ban_hanh: data.ngay_ban_hanh,
        ngay_den: data.ngay_den || new Date().toISOString().split('T')[0],
        co_quan_gui: data.co_quan_gui,
        trich_yeu: data.trich_yeu,
        loai_van_ban: data.loai_van_ban || 'Công văn',
        do_khan: data.do_khan || 'Bình thường',
        do_mat: data.do_mat || 'Bình thường',
        han_xu_ly: data.han_xu_ly || '',
        nguoi_ky: data.nguoi_ky || '',
        nguoi_phan_cong: null,
        chuyen_vien_xu_ly: null,
        trang_thai: 'CHUA_PHAN_CONG',
        noi_dung_chi_dao: '',
        tep_dinh_kem: [{ ten_tep: data.ten_tep || 'VanBanDinhKem.pdf', dung_luong: '1.5 MB' }]
      };
      MOCK_VAN_BAN_DEN.unshift(newDoc);
      return newDoc;
    },

    // TODO(nhóm): thay bằng api.post(`/api/van-ban-den/${id}/phan-cong`, assignData)
    assign: async function (id, assignData) {
      const doc = MOCK_VAN_BAN_DEN.find(d => d.id === parseInt(id));
      if (!doc) throw new Error('Không tìm thấy văn bản để phân công.');
      doc.nguoi_phan_cong = assignData.nguoi_phan_cong || 'Lãnh đạo Sở';
      doc.chuyen_vien_xu_ly = assignData.chuyen_vien_xu_ly;
      doc.noi_dung_chi_dao = assignData.noi_dung_chi_dao || '';
      doc.han_xu_ly = assignData.han_xu_ly || doc.han_xu_ly;
      doc.trang_thai = 'DANG_XU_LY';
      return doc;
    }
  };

  // ==========================================
  // SERVICE VĂN BẢN ĐI (KẾT NỐI REAL API FLASK)
  // ==========================================
  const vanBanDiService = {
    getAll: async function (filters = {}) {
      try {
        if (window.api && typeof window.api.get === 'function') {
          const res = await window.api.get('/api/van-ban-di', filters);
          if (res && res.thanh_cong) {
            return (res.du_lieu || []).map(item => ({
              ...item,
              id: item.id || item.van_ban_id,
              van_ban_id: item.van_ban_id || item.id
            }));
          }
        }
      } catch (err) {
        console.warn('Dùng dữ liệu dự phòng:', err.message);
      }
      return [...MOCK_VAN_BAN_DI];
    },

    getById: async function (id) {
      try {
        if (window.api && typeof window.api.get === 'function') {
          const res = await window.api.get('/api/van-ban-di/' + id);
          if (res && res.thanh_cong) return res.du_lieu;
        }
      } catch (err) {
        console.warn('Lỗi chi tiết VB:', err.message);
      }
      const item = MOCK_VAN_BAN_DI.find(doc => doc.id === parseInt(id));
      if (!item) throw new Error('Không tìm thấy văn bản đi.');
      return { ...item };
    },

    create: async function (data) {
      if (window.api && typeof window.api.post === 'function') {
        let payload = data;
        if (!(data instanceof FormData)) {
          payload = new FormData();
          for (const [k, v] of Object.entries(data)) {
            if (v !== undefined && v !== null) payload.append(k, v);
          }
        }
        const res = await window.api.post('/api/van-ban-di', payload);
        if (res && res.thanh_cong) return res.du_lieu;
      }
      return data;
    },

    forwardToLeader: async function (id, note = '') {
      if (window.api && typeof window.api.post === 'function') {
        return await window.api.post('/api/van-ban-di/' + id + '/trinh-lanh-dao', { ghi_chu: note });
      }
      return { thanh_cong: true };
    },

    approve: async function (id, note = '', signCoords = null) {
      if (window.api && typeof window.api.post === 'function') {
        const body = signCoords || {
          y_kien: note,
          is_percentage: true,
          page: 1,
          x: 60.0,
          y: 75.0
        };
        const res = await window.api.post('/api/van-ban-di/' + id + '/ky-so', body);
        if (res && res.thanh_cong) return res.du_lieu;
      }
      const doc = MOCK_VAN_BAN_DI.find(d => d.id === parseInt(id));
      if (doc) doc.trang_thai = 'DA_KY_CHO_BAN_HANH';
      return doc;
    },

    reject: async function (id, reason) {
      if (window.api && typeof window.api.post === 'function') {
        return await window.api.post('/api/van-ban-di/' + id + '/tu-choi', { ly_do: reason });
      }
      const doc = MOCK_VAN_BAN_DI.find(d => d.id === parseInt(id));
      if (doc) doc.trang_thai = 'VAN_THU_TRA_LAI';
      return doc;
    },

    publish: async function (id, publishData) {
      if (window.api && typeof window.api.post === 'function') {
        const res = await window.api.post('/api/van-ban-di/' + id + '/ban-hanh', publishData);
        if (res && res.thanh_cong) return res.du_lieu;
      }
      const doc = MOCK_VAN_BAN_DI.find(d => d.id === parseInt(id));
      if (doc) doc.trang_thai = 'DA_BAN_HANH';
      return doc;
    }
  };

  window.vanBanDenService = vanBanDenService;
  window.vanBanDiService = vanBanDiService;
})(window);
