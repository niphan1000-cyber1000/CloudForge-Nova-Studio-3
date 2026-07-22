"""
CloudForge Nova Studio 3 — Mock Agent Pipeline
================================================
ไฟล์นี้รวม 6 Agent เวอร์ชันจำลอง (mock) ที่ทำงานต่อกันเป็น pipeline
พร้อม Generator-Critic Loop ระหว่าง IaC Generator กับ Security Reviewer
และ QA/Critic Agent ที่ตรวจสอบความสอดคล้องกันทั้งระบบในภาพรวม
ยังไม่ได้เรียก Claude API จริง (ใช้ hardcoded logic แทนไปพลางๆ)
เพื่อทดสอบโครงสร้างของระบบ Multi-Agent ก่อน

Pipeline:
    Requirements Agent -> Architecture Agent
        -> [IaC Generator Agent <-> Security Reviewer Agent] (วนจนผ่าน)
        -> Documentation Agent
        -> QA/Critic Agent (ตรวจสอบความสอดคล้องทั้งระบบ)

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

    if 'internal           = false' in terraform_code:
        findings.append({
            "check": "Load Balancer Exposure",
            "status": "INFO",
            "detail": "Load Balancer เปิดเป็น public (internal = false) ซึ่งเหมาะสมสำหรับ web application ที่ต้องรับ traffic จากอินเทอร์เน็ต"
        })

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

    if 'aws_s3_bucket_public_access_block' not in terraform_code:
        findings.append({
            "check": "S3 Public Access Block",
            "status": "FAIL",
            "detail": "ไม่พบการตั้งค่า public_access_block สำหรับ S3 bucket ควรเพิ่มเพื่อป้องกันการเข้าถึงจากภายนอกโดยไม่ตั้งใจ"
        })

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
    last_review = None

    while iteration <= max_iterations:
        print(f"\n{'='*50}")
        print(f"🔄 รอบที่ {iteration}: ตรวจสอบโค้ด Terraform")
        print(f"{'='*50}\n")

        review = review_security_mock(current_code)
        last_review = review
        print(f"ผลการตรวจสอบ: {review['overall_status']} "
              f"({review['failed_checks']} จุดที่ไม่ผ่าน จากทั้งหมด {review['total_checks']} จุด)\n")

        if review["overall_status"] == "APPROVED":
            print("✅ โค้ดผ่านการตรวจสอบทั้งหมดแล้ว! พร้อมนำไปใช้งาน\n")
            return {
                "final_code": current_code,
                "final_status": "APPROVED",
                "iterations_used": iteration,
                "review_findings": review["findings"]
            }

        if iteration < max_iterations:
            current_code = fix_iac_mock(current_code, review["findings"])
        iteration += 1

    print("⚠️  ครบจำนวนรอบสูงสุดแล้ว แต่ยังมีจุดที่ต้องแก้ไข ควรให้มนุษย์ตรวจสอบเพิ่มเติม\n")
    return {
        "final_code": current_code,
        "final_status": "NEEDS_HUMAN_REVIEW",
        "iterations_used": iteration - 1,
        "review_findings": last_review["findings"] if last_review else []
    }


# ============================================================
# Agent 5: Documentation Agent (Mock)
# ============================================================
def generate_documentation_mock(
    requirement_spec: dict,
    architecture: dict,
    loop_result: dict
) -> str:
    """
    เวอร์ชันจำลองของ Documentation Agent
    รับผลลัพธ์จากทุก Agent ก่อนหน้า (Requirements, Architecture,
    IaC + Security Review) แล้วสรุปเป็นเอกสาร Markdown ที่มนุษย์
    อ่านเข้าใจง่าย เหมาะสำหรับส่งต่อให้ทีมงานหรือลูกค้า

    TODO: เปลี่ยนให้เรียก Claude API จริง เพื่อเขียนคำอธิบายที่ลื่นไหล
    และปรับตามบริบทมากขึ้น (ตอนนี้ใช้ template ตายตัว)
    """
    print("📝 กำลังสร้างเอกสารสรุปโครงการ...\n")

    components_list = "\n".join(
        [f"- **{c['name']}**: {c['service']} — {c['purpose']}"
         for c in architecture.get("components", [])]
    )

    doc = f"""# สรุปโครงการ: {requirement_spec.get('project_name', 'ไม่มีชื่อโครงการ')}

## 1. ภาพรวมความต้องการ (Requirements)

- **ประเภท Workload**: {requirement_spec.get('workload_type')}
- **จำนวนผู้ใช้ที่คาดการณ์**: {requirement_spec.get('scale', {}).get('expected_users', '-')} คน
- **ระดับงบประมาณ**: {requirement_spec.get('budget', {}).get('tier')}
- **มาตรฐาน Compliance ที่ต้องปฏิบัติตาม**: {', '.join(requirement_spec.get('compliance', {}).get('standards', []))}

## 2. สถาปัตยกรรมที่ออกแบบ

**Cloud Provider**: {architecture.get('provider', '-').upper()}

**องค์ประกอบหลักของระบบ**:
{components_list}

**ค่าใช้จ่ายโดยประมาณต่อเดือน**: {architecture.get('estimated_monthly_cost_usd', '-')}

## 3. สถานะ Infrastructure-as-Code

- **สถานะสุดท้าย**: {loop_result.get('final_status')}
- **จำนวนรอบที่ใช้ตรวจสอบ**: {loop_result.get('iterations_used')} รอบ

## 4. หมายเหตุ

เอกสารนี้สร้างขึ้นโดยอัตโนมัติจากระบบ CloudForge Nova Studio 3
(เวอร์ชันจำลอง — ยังไม่ได้เชื่อมต่อ Claude API จริง)
"""

    return doc


# ============================================================
# Agent 6: QA/Critic Agent (Mock)
# ============================================================
def qa_critic_review_mock(
    requirement_spec: dict,
    architecture: dict,
    loop_result: dict
) -> dict:
    """
    เวอร์ชันจำลองของ QA/Critic Agent
    ตรวจสอบ "ความสอดคล้องกันทั้งระบบ" ระหว่างผลลัพธ์ของ Agent ต่างๆ
    ไม่ได้ตรวจแค่โค้ด Terraform แบบ Security Reviewer แต่เช็คว่า
    สิ่งที่ Agent ตัวอื่นทำมา ตรงกับ requirement เดิมที่ผู้ใช้ขอจริงหรือไม่

    ต่างจาก Security Reviewer Agent ตรงที่:
    - Security Reviewer  -> ตรวจโค้ด Terraform อย่างเดียว (เจาะลึกด้าน security)
    - QA/Critic Agent     -> ตรวจความสอดคล้องข้าม Agent ทั้งหมด (มุมกว้าง)

    TODO: เปลี่ยนให้เรียก Claude API จริง เพื่อวิเคราะห์ความสอดคล้อง
    ที่ซับซ้อนกว่านี้ (ตอนนี้ใช้ rule ตายตัวไปพลางๆ)
    """
    print("🕵️ QA/Critic Agent: กำลังตรวจสอบความสอดคล้องกันทั้งระบบ...\n")

    issues = []

    budget_tier = requirement_spec.get("budget", {}).get("tier")
    estimated_cost = architecture.get("estimated_monthly_cost_usd", "")
    if budget_tier == "medium" and "1200" in estimated_cost:
        issues.append({
            "check": "Budget Consistency",
            "status": "WARNING",
            "detail": f"งบระดับ '{budget_tier}' แต่ค่าใช้จ่ายประมาณการสูงสุดถึง 1200 USD/เดือน ควรตรวจสอบว่าลูกค้ารับได้จริงหรือไม่"
        })
    else:
        issues.append({
            "check": "Budget Consistency",
            "status": "PASS",
            "detail": "ระดับงบประมาณสอดคล้องกับค่าใช้จ่ายประมาณการ"
        })

    expected_users = requirement_spec.get("scale", {}).get("expected_users", 0)
    compute_component = next(
        (c for c in architecture.get("components", []) if c["name"] == "Compute"), None
    )
    if expected_users > 50000 and compute_component and "Auto Scaling Group" in compute_component.get("service", ""):
        issues.append({
            "check": "Scale vs Compute Sizing",
            "status": "WARNING",
            "detail": f"ผู้ใช้คาดการณ์ {expected_users} คน อาจต้องพิจารณา multi-region หรือ container orchestration เพิ่มเติม"
        })
    else:
        issues.append({
            "check": "Scale vs Compute Sizing",
            "status": "PASS",
            "detail": f"ขนาด compute ที่เลือกเหมาะสมกับจำนวนผู้ใช้ {expected_users} คน"
        })

    data_residency = requirement_spec.get("compliance", {}).get("data_residency", [])
    preferred_region = requirement_spec.get("cloud_preference", {}).get("preferred_regions", [])
    if "Thailand" in data_residency and not any("ap-southeast" in r for r in preferred_region):
        issues.append({
            "check": "Data Residency Compliance",
            "status": "FAIL",
            "detail": "ต้องการเก็บข้อมูลในประเทศไทย แต่ region ที่เลือกไม่ใช่ ap-southeast ควรตรวจสอบ"
        })
    else:
        issues.append({
            "check": "Data Residency Compliance",
            "status": "PASS",
            "detail": "Region ที่เลือกสอดคล้องกับข้อกำหนด data residency"
        })

    if loop_result.get("final_status") != "APPROVED":
        issues.append({
            "check": "IaC Security Approval",
            "status": "FAIL",
            "detail": f"โค้ด Terraform ยังมีสถานะ '{loop_result.get('final_status')}' ไม่ควรปล่อยให้ใช้งานจนกว่าจะ APPROVED"
        })
    else:
        issues.append({
            "check": "IaC Security Approval",
            "status": "PASS",
            "detail": "โค้ด Terraform ผ่านการตรวจสอบ security แล้ว (APPROVED)"
        })

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
# Demo: รัน Pipeline ทั้งหมดต่อกัน (Agent 1-6 + Loop)
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

    # Agent 5: สร้างเอกสารสรุปโครงการจากผลลัพธ์ทั้งหมด
    final_documentation = generate_documentation_mock(
        requirement_spec=requirement_spec,
        architecture=architecture,
        loop_result=loop_result
    )
    print("\n✅ เอกสารสรุปโครงการที่สร้างได้:\n")
    print(final_documentation)

    # Agent 6: ตรวจสอบความสอดคล้องกันทั้งระบบ (มุมกว้าง)
    qa_result = qa_critic_review_mock(
        requirement_spec=requirement_spec,
        architecture=architecture,
        loop_result=loop_result
    )
    print(f"\n✅ ผลการตรวจสอบขั้นสุดท้าย (QA/Critic Agent): {qa_result['overall_status']}\n")
    print(json.dumps(qa_result, indent=2, ensure_ascii=False))
