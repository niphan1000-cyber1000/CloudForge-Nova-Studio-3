"""
Golden Test Cases — Requirement Spec Validation
==================================================
ทดสอบว่า pydantic model ของ Requirement Spec ทำงานถูกต้องตาม
docs/requirement-spec-schema.json

รันด้วยคำสั่ง: pytest tests/test_requirement_spec.py -v
"""

import pytest
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Literal


# ============================================================
# Pydantic Models (ตรงตาม docs/requirement-spec-schema.json)
# ============================================================
class ScaleSpec(BaseModel):
    expected_users: int
    expected_requests_per_second: Optional[int] = None
    data_volume_gb: Optional[float] = None
    growth_expectation: Optional[Literal["stable", "moderate_growth", "rapid_growth", "unpredictable"]] = None


class AvailabilitySpec(BaseModel):
    sla_target: Optional[Literal["99%", "99.9%", "99.95%", "99.99%"]] = None
    multi_region: Optional[bool] = None
    disaster_recovery: Optional[bool] = None


class BudgetSpec(BaseModel):
    tier: Literal["minimal", "low", "medium", "high", "enterprise"]
    monthly_budget_usd: Optional[float] = None
    cost_priority: Optional[Literal["minimize_cost", "balanced", "prioritize_performance"]] = None


class ComplianceSpec(BaseModel):
    standards: Optional[List[str]] = []
    data_residency: Optional[List[str]] = []
    data_sensitivity: Optional[Literal["public", "internal", "confidential", "restricted"]] = None


class CloudPreferenceSpec(BaseModel):
    providers: List[Literal["aws", "azure", "gcp"]] = Field(min_length=1)
    preferred_regions: Optional[List[str]] = []
    existing_infrastructure: Optional[str] = None


class RequirementSpec(BaseModel):
    """Pydantic model บังคับโครงสร้างของ Requirement Spec"""
    project_name: str
    workload_type: Literal[
        "web_application", "api_backend", "data_pipeline",
        "machine_learning", "batch_processing", "static_website",
        "microservices", "other"
    ]
    scale: ScaleSpec
    budget: BudgetSpec
    cloud_preference: CloudPreferenceSpec
    availability: Optional[AvailabilitySpec] = None
    compliance: Optional[ComplianceSpec] = None
    additional_notes: Optional[str] = None


# ============================================================
# Golden Test Cases
# ============================================================
def test_valid_requirement_spec_passes():
    """ข้อมูลที่ถูกต้องครบถ้วนต้อง validate ผ่าน"""
    valid_data = {
        "project_name": "ระบบตัวอย่าง",
        "workload_type": "web_application",
        "scale": {"expected_users": 5000},
        "budget": {"tier": "medium"},
        "cloud_preference": {"providers": ["aws"]}
    }
    spec = RequirementSpec(**valid_data)
    assert spec.project_name == "ระบบตัวอย่าง"
    assert spec.scale.expected_users == 5000
    assert spec.budget.tier == "medium"
    assert spec.cloud_preference.providers == ["aws"]


def test_invalid_budget_tier_raises_error():
    """budget.tier ที่ไม่อยู่ในรายการที่อนุญาต ต้อง raise ValidationError"""
    invalid_data = {
        "project_name": "ระบบตัวอย่าง",
        "workload_type": "web_application",
        "scale": {"expected_users": 5000},
        "budget": {"tier": "super_expensive"},  # ค่าที่ไม่มีใน schema
        "cloud_preference": {"providers": ["aws"]}
    }
    with pytest.raises(ValidationError) as exc_info:
        RequirementSpec(**invalid_data)
    assert "budget.tier" in str(exc_info.value) or "tier" in str(exc_info.value)


def test_invalid_workload_type_raises_error():
    """workload_type ที่ไม่อยู่ในรายการที่อนุญาต ต้อง raise ValidationError"""
    invalid_data = {
        "project_name": "ระบบตัวอย่าง",
        "workload_type": "quantum_computing",  # ค่าที่ไม่มีใน schema
        "scale": {"expected_users": 5000},
        "budget": {"tier": "medium"},
        "cloud_preference": {"providers": ["aws"]}
    }
    with pytest.raises(ValidationError):
        RequirementSpec(**invalid_data)


def test_missing_required_field_raises_error():
    """ถ้าขาด field ที่จำเป็น (เช่น project_name) ต้อง raise ValidationError"""
    incomplete_data = {
        "workload_type": "web_application",
        "scale": {"expected_users": 5000},
        "budget": {"tier": "medium"},
        "cloud_preference": {"providers": ["aws"]}
        # ขาด project_name ไป
    }
    with pytest.raises(ValidationError):
        RequirementSpec(**incomplete_data)


def test_empty_cloud_providers_list_raises_error():
    """cloud_preference.providers ต้องมีอย่างน้อย 1 ตัว ห้ามเป็น list ว่าง"""
    invalid_data = {
        "project_name": "ระบบตัวอย่าง",
        "workload_type": "web_application",
        "scale": {"expected_users": 5000},
        "budget": {"tier": "medium"},
        "cloud_preference": {"providers": []}  # list ว่าง ไม่ควรผ่าน
    }
    with pytest.raises(ValidationError):
        RequirementSpec(**invalid_data)


def test_multi_cloud_providers_allowed():
    """providers ควรรองรับการระบุหลาย cloud พร้อมกัน (สำหรับ Phase 5 multi-cloud)"""
    valid_data = {
        "project_name": "ระบบ multi-cloud",
        "workload_type": "web_application",
        "scale": {"expected_users": 1000},
        "budget": {"tier": "high"},
        "cloud_preference": {"providers": ["aws", "azure", "gcp"]}
    }
    spec = RequirementSpec(**valid_data)
    assert len(spec.cloud_preference.providers) == 3
