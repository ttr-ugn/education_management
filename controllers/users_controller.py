"""
USERS CONTROLLER - ĐIỀU KHIỂN QUẢN TRỊ NGƯỜI DÙNG & TÀI KHOẢN (MVC ARCHITECTURE)
Route prefix: /api/users
"""

from backend.users.routes import users_bp

__all__ = ['users_bp']
