"""
Unit Tests สำหรับ agents/cost_estimation.py
==============================================
ทดสอบ Cost Estimation Agent (Agent ตัวที่ 7)

รันด้วยคำสั่ง: pytest tests/test_cost_estimation.py -v
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.cost_estimation import estimate_cost_mock


# ============================================================
# ข้อมูลทดสอบร่วม
# ============================================================
SAMPLE_ARCHITECTURE = {
    "components": [
        {"name": "Load Balancer", "service": "AWS Application Load Balancer (ALB)"},
        {"name": "Compute", "service": "Amazon EC2 Auto Scaling Group"},
        {"name": "Database", "service": "Amazon RDS (PostgreSQL)"},
        {"name": "Cache", "service": "Amazon ElastiCache (Redis)"},
        {"name": "Storage", "service": "Amazon S3"},
    ]
}


class TestCostEstimationAgent:

    def test_returns_dict_with_required_keys(self):
        req = {"budget": {"monthly_budget_usd": 1000}}
        result = estimate_cost_mock(SAMPLE_ARCHITECTURE, req)
        required_keys = ["line_items", "total_estimated_monthly_usd", "budget_status", "budget_message"]
        for key in required_keys:
            assert key in result

    def test_line_items_match_number_of_components(self):
        req = {"budget": {"monthly_budget_usd": 1000}}
        result = estimate_cost_mock(SAMPLE_ARCHITECTURE, req)
        assert len(result["line_items"]) == len(SAMPLE_ARCHITECTURE["components"])

    def test_total_cost_is_sum_of_line_items(self):
        req = {"budget": {"monthly_budget_usd": 1000}}
        result = estimate_cost_mock(SAMPLE_ARCHITECTURE, req)
        expected_total = sum(item["estimated_monthly_usd"] for item in result["line_items"])
        assert result["total_estimated_monthly_usd"] == round(expected_total, 2)

    def test_within_budget_status_when_cost_is_low(self):
        req = {"budget": {"monthly_budget_usd": 10000}}  # งบสูงมาก ควรอยู่ในงบแน่นอน
        result = estimate_cost_mock(SAMPLE_ARCHITECTURE, req)
        assert result["budget_status"] == "WITHIN_BUDGET"

    def test_over_budget_status_when_budget_too_low(self):
        req = {"budget": {"monthly_budget_usd": 10}}  # งบต่ำมาก ควรเกินงบแน่นอน
        result = estimate_cost_mock(SAMPLE_ARCHITECTURE, req)
        assert result["budget_status"] == "OVER_BUDGET"
        assert "เกินงบ" in result["budget_message"]

    def test_unknown_status_when_no_budget_specified(self):
        req = {"budget": {}}  # ไม่ได้ระบุ monthly_budget_usd
        result = estimate_cost_mock(SAMPLE_ARCHITECTURE, req)
        assert result["budget_status"] == "UNKNOWN"

    def test_auto_scaling_group_costs_double_base_price(self):
        """Compute แบบ Auto Scaling Group ควรคิดราคาเป็น 2 เท่า (2 instances)"""
        single_component_arch = {
            "components": [
                {"name": "Compute", "service": "Amazon EC2 Auto Scaling Group"}
            ]
        }
        req = {"budget": {"monthly_budget_usd": 1000}}
        result = estimate_cost_mock(single_component_arch, req)
        # base price = 60, multiplier = 2 -> ควรได้ 120
        assert result["line_items"][0]["estimated_monthly_usd"] == 120

    def test_unknown_service_uses_default_price(self):
        """Service ที่ไม่รู้จักในตารางราคา ควรใช้ราคา default แทน ไม่ error"""
        unknown_service_arch = {
            "components": [
                {"name": "Mystery Component", "service": "Some Unknown AWS Service"}
            ]
        }
        req = {"budget": {"monthly_budget_usd": 1000}}
        result = estimate_cost_mock(unknown_service_arch, req)
        assert result["line_items"][0]["estimated_monthly_usd"] == 30  # default price

    def test_empty_components_list_returns_zero_total(self):
        empty_arch = {"components": []}
        req = {"budget": {"monthly_budget_usd": 1000}}
        result = estimate_cost_mock(empty_arch, req)
        assert result["total_estimated_monthly_usd"] == 0
        assert result["line_items"] == []
