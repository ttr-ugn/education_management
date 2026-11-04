"""
MODELS PACKAGE - TẦNG MODEL TRONG KIẾN TRÚC MVC
Cung cấp các thực thể dữ liệu và lớp truy cập cơ sở dữ liệu SQLite.
"""

from .base_model import BaseModel
from .user_model import UserModel
from .document_model import DocumentModel
from .dossier_model import DossierModel
from .task_model import TaskModel
from .notification_model import NotificationModel
from .repository_model import RepositoryModel
from .chatbot_model import ChatbotModel

__all__ = [
    'BaseModel',
    'UserModel',
    'DocumentModel',
    'DossierModel',
    'TaskModel',
    'NotificationModel',
    'RepositoryModel',
    'ChatbotModel'
]
