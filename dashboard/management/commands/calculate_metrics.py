"""
Management Command: calculate_metrics
Tính toán và kết xuất tổng hợp chỉ số KPI điều hành hàng ngày của Sở GD&ĐT.
"""

from datetime import datetime
from django.core.management.base import BaseCommand
from dashboard.services import DashboardMetricsService
from common.audit import log_system_action


class Command(BaseCommand):
    help = 'Tính toán và ghi nhận báo cáo tổng hợp hiệu suất điều hành hàng ngày'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Bắt đầu tính toán chỉ số điều hành tổng thể..."))

        summary = DashboardMetricsService.get_summary_cards()
        dept_workload = DashboardMetricsService.get_department_workload()

        report_lines = [
            f"=== BÁO CÁO ĐIỀU HÀNH NGÀY {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ===",
            f"- Văn bản đi: Tổng {summary['van_ban_di']['total']} (Đã ban hành: {summary['van_ban_di']['issued']}, Đang xử lý: {summary['van_ban_di']['pending']})",
            f"- Văn bản đến: Tổng {summary['van_ban_den']['total']} (Đang xử lý: {summary['van_ban_den']['processing']})",
            f"- Nhiệm vụ / Công việc: Tổng {summary['cong_viec']['total']} (Hoàn thành: {summary['cong_viec']['completed']}, Quá hạn: {summary['cong_viec']['overdue']})",
            f"- Tỷ lệ đạt KPI: {summary['cong_viec']['kpi_rate']}%",
            f"- Hồ sơ lưu trữ: {summary['ho_so']['total_dossiers']} hồ sơ ({summary['ho_so']['archived_docs']} văn bản lưu trữ)",
            "-------------------------------------------------------",
            "Khối lượng công việc theo phòng ban:",
        ]

        for dept in dept_workload:
            report_lines.append(f"  + {dept['phong_ban']}: {dept['completed']}/{dept['total_tasks']} hoàn thành ({dept['completion_pct']}%)")

        full_report = "\n".join(report_lines)
        self.stdout.write(full_report)

        # Lưu lại vào nhật ký hệ thống
        log_system_action(
            hanh_dong="Tính toán chỉ số KPI tự động",
            chi_tiet=f"Đã tổng hợp số liệu ngày {datetime.now().strftime('%d/%m/%Y')}: KPI={summary['cong_viec']['kpi_rate']}%",
            nguoi_thuc_hien="Cron Job / Scheduler"
        )

        self.stdout.write(self.style.SUCCESS("Đã ghi nhận báo cáo KPI vào nhật ký hệ thống thành công."))
