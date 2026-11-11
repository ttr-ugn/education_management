"""
Education Management - Custom Middleware Suite
Cung cấp các lớp middleware xử lý CORS, an toàn thông tin (Security Headers), và đo lường hiệu năng.
"""

import time
import uuid
from django.http import HttpResponse


class CorsMiddleware:
    """
    Middleware xử lý CORS và vô hiệu hóa bộ nhớ đệm (Cache-Control: no-store).
    Đảm bảo trình duyệt luôn nạp mã nguồn JavaScript, CSS và HTML mới nhất.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response.status_code = 200
        else:
            response = self.get_response(request)

        # 1. Cấu hình CORS đa nguồn (PyCharm 63342, Live Server 5500, Port 8000)
        origin = request.headers.get('Origin')
        if origin:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
        else:
            response['Access-Control-Allow-Origin'] = '*'

        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, X-CSRFToken'

        # 2. Xóa bỏ hoàn toàn nguy cơ lưu bộ nhớ đệm cũ (Anti-Cache Headers)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response


class SecurityHeadersMiddleware:
    """
    Middleware bổ sung các tiêu chuẩn bảo vệ HTTP Security Headers cho cổng thông tin cơ quan nhà nước.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Ngăn chặn clickjacking
        response['X-Frame-Options'] = 'SAMEORIGIN'
        # Ngăn chặn MIME-type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        # Kích hoạt bộ lọc XSS của trình duyệt
        response['X-XSS-Protection'] = '1; mode=block'
        # Kiểm soát chính sách Referrer
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response


class PerformanceProfilingMiddleware:
    """
    Middleware đo thời gian thực thi của mỗi request và gắn mã định danh Request-ID.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        request.request_id = request_id

        response = self.get_response(request)

        duration = time.time() - start_time
        response['X-Request-ID'] = request_id
        response['X-Response-Time-Ms'] = f"{duration * 1000:.2f}"

        return response
