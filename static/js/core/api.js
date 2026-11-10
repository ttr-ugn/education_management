/**
 * API.JS - FETCH WRAPPER CHUẨN CHO BACKEND FLASK
 * Hỗ trợ credentials (session cookie), xử lý mã lỗi HTTP và JSON trả về.
 */

(function (window) {
  // Tự động nhận diện host: nếu chạy cùng port hoặc khác port (Live Server)
  const API_BASE = window.location.origin.includes(':5000') ? '' : 'http://localhost:5000';

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
