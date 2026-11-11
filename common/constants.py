"""
Education Management - System Constants & Enums
Định nghĩa toàn bộ các hằng số trạng thái, vai trò, quyền hạn và mã lỗi của hệ thống.
"""

from enum import Enum


class VaiTroNguoiDung:
    """Các vai trò người dùng trong hệ thống"""
    VAN_THU = 'VAN_THU'
    CHUYEN_VIEN = 'CHUYEN_VIEN'
    LANH_DAO = 'LANH_DAO'

    LABELS = {
        VAN_THU: 'Văn thư Sở',
        CHUYEN_VIEN: 'Chuyên viên Phòng ban',
        LANH_DAO: 'Lãnh đạo Sở',
    }

    CHOICES = [
        (VAN_THU, 'Văn thư'),
        (CHUYEN_VIEN, 'Chuyên viên'),
        (LANH_DAO, 'Lãnh đạo'),
    ]

    @classmethod
    def get_label(cls, role_code: str) -> str:
        return cls.LABELS.get(role_code, role_code)


class TrangThaiNguoiDung:
    """Trạng thái tài khoản người dùng"""
    CHO_DUYET = 'CHO_DUYET'
    HOAT_DONG = 'HOAT_DONG'
    TU_CHOI = 'TU_CHOI'
    BI_KHOA = 'BI_KHOA'

    CHOICES = [
        (CHO_DUYET, 'Chờ duyệt'),
        (HOAT_DONG, 'Hoạt động'),
        (TU_CHOI, 'Từ chối'),
        (BI_KHOA, 'Bị khóa'),
    ]


class TrangThaiVanBanDi:
    """Trạng thái chu trình xử lý Văn bản đi"""
    DU_THAO = 'DU_THAO'
    CHO_VAN_THU_KIEM_TRA = 'CHO_VAN_THU_KIEM_TRA'
    VAN_THU_TRA_LAI = 'VAN_THU_TRA_LAI'
    CHO_LANH_DAO_DUYET = 'CHO_LANH_DAO_DUYET'
    LANH_DAO_TRA_LAI = 'LANH_DAO_TRA_LAI'
    DA_KY_SO = 'DA_KY_SO'
    CHO_CAP_SO = 'CHO_CAP_SO'
    DA_BAN_HANH = 'DA_BAN_HANH'
    HUY_BO = 'HUY_BO'

    LABELS = {
        DU_THAO: 'Dự thảo',
        CHO_VAN_THU_KIEM_TRA: 'Chờ Văn thư kiểm tra',
        VAN_THU_TRA_LAI: 'Văn thư trả lại hiệu chỉnh',
        CHO_LANH_DAO_DUYET: 'Chờ Lãnh đạo duyệt ký',
        LANH_DAO_TRA_LAI: 'Lãnh đạo trả lại hiệu chỉnh',
        DA_KY_SO: 'Đã ký số phê duyệt',
        CHO_CAP_SO: 'Chờ cấp số văn bản',
        DA_BAN_HANH: 'Đã ban hành chính thức',
        HUY_BO: 'Hủy bỏ',
    }

    CHOICES = [(k, v) for k, v in LABELS.items()]

    @classmethod
    def get_label(cls, code: str) -> str:
        return cls.LABELS.get(code, code)


class TrangThaiVanBanDen:
    """Trạng thái xử lý Văn bản đến"""
    CHO_TIEP_NHAN = 'CHO_TIEP_NHAN'
    DA_TIEP_NHAN = 'DA_TIEP_NHAN'
    CHO_CHI_DAO = 'CHO_CHI_DAO'
    DANG_XU_LY = 'DANG_XU_LY'
    HOAN_THANH = 'HOAN_THANH'
    LUU_TRU = 'LUU_TRU'

    LABELS = {
        CHO_TIEP_NHAN: 'Chờ tiếp nhận vào sổ',
        DA_TIEP_NHAN: 'Đã tiếp nhận',
        CHO_CHI_DAO: 'Chờ Lãnh đạo cho ý kiến chỉ đạo',
        DANG_XU_LY: 'Đang triển khai xử lý',
        HOAN_THANH: 'Đã xử lý xong',
        LUU_TRU: 'Đã đưa vào hồ sơ lưu trữ',
    }


class TrangThaiCongViec:
    """Trạng thái tiến độ thực hiện Công việc"""
    CHUA_THUC_HIEN = 'CHUA_THUC_HIEN'
    DANG_THUC_HIEN = 'DANG_THUC_HIEN'
    CHO_DANH_GIA = 'CHO_DANH_GIA'
    HOAN_THANH = 'HOAN_THANH'
    QUA_HAN = 'QUA_HAN'

    LABELS = {
        CHUA_THUC_HIEN: 'Chưa thực hiện',
        DANG_THUC_HIEN: 'Đang thực hiện',
        CHO_DANH_GIA: 'Chờ đánh giá nghiệm thu',
        HOAN_THANH: 'Hoàn thành đúng hạn',
        QUA_HAN: 'Quá hạn hoàn thành',
    }

    CHOICES = [(k, v) for k, v in LABELS.items()]


class MucDoUuTien:
    """Mức độ ưu tiên của công việc và văn bản"""
    THAP = 'THAP'
    TRUNG_BINH = 'TRUNG_BINH'
    CAO = 'CAO'
    KHAN_CAP = 'KHAN_CAP'

    LABELS = {
        THAP: 'Thấp',
        TRUNG_BINH: 'Trung bình',
        CAO: 'Cao',
        KHAN_CAP: 'Khẩn cấp / Hỏa tốc',
    }

    CHOICES = [(k, v) for k, v in LABELS.items()]


class TrangThaiHoSo:
    """Tình trạng hồ sơ lưu trữ"""
    DANG_THU_THAP = 'DANG_THU_THAP'
    DA_NOP_LUU_TRU = 'DA_NOP_LUU_TRU'
    HOAN_TAT = 'HOAN_TAT'
    HUY_LUC = 'HUY_LUC'

    LABELS = {
        DANG_THU_THAP: 'Đang thu thập tài liệu',
        DA_NOP_LUU_TRU: 'Đã nộp lưu trữ cơ quan',
        HOAN_TAT: 'Đã hoàn tất đóng băng hồ sơ',
        HUY_LUC: 'Hết thời hạn bảo quản / Đã tiêu hủy',
    }

    CHOICES = [(k, v) for k, v in LABELS.items()]


class ThoiHanBaoQuan:
    """Quy chuẩn thời hạn bảo quản hồ sơ theo Nghị định 30/2020/NĐ-CP"""
    MOT_NAM = '1 năm'
    NAM_NAM = '5 năm'
    MUOI_NAM = '10 năm'
    HAI_MUOI_NAM = '20 năm'
    BA_MUOI_NAM = '30 năm'
    VINH_VIEN = 'Vĩnh viễn'

    CHOICES = [
        (MOT_NAM, '1 năm'),
        (NAM_NAM, '5 năm'),
        (MUOI_NAM, '10 năm'),
        (HAI_MUOI_NAM, '20 năm'),
        (BA_MUOI_NAM, '30 năm'),
        (VINH_VIEN, 'Vĩnh viễn'),
    ]


class LoaiThongBao:
    """Phân loại thông báo hệ thống"""
    VAN_BAN = 'Văn bản'
    CONG_VIEC = 'Công việc'
    HO_SO = 'Hồ sơ'
    HE_THONG = 'Hệ thống'
    CANH_BAO = 'Cảnh báo'


class SystemErrorCodes:
    """Mã định danh lỗi chuẩn hóa cho toàn hệ thống"""
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    AUTHENTICATION_FAILED = 1001
    PERMISSION_DENIED = 1002
    INVALID_PARAMETERS = 1003
    RECORD_NOT_FOUND = 1004
    STATE_TRANSITION_INVALID = 1005
    DOCUMENT_ALREADY_ISSUED = 1006
    SIGNATURE_VERIFICATION_FAILED = 1007
    TASK_ALREADY_COMPLETED = 1008
    FILE_FORMAT_NOT_ALLOWED = 1009
    FILE_SIZE_EXCEEDED = 1010
