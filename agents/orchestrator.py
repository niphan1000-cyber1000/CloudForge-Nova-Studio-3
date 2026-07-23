"""
CloudForge Nova Studio 3 — Orchestrator Agent (v2 — Fixed)
================================================================
เวอร์ชันแก้ไข 3 จุดที่ตรวจพบจากการรีวิวโค้ด:

1. Logic ถดถอย (Regression) ใน QA/Critic — เดิมเช็คแค่ IaC Security
   Approval อย่างเดียว ตอนนี้ย้าย logic เต็มรูปแบบจาก mock_pipeline.py
   กลับมา (Budget Consistency, Scale vs Compute, Data Residency,
   IaC Security Approval)

2. Hardcoded region — เดิม generate_iac_mock() เขียน
   region = "ap-southeast-1" ตายตัว ทั้งที่ requirement_spec มี
   preferred_regions อยู่แล้ว ตอนนี้ดึงค่ามาใช้แบบ dynamic

3. ไม่จัดการ error ของ subprocess (checkov) — เดิมถ้า checkov ไม่ได้
   ติดตั้ง หรือ crash จะทำให้ทั้งโปรแกรม error แบบไม่เป็นมิตร ตอนนี้
   เพิ่ม try/except และเช็ค returncode ก่อน parse ผลลัพธ์

Pipeline:
    Orchestrator
        -> Requirements Agent (mock)
        -> Architecture Agent (mock)
        -> IaC Generator Agent (mock, ใช้ region แบบ dynamic)
        -> Security Reviewer (checkov จริง, error handling ครบ)
        -> Documentation Agent (mock)
        -> QA/Critic Agent (ตรวจสอบครบ 4 มิติ เหมือน mock_pipeline.py)

พัฒนาและทดสอบบน Google Colab
ต้องติดตั้งก่อนใช้งาน: !pip install anthropic checkov -q
ดู schema ที่ใช้ร่วมกันได้ที่ docs/requirement-spec-schema.json
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
# แก้ไข #2: ดึง region จาก requirement_spec แบบ dynamic แทน hardcode
# ============================================================
def generate_iac_mock(architecture: dict, requirement_spec: dict) -> str:
    provider = architecture.get("provider", "aws")

    # ดึง region จาก requirement_spec แบบ dynamic แทนการ hardcode
    preferred_regions = requirement_spec.get("cloud_preference", {}).get("preferred_regions", [])
    region = preferred_regions[0] if preferred_regions else "ap-southeast-1"  # fallback ถ้าไม่ได้ระบุมา

    print(f"⚙️  [IaC Generator Agent] สร้าง Terraform code สำหรับ {provider} (region: {region})\n")

    return f'''terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{region}"
}}

resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {{ Name = "cloudforge-vpc" }}
}}

resource "aws_lb" "main" {{
  name               = "cloudforge-alb"
  internal           = false
  load_balancer_type = "application"
  tags = {{ Name = "cloudforge-load-balancer" }}
}}

resource "aws_autoscaling_group" "app" {{
  name             = "cloudforge-asg"
  min_size         = 2
  max_size         = 6
  desired_capacity = 2
  tag {{
    key                 = "Name"
    value               = "cloudforge-app-instance"
    propagate_at_launch = true
  }}
}}

resource "aws_db_instance" "main" {{
  identifier         = "cloudforge-db"
  engine             = "postgres"
  engine_version     = "15"
  instance_class     = "db.t3.medium"
  allocated_storage  = 50
  storage_encrypted  = true
  tags = {{ Name = "cloudforge-database" }}
}}

resource "aws_elasticache_cluster" "main" {{
  cluster_id      = "cloudforge-cache"
  engine          = "redis"
  node_type       = "cache.t3.micro"
  num_cache_nodes = 1
}}

resource "aws_s3_bucket" "main" {{
  bucket = "cloudforge-storage-bucket"
  tags = {{ Name = "cloudforge-storage" }}
}}

resource "aws_s3_bucket_public_access_block" "main" {{
  bucket                  = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}
'''


# ============================================================
# Agent 4: Security Reviewer — สแกนจริงด้วย checkov
# แก้ไข #3: เพิ่ม try/except + เช็ค returncode ก่อน parse
# ============================================================
def run_checkov_scan(terraform_code: str) -> dict:
    print("🔒 [Security Reviewer Agent] กำลังสแกนด้วย checkov จริง...\n")

    try:
        os.makedirs("./cloudforge_iac", exist_ok=True)
        with open("./cloudforge_iac/main.tf", "w") as f:
            f.write(terraform_code)
    except OSError as e:
        print(f"❌ ไม่สามารถเขียนไฟล์ Terraform ได้: {e}\n")
        return {
            "status": "ERROR",
            "failed_checks": -1,
            "error_message": f"File write error: {e}",
            "raw_output": ""
        }

    try:
        result = subprocess.run(
            ["checkov", "-d", "./cloudforge_iac", "--compact", "--quiet"],
            capture_output=True, text=True, timeout=120
        )
    except FileNotFoundError:
        print("❌ ไม่พบคำสั่ง 'checkov' — ตรวจสอบว่าติดตั้งไว้แล้วหรือยัง "
              "(รัน: pip install checkov)\n")
        return {
            "status": "ERROR",
            "failed_checks": -1,
            "error_message": "checkov not installed",
            "raw_output": ""
        }
    except subprocess.TimeoutExpired:
        print("❌ checkov ใช้เวลานานเกินไป (timeout 120 วินาที)\n")
        return {
            "status": "ERROR",
            "failed_checks": -1,
            "error_message": "checkov scan timed out",
            "raw_output": ""
        }

    # เช็ค returncode ก่อน parse ผลลัพธ์
    # checkov คืนค่า 0 = ผ่านหมด, 1 = พบปัญหา (ยังถือว่ารันสำเร็จ), อื่นๆ = error จริง
    if result.returncode not in (0, 1):
        print(f"❌ checkov คืนค่า error code {result.returncode} (ไม่ใช่ผลสแกนปกติ)\n")
        print(f"   stderr: {result.stderr[:300]}\n")
        return {
            "status": "ERROR",
            "failed_checks": -1,
            "error_message": f"checkov exited with code {result.returncode}: {result.stderr[:200]}",
            "raw_output": result.stdout
        }

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
# Agent 6: QA/Critic Agent
# แก้ไข #1: ย้าย logic เต็มรูปแบบจาก mock_pipeline.py กลับมา
# (เดิมเช็คแค่ IaC Security Approval อย่างเดียว)
# ============================================================
def qa_critic_review(requirement_spec: dict, architecture: dict, security_result: dict) -> dict:
    """
    ตรวจสอบความสอดคล้องกันทั้งระบบ ครบ 4 มิติ ตามที่ mock_pipeline.py
    ออกแบบไว้ตั้งแต่แรก (เดิม orchestrator.py เช็คแค่มิติเดียว เป็นการ
    ถดถอยของฟีเจอร์ที่แก้ไขในเวอร์ชันนี้)
    """
    print("🕵️ [QA/Critic Agent] ตรวจสอบความสอดคล้องกันทั้งระบบ (4 มิติ)...\n")

    issues = []

    # มิติที่ 1: Budget Consistency
    budget_tier = requirement_spec.get("budget", {}).get("tier")
    estimated_cost = architecture.get("estimated_monthly_cost_usd", "")
    if budget_tier == "medium" and "1200" in estimated_cost:
        issues.append({
            "check": "Budget Consistency",
            "status": "WARNING",
            "detail": f"งบระดับ '{budget_tier}' แต่ค่าใช้จ่ายประมาณการสูงสุดถึง 1200 USD/เดือน ควรตรวจสอบว่าลูกค้ารับได้จริงหรือไม่"
        })
    else:
        issues.append({"check": "Budget Consistency", "status": "PASS", "detail": "ระดับงบประมาณสอดคล้องกับค่าใช้จ่ายประมาณการ"})

    # มิติที่ 2: Scale vs Compute Sizing
    expected_users = requirement_spec.get("scale", {}).get("expected_users", 0)
    compute_component = next((c for c in architecture.get("components", []) if c["name"] == "Compute"), None)
    if expected_users > 50000 and compute_component and "Auto Scaling Group" in compute_component.get("service", ""):
        issues.append({
            "check": "Scale vs Compute Sizing",
            "status": "WARNING",
            "detail": f"ผู้ใช้คาดการณ์ {expected_users} คน อาจต้องพิจารณา multi-region หรือ container orchestration เพิ่มเติม"
        })
    else:
        issues.append({"check": "Scale vs Compute Sizing", "status": "PASS", "detail": f"ขนาด compute ที่เลือกเหมาะสมกับจำนวนผู้ใช้ {expected_users} คน"})

    # มิติที่ 3: Data Residency Compliance
    data_residency = requirement_spec.get("compliance", {}).get("data_residency", [])
    preferred_region = requirement_spec.get("cloud_preference", {}).get("preferred_regions", [])
    if "Thailand" in data_residency and not any("ap-southeast" in r for r in preferred_region):
        issues.append({
            "check": "Data Residency Compliance",
            "status": "FAIL",
            "detail": "ต้องการเก็บข้อมูลในประเทศไทย แต่ region ที่เลือกไม่ใช่ ap-southeast ควรตรวจสอบ"
        })
    else:
        issues.append({"check": "Data Residency Compliance", "status": "PASS", "detail": "Region ที่เลือกสอดคล้องกับข้อกำหนด data residency"})

    # มิติที่ 4: IaC Security Approval
    if security_result.get("status") == "ERROR":
        issues.append({
            "check": "IaC Security Approval",
            "status": "FAIL",
            "detail": f"ไม่สามารถตรวจสอบ security ได้: {security_result.get('error_message', 'unknown error')}"
        })
    elif security_result.get("status") != "APPROVED":
        issues.append({
            "check": "IaC Security Approval",
            "status": "FAIL",
            "detail": f"โค้ด Terraform ยังมีสถานะ '{security_result.get('status')}' ({security_result.get('failed_checks')} จุด) ไม่ควรปล่อยให้ใช้งานจนกว่าจะ APPROVED"
        })
    else:
        issues.append({"check": "IaC Security Approval", "status": "PASS", "detail": "โค้ด Terraform ผ่านการตรวจสอบ security แล้ว (APPROVED)"})

    fail_count = sum(1 for i in issues if i["status"] == "FAIL")
    warning_count = sum(1 for i in issues if i["status"] == "WARNING")

    if fail_count > 0:
        overall = "REJECTED"
    elif warning_count > 0:
        overall = "APPROVED_WITH_WARNINGS"
    else:
        overall = "APPROVED"

    return {
        "overall_status": overall,
        "total_checks": len(issues),
        "failed_checks": fail_count,
        "warning_checks": warning_count,
        "issues": issues
    }


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
    terraform_code = generate_iac_mock(architecture, requirement_spec)  # ส่ง requirement_spec เข้าไปด้วยแล้ว
    security_result = run_checkov_scan(terraform_code)
    documentation = generate_documentation_mock(requirement_spec, architecture, security_result)
    qa_result = qa_critic_review(requirement_spec, architecture, security_result)  # ใช้ฟังก์ชันเต็มรูปแบบแล้ว

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
            print(f"  [{issue['status']}] {issue['check']}: {issue['detail']}")
