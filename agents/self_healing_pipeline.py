"""
CloudForge Nova Studio 3 — Self-Healing Pipeline
====================================================
ไฟล์นี้ทดสอบ Self-Healing Loop ที่อ่านผลจาก checkov จริง (JSON output)
แล้วพยายามแก้ไขโค้ด Terraform อัตโนมัติตาม FIX_REGISTRY จนกว่าจะผ่าน
หรือครบจำนวนรอบสูงสุด (max_retries) เพื่อป้องกัน Infinite Loop

สถานะปัจจุบัน: ⚠️ ทดลองแล้วพบว่า fix บางตัวยังไม่ได้ผลจริง (จำนวนจุดที่
ไม่ผ่านไม่ลดลงหลังแก้ไข) — เก็บไว้เป็นหลักฐานพัฒนาการและจุดเริ่มต้น
สำหรับแก้ไขต่อ ไม่ใช่เวอร์ชัน production-ready

ทดสอบผลลัพธ์จริง (3 รอบ, max_retries=3):
    รอบที่ 1: พบ 23 จุดไม่ผ่าน -> พยายามแก้ CKV2_AWS_6, CKV_AWS_145
    รอบที่ 2: พบ 23 จุด (เท่าเดิม) -> พยายามแก้ซ้ำ
    รอบที่ 3: พบ 23 จุด (เท่าเดิม) -> ครบ max_retries
    ผลสุดท้าย: NEEDS_HUMAN_REVIEW

TODO ที่ต้องแก้ต่อ:
- ตรวจสอบว่า snippet ใน FIX_REGISTRY เขียนถูกต้องตาม Terraform syntax จริงไหม
- เช็คว่า checkov อ่านไฟล์ที่ต่อ (append) กันไปเรื่อยๆ ได้ถูกต้องหรือไม่
  (อาจมี resource block ซ้ำชื่อ ทำให้ parse ผิดพลาด)
- พิจารณาแก้แบบ "แทนที่ resource block เดิม" แทนการ "ต่อท้ายไฟล์"
  เพื่อไม่ให้เกิดความขัดแย้งของ resource name

พัฒนาและทดสอบบน Google Colab
ต้องติดตั้งก่อนใช้งาน: !pip install checkov -q
"""

import json
import os
import subprocess


def generate_iac(architecture: dict) -> str:
    """สร้างโค้ด Terraform พื้นฐาน (จงใจไม่ใส่ S3 public access block เพื่อทดสอบ self-healing)"""
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

resource "aws_db_instance" "main" {
  identifier         = "cloudforge-db"
  engine             = "postgres"
  engine_version     = "15"
  instance_class     = "db.t3.medium"
  allocated_storage  = 50
  storage_encrypted  = true
  tags = { Name = "cloudforge-database" }
}

resource "aws_s3_bucket" "main" {
  bucket = "cloudforge-storage-bucket"
  tags = { Name = "cloudforge-storage" }
}
'''


def run_checkov_json(tf_dir: str = "./cloudforge_iac") -> dict:
    """รัน checkov แล้วขอผลลัพธ์เป็น JSON เพื่ออ่าน check_id ได้แม่นยำ"""
    result = subprocess.run(
        ["checkov", "-d", tf_dir, "--output", "json", "--quiet", "--compact"],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"results": {"failed_checks": []}}


# ============================================================
# "คลังวิธีแก้" — รู้จักปัญหาที่พบบ่อยและวิธีแก้แต่ละอัน
# (ยังต้องปรับปรุง — ดู TODO ด้านบน)
# ============================================================
FIX_REGISTRY = {
    "CKV2_AWS_6": {
        "description": "S3 bucket ควรมี public access block",
        "snippet": '''
resource "aws_s3_bucket_public_access_block" "main" {
  bucket                  = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
'''
    },
    "CKV_AWS_145": {
        "description": "S3 bucket ควรเข้ารหัสด้วย KMS",
        "snippet": '''
resource "aws_kms_key" "s3_key" {
  description = "KMS key for S3 encryption"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3_key.arn
    }
  }
}
'''
    },
    "CKV_AWS_18": {
        "description": "S3 bucket ควรเปิด access logging",
        "snippet": '''
resource "aws_s3_bucket" "log_bucket" {
  bucket = "cloudforge-log-bucket"
}

resource "aws_s3_bucket_logging" "main" {
  bucket        = aws_s3_bucket.main.id
  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "log/"
}
'''
    },
}


def apply_fixes(terraform_code: str, failed_check_ids: set) -> tuple:
    """เติม snippet แก้ไขที่รู้จักจาก FIX_REGISTRY ต่อท้ายโค้ด"""
    fixed_code = terraform_code
    unfixable = []

    for check_id in failed_check_ids:
        fix = FIX_REGISTRY.get(check_id)
        if fix:
            print(f"  🔧 แก้ไข {check_id}: {fix['description']}")
            fixed_code += fix["snippet"]
        else:
            unfixable.append(check_id)

    return fixed_code, unfixable


def run_self_healing_loop(architecture: dict, max_retries: int = 3) -> dict:
    """
    Self-Healing Loop: สร้างโค้ด -> สแกนด้วย checkov จริง -> ถ้าไม่ผ่าน
    แก้ไขตาม FIX_REGISTRY -> วนใหม่ จนกว่าจะผ่านหรือครบ max_retries
    """
    os.makedirs("./cloudforge_iac", exist_ok=True)
    current_code = generate_iac(architecture)
    attempt = 1

    while attempt <= max_retries:
        print(f"\n{'='*60}")
        print(f"🔄 รอบที่ {attempt}/{max_retries}: เขียนไฟล์และสแกนด้วย checkov")
        print(f"{'='*60}\n")

        with open("./cloudforge_iac/main.tf", "w") as f:
            f.write(current_code)

        scan_result = run_checkov_json()
        failed_checks = scan_result.get("results", {}).get("failed_checks", [])
        failed_ids = {c["check_id"] for c in failed_checks}

        print(f"📊 พบจุดที่ไม่ผ่าน: {len(failed_ids)} รายการ")
        if failed_ids:
            print(f"   Check IDs: {sorted(failed_ids)}\n")

        if not failed_ids:
            print("✅ ผ่านการตรวจสอบทั้งหมดแล้ว!\n")
            return {
                "final_code": current_code,
                "status": "APPROVED",
                "attempts_used": attempt,
                "unfixable_issues": []
            }

        current_code, unfixable = apply_fixes(current_code, failed_ids)

        if attempt == max_retries:
            print(f"\n⚠️  ครบ {max_retries} รอบแล้ว ยังมีปัญหาค้างอยู่ ต้องให้มนุษย์ตรวจสอบ")
            if unfixable:
                print(f"   ปัญหาที่ไม่มีวิธีแก้อัตโนมัติ: {sorted(unfixable)}")
            return {
                "final_code": current_code,
                "status": "NEEDS_HUMAN_REVIEW",
                "attempts_used": attempt,
                "unfixable_issues": list(unfixable)
            }

        attempt += 1

    return {"final_code": current_code, "status": "UNKNOWN", "attempts_used": attempt, "unfixable_issues": []}


if __name__ == "__main__":
    test_architecture = {"provider": "aws", "workload_type": "web_application"}
    healing_result = run_self_healing_loop(test_architecture, max_retries=3)
    print(f"\n🎯 สรุปผลสุดท้าย: {healing_result['status']} (ใช้ {healing_result['attempts_used']} รอบ)")
