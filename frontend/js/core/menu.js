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
    dashboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    docOut: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/><line x1="12" y1="11" x2="12" y2="17"/><polyline points="9 14 12 11 15 14"/></svg>',
    checkDraft: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
    signDoc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>',
    publish: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    tasks: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><polyline points="9 14 12 17 22 7"/></svg>',
    folder: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    notify: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
    chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    bot: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>',
    userCheck: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg>',
    userPlus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>',
    users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
  };

  function getMenuConfig(role) {
    const root = getRootPath();

    if (role === 'VAN_THU') {
      return [
        {
          title: 'Tổng quan',
          items: [
            { label: 'Bảng điều khiển', href: `${root}pages/dashboard.html`, icon: ICONS.dashboard, id: 'nav-dashboard' }
          ]
        },
        {
          title: 'Quản lý văn bản nội bộ',
          items: [
            { label: '📥 Tiếp nhận dự thảo từ Chuyên viên', href: `${root}pages/van-ban-di/kiem-tra.html`, icon: ICONS.checkDraft, id: 'nav-vb-kiemtra' },
            { label: 'Sổ theo dõi Văn bản đi', href: `${root}pages/van-ban-di/danh-sach.html`, icon: ICONS.docOut, id: 'nav-vb-di' },
            { label: '📑 Cấp số & Ban hành', href: `${root}pages/van-ban-di/ban-hanh.html`, icon: ICONS.publish, id: 'nav-vb-banhanh' }
          ]
        },
        {
          title: 'Nghiệp vụ lưu trữ & điều hành',
          items: [
            { label: 'Hồ sơ tài liệu', href: `${root}pages/ho-so/danh-sach.html`, icon: ICONS.folder, id: 'nav-ho-so' },
            { label: 'Theo dõi công việc', href: `${root}pages/cong-viec/danh-sach.html`, icon: ICONS.tasks, id: 'nav-cong-viec' },
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
            { label: 'Bảng điều khiển Lãnh đạo', href: `${root}pages/dashboard.html`, icon: ICONS.dashboard, id: 'nav-dashboard' }
          ]
        },
        {
          title: 'Phê duyệt & Ký số văn bản',
          items: [
            { label: '✍ Ký số & Duyệt văn bản', href: `${root}pages/van-ban-di/phe-duyet.html`, icon: ICONS.signDoc, id: 'nav-vb-phe-duyet' },
            { label: 'Sổ theo dõi Văn bản đi', href: `${root}pages/van-ban-di/danh-sach.html`, icon: ICONS.docOut, id: 'nav-vb-di' }
          ]
        },
        {
          title: 'Chỉ đạo & Điều hành',
          items: [
            { label: 'Giao việc mới', href: `${root}pages/cong-viec/giao-viec.html`, icon: ICONS.tasks, id: 'nav-giao-viec' },
            { label: 'Theo dõi tiến độ công việc', href: `${root}pages/cong-viec/danh-sach.html`, icon: ICONS.tasks, id: 'nav-cong-viec' },
            { label: 'Hồ sơ lưu trữ', href: `${root}pages/ho-so/danh-sach.html`, icon: ICONS.folder, id: 'nav-ho-so' },
            { label: 'Thông báo điều hành', href: `${root}pages/thong-bao.html`, icon: ICONS.notify, id: 'nav-thong-bao' },
            { label: 'Báo cáo thống kê', href: `${root}pages/thong-ke.html`, icon: ICONS.chart, id: 'nav-thong-ke' },
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
            { label: 'Bảng điều khiển cá nhân', href: `${root}pages/dashboard.html`, icon: ICONS.dashboard, id: 'nav-dashboard' }
          ]
        },
        {
          title: 'Quản lý văn bản nội bộ',
          items: [
            { label: '+ Soạn thảo dự thảo mới', href: `${root}pages/van-ban-di/soan-thao.html`, icon: ICONS.docOut, id: 'nav-vb-soan' },
            { label: 'Văn bản của tôi', href: `${root}pages/van-ban-di/danh-sach.html`, icon: ICONS.folder, id: 'nav-vb-di' }
          ]
        },
        {
          title: 'Nhiệm vụ & Báo cáo',
          items: [
            { label: 'Công việc được giao', href: `${root}pages/cong-viec/danh-sach.html`, icon: ICONS.tasks, id: 'nav-cong-viec' },
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
    const currentPath = window.location.pathname;

    let html = '';
    sections.forEach(sec => {
      html += `<div class="nav-section-title">${sec.title}</div>`;
      html += '<ul class="nav-list">';
      sec.items.forEach(item => {
        const itemFileName = item.href.split('/').pop().split('?')[0];
        const isActive = currentPath.endsWith(itemFileName) || (currentPath.endsWith('/') && itemFileName === 'index.html');

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
  }

  window.MenuBuilder = {
    render: renderMenu
  };
})(window);
