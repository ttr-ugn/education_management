/**
 * DU-LIEU-CONG-VIEC.JS - SERVICE KẾT NỐI API QUẢN LÝ CÔNG VIỆC
 * Nhánh: task-management
 * Kết nối trực tiếp API Backend Flask (/api/cong-viec)
 */

(function (window) {
  const congViecService = {
    /**
     * Lấy danh sách công việc (có lọc, tìm kiếm, phân quyền theo role)
     */
    getAll: async function (filters = {}) {
      try {
        const res = await window.api.get('/api/cong-viec', filters);
        return res.du_lieu || [];
      } catch (err) {
        console.error('Lỗi tải danh sách công việc:', err);
        if (window.Toast) window.Toast.error(err.message || 'Không thể tải danh sách công việc.');
        return [];
      }
    },

    /**
     * Lấy chi tiết 1 công việc kèm thông tin văn bản và lịch sử tiến độ
     */
    getById: async function (id) {
      try {
        const res = await window.api.get(`/api/cong-viec/${id}`);
        return res.du_lieu;
      } catch (err) {
        console.error('Lỗi tải chi tiết công việc:', err);
        throw err;
      }
    },

    /**
     * Giao nhiệm vụ / tạo công việc mới (Văn thư hoặc Lãnh đạo)
     */
    create: async function (data) {
      try {
        const res = await window.api.post('/api/cong-viec', data);
        if (window.Toast) window.Toast.success(res.thong_bao || 'Giao nhiệm vụ thành công.');
        return res;
      } catch (err) {
        console.error('Lỗi tạo công việc:', err);
        if (window.Toast) window.Toast.error(err.message || 'Lỗi khi giao nhiệm vụ.');
        throw err;
      }
    },

    /**
     * Cập nhật tiến độ & nộp báo cáo kết quả (Chuyên viên)
     */
    updateProgress: async function (id, progress, note, attachment = '') {
      try {
        const body = {
          tien_do: parseInt(progress),
          ket_qua_bao_cao: note,
          tep_dinh_kem_ket_qua: attachment
        };
        const res = await window.api.put(`/api/cong-viec/${id}/tien-do`, body);
        if (window.Toast) window.Toast.success(res.thong_bao || 'Cập nhật tiến độ thành công.');
        return res;
      } catch (err) {
        console.error('Lỗi cập nhật tiến độ:', err);
        if (window.Toast) window.Toast.error(err.message || 'Lỗi cập nhật tiến độ.');
        throw err;
      }
    },

    /**
     * Đánh giá / Nghiệm thu kết quả công việc (Văn thư hoặc Lãnh đạo)
     */
    evaluate: async function (id, conclusion, comment) {
      try {
        const body = {
          ket_luan: conclusion,
          nhan_xet: comment
        };
        const res = await window.api.put(`/api/cong-viec/${id}/danh-gia`, body);
        if (window.Toast) window.Toast.success(res.thong_bao || 'Đã lưu đánh giá kết quả.');
        return res;
      } catch (err) {
        console.error('Lỗi đánh giá công việc:', err);
        if (window.Toast) window.Toast.error(err.message || 'Lỗi khi nghiệm thu công việc.');
        throw err;
      }
    },

    /**
     * Lấy báo cáo thống kê & dữ liệu biểu đồ Chart.js
     */
    getStatistics: async function (filters = {}) {
      try {
        const res = await window.api.get('/api/cong-viec/thong-ke', filters);
        return res.du_lieu;
      } catch (err) {
        console.error('Lỗi tải thống kê công việc:', err);
        return null;
      }
    },

    /**
     * Xóa nhiệm vụ (Văn thư hoặc Lãnh đạo)
     */
    delete: async function (id) {
      try {
        const res = await window.api.delete(`/api/cong-viec/${id}`);
        if (window.Toast) window.Toast.success(res.thong_bao || 'Đã xóa công việc.');
        return res;
      } catch (err) {
        console.error('Lỗi xóa công việc:', err);
        if (window.Toast) window.Toast.error(err.message || 'Không thể xóa công việc.');
        throw err;
      }
    }
  };

  window.congViecService = congViecService;
})(window);
