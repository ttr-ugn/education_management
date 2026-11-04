"""
CONTROLLERS PACKAGE - TẦNG CONTROLLER TRONG KIẾN TRÚC MVC
Cung cấp các bộ điều khiển tiếp nhận yêu cầu HTTP và điều phối dữ liệu với Model.
"""

from .auth_controller import auth_bp
from .users_controller import users_bp
from .documents_controller import documents_bp
from .ho_so_controller import ho_so_bp
from .kho_van_ban_controller import kho_van_ban_bp
from .thong_bao_controller import thong_bao_bp
from .cong_viec_controller import cong_viec_bp
from .chatbot_controller import chatbot_bp
from .decorators import login_required, role_required

__all__ = [
    'auth_bp',
    'users_bp',
    'documents_bp',
    'ho_so_bp',
    'kho_van_ban_bp',
    'thong_bao_bp',
    'cong_viec_bp',
    'chatbot_bp',
    'login_required',
    'role_required'
]
