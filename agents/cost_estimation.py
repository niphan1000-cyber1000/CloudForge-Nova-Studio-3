"""
CloudForge Nova Studio 3 — Cost Estimation Agent
====================================================
Agent ตัวที่ 7 ของระบบ ประเมินค่าใช้จ่ายรายเดือนแยกตาม component
ของสถาปัตยกรรมที่ Architecture Agent ออกแบบไว้ พร้อมเปรียบเทียบกับ
งบประมาณที่ผู้ใช้ระบุไว้ใน Requirement Spec

ตอบโจทย์ requirement ตัวอย่างที่ใช้ทดสอบมาตลอด ("งบไม่เยอะ") ให้มี
ตัวเลขที่จับต้องได้จริง แทนที่จะเป็นแค่ข้อความประมาณการกว้างๆ แบบ
"800-1200 USD" ที่ Architecture Agent เคยให้ไว้

TODO ในอนาคต:
- เปลี่ยนจากตารางราคาคงที่ (PRICE_TABLE) ให้เรียก Infracost API จริง
  หรือ AWS Pricing API เพื่อความแม่นยำของราคาที่อัปเดตตามเวลาจริง
- รองรับ multi-region pricing (ราคาต่าง region ไม่เท่ากัน)
- รองรับ multi-cloud pricing (Azure, GCP) เมื่อถึง Phase 5

พัฒนาและทดสอบบน Google Colab
"""


def estimate_cost_mock(architecture: dict, requirement_spec: dict) -> dict:
    """
    Cost Estimation Agent (Mock)
    รับ Architecture + Requirement Spec แล้วประเมินค่าใช้จ่ายรายเดือน
    แยกตาม component พร้อมเทียบกับงบประมาณที่ผู้ใช้ระบุไว้

    ราคาอ้างอิงคร่าวๆ จาก AWS ap-southeast-1 (ไม่ใช่ราคาจริงล่าสุด
    ในโลกจริงควรใช้เครื่องมือเช่น Infracost แทนตารางราคานี้)
    """
    print("💰 [Cost Estimation Agent] กำลังประเมินค่าใช้จ่าย...\n")

    # ตารางราคาโดยประมาณต่อเดือน (USD) แยกตามชื่อ service
    PRICE_TABLE = {
        "AWS Application Load Balancer (ALB)": 20,
        "Amazon EC2 Auto Scaling Group": 60,   # ต่อ instance, สมมติ 2 instances = 120
        "AWS ECS Fargate": 45,
        "Amazon RDS (PostgreSQL)": 130,
        "Amazon ElastiCache (Redis)": 25,
        "Amazon S3": 15,
    }

    line_items = []
    total = 0.0

    for component in architecture.get("components", []):
        service = component.get("service", "")
        base_price = PRICE_TABLE.get(service, 30)  # default ถ้าไม่รู้จัก

        # Compute แบบ Auto Scaling Group คูณ 2 เพราะ desired_capacity = 2
        # ตามที่ IaC Generator ตั้งไว้ใน orchestrator.py / mock_pipeline.py
        multiplier = 2 if "Auto Scaling Group" in service else 1
        cost = base_price * multiplier

        line_items.append({
            "component": component.get("name"),
            "service": service,
            "estimated_monthly_usd": cost
        })
        total += cost

    # เทียบกับงบที่ผู้ใช้ระบุไว้
    monthly_budget = requirement_spec.get("budget", {}).get("monthly_budget_usd")
    budget_status = "UNKNOWN"
    budget_message = "ไม่ได้ระบุงบประมาณที่ชัดเจนไว้เปรียบเทียบ"

    if monthly_budget is not None:
        if total <= monthly_budget:
            budget_status = "WITHIN_BUDGET"
            budget_message = f"ประมาณการ ${total:.0f}/เดือน อยู่ในงบ ${monthly_budget:.0f}/เดือน"
        else:
            over_by = total - monthly_budget
            budget_status = "OVER_BUDGET"
            budget_message = f"ประมาณการ ${total:.0f}/เดือน เกินงบ ${monthly_budget:.0f}/เดือน ไปประมาณ ${over_by:.0f}"

    return {
        "line_items": line_items,
        "total_estimated_monthly_usd": round(total, 2),
        "budget_status": budget_status,
        "budget_message": budget_message
    }


if __name__ == "__main__":
    test_requirement = {
        "budget": {"tier": "medium", "monthly_budget_usd": 1000}
    }

    test_architecture = {
        "components": [
            {"name": "Load Balancer", "service": "AWS Application Load Balancer (ALB)"},
            {"name": "Compute", "service": "Amazon EC2 Auto Scaling Group"},
            {"name": "Database", "service": "Amazon RDS (PostgreSQL)"},
            {"name": "Cache", "service": "Amazon ElastiCache (Redis)"},
            {"name": "Storage", "service": "Amazon S3"},
        ]
    }

    cost_result = estimate_cost_mock(test_architecture, test_requirement)

    print("✅ ผลการประเมินค่าใช้จ่าย:\n")
    for item in cost_result["line_items"]:
        print(f"  - {item['component']} ({item['service']}): ${item['estimated_monthly_usd']}/เดือน")

    print(f"\n💵 รวมประมาณการ: ${cost_result['total_estimated_monthly_usd']}/เดือน")
    print(f"📊 สถานะงบประมาณ: {cost_result['budget_status']}")
    print(f"   {cost_result['budget_message']}")
