# Architecture — CloudForge Nova Studio 3

## ภาพรวมระบบ

เอกสารนี้อธิบายสถาปัตยกรรมของ CloudForge Nova Studio ในระดับ high-level
จะถูกขยายรายละเอียดเพิ่มเรื่อย ๆ ตามที่ระบบพัฒนาไป

## แนวคิดหลัก: Multi-Agent System

ระบบประกอบด้วย AI Agent หลายตัวที่ทำงานร่วมกันภายใต้การควบคุมของ Orchestrator Agent

```
Orchestrator Agent (วางแผนงาน, มอบหมาย, รวมผล)
├── Requirements Agent      — รวบรวมและสรุป requirement จากผู้ใช้
├── Architecture Agent      — ออกแบบ high-level architecture ต่อ cloud provider
├── IaC Generator Agent     — สร้าง Infrastructure-as-Code (Terraform ฯลฯ)
├── Security Reviewer Agent — ตรวจสอบ security/compliance ของ IaC ที่สร้างขึ้น
├── Documentation Agent     — สร้างเอกสารประกอบและ diagram
└── QA/Critic Agent         — ตรวจสอบ cross-check งานของ agent อื่น ๆ
```

## หลักการออกแบบ

1. **Generator–Critic Loop**: งานที่ agent หนึ่งสร้างขึ้น จะถูกอีก agent ตรวจสอบก่อนส่งต่อเสมอ
2. **Shared Contract**: ทุก agent สื่อสารกันผ่าน schema กลางที่ตกลงร่วมกัน (ดูหัวข้อถัดไป)
3. **Provider-agnostic ก่อน แล้วค่อย Provider-specific**: ออกแบบ architecture แบบ abstract ก่อน แล้วค่อยแปลงเป็น IaC ของแต่ละ cloud

## Requirement Spec (ร่างเบื้องต้น)

Schema กลางที่ทุก agent จะใช้ร่วมกัน (จะปรับปรุงในขั้นตอนถัดไป):

```json
{
  "workload_type": "string",
  "expected_users": "number",
  "compliance_needs": ["string"],
  "budget_tier": "low | medium | high",
  "preferred_cloud": ["aws", "azure", "gcp"],
  "preferred_regions": ["string"]
}
```

## สถานะปัจจุบัน

- [x] กำหนดวิสัยทัศน์และเป้าหมาย
- [ ] ออกแบบ Requirement Spec Schema แบบละเอียด
- [ ] Scaffold Orchestrator Agent ตัวแรก
- [ ] MVP: single-agent, single-cloud (AWS), end-to-end

## เอกสารที่เกี่ยวข้อง

- [README](../README.md)
- [Roadmap](./roadmap.md)
