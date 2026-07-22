"""
CloudForge Nova Studio 3 — Orchestrator Agent
================================================
ไฟล์นี้คือ Orchestrator Agent ตัวคุมกลาง ที่รวม Agent ทั้ง 6 ตัว
(Requirements, Architecture, IaC Generator, Security Reviewer,
Documentation, QA/Critic) เข้าด้วยกันเป็น pipeline เดียว

ผู้ใช้เรียกใช้แค่ฟังก์ชันเดียว run_cloudforge_pipeline() แล้วระบบ
จะเรียก Agent ทั้งหมดเรียงตามลำดับให้อัตโนมัติ รวมการเขียนไฟล์
Terraform ลงดิสก์จริง และสแกนด้วย checkov (เครื่องมือ security
มาตรฐานอุตสาหกรรมจริง)

Pipeline:
    Orchestrator
        -> Requirements Agent (mock)
        -> Architecture Agent (mock)
        -> IaC Generator Agent (mock) -> เขียนไฟล์ .tf ลงดิสก์
        -> Security Reviewer (checkov จริง)
        -> Documentation Agent (mock)
        -> QA/Critic Agent (mock)

พัฒนาและทดสอบบน Google Colab
ต้องติดตั้งก่อนใช้งาน: !pip install anthropic checkov -q
ดู schema ที่ใช้ร่วมกันได้ที่ docs/requirement-spec-schema.json

TODO ถัดไป:
- เปลี่ยน Agent แต่ละตัวให้เรียก Claude API จริง (ดู Phase 3 ใน docs/roadmap.md)
- ให้ Orchestrator วน retry อัตโนมัติเมื่อ QA/Critic ตัดสิน REJECTED
  (ตอนนี้แค่รายงานผล ยังไม่ได้วนแก้ไขเองเหมือนใน mock_pipeline.py)
"""

import json
import os
import subprocess


# ============================================================
# Agent 1: Requirements Agent (Mock)
# ============================================================
def analyze_requirement_mock(user_input: str) -> dict:
    print(f"📥 [Requirements Agent] ได้รับ requirement: \"{user_input}\"\n")
    return {
        "project_name": "ระบบตัวอย่างจาก Mock Agent",
        "workload_type": "web_application",
        "scale": {"expected_users": 5000, "expected_requests_per_second": 100,
                   "data_volume_gb": 20, "growth_expectation": "moderate_growth"},
        "availability": {"sla_target": "99.9%", "multi_region": False, "disaster_recovery": True},
        "budget": {"tier": "medium", "monthly_budget_usd": 1000, "cost_priority": "balanced"},
        "compliance": {"standards": ["PDPA"], "data_residency": ["Thailand"], "data_sensitivity": "internal"},
        "cloud_preference": {"providers": ["aws"], "preferred_regions": ["ap-southeast-1"], "existing_infrastructure": "ไม่มี"}
    }


# ============================================================
# Agent 2: Architecture Agent (Mock)
# ============================================================
def design_architecture_mock(requirement_spec: dict) -> dict:
    provider = requirement_spec.get("cloud_preference", {}).get("providers", ["aws"])[0]
    workload = requirement_spec.get("workload_type", "web_application")
    print(f"📐 [Architecture Agent] ออกแบบสถาปัตยกรรมสำหรับ {workload} บน {provider}\n")
    return {
        "provider": provider,
        "workload_type": workload,
        "components": [
            {"name": "Load Balancer", "service": "AWS Application Load Balancer (ALB)", "purpose": "กระจาย traffic"},
            {"name": "Compute", "service": "Amazon EC2 Auto Scaling Group", "purpose": "รันแอปพลิเคชันหลัก"},
            {"name": "Database", "service": "Amazon RDS (PostgreSQL)", "purpose": "จัดเก็บข้อมูลหลัก"},
            {"name": "Cache", "service": "Amazon ElastiCache (Redis)", "purpose": "ลด latency"},
            {"name": "Storage", "service": "Amazon S3", "purpose": "จัดเก็บไฟล์ static และ backup"}
        ],
        "networking": {"vpc": True, "public_subnets": ["load_balancer"], "private_subnets": ["compute", "database", "cache"]},
        "estimated_monthly_cost_usd": "800-1200 (โดยประมาณ ขึ้นอยู่กับ traffic จริง)"
    }


# ============================================================
# Agent 3: IaC Generator Agent (Mock)
# ============================================================
def generate_iac_mock(architecture: dict) -> str:
    provider = architecture.get("provider", "aws")
    print(f"⚙️  [IaC Generator Agent] สร้าง Terraform code สำหรับ {provider}\n")
    return '''terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "cloudforge-vpc" }
}

resource "aws_lb" "main" {
  name               = "cloudforge-alb"
  internal           = false
  load_balancer_type = "application"
  tags = { Name = "cloudforge-load-balancer" }
}

resource "aws_autoscaling_group" "app" {
  name             = "cloudforge-asg"
  min_size         = 2
  max_size         = 6
  desired_capacity = 2
  tag {
    key                 = "Name"
    value               = "cloudforge-app-instance"
    propagate_at_launch = true
  }
}

resource "aws_db_instance" "main" {
  identifier         = "cloudforge-db"
  engine             = "postgres"
  engine_version     = "15"
  instance_class     = "db.t3.medium"
  allocated_storage  = 50
  storage_encrypted  = true
  tags = { Name = "cloudforge-database" }
}

resource "aws_elasticache_cluster" "main" {
  cluster_id      = "cloudforge-cache"
  engine          = "redis"
  node_type       = "cache.t3.micro"
  num_cache_nodes = 1
}

resource "aws_s3_bucket" "main" {
  bucket = "cloudforge-storage-bucket"
  tags = { Name = "cloudforge-storage" }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket                  = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
'''


# ============================================================
# Agent 4: Security Reviewer — สแกนจริงด้วย checkov
# ============================================================
def run_checkov_scan(terraform_code: str) -> dict:
    print("🔒 [Security Reviewer Agent] กำลังสแกนด้วย checkov จริง...\n")
    os.makedirs("./cloudforge_iac", exist_ok=True)
    with open("./cloudforge_iac/main.tf", "w") as f:
        f.write(terraform_code)

    result = subprocess.run(
        ["checkov", "-d", "./cloudforge_iac", "--compact", "--quiet"],
        capture_output=True, text=True
    )
    output = result.stdout

    passed = output.count("Check:") - output.count("FAILED for resource")
    failed = output.count("FAILED for resource")

    return {
        "raw_output": output,
        "failed_checks": failed,
        "status": "NEEDS_REVISION" if failed > 0 else "APPROVED"
    }


# ============================================================
# Agent 5: Documentation Agent (Mock)
# ============================================================
def generate_documentation_mock(requirement_spec: dict, architecture: dict, security_result: dict) -> str:
    print("📝 [Documentation Agent] กำลังสร้างเอกสารสรุป...\n")
    components_list = "\n".join(
        [f"- **{c['name']}**: {c['service']} — {c['purpose']}" for c in architecture.get("components", [])]
    )
    return f"""# สรุปโครงการ: {requirement_spec.get('project_name')}

## ภาพรวมความต้องการ
- ประเภท Workload: {requirement_spec.get('workload_type')}
- จำนวนผู้ใช้ที่คาดการณ์: {requirement_spec.get('scale', {}).get('expected_users')} คน
- ระดับงบประมาณ: {requirement_spec.get('budget', {}).get('tier')}

## สถาปัตยกรรม
Provider: {architecture.get('provider', '-').upper()}

{components_list}

## ผลการตรวจสอบ Security (checkov จริง)
สถานะ: {security_result.get('status')}
จำนวนจุดที่ไม่ผ่าน: {security_result.get('failed_checks')}
"""


# ============================================================
# Agent 6: QA/Critic Agent (Mock)
# ============================================================
def qa_critic_review_mock(requirement_spec: dict, architecture: dict, security_result: dict) -> dict:
    print("🕵️ [QA/Critic Agent] ตรวจสอบความสอดคล้องกันทั้งระบบ...\n")
    issues = []
    if security_result.get("status") != "APPROVED":
        issues.append(f"โค้ด Terraform ยังมี {security_result.get('failed_checks')} จุดที่ checkov ตรวจพบ ควรแก้ก่อน deploy จริง")
    overall = "REJECTED" if issues else "APPROVED"
    return {"overall_status": overall, "issues": issues}


# ============================================================
# 🎯 ORCHESTRATOR AGENT — ตัวคุมทั้งหมด
# ============================================================
def run_cloudforge_pipeline(user_requirement: str) -> dict:
    """
    Orchestrator Agent: รับ requirement จากผู้ใช้ครั้งเดียว
    แล้วเรียก Agent ทั้งหมดเรียงตามลำดับให้อัตโนมัติ จนจบ pipeline
    """
    print("="*60)
    print("🚀 CloudForge Nova Studio — เริ่มทำงาน Pipeline")
    print("="*60 + "\n")

    requirement_spec = analyze_requirement_mock(user_requirement)
    architecture = design_architecture_mock(requirement_spec)
    terraform_code = generate_iac_mock(architecture)
    security_result = run_checkov_scan(terraform_code)
    documentation = generate_documentation_mock(requirement_spec, architecture, security_result)
    qa_result = qa_critic_review_mock(requirement_spec, architecture, security_result)

    print("="*60)
    print("✅ Pipeline เสร็จสมบูรณ์!")
    print("="*60 + "\n")

    return {
        "requirement_spec": requirement_spec,
        "architecture": architecture,
        "terraform_code": terraform_code,
        "security_result": security_result,
        "documentation": documentation,
        "qa_result": qa_result
    }


# ============================================================
# Demo: เรียก Orchestrator เพียงครั้งเดียว
# ============================================================
if __name__ == "__main__":
    final_result = run_cloudforge_pipeline(
        "อยากทำระบบเว็บแอปสำหรับร้านค้าออนไลน์ รองรับผู้ใช้ประมาณ 5000 คน งบไม่เยอะ"
    )

    print("📄 เอกสารสรุปโครงการ:\n")
    print(final_result["documentation"])

    print("\n🕵️ ผล QA/Critic:", final_result["qa_result"]["overall_status"])
    if final_result["qa_result"]["issues"]:
        for issue in final_result["qa_result"]["issues"]:
            print(f"  - {issue}")
