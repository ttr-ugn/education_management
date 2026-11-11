/**
 * MENU.JS - DỰNG THANH ĐIỀU HƯỚNG SIDEBAR THEO VAI TRÒ
 * Tự động tạo menu chuẩn xác cho: VAN_THU, LANH_DAO, CHUYEN_VIEN
 * Đã tinh gọn chuẩn hóa theo mô hình QUẢN LÝ VĂN BẢN NỘI BỘ SỞ GD&ĐT
 */

(function (window) {
  function getRootPath() {
    return window.AuthGuard ? window.AuthGuard.getRootPath() : '../';
  }

  const ICONS = {
    dashboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></svg>',
    checkDraft: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="m9 15 2 2 4-4"/></svg>',
    docOut: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="15" y2="11"/></svg>',
    publish: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><circle cx="12" cy="14" r="3"/><path d="m14 16 2 2"/></svg>',
    signDoc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 2 4 4-10 10H8v-4L18 2z"/><path d="m14.5 5.5 3 3"/><path d="M4 20h16"/></svg>',
    folder: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    giaoViec: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/></svg>',
    tienDo: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="m9 14 2 2 4-4"/></svg>',
    tasks: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><polyline points="9 14 12 17 22 7"/></svg>',
    notify: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
    chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    bot: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="3"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><circle cx="8" cy="16" r="1" fill="currentColor"/><circle cx="16" cy="16" r="1" fill="currentColor"/></svg>',
    userCheck: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg>',
    userPlus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>',
    users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
  };

  function getMenuConfig(role) {
    const root = getRootPath();

    if (role === 'VAN_THU') {
      return [
        {
          title: 'Tổng quan',
          items: [
            { label: 'Trang chủ', href: `${root}pages/dashboard.html`, icon: ICONS.dashboard, id: 'nav-dashboard' }
          ]
        },
        {
          title: 'Quản lý văn bản nội bộ',
          items: [
            { label: 'Tiếp nhận dự thảo từ Chuyên viên', href: `${root}pages/van-ban-di/kiem-tra.html`, icon: ICONS.checkDraft, id: 'nav-vb-kiemtra' },
            { label: 'Sổ theo dõi Văn bản đi', href: `${root}pages/van-ban-di/danh-sach.html`, icon: ICONS.docOut, id: 'nav-vb-di' },
            { label: 'Cấp số & Ban hành', href: `${root}pages/van-ban-di/ban-hanh.html`, icon: ICONS.publish, id: 'nav-vb-banhanh' }
          ]
        },
        {
          title: 'Nghiệp vụ lưu trữ & điều hành',
          items: [
            { label: 'Hồ sơ tài liệu', href: `${root}pages/ho-so/danh-sach.html`, icon: ICONS.folder, id: 'nav-ho-so' },
            { label: 'Giao nhiệm vụ mới', href: `${root}pages/cong-viec/giao-viec.html`, icon: ICONS.giaoViec, id: 'nav-giao-viec' },
            { label: 'Theo dõi tiến độ công việc', href: `${root}pages/cong-viec/danh-sach.html`, icon: ICONS.tienDo, id: 'nav-cong-viec' },
            { label: 'Thông báo điều hành', href: `${root}pages/thong-bao.html`, icon: ICONS.notify, id: 'nav-thong-bao' },
            { label: 'Báo cáo thống kê', href: `${root}pages/thong-ke.html`, icon: ICONS.chart, id: 'nav-thong-ke' },
            { label: 'Trợ lý ảo Chatbot', href: `${root}pages/chatbot.html`, icon: ICONS.bot, id: 'nav-chatbot' }
          ]
        },
        {
          title: 'Quản trị hệ thống (Văn thư)',
          items: [
            { label: 'Duyệt tài khoản Chuyên viên', href: `${root}pages/admin/duyet-tai-khoan.html`, icon: ICONS.userCheck, id: 'nav-duyet-tk' },
            { label: 'Tạo tài khoản Lãnh đạo', href: `${root}pages/admin/tao-lanh-dao.html`, icon: ICONS.userPlus, id: 'nav-tao-ld' },
            { label: 'Quản lý người dùng', href: `${root}pages/admin/quan-ly-nguoi-dung.html`, icon: ICONS.users, id: 'nav-ql-user' }
          ]
        }
      ];
    } else if (role === 'LANH_DAO') {
      return [
        {
          title: 'Tổng quan',
          items: [
            { label: 'Trang chủ', href: `${root}pages/dashboard.html`, icon: ICONS.dashboard, id: 'nav-dashboard' }
          ]
        },
        {
          title: 'Ký duyệt văn bản',
          items: [
            { label: 'Ký số & Duyệt văn bản', href: `${root}pages/van-ban-di/phe-duyet.html`, icon: ICONS.signDoc, id: 'nav-vb-phe-duyet' },
            { label: 'Sổ theo dõi Văn bản đi', href: `${root}pages/van-ban-di/danh-sach.html`, icon: ICONS.docOut, id: 'nav-vb-di' }
          ]
        },
        {
          title: 'Lưu trữ & Báo cáo thống kê',
          items: [
            { label: 'Hồ sơ tài liệu', href: `${root}pages/ho-so/danh-sach.html`, icon: ICONS.folder, id: 'nav-ho-so' },
            { label: 'Báo cáo thống kê', href: `${root}pages/thong-ke.html`, icon: ICONS.chart, id: 'nav-thong-ke' },
            { label: 'Thông báo điều hành', href: `${root}pages/thong-bao.html`, icon: ICONS.notify, id: 'nav-thong-bao' },
            { label: 'Trợ lý ảo Chatbot', href: `${root}pages/chatbot.html`, icon: ICONS.bot, id: 'nav-chatbot' }
          ]
        }
      ];
    } else {
      // CHUYEN_VIEN
      return [
        {
          title: 'Tổng quan',
          items: [
            { label: 'Trang chủ', href: `${root}pages/dashboard.html`, icon: ICONS.dashboard, id: 'nav-dashboard' }
          ]
        },
        {
          title: 'Quản lý văn bản nội bộ',
          items: [
            { label: 'Soạn thảo dự thảo mới', href: `${root}pages/van-ban-di/soan-thao.html`, icon: ICONS.checkDraft, id: 'nav-vb-soan' },
            { label: 'Văn bản của tôi', href: `${root}pages/van-ban-di/danh-sach.html`, icon: ICONS.folder, id: 'nav-vb-di' }
          ]
        },
        {
          title: 'Nhiệm vụ & Báo cáo',
          items: [
            { label: 'Công việc được giao', href: `${root}pages/cong-viec/danh-sach.html`, icon: ICONS.tienDo, id: 'nav-cong-viec' },
            { label: 'Báo cáo xử lý tiến độ', href: `${root}pages/cong-viec/xu-ly.html`, icon: ICONS.tasks, id: 'nav-cong-viec-xuly' },
            { label: 'Hồ sơ công việc', href: `${root}pages/ho-so/danh-sach.html`, icon: ICONS.folder, id: 'nav-ho-so' },
            { label: 'Thông báo điều hành', href: `${root}pages/thong-bao.html`, icon: ICONS.notify, id: 'nav-thong-bao' },
            { label: 'Báo cáo cá nhân', href: `${root}pages/thong-ke.html`, icon: ICONS.chart, id: 'nav-thong-ke' },
            { label: 'Trợ lý ảo Chatbot', href: `${root}pages/chatbot.html`, icon: ICONS.bot, id: 'nav-chatbot' }
          ]
        }
      ];
    }
  }

  function renderMenu(role) {
    const navContainer = document.getElementById('sidebarNav') || document.querySelector('.sidebar-nav');
    if (!navContainer) return;

    const sections = getMenuConfig(role);
    const currentPath = window.location.pathname.replace(/\/+$/, '');
    const currentHref = window.location.href;

    // Tìm duy nhất 1 mục (activeItemId) khớp với trang hiện tại
    let activeItemId = null;

    // Bước 1: Khớp chính xác tuyệt đối theo URL hoàn chỉnh
    for (const sec of sections) {
      for (const item of sec.items) {
        try {
          const itemUrl = new URL(item.href, currentHref);
          const itemPath = itemUrl.pathname.replace(/\/+$/, '');
          if (itemPath === currentPath) {
            activeItemId = item.id;
            break;
          }
        } catch (e) {}
      }
      if (activeItemId) break;
    }

    // Bước 2: Trang chủ / dashboard fallback
    if (!activeItemId) {
      if (currentPath === '' || currentPath === '/' || currentPath === '/pages' || currentPath.endsWith('/index.html') || currentPath.endsWith('/dashboard.html')) {
        activeItemId = 'nav-dashboard';
      }
    }

    // Bước 3: Các trang chi tiết hoặc trang con thuộc phân hệ
    if (!activeItemId) {
      if (currentPath.includes('/pages/van-ban-di/')) {
        const isKiemTra = currentPath.includes('kiem-tra');
        const isBanHanh = currentPath.includes('ban-hanh');
        const isPheDuyet = currentPath.includes('phe-duyet');
        const isSoanThao = currentPath.includes('soan-thao');
        if (role === 'VAN_THU') {
          if (isKiemTra) activeItemId = 'nav-vb-kiemtra';
          else if (isBanHanh) activeItemId = 'nav-vb-banhanh';
          else activeItemId = 'nav-vb-di';
        } else if (role === 'LANH_DAO') {
          if (isPheDuyet) activeItemId = 'nav-vb-phe-duyet';
          else activeItemId = 'nav-vb-di';
        } else {
          if (isSoanThao) activeItemId = 'nav-vb-soan';
          else activeItemId = 'nav-vb-di';
        }
      } else if (currentPath.includes('/pages/ho-so/')) {
        activeItemId = 'nav-ho-so';
      } else if (currentPath.includes('/pages/cong-viec/')) {
        const isGiaoViec = currentPath.includes('giao-viec');
        const isXuLy = currentPath.includes('xu-ly');
        if (role === 'VAN_THU' && isGiaoViec) activeItemId = 'nav-giao-viec';
        else if (role === 'CHUYEN_VIEN' && isXuLy) activeItemId = 'nav-cong-viec-xuly';
        else activeItemId = 'nav-cong-viec';
      }
    }

    let html = '';
    sections.forEach(sec => {
      html += `<div class="nav-section-title">${sec.title}</div>`;
      html += '<ul class="nav-list">';
      sec.items.forEach(item => {
        const isActive = (item.id === activeItemId);

        html += `
          <li class="nav-item">
            <a href="${item.href}" class="nav-link ${isActive ? 'active' : ''}" id="${item.id}">
              ${item.icon}
              <span>${item.label}</span>
            </a>
          </li>
        `;
      });
      html += '</ul>';
    });

    navContainer.innerHTML = html;

    // Lắng nghe sự kiện click: Khi người dùng bấm vào bất kỳ mục nào
    // thì lập tức mục đó sáng lên (màu xanh), đồng thời tắt sáng tất cả các mục còn lại
    navContainer.onclick = function (e) {
      const link = e.target.closest('.nav-link');
      if (!link) return;
      navContainer.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
      link.classList.add('active');
    };
  }

  window.MenuBuilder = {
    render: renderMenu
  };
})(window);
