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
        console.warn('Không thể gọi API /api/thong-bao, chuyển sang fallback:', err.message);
      }
      return [];
    },

    /**
     * Lấy số lượng thông báo chưa đọc để hiển thị icon chuông
     */
    getUnreadCount: async function () {
      try {
        if (window.api && typeof window.api.get === 'function') {
          const res = await window.api.get('/api/thong-bao/dem-chua-doc');
          if (res && res.thanh_cong) {
            return res.chua_doc || 0;
          }
        }
      } catch (err) {
        console.warn('Lỗi lấy số lượng chưa đọc:', err);
      }
      return 0;
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
     * Tạo thông báo điều hành hoặc lời nhắc nhở mới
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
