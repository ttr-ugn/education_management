/**
 * DU-LIEU-HO-SO.JS - DỊCH VỤ QUẢN LÝ HỒ SƠ LƯU TRỮ CƠ QUAN
 * Đã kết nối trực tiếp với Backend Flask API (/api/ho-so).
 */

(function (window) {
  const hoSoService = {
    getAll: async function (filters = {}) {
      try {
        const res = await window.api.get('/api/ho-so', filters);
        const list = res.du_lieu || [];
        return list.map(item => ({
          ...item,
          id: item.ho_so_id || item.id
        }));
      } catch (err) {
        console.error('Lỗi tải danh sách hồ sơ từ backend:', err);
        throw err;
      }
    },

    getById: async function (id) {
      try {
        const res = await window.api.get(`/api/ho-so/${id}`);
        const item = res.du_lieu;
        if (item) {
          item.id = item.ho_so_id || item.id;
        }
        return item;
      } catch (err) {
        console.error('Lỗi tải chi tiết hồ sơ:', err);
        throw err;
      }
    },

    create: async function (data) {
      try {
        const res = await window.api.post('/api/ho-so', data);
        return res.du_lieu;
      } catch (err) {
        console.error('Lỗi tạo mới hồ sơ:', err);
        throw err;
      }
    },

    update: async function (id, data) {
      try {
        const res = await window.api.put(`/api/ho-so/${id}`, data);
        return res.du_lieu;
      } catch (err) {
        console.error('Lỗi cập nhật hồ sơ:', err);
        throw err;
      }
    },

    delete: async function (id) {
      try {
        const res = await window.api.delete(`/api/ho-so/${id}`);
        return res;
      } catch (err) {
        console.error('Lỗi xóa hồ sơ:', err);
        throw err;
      }
    },

    submitToArchive: async function (id) {
      try {
        const res = await window.api.post(`/api/ho-so/${id}/nop-luu-tru`);
        return res.du_lieu;
      } catch (err) {
        console.error('Lỗi nộp lưu trữ hồ sơ:', err);
        throw err;
      }
    },

    closeArchive: async function (id) {
      try {
        const res = await window.api.post(`/api/ho-so/${id}/dong`);
        return res.du_lieu;
      } catch (err) {
        console.error('Lỗi đóng hồ sơ:', err);
        throw err;
      }
    }
  };

  window.hoSoService = hoSoService;
})(window);
