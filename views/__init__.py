"""
VIEWS PACKAGE - TẦNG VIEW TRONG KIẾN TRÚC MVC
Chứa định nghĩa điều hướng và phục vụ giao diện người dùng (User Interface).
Toàn bộ các trang giao diện HTML5, CSS3, JavaScript tương tác nằm tại thư mục frontend/.
"""

import os
from pathlib import Path
from flask import send_from_directory

VIEW_DIR = Path(__file__).resolve().parent.parent / 'frontend'

def render_page(page_path: str):
    """Phục vụ file giao diện HTML từ thư mục Views (frontend)."""
    return send_from_directory(str(VIEW_DIR), page_path)
