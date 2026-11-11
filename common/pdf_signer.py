"""
Education Management - PDF Digital Signing & Verification Engine
Module mô phỏng ký số số hóa và thẩm định tính toàn vẹn tài liệu theo Nghị định 30/2020/NĐ-CP.
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


class DigitalSignatureMetadata:
    """Đối tượng lưu trữ thông tin chứng thư số và dấu thời gian ký điện tử"""
    def __init__(
        self,
        signer_name: str,
        signer_title: str,
        organization: str,
        timestamp: Optional[datetime] = None,
        cert_serial: Optional[str] = None,
        x_coord: float = 400.0,
        y_coord: float = 650.0,
        page_number: int = 1
    ):
        self.signer_name = signer_name
        self.signer_title = signer_title
        self.organization = organization
        self.timestamp = timestamp or datetime.now()
        self.cert_serial = cert_serial or self._generate_cert_serial()
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.page_number = page_number

    def _generate_cert_serial(self) -> str:
        raw = f"{self.signer_name}:{self.organization}:{self.timestamp.isoformat()}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16].upper()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'signer_name': self.signer_name,
            'signer_title': self.signer_title,
            'organization': self.organization,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'cert_serial': self.cert_serial,
            'x_coord': self.x_coord,
            'y_coord': self.y_coord,
            'page_number': self.page_number,
        }


class PDFSignerService:
    """
    Dịch vụ ký số văn bản điện tử và thẩm định tính toàn vẹn checksum tệp tin.
    """

    @staticmethod
    def calculate_file_hash(file_path: str) -> Optional[str]:
        """
        Tính toán chuỗi băm mật mã SHA-256 của tệp tài liệu.
        """
        if not os.path.exists(file_path):
            return None
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def calculate_text_hash(content: str) -> str:
        """
        Tính toán chuỗi băm SHA-256 từ chuỗi nội dung văn bản.
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @classmethod
    def apply_digital_signature(
        cls,
        document_id: int,
        signer_name: str,
        signer_title: str,
        organization: str = "Sở Giáo dục và Đào tạo TP. Đà Nẵng",
        x: float = 400.0,
        y: float = 650.0,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Thực hiện gắn chứng thư số điện tử vào văn bản đi.
        """
        sig_meta = DigitalSignatureMetadata(
            signer_name=signer_name,
            signer_title=signer_title,
            organization=organization,
            x_coord=x,
            y_coord=y
        )
        file_checksum = cls.calculate_file_hash(file_path) if file_path else cls.calculate_text_hash(f"DOC-{document_id}")

        result = {
            'success': True,
            'document_id': document_id,
            'signature': sig_meta.to_dict(),
            'file_checksum': file_checksum,
            'signed_at': sig_meta.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'stamp_image': '/static/assets/img/seal-sgddt-signed.png',
            'status': 'VALID',
            'message': f"Đã hoàn tất ký số điện tử bởi {signer_name} ({signer_title})"
        }
        return result

    @classmethod
    def verify_signature_integrity(
        cls,
        original_checksum: str,
        current_file_path: str
    ) -> Tuple[bool, str]:
        """
        Kiểm tra văn bản có bị thay đổi hoặc giả mạo sau khi ký số hay không.
        """
        if not original_checksum:
            return False, "Thiếu mã băm chứng thực ban đầu để đối chiếu."
        
        current_hash = cls.calculate_file_hash(current_file_path)
        if not current_hash:
            return False, "Không tìm thấy tệp tin hiện tại trên hệ thống lưu trữ."

        if current_hash.lower() == original_checksum.lower():
            return True, "Chữ ký số hợp lệ và toàn vẹn. Tài liệu không bị chỉnh sửa sau khi ký."
        else:
            return False, "CẢNH BÁO: Mã băm tài liệu không trùng khớp! Tệp có dấu hiệu bị thay đổi sau khi ký."
