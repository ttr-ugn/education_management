/**
 * DU-LIEU-THONG-BAO.JS - KẾT NỐI BACKEND API THÔNG BÁO & NHẮC NHỞ
 * Nhánh: notifications-reminders
 */

(function (window) {
  const thongBaoService = {
    /**
     * Lấy danh sách thông báo điều hành & nhắc nhở từ Backend Flask
     * @param {Object} params - { loai, muc_do, chua_doc }
     */
    getAll: async function (params = {}) {
      try {
        if (window.api && typeof window.api.get === 'function') {
          const res = await window.api.get('/api/thong-bao', params);
          if (res && res.thanh_cong) {
            return res.du_lieu || [];
          }
        }
      } catch (err) {
        console.warn('Không thể gọi API /api/thong-bao:', err.message);
      }
      return [];
    },

    /**
     * Lấy số lượng thông báo chưa đọc và số nhắc nhở đến hạn
     */
    getStats: async function () {
      try {
        if (window.api && typeof window.api.get === 'function') {
          const res = await window.api.get('/api/thong-bao/dem-chua-doc');
          if (res && res.thanh_cong) {
            return {
              chua_doc: res.chua_doc || 0,
              den_han: res.den_han || 0
            };
          }
        }
      } catch (err) {
        console.warn('Lỗi lấy thống kê thông báo:', err);
      }
      return { chua_doc: 0, den_han: 0 };
    },

    getUnreadCount: async function () {
      const stats = await this.getStats();
      return stats.chua_doc;
    },

    /**
     * Kiểm tra các nhắc nhở đã đến hạn xử lý
     */
    getDueReminders: async function () {
      try {
        if (window.api && typeof window.api.get === 'function') {
          const res = await window.api.get('/api/thong-bao/kiem-tra-den-han');
          if (res && res.thanh_cong) {
            return res.nhac_nho_den_han || [];
          }
        }
      } catch (err) {
        console.warn('Lỗi kiểm tra nhắc nhở đến hạn:', err);
      }
      return [];
    },

    /**
     * Đánh dấu một thông báo là đã đọc
     * @param {number|string} id 
     */
    markAsRead: async function (id) {
      if (window.api && typeof window.api.post === 'function') {
        return await window.api.post(`/api/thong-bao/${id}/da-doc`);
      }
      return { thanh_cong: true };
    },

    /**
     * Đánh dấu tất cả thông báo là đã đọc
     */
    markAllAsRead: async function () {
      if (window.api && typeof window.api.post === 'function') {
        return await window.api.post('/api/thong-bao/doc-tat-ca');
      }
      return { thanh_cong: true };
    },

    /**
     * Tạo thông báo điều hành (Văn thư/Lãnh đạo) hoặc lời nhắc nhở cá nhân
     * @param {Object} data - { tieu_de, noi_dung, loai, muc_do, nguoi_nhan_id, ngay_hen_gio, lien_ket }
     */
    create: async function (data) {
      if (window.api && typeof window.api.post === 'function') {
        return await window.api.post('/api/thong-bao', data);
      }
      throw new Error('API chưa sẵn sàng');
    },

    /**
     * Xóa thông báo (chỉ Văn thư hoặc người tạo)
     * @param {number|string} id 
     */
    delete: async function (id) {
      if (window.api && typeof window.api.delete === 'function') {
        return await window.api.delete(`/api/thong-bao/${id}`);
      }
      return { thanh_cong: true };
    }
  };

  window.thongBaoService = thongBaoService;
})(window);
