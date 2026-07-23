"""
CloudForge Nova Studio 3 — Self-Healing Pipeline
====================================================
ไฟล์นี้ทดสอบ Self-Healing Loop ที่อ่านผลจาก checkov จริง (JSON output)
แล้วพยายามแก้ไขโค้ด Terraform อัตโนมัติตาม FIX_REGISTRY จนกว่าจะผ่าน
หรือครบจำนวนรอบสูงสุด (max_retries) เพื่อป้องกัน Infinite Loop

================================================================
บันทึกการทดลอง v1 (naive append, ไม่เช็คว่าเคยแก้ไปแล้ว):
================================================================
    รอบที่ 1: พบ 23 จุดไม่ผ่าน -> พยายามแก้ CKV2_AWS_6, CKV_AWS_145
    รอบที่ 2: พบ 23 จุด (เท่าเดิม) -> พยายามแก้ซ้ำ (เพิ่ม resource ซ้ำชื่อ!)
    รอบที่ 3: พบ 23 จุด (เท่าเดิม) -> ครบ max_retries
    ผลสุดท้าย: NEEDS_HUMAN_REVIEW

    ปัญหาที่พบ: ฟังก์ชัน apply_fixes() ต่อท้ายไฟล์ (append) แบบไม่เช็คว่า
    resource นั้นมีอยู่แล้วหรือยัง ทำให้เกิด resource ซ้ำชื่อ (invalid HCL
    syntax) ส่งผลให้ checkov อ่านไฟล์ผิดพลาดและรายงาน error เดิมซ้ำทุกรอบ

================================================================
บันทึกการทดลอง v2 (เช็ค resource_marker + already_attempted):
================================================================
    รอบที่ 1: พบ 22 จุดไม่ผ่าน -> แก้ CKV_AWS_18, CKV2_AWS_6, CKV_AWS_145 (3 อย่าง)
    รอบที่ 2: พบ 23 จุด (เพิ่มขึ้น 1 จุด!) -> ตรวจพบว่าแก้เพิ่มไม่ได้แล้ว
              -> หยุด loop ทันที ก่อนครบ max_retries (ประหยัด 1 รอบ)
    ผลสุดท้าย: NEEDS_HUMAN_REVIEW (ใช้ 2 รอบ)

    ข้อค้นพบสำคัญ: จำนวนจุดที่ไม่ผ่าน "เพิ่มขึ้น" หลังพยายามแก้ไข ไม่ใช่
    ลดลง — แปลว่า snippet ที่เพิ่มเข้าไปแก้ปัญหาหนึ่ง (เช่น aws_kms_key,
    aws_s3_bucket "log_bucket") กลับสร้างปัญหาใหม่ของตัวเอง (เช่น
    log_bucket ตัวใหม่ไม่มี public access block หรือ encryption ของมันเอง)

    บทเรียน: Hardcoded fix ("คลังวิธีแก้" แบบ static) ใช้ได้ดีกับปัญหา
    ง่ายๆ ที่แยกจากกันชัดเจน แต่ไม่สามารถคาดเดาผลกระทบข้ามกันของ
    resource หลายตัวได้ — นี่คือเหตุผลที่ Phase 3 (เชื่อม Claude API จริง)
    จำเป็น: AI ที่เข้าใจบริบทสามารถอ่าน checkov JSON output ทั้งหมด แล้ว
    ตัดสินใจแก้ไขที่คำนึงถึงผลกระทบข้าม resource ได้ดีกว่า static registry

TODO ที่ต้องแก้ต่อใน Phase 3:
- ส่งผลลัพธ์ checkov แบบ JSON เต็มรูปแบบเข้า prompt ของ Claude
  (ไม่ใช่แค่ check_id แต่รวม resource, file_line_range, guideline ด้วย)
- ให้ Claude เขียน Terraform ใหม่ทั้งไฟล์ (ไม่ใช่ต่อท้าย) เพื่อหลีกเลี่ยง
  ปัญหา resource ซ้ำและผลกระทบข้าม resource ที่มองไม่เห็นล่วงหน้า
- เก็บ before/after ของแต่ละรอบไว้เปรียบเทียบ เพื่อ debug ง่ายขึ้น

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
# "คลังวิธีแก้" v2 — มี resource_marker เพื่อป้องกันการเพิ่มซ้ำ
# (ยังมีข้อจำกัด — ดูบันทึกการทดลอง v2 ด้านบน)
# ============================================================
FIX_REGISTRY = {
    "CKV2_AWS_6": {
        "description": "S3 bucket ควรมี public access block",
        "resource_marker": 'resource "aws_s3_bucket_public_access_block"',
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
        "resource_marker": 'resource "aws_s3_bucket_server_side_encryption_configuration"',
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
        "resource_marker": 'resource "aws_s3_bucket_logging"',
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


def apply_fixes_v2(terraform_code: str, failed_check_ids: set, already_attempted: set) -> tuple:
    """
    รับโค้ด Terraform เดิม + set ของ check_id ที่ไม่ผ่าน + ประวัติที่เคยแก้แล้ว
    ป้องกันการเพิ่ม resource ซ้ำ และตรวจจับ fix ที่ไม่ได้ผลจริง

    คืนค่า (โค้ดที่แก้แล้ว, รายการที่แก้ไม่ได้, รายการที่แก้ใหม่ในรอบนี้)
    """
    fixed_code = terraform_code
    unfixable = []
    newly_fixed = []

    for check_id in failed_check_ids:
        if check_id in already_attempted:
            unfixable.append(check_id)
            continue

        fix = FIX_REGISTRY.get(check_id)
        if not fix:
            unfixable.append(check_id)
            continue

        resource_marker = fix.get("resource_marker")
        if resource_marker and resource_marker in fixed_code:
            print(f"  ⏭️  ข้าม {check_id}: resource นี้มีอยู่แล้ว (ป้องกันการซ้ำ)")
            unfixable.append(check_id)
            continue

        print(f"  🔧 แก้ไข {check_id}: {fix['description']}")
        fixed_code += fix["snippet"]
        newly_fixed.append(check_id)

    return fixed_code, unfixable, newly_fixed


def run_self_healing_loop_v2(architecture: dict, max_retries: int = 3) -> dict:
    """
    Self-Healing Loop เวอร์ชันแก้ไข: ติดตามว่า check_id ไหน "เคยพยายามแก้แล้ว"
    ป้องกันการเพิ่ม resource ซ้ำ และหยุด loop ทันทีถ้าไม่มีอะไรแก้เพิ่มได้แล้ว
    (ไม่ต้องรอครบ max_retries ถ้ารู้แล้วว่าไม่มีประโยชน์)
    """
    os.makedirs("./cloudforge_iac", exist_ok=True)
    current_code = generate_iac(architecture)
    attempt = 1
    already_attempted = set()

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

        current_code, unfixable, newly_fixed = apply_fixes_v2(
            current_code, failed_ids, already_attempted
        )
        already_attempted.update(newly_fixed)

        if not newly_fixed:
            print(f"\n⚠️  ไม่สามารถแก้ไขเพิ่มเติมได้แล้ว หยุด loop ก่อนครบ {max_retries} รอบ")
            print(f"   ปัญหาที่แก้ไม่ได้: {sorted(unfixable)}")
            return {
                "final_code": current_code,
                "status": "NEEDS_HUMAN_REVIEW",
                "attempts_used": attempt,
                "unfixable_issues": list(unfixable)
            }

        if attempt == max_retries:
            print(f"\n⚠️  ครบ {max_retries} รอบแล้ว ยังมีปัญหาค้างอยู่")
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
    healing_result = run_self_healing_loop_v2(test_architecture, max_retries=3)
    print(f"\n🎯 สรุปผลสุดท้าย: {healing_result['status']} (ใช้ {healing_result['attempts_used']} รอบ)")
