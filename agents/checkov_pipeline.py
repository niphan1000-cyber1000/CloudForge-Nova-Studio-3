"""
CloudForge Nova Studio 3 — Pipeline พร้อม Checkov (Real Security Scanner)
==========================================================================
ไฟล์นี้เป็นเวอร์ชันที่เชื่อมต่อกับ checkov เครื่องมือสแกน security
มาตรฐานอุตสาหกรรมจริง (ไม่ใช่ mock อีกต่อไปสำหรับขั้นตอนตรวจสอบ)

Pipeline:
    Requirements Agent (mock) -> Architecture Agent (mock)
        -> IaC Generator Agent (mock) -> เขียนไฟล์ .tf ลงดิสก์จริง
        -> checkov สแกนไฟล์จริง (เครื่องมือจริง 100%)

พัฒนาและทดสอบบน Google Colab
ต้องติดตั้งก่อนใช้งาน: !pip install anthropic checkov -q
ดู schema ที่ใช้ร่วมกันได้ที่ docs/requirement-spec-schema.json

TODO ถัดไป:
- เปลี่ยน Agent 1-3 ให้เรียก Claude API จริง แทน mock logic
- อ่านผลลัพธ์จาก checkov (JSON output) แล้วส่งต่อให้ agent อื่นแก้ไขอัตโนมัติ
  (ปิด generator-critic loop ด้วยเครื่องมือสแกนจริง แทนการ mock เหมือนไฟล์ mock_pipeline.py)
"""

import json
import os


# ============================================================
# Agent 1: Requirements Agent (Mock)
# ============================================================
def analyze_requirement_mock(user_input: str) -> dict:
    print(f"📥 ได้รับ requirement จากผู้ใช้: \n\"{user_input}\"\n")
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
    print(f"📐 กำลังออกแบบสถาปัตยกรรมสำหรับ workload: {workload} บน provider: {provider}\n")
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
    print(f"⚙️  กำลังสร้าง Terraform code สำหรับ provider: {provider}\n")
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
# Demo: รัน Pipeline + เขียนไฟล์จริง + สแกนด้วย checkov จริง
# ============================================================
if __name__ == "__main__":
    # Agent 1-3: สร้าง requirement -> architecture -> terraform code
    test_input = "อยากทำระบบเว็บแอปสำหรับร้านค้าออนไลน์ รองรับผู้ใช้ประมาณ 5000 คน งบไม่เยอะ"
    requirement_spec = analyze_requirement_mock(test_input)
    architecture = design_architecture_mock(requirement_spec)
    terraform_code = generate_iac_mock(architecture)

    print("✅ โค้ด Terraform ที่สร้างได้:\n")
    print(terraform_code)

    # เขียนไฟล์ Terraform ลงดิสก์จริง (สำหรับให้ checkov สแกน)
    os.makedirs("./cloudforge_iac", exist_ok=True)
    with open("./cloudforge_iac/main.tf", "w") as f:
        f.write(terraform_code)

    print("\n📁 บันทึกไฟล์ ./cloudforge_iac/main.tf เรียบร้อยแล้ว\n")

    # สั่ง checkov สแกนไฟล์จริง
    # หมายเหตุ: บรรทัดนี้ใช้ syntax แบบ Google Colab (!command)
    # ถ้ารันนอก Colab ให้ใช้ subprocess.run(["checkov", "-d", "./cloudforge_iac", "--compact"])
    print("🔍 กำลังสแกนด้วย checkov...\n")
    os.system("checkov -d ./cloudforge_iac --compact")
