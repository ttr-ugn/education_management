"""
Education Management - Custom Pagination & Sliding Window Helper
Cung cấp các tiện ích phân trang thông minh với dải số trang trượt và giữ nguyên tham số lọc URL.
"""

from typing import List, Dict, Any, Union, Optional
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def build_page_range(
    current_page: int,
    total_pages: int,
    delta: int = 2
) -> List[Union[int, str]]:
    """
    Tạo danh sách phân trang dạng rút gọn với dấu '...':
    Ví dụ: [1, 2, 3, 4, 5, '...', 20] hoặc [1, '...', 7, 8, 9, 10, 11, '...', 30]
    """
    if total_pages <= 1:
        return [1] if total_pages == 1 else []

    range_left = max(1, current_page - delta)
    range_right = min(total_pages, current_page + delta)

    pages: List[Union[int, str]] = []
    
    # Luôn hiển thị trang đầu tiên
    if range_left > 1:
        pages.append(1)
        if range_left > 2:
            pages.append('...')

    for p in range(range_left, range_right + 1):
        pages.append(p)

    # Luôn hiển thị trang cuối cùng
    if range_right < total_pages:
        if range_right < total_pages - 1:
            pages.append('...')
        pages.append(total_pages)

    return pages


def paginate_queryset(
    queryset_or_list: Any,
    page_number: Union[int, str] = 1,
    per_page: int = 10
) -> Dict[str, Any]:
    """
    Phân trang tập dữ liệu với đầy đủ metadata điều hướng.
    """
    paginator = Paginator(queryset_or_list, per_page)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    current = page_obj.number
    total = paginator.num_pages

    return {
        'items': page_obj.object_list,
        'page_obj': page_obj,
        'current_page': current,
        'total_pages': total,
        'total_items': paginator.count,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'start_index': page_obj.start_index(),
        'end_index': page_obj.end_index(),
        'page_range': build_page_range(current, total),
    }
