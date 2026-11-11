/**
 * API.JS - FETCH WRAPPER CHUẨN CHO BACKEND HỆ THỐNG
 * Hỗ trợ credentials (session cookie), xử lý mã lỗi HTTP, JSON trả về và CORS đa nguồn.
 */

(function (window) {
  // Tự động nhận diện host:
  // - Nếu chạy cùng port 8000 (Django): dùng relative ''
  // - Nếu chạy từ PyCharm (63342), Live Server (5500), file:/// hoặc port khác: tự động kết nối http://127.0.0.1:8000
  let API_BASE = '';
  if (typeof window !== 'undefined' && window.location) {
    const origin = window.location.origin || '';
    const protocol = window.location.protocol || '';
    if (protocol === 'file:' || (!origin.includes(':8000') && !origin.includes('localhost:8000') && !origin.includes('127.0.0.1:8000'))) {
      API_BASE = 'http://127.0.0.1:8000';
    }
  }

  async function request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    
    const defaultHeaders = {
      'Accept': 'application/json'
    };

    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
      defaultHeaders['Content-Type'] = 'application/json';
      options.body = JSON.stringify(options.body);
    }

    const config = {
      credentials: 'include', // Bắt buộc gửi kèm session cookie HttpOnly
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMsg = data.thong_bao || data.message || `Lỗi máy chủ (HTTP ${response.status})`;
        const error = new Error(errorMsg);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      return data;
    } catch (err) {
      // Ném lỗi để caller xử lý hiển thị giao diện
      throw err;
    }
  }

  const api = {
    get: function (endpoint, params = null) {
      let url = endpoint;
      if (params && typeof params === 'object') {
        const query = Object.entries(params)
          .filter(([_, v]) => v !== undefined && v !== null && v !== '')
          .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
          .join('&');
        if (query) {
          url += (url.includes('?') ? '&' : '?') + query;
        }
      }
      return request(url, { method: 'GET' });
    },

    post: function (endpoint, body = {}) {
      return request(endpoint, {
        method: 'POST',
        body: body
      });
    },

    put: function (endpoint, body = {}) {
      return request(endpoint, {
        method: 'PUT',
        body: body
      });
    },

    delete: function (endpoint) {
      return request(endpoint, {
        method: 'DELETE'
      });
    }
  };

  window.api = api;
})(window);
