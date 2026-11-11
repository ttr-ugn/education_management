"""
Education Management - Unit Tests for Dashboard Metrics & Analytics (Dashboard)
Kiểm tra tổng hợp các thẻ chỉ số KPI, dữ liệu biểu đồ xu hướng tháng và tỷ lệ phòng ban.
"""

from django.test import TestCase

from dashboard.services import DashboardMetricsService
from van_ban.models import VanBanDi
from cong_viec.models import CongViec
from ho_so.models import HoSoLuuTru


class DashboardServiceTestCase(TestCase):
    """Kiểm tra dịch vụ phân tích dữ liệu tổng thể"""

    def test_get_summary_cards(self):
        summary = DashboardMetricsService.get_summary_cards()
        self.assertIn('van_ban_di', summary)
        self.assertIn('van_ban_den', summary)
        self.assertIn('cong_viec', summary)
        self.assertIn('ho_so', summary)
        self.assertIsInstance(summary['cong_viec']['kpi_rate'], float)

    def test_get_monthly_chart_data(self):
        chart_data = DashboardMetricsService.get_monthly_chart_data(2026)
        self.assertEqual(len(chart_data['labels']), 12)
        self.assertEqual(len(chart_data['van_ban_di']), 12)
        self.assertEqual(len(chart_data['van_ban_den']), 12)

    def test_get_department_workload(self):
        workload = DashboardMetricsService.get_department_workload()
        self.assertIsInstance(workload, list)
        self.assertGreater(len(workload), 0)
        self.assertIn('phong_ban', workload[0])
        self.assertIn('completion_pct', workload[0])
