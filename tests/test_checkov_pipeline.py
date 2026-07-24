"""
Unit Tests สำหรับ agents/checkov_pipeline.py
==============================================
ทดสอบฟังก์ชัน Agent 1-3 (mock) และการเขียนไฟล์ Terraform ลงดิสก์

หมายเหตุสำคัญ: การทดสอบที่เรียก checkov จริงจะถูก skip อัตโนมัติ
ถ้าเครื่องที่รัน test ไม่มี checkov ติดตั้งอยู่ (เช่น ใน CI ที่ยังไม่ได้
ติดตั้ง หรือเครื่อง dev บางเครื่อง) เพื่อไม่ให้ test พังโดยไม่จำเป็น

รันด้วยคำสั่ง: pytest tests/test_checkov_pipeline.py -v
"""

import sys
import os
import shutil
import subprocess
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.checkov_pipeline import (
    analyze_requirement_mock,
    design_architecture_mock,
    generate_iac_mock,
)


# เช็คว่ามี checkov ติดตั้งในเครื่องหรือไม่ ใช้สำหรับ skip test ที่เกี่ยวข้อง
CHECKOV_AVAILABLE = shutil.which("checkov") is not None


# ============================================================
# Agent 1-3: ทดสอบฟังก์ชัน mock (ไม่ต้องพึ่ง checkov)
# ============================================================
class TestMockAgentsInCheckovPipeline:
    def test_requirement_agent_returns_dict(self):
        result = analyze_requirement_mock("ทดสอบระบบ")
        assert isinstance(result, dict)
        assert "project_name" in result

    def test_architecture_agent_returns_components(self):
        req = analyze_requirement_mock("ทดสอบระบบ")
        arch = design_architecture_mock(req)
        assert "components" in arch
        assert len(arch["components"]) == 5  # LB, Compute, DB, Cache, Storage

    def test_iac_generator_produces_valid_looking_terraform(self):
        req = analyze_requirement_mock("ทดสอบระบบ")
        arch = design_architecture_mock(req)
        code = generate_iac_mock(arch)
        assert "terraform {" in code
        assert 'resource "aws_s3_bucket_public_access_block"' in code  # เวอร์ชันนี้ควรมี fix ในตัวแล้ว


# ============================================================
# ทดสอบการเขียนไฟล์ลงดิสก์ (ไม่ต้องพึ่ง checkov)
# ============================================================
class TestFileWriting:
    def setup_method(self):
        self.test_dir = "./test_cloudforge_iac_temp"

    def teardown_method(self):
        # ลบโฟลเดอร์ทดสอบทิ้งหลังทดสอบเสร็จ ไม่ให้ค้างเกะกะ repo
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_can_write_terraform_file(self):
        req = analyze_requirement_mock("ทดสอบระบบ")
        arch = design_architecture_mock(req)
        code = generate_iac_mock(arch)

        os.makedirs(self.test_dir, exist_ok=True)
        file_path = os.path.join(self.test_dir, "main.tf")
        with open(file_path, "w") as f:
            f.write(code)

        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            content = f.read()
        assert content == code


# ============================================================
# ทดสอบที่ต้องพึ่ง checkov จริง — skip อัตโนมัติถ้าไม่มีติดตั้ง
# ============================================================
@pytest.mark.skipif(not CHECKOV_AVAILABLE, reason="checkov ไม่ได้ติดตั้งในเครื่องนี้")
class TestCheckovIntegration:
    def setup_method(self):
        self.test_dir = "./test_cloudforge_iac_checkov"
        req = analyze_requirement_mock("ทดสอบระบบ")
        arch = design_architecture_mock(req)
        self.terraform_code = generate_iac_mock(arch)

        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "main.tf"), "w") as f:
            f.write(self.terraform_code)

    def teardown_method(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_checkov_runs_without_crashing(self):
        result = subprocess.run(
            ["checkov", "-d", self.test_dir, "--compact", "--quiet"],
            capture_output=True, text=True, timeout=60
        )
        # checkov คืนค่า 0 (ผ่านหมด) หรือ 1 (พบปัญหา) ถือว่ารันสำเร็จทั้งคู่
        assert result.returncode in (0, 1)

    def test_checkov_produces_output(self):
        result = subprocess.run(
            ["checkov", "-d", self.test_dir, "--compact", "--quiet"],
            capture_output=True, text=True, timeout=60
        )
        assert len(result.stdout) > 0
