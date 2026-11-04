/**
 * DU-LIEU-CHATBOT.JS - DỮ LIỆU MẪU TRỢ LÝ ẢO HỖ TRỢ VĂN BẢN ĐIỀU HÀNH
 */

(function (window) {
  const KNOWLEDGE_BASE = [
    {
      keywords: ['quy trình', 'tiếp nhận', 'văn bản đến'],
      response: 'Quy trình tiếp nhận văn bản đến tại Sở GD&ĐT Đà Nẵng gồm 4 bước:<br>1. <b>Văn thư tiếp nhận:</b> Kiểm tra tính hợp lệ, đóng dấu đến, vào sổ văn bản và scan đính kèm file.<br>2. <b>Trình Lãnh đạo:</b> Văn thư chuyển văn bản đến Lãnh đạo Sở phê duyệt và chỉ đạo phân công.<br>3. <b>Phân công chuyên viên:</b> Lãnh đạo chọn chuyên viên/phòng ban chủ trì kèm thời hạn xử lý.<br>4. <b>Chuyên viên xử lý:</b> Nghiên cứu văn bản, soạn thảo văn bản phản hồi hoặc lưu hồ sơ theo dõi.'
    },
    {
      keywords: ['văn bản đi', 'ban hành', 'soạn thảo'],
      response: 'Quy trình ban hành văn bản đi gồm các bước:<br>1. <b>Chuyên viên soạn thảo:</b> Tạo dự thảo, đính kèm tệp văn bản và tờ trình.<br>2. <b>Lãnh đạo phê duyệt:</b> Lãnh đạo Sở kiểm duyệt nội dung, ký số hoặc yêu cầu chỉnh sửa.<br>3. <b>Văn thư phát hành:</b> Văn thư kiểm tra thể thức, lấy số văn bản chính thức, đóng dấu số và gửi đến các cơ quan nhận.'
    },
    {
      keywords: ['lãnh đạo', 'duyệt', 'chức năng'],
      response: 'Lãnh đạo cơ quan trong hệ thống có các thẩm quyền:<br>- Phê duyệt chỉ đạo và phân công văn bản đến cho các phòng ban.<br>- Ký duyệt dự thảo văn bản đi.<br>- Giao việc, đôn đốc tiến độ và đánh giá kết quả hoàn thành nhiệm vụ của chuyên viên.<br>- Tra cứu toàn bộ hồ sơ, văn bản lưu trữ và báo cáo thống kê ngành.'
    },
    {
      keywords: ['đổi mật khẩu', 'mật khẩu', 'quên'],
      response: 'Để đổi mật khẩu, đồng chí vào mục <b>"Hồ sơ cá nhân"</b> hoặc chọn <b>"Đổi mật khẩu"</b> trên thanh điều hướng. Nếu quên mật khẩu, đồng chí vui lòng liên hệ trực tiếp <b>Văn thư Sở</b> để được cấp lại mật khẩu tạm thời.'
    },
    {
      keywords: ['chào', 'hello', 'hi', 'bạn là ai'],
      response: 'Xin chào đồng chí! Tôi là Trợ lý ảo điều hành văn bản của Sở Giáo dục và Đào tạo TP. Đà Nẵng. Tôi có thể hỗ trợ đồng chí tra cứu quy trình văn bản đi - đến, thể thức văn bản hành chính và thông tin điều hành nội bộ. Đồng chí cần hỗ trợ vấn đề gì hôm nay?'
    }
  ];

  const chatbotService = {
    // TODO(nhóm): thay bằng api.post('/api/chatbot', { message })
    sendMessage: async function (userText) {
      // Giả lập độ trễ phản hồi của AI (400ms)
      await new Promise(r => setTimeout(r, 450));

      const lower = userText.toLowerCase();
      for (const item of KNOWLEDGE_BASE) {
        if (item.keywords.some(k => lower.includes(k))) {
          return item.response;
        }
      }

      return `Hệ thống đã ghi nhận câu hỏi: "<i>${userText}</i>". Trợ lý ảo khuyến nghị đồng chí kiểm tra trong danh mục văn bản hoặc liên hệ Văn phòng Sở GD&ĐT (SĐT: 0236.3822.456) để được hướng dẫn chi tiết nhất.`;
    }
  };

  window.chatbotService = chatbotService;
})(window);
