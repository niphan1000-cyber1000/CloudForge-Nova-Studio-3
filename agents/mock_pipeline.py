"""
CloudForge Nova Studio 3 — Mock Agent Pipeline
================================================
ไฟล์นี้รวม 4 Agent เวอร์ชันจำลอง (mock) ที่ทำงานต่อกันเป็น pipeline
พร้อม Generator-Critic Loop ระหว่าง IaC Generator กับ Security Reviewer
ยังไม่ได้เรียก Claude API จริง (ใช้ hardcoded logic แทนไปพลางๆ)
เพื่อทดสอบโครงสร้างของระบบ Multi-Agent ก่อน

Pipeline:
    Requirements Agent -> Architecture Agent
        -> [IaC Generator Agent <-> Security Reviewer Agent] (วนจนผ่าน)

พัฒนาและทดสอบครั้งแรกบน Google Colab
ดู schema ที่ใช้ร่วมกันได้ที่ docs/requirement-spec-schema.json
"""

import json


# ============================================================
# Agent 1: Requirements Agent (Mock)
# ============================================================
def analyze_requirement_mock(user_input: str) -> dict:
    """
    เวอร์ชันจำลองของ Requirements Agent
    รับคำอธิบายโปรเจกต์จากผู้ใช้ (ข้อความอิสระ) แล้วคืนค่าเป็น
    Requirement Spec ตาม schema ที่กำหนดไว้ใน docs/requirement-spec-schema.json

    TODO: เปลี่ยนให้เรียก Claude API จริง แทนการคืนค่าตายตัว
    """
    print(f"📥 ได้รับ requirement จากผู้ใช้: \n\"{user_input}\"\n")
    print("🤖 (จำลอง) กำลังวิเคราะห์...\n")

    mock_result = {
        "project_name": "ระบบตัวอย่างจาก Mock Agent",
        "workload_type": "web_application",
        "scale": {
            "expected_users": 5000,
            "expected_requests_per_second": 100,
            "data_volume_gb": 20,
            "growth_expectation": "moderate_growth"
        },
        "availability": {
            "sla_target": "99.9%",
            "multi_region": False,
            "disaster_recovery": True
        },
        "budget": {
            "tier": "medium",
            "monthly_budget_usd": 1000,
            "cost_priority": "balanced"
        },
        "compliance": {
            "standards": ["PDPA"],
            "data_residency": ["Thailand"],
            "data_sensitivity": "internal"
        },
        "cloud_preference": {
            "providers": ["aws"],
            "preferred_regions": ["ap-southeast-1"],
            "existing_infrastructure": "ไม่มี"
        }
    }

    return mock_result


# ============================================================
# Agent 2: Architecture Agent (Mock)
# ============================================================
def design_architecture_mock(requirement_spec: dict) -> dict:
    """
    เวอร์ชันจำลองของ Architecture Agent
    รับ Requirement Spec (ผลลัพธ์จาก Requirements Agent) แล้วออกแบบ
    สถาปัตยกรรมคร่าวๆ กลับมา

    TODO: เปลี่ยนให้เรียก Claude API จริง เพื่อออกแบบตาม requirement
    ที่หลากหลายมากขึ้น (ตอนนี้ hardcode เฉพาะกรณี AWS + web_application)
    """
    provider = requirement_spec.get("cloud_preference", {}).get("providers", ["aws"])[0]
    workload = requirement_spec.get("workload_type", "web_application")

    print(f"📐 กำลังออกแบบสถาปัตยกรรมสำหรับ workload: {workload} บน provider: {provider}\n")

    mock_architecture = {
        "provider": provider,
        "workload_type": workload,
        "components": [
            {
                "name": "Load Balancer",
                "service": "AWS Application Load Balancer (ALB)",
                "purpose": "กระจาย traffic ไปยัง backend หลายตัว"
            },
            {
                "name": "Compute",
                "service": "AWS ECS Fargate" if requirement_spec.get("technical_constraints", {}).get("container_strategy") == "serverless" else "Amazon EC2 Auto Scaling Group",
                "purpose": "รันแอปพลิเคชันหลัก"
            },
            {
                "name": "Database",
                "service": "Amazon RDS (PostgreSQL)",
                "purpose": "จัดเก็บข้อมูลหลักแบบ relational"
            },
            {
                "name": "Cache",
                "service": "Amazon ElastiCache (Redis)",
                "purpose": "ลด latency สำหรับข้อมูลที่เรียกใช้บ่อย"
            },
            {
                "name": "Storage",
                "service": "Amazon S3",
                "purpose": "จัดเก็บไฟล์ static และ backup"
            }
        ],
        "networking": {
            "vpc": True,
            "public_subnets": ["load_balancer"],
            "private_subnets": ["compute", "database", "cache"]
        },
        "estimated_monthly_cost_usd": "800-1200 (โดยประมาณ ขึ้นอยู่กับ traffic จริง)"
    }

    return mock_architecture


# ============================================================
# Agent 3: IaC Generator Agent (Mock)
# ============================================================
def generate_iac_mock(architecture: dict) -> str:
    """
    เวอร์ชันจำลองของ IaC Generator Agent
    รับผลลัพธ์จาก Architecture Agent แล้วแปลงเป็นโค้ด Terraform

    TODO: เปลี่ยนให้เรียก Claude API จริง เพื่อสร้างโค้ดที่ปรับตาม
    architecture ที่หลากหลายมากขึ้น (ตอนนี้ใช้ template ตายตัว)
    """
    provider = architecture.get("provider", "aws")
    print(f"⚙️  กำลังสร้าง Terraform code สำหรับ provider: {provider}\n")

    terraform_code = f'''# ==============================================
# Terraform Configuration (Auto-generated by CloudForge Nova Studio)
# Provider: {provider}
# ==============================================

terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "ap-southeast-1"
}}

# --- Networking: VPC ---
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {{
    Name = "cloudforge-vpc"
  }}
}}

# --- Load Balancer ---
resource "aws_lb" "main" {{
  name               = "cloudforge-alb"
  internal           = false
  load_balancer_type = "application"

  tags = {{
    Name = "cloudforge-load-balancer"
  }}
}}

# --- Compute: Auto Scaling Group ---
resource "aws_autoscaling_group" "app" {{
  name             = "cloudforge-asg"
  min_size         = 2
  max_size         = 6
  desired_capacity = 2

  tags = [
    {{
      key                 = "Name"
      value               = "cloudforge-app-instance"
      propagate_at_launch = true
    }}
  ]
}}

# --- Database: RDS PostgreSQL ---
resource "aws_db_instance" "main" {{
  identifier        = "cloudforge-db"
  engine            = "postgres"
  engine_version     = "15"
  instance_class    = "db.t3.medium"
  allocated_storage = 50
  storage_encrypted = true

  tags = {{
    Name = "cloudforge-database"
  }}
}}

# --- Cache: ElastiCache Redis ---
resource "aws_elasticache_cluster" "main" {{
  cluster_id      = "cloudforge-cache"
  engine          = "redis"
  node_type       = "cache.t3.micro"
  num_cache_nodes = 1
}}

# --- Storage: S3 Bucket ---
resource "aws_s3_bucket" "main" {{
  bucket = "cloudforge-storage-bucket"

  tags = {{
    Name = "cloudforge-storage"
  }}
}}
'''

    return terraform_code


# ============================================================
# Agent 4: Security Reviewer Agent (Mock)
# ============================================================
def review_security_mock(terraform_code: str) -> dict:
    """
    เวอร์ชันจำลองของ Security Reviewer Agent
    รับโค้ด Terraform ที่ IaC Generator Agent สร้างมา แล้วตรวจสอบ
    ตาม checklist ด้าน security เบื้องต้น

    นี่คือจุดเริ่มต้นของ "Generator-Critic Loop" ตามที่ออกแบบไว้ใน
    docs/architecture.md — Agent ตัวนี้ตรวจงานของ Agent ตัวอื่น
    ก่อนปล่อยผ่านให้ใช้งานจริง

    TODO: เปลี่ยนให้เรียก Claude API จริง เพื่อตรวจสอบโค้ดที่หลากหลาย
    มากขึ้น (ตอนนี้ใช้ checklist ตายตัวแบบง่ายๆ ไปพลางๆ)
    """
    print("🔒 กำลังตรวจสอบ security ของโค้ด Terraform...\n")

    findings = []

    # เช็คที่ 1: มีการเข้ารหัสข้อมูลที่พักอยู่ (encryption at rest) หรือไม่
    if "storage_encrypted = true" in terraform_code:
        findings.append({
            "check": "Database Encryption at Rest",
            "status": "PASS",
            "detail": "พบการตั้งค่า storage_encrypted = true ใน RDS instance"
        })
    else:
        findings.append({
            "check": "Database Encryption at Rest",
            "status": "FAIL",
            "detail": "ไม่พบการเข้ารหัสข้อมูลใน database ควรเพิ่ม storage_encrypted = true"
        })

    # เช็คที่ 2: Load Balancer เปิด public หรือไม่ (ควรมี ถ้าเป็น web app)
    if 'internal           = false' in terraform_code:
        findings.append({
            "check": "Load Balancer Exposure",
            "status": "INFO",
            "detail": "Load Balancer เปิดเป็น public (internal = false) ซึ่งเหมาะสมสำหรับ web application ที่ต้องรับ traffic จากอินเทอร์เน็ต"
        })

    # เช็คที่ 3: มีการระบุ VPC แยกต่างหากหรือไม่ (ไม่ใช้ default VPC)
    if 'resource "aws_vpc" "main"' in terraform_code:
        findings.append({
            "check": "Network Isolation (VPC)",
            "status": "PASS",
            "detail": "พบการสร้าง VPC แยกต่างหาก ไม่ได้ใช้ default VPC ของบัญชี"
        })
    else:
        findings.append({
            "check": "Network Isolation (VPC)",
            "status": "FAIL",
            "detail": "ไม่พบการสร้าง VPC แยก ควรหลีกเลี่ยงการใช้ default VPC"
        })

    # เช็คที่ 4: S3 Bucket มีการตั้งค่า public access หรือไม่ (ควรปิดถ้าไม่จำเป็น)
    if 'aws_s3_bucket_public_access_block' not in terraform_code:
        findings.append({
            "check": "S3 Public Access Block",
            "status": "FAIL",
            "detail": "ไม่พบการตั้งค่า public_access_block สำหรับ S3 bucket ควรเพิ่มเพื่อป้องกันการเข้าถึงจากภายนอกโดยไม่ตั้งใจ"
        })

    # สรุปผลรวม
    fail_count = sum(1 for f in findings if f["status"] == "FAIL")
    overall_status = "NEEDS_REVISION" if fail_count > 0 else "APPROVED"

    review_result = {
        "overall_status": overall_status,
        "total_checks": len(findings),
        "failed_checks": fail_count,
        "findings": findings
    }

    return review_result


# ============================================================
# Fix Function: แก้ไขโค้ดตามคำแนะนำของ Security Reviewer
# ============================================================
def fix_iac_mock(terraform_code: str, findings: list) -> str:
    """
    เวอร์ชันจำลองของฟังก์ชันแก้ไขโค้ด
    รับโค้ด Terraform เดิม + รายการปัญหาที่ Security Reviewer พบ
    แล้วแก้ไขโค้ดตามคำแนะนำนั้น

    TODO: เปลี่ยนให้ Claude API อ่าน findings แล้วแก้โค้ดเองแบบยืดหยุ่น
    (ตอนนี้ hardcode วิธีแก้เฉพาะปัญหาที่รู้จักไปพลางๆ)
    """
    fixed_code = terraform_code

    for finding in findings:
        if finding["status"] == "FAIL" and finding["check"] == "S3 Public Access Block":
            print("🔧 กำลังแก้ไข: เพิ่ม public_access_block ให้กับ S3 bucket...\n")
            fix_snippet = '''
# --- Security Fix: Block public access to S3 bucket ---
resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
'''
            fixed_code = fixed_code + fix_snippet

    return fixed_code


# ============================================================
# Generator-Critic Loop: วนสร้าง-ตรวจสอบ-แก้ไข จนกว่าจะผ่าน
# ============================================================
def run_generator_critic_loop(architecture: dict, max_iterations: int = 3) -> dict:
    """
    วน Loop ระหว่าง IaC Generator Agent และ Security Reviewer Agent
    จนกว่าโค้ดจะผ่านการตรวจสอบ (APPROVED) หรือครบจำนวนรอบสูงสุด

    นี่คือแกนหลักของแนวคิด "Generator-Critic Loop" ตามที่ระบุไว้ใน
    docs/architecture.md ข้อ 1 (หลักการออกแบบ)
    """
    current_code = generate_iac_mock(architecture)
    iteration = 1

    while iteration <= max_iterations:
        print(f"\n{'='*50}")
        print(f"🔄 รอบที่ {iteration}: ตรวจสอบโค้ด Terraform")
        print(f"{'='*50}\n")

        review = review_security_mock(current_code)
        print(f"ผลการตรวจสอบ: {review['overall_status']} "
              f"({review['failed_checks']} จุดที่ไม่ผ่าน จากทั้งหมด {review['total_checks']} จุด)\n")

        if review["overall_status"] == "APPROVED":
            print("✅ โค้ดผ่านการตรวจสอบทั้งหมดแล้ว! พร้อมนำไปใช้งาน\n")
            return {
                "final_code": current_code,
                "final_status": "APPROVED",
                "iterations_used": iteration
            }

        if iteration < max_iterations:
            current_code = fix_iac_mock(current_code, review["findings"])
        iteration += 1

    print("⚠️  ครบจำนวนรอบสูงสุดแล้ว แต่ยังมีจุดที่ต้องแก้ไข ควรให้มนุษย์ตรวจสอบเพิ่มเติม\n")
    return {
        "final_code": current_code,
        "final_status": "NEEDS_HUMAN_REVIEW",
        "iterations_used": iteration - 1
    }


# ============================================================
# Demo: รัน Pipeline ทั้งหมดต่อกัน (Agent 1-4 + Loop)
# ============================================================
if __name__ == "__main__":
    # Agent 1: รับ requirement จากผู้ใช้
    test_input = "อยากทำระบบเว็บแอปสำหรับร้านค้าออนไลน์ รองรับผู้ใช้ประมาณ 5000 คน งบไม่เยอะ"
    requirement_spec = analyze_requirement_mock(test_input)
    print("✅ ผลลัพธ์จาก Requirements Agent:\n")
    print(json.dumps(requirement_spec, indent=2, ensure_ascii=False))

    # Agent 2: ออกแบบสถาปัตยกรรมจาก requirement spec
    architecture = design_architecture_mock(requirement_spec)
    print("\n✅ ผลลัพธ์จาก Architecture Agent:\n")
    print(json.dumps(architecture, indent=2, ensure_ascii=False))

    # Agent 3 + 4: สร้างโค้ด Terraform แล้ววน generator-critic loop จนผ่าน
    loop_result = run_generator_critic_loop(architecture)

    print(f"\n🎯 สรุปผลสุดท้าย: {loop_result['final_status']} "
          f"(ใช้ไป {loop_result['iterations_used']} รอบ)")
    print("\n📄 โค้ด Terraform สุดท้าย (ผ่านการตรวจสอบแล้ว):\n")
    print(loop_result["final_code"])
