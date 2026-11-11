"""
Education Management - Model & QuerySet Serializer Engine
Cung cấp bộ tuần tự hóa đối tượng Django Model sang định dạng từ điển (Dictionary) và JSON chuẩn RESTful.
"""

import json
from datetime import datetime, date, time
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, Union
from django.db import models
from django.db.models import QuerySet


class ModelJsonEncoder(json.JSONEncoder):
    """
    JSON Encoder mở rộng xử lý kiểu dữ liệu datetime, date, Decimal và UUID.
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%Y-%m-%d %H:%M:%S') if isinstance(obj, datetime) else obj.strftime('%Y-%m-%d')
        elif isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            return obj.to_dict()
        return super().default(obj)


class ModelSerializer:
    """
    Bộ tuần tự hóa đối tượng Django Model linh hoạt có hỗ trợ lọc trường và hiển thị nhãn choices.
    """

    @classmethod
    def serialize_instance(
        cls,
        instance: models.Model,
        fields: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        datetime_format: str = '%Y-%m-%d %H:%M:%S',
        date_format: str = '%Y-%m-%d',
        include_display_labels: bool = True
    ) -> Dict[str, Any]:
        """
        Chuyển một instance của Model sang từ điển Python.
        """
        if not instance:
            return {}

        # Nếu model có định nghĩa sẵn to_dict và không yêu cầu custom fields, ưu tiên dùng to_dict
        if hasattr(instance, 'to_dict') and not fields and not exclude:
            return instance.to_dict()

        opts = instance._meta
        data = {}

        fields_set = set(fields) if fields else None
        exclude_set = set(exclude) if exclude else set()

        for field in opts.concrete_fields:
            name = field.name
            if fields_set is not None and name not in fields_set:
                continue
            if name in exclude_set:
                continue

            value = getattr(instance, name)

            # Xử lý các kiểu dữ liệu đặc biệt
            if isinstance(value, datetime):
                data[name] = value.strftime(datetime_format)
            elif isinstance(value, date):
                data[name] = value.strftime(date_format)
            elif isinstance(value, models.Model):
                data[name] = value.pk
                data[f"{name}_ten"] = str(value)
            elif isinstance(field, models.ForeignKey) and value is None:
                data[name] = None
                data[f"{name}_ten"] = ""
            else:
                data[name] = value

            # Bổ sung nhãn display nếu trường có choices
            if include_display_labels and field.choices:
                display_method = getattr(instance, f"get_{name}_display", None)
                if display_method:
                    data[f"{name}_display"] = display_method()

        return data

    @classmethod
    def serialize_queryset(
        cls,
        queryset: Union[QuerySet, List[models.Model]],
        fields: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        datetime_format: str = '%Y-%m-%d %H:%M:%S'
    ) -> List[Dict[str, Any]]:
        """
        Tuần tự hóa toàn bộ danh sách QuerySet sang danh sách từ điển.
        """
        if not queryset:
            return []
        return [
            cls.serialize_instance(obj, fields=fields, exclude=exclude, datetime_format=datetime_format)
            for obj in queryset
        ]

    @classmethod
    def to_json(cls, data: Any, indent: Optional[int] = None) -> str:
        """
        Xuất dữ liệu sang chuỗi JSON chuẩn UTF-8.
        """
        return json.dumps(data, cls=ModelJsonEncoder, ensure_ascii=False, indent=indent)
