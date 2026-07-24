"""
Unit Tests สำหรับ agents/mock_pipeline.py
==============================================
ทดสอบ 6 Agent + Generator-Critic Loop เวอร์ชัน mock ทั้งหมด

รันด้วยคำสั่ง: pytest tests/test_mock_pipeline.py -v

หมายเหตุ: ไฟล์นี้ import ฟังก์ชันจาก agents/mock_pipeline.py โดยตรง
ต้องรันจาก root ของ repo (ที่มีโฟลเดอร์ agents/ อยู่ระดับเดียวกับ tests/)
"""

import sys
import os
import json
import pytest

# เพิ่ม root ของ repo เข้า path เพื่อให้ import agents ได้
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.mock_pipeline import (
    analyze_requirement_mock,
    design_architecture_mock,
    generate_iac_mock,
    review_security_mock,
    fix_iac_mock,
    run_generator_critic_loop,
    generate_documentation_mock,
    qa_critic_review_mock,
)


# ============================================================
# Agent 1: Requirements Agent
# ============================================================
class TestRequirementsAgent:
    def test_returns_dict(self):
        result = analyze_requirement_mock("ทดสอบระบบเว็บแอป")
        assert isinstance(result, dict)

    def test_has_required_top_level_keys(self):
        result = analyze_requirement_mock("ทดสอบระบบเว็บแอป")
        required_keys = ["project_name", "workload_type", "scale", "budget", "cloud_preference"]
        for key in required_keys:
            assert key in result, f"ขาด key: {key}"

    def test_cloud_preference_has_at_least_one_provider(self):
        result = analyze_requirement_mock("ทดสอบระบบเว็บแอป")
        providers = result["cloud_preference"]["providers"]
        assert len(providers) >= 1
        assert providers[0] in ["aws", "azure", "gcp"]


# ============================================================
# Agent 2: Architecture Agent
# ============================================================
class TestArchitectureAgent:
    def setup_method(self):
        self.requirement_spec = analyze_requirement_mock("ทดสอบระบบเว็บแอป")

    def test_returns_dict_with_components(self):
        result = design_architecture_mock(self.requirement_spec)
        assert "components" in result
        assert isinstance(result["components"], list)
        assert len(result["components"]) > 0

    def test_provider_matches_requirement(self):
        result = design_architecture_mock(self.requirement_spec)
        expected_provider = self.requirement_spec["cloud_preference"]["providers"][0]
        assert result["provider"] == expected_provider

    def test_each_component_has_required_fields(self):
        result = design_architecture_mock(self.requirement_spec)
        for component in result["components"]:
            assert "name" in component
            assert "service" in component
            assert "purpose" in component


# ============================================================
# Agent 3: IaC Generator Agent
# ============================================================
class TestIaCGeneratorAgent:
    def setup_method(self):
        requirement_spec = analyze_requirement_mock("ทดสอบระบบเว็บแอป")
        self.architecture = design_architecture_mock(requirement_spec)

    def test_returns_string(self):
        result = generate_iac_mock(self.architecture)
        assert isinstance(result, str)

    def test_contains_terraform_provider_block(self):
        result = generate_iac_mock(self.architecture)
        assert "terraform {" in result
        assert 'provider "aws"' in result

    def test_contains_expected_resources(self):
        result = generate_iac_mock(self.architecture)
        assert 'resource "aws_vpc"' in result
        assert 'resource "aws_s3_bucket"' in result
        assert 'resource "aws_db_instance"' in result


# ============================================================
# Agent 4: Security Reviewer Agent
# ============================================================
class TestSecurityReviewerAgent:
    def test_detects_missing_encryption(self):
        code_without_encryption = 'resource "aws_db_instance" "main" {\n  engine = "postgres"\n}'
        result = review_security_mock(code_without_encryption)
        assert result["overall_status"] == "NEEDS_REVISION"
        assert result["failed_checks"] > 0

    def test_approves_code_with_all_checks_passed(self):
        good_code = '''
storage_encrypted = true
resource "aws_vpc" "main" {}
internal           = false
'''
        # เพิ่ม public_access_block เพื่อให้ผ่านครบทุกเช็ค
        good_code_full = good_code + '\naws_s3_bucket_public_access_block'
        result = review_security_mock(good_code_full)
        assert result["overall_status"] == "APPROVED"
        assert result["failed_checks"] == 0

    def test_returns_findings_list(self):
        result = review_security_mock("")
        assert "findings" in result
        assert isinstance(result["findings"], list)


# ============================================================
# Fix Function
# ============================================================
class TestFixIaCFunction:
    def test_adds_public_access_block_when_missing(self):
        code = 'resource "aws_s3_bucket" "main" {}'
        findings = [{"status": "FAIL", "check": "S3 Public Access Block"}]
        fixed = fix_iac_mock(code, findings)
        assert "aws_s3_bucket_public_access_block" in fixed

    def test_does_not_modify_code_when_no_findings_need_fixing(self):
        code = 'resource "aws_s3_bucket" "main" {}'
        findings = [{"status": "PASS", "check": "Something else"}]
        fixed = fix_iac_mock(code, findings)
        assert fixed == code


# ============================================================
# Generator-Critic Loop
# ============================================================
class TestGeneratorCriticLoop:
    def setup_method(self):
        requirement_spec = analyze_requirement_mock("ทดสอบระบบเว็บแอป")
        self.architecture = design_architecture_mock(requirement_spec)

    def test_loop_eventually_approves_or_gives_up(self):
        result = run_generator_critic_loop(self.architecture, max_iterations=3)
        assert result["final_status"] in ["APPROVED", "NEEDS_HUMAN_REVIEW"]

    def test_loop_respects_max_iterations(self):
        result = run_generator_critic_loop(self.architecture, max_iterations=2)
        assert result["iterations_used"] <= 2

    def test_loop_returns_final_code_as_string(self):
        result = run_generator_critic_loop(self.architecture, max_iterations=3)
        assert isinstance(result["final_code"], str)
        assert len(result["final_code"]) > 0


# ============================================================
# Agent 5: Documentation Agent
# ============================================================
class TestDocumentationAgent:
    def test_returns_markdown_string(self):
        requirement_spec = analyze_requirement_mock("ทดสอบระบบเว็บแอป")
        architecture = design_architecture_mock(requirement_spec)
        loop_result = run_generator_critic_loop(architecture, max_iterations=2)
        doc = generate_documentation_mock(requirement_spec, architecture, loop_result)

        assert isinstance(doc, str)
        assert "#" in doc  # มี markdown heading
        assert requirement_spec["project_name"] in doc


# ============================================================
# Agent 6: QA/Critic Agent
# ============================================================
class TestQACriticAgent:
    def setup_method(self):
        self.requirement_spec = analyze_requirement_mock("ทดสอบระบบเว็บแอป")
        self.architecture = design_architecture_mock(self.requirement_spec)
        self.loop_result = run_generator_critic_loop(self.architecture, max_iterations=2)

    def test_returns_overall_status(self):
        result = qa_critic_review_mock(self.requirement_spec, self.architecture, self.loop_result)
        assert result["overall_status"] in ["APPROVED", "APPROVED_WITH_WARNINGS", "REJECTED"]

    def test_rejects_when_security_not_approved(self):
        fake_loop_result = {"final_status": "NEEDS_HUMAN_REVIEW"}
        result = qa_critic_review_mock(self.requirement_spec, self.architecture, fake_loop_result)
        assert result["overall_status"] == "REJECTED"

    def test_checks_all_four_dimensions(self):
        result = qa_critic_review_mock(self.requirement_spec, self.architecture, self.loop_result)
        assert result["total_checks"] == 4
