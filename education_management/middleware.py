from django.http import HttpResponse

class CorsMiddleware:
    """
    Middleware xử lý CORS và vô hiệu hóa triệt để bộ nhớ đệm (Cache-Control: no-store)
    Đảm bảo trình duyệt luôn nạp mã nguồn JavaScript, CSS và HTML mới nhất 100%.
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
