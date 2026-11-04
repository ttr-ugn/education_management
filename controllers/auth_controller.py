"""
AUTH CONTROLLER - ĐIỀU KHIỂN XÁC THỰC & PHIÊN ĐĂNG NHẬP (MVC ARCHITECTURE)
Route prefix: /api/auth
"""

from backend.auth.routes import auth_bp

__all__ = ['auth_bp']
