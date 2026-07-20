# Roadmap — CloudForge Nova Studio 3

แผนการพัฒนาแบ่งเป็นเฟส เพื่อให้ทำทีละขั้น เห็นผลเร็ว และไม่ over-engineer ตั้งแต่ต้น

## Phase 0 — Foundation (ตอนนี้)

- [x] กำหนดวิสัยทัศน์และเป้าหมาย (README)
- [x] ร่างสถาปัตยกรรมระดับ high-level (architecture.md)
- [ ] ออกแบบ Requirement Spec Schema แบบละเอียด
- [x] ตั้งค่าโครงสร้าง repo (โฟลเดอร์ agents/, templates/, tests/ ฯลฯ)

## Phase 1 — Single-Agent MVP

เป้าหมาย: ทำ 1 use case ให้จบ end-to-end ก่อนขยายเป็น multi-agent

- [ ] สร้าง Requirements Agent ตัวแรก (รับ input แบบข้อความ → สรุปเป็น structured spec)
- [ ] สร้าง Architecture Agent (ออกแบบ high-level architecture สำหรับ AWS เท่านั้น)
- [ ] สร้าง IaC Generator Agent (สร้าง Terraform สำหรับ AWS)
- [ ] ทดสอบ flow แบบ end-to-end: requirement → spec → architecture → Terraform

## Phase 2 — Multi-Agent Review Loop

เป้าหมาย: เพิ่มการตรวจสอบงานระหว่าง agent (generator–critic pattern)

- [ ] สร้าง Security Reviewer Agent (ตรวจ IaC ที่สร้างขึ้น)
- [ ] สร้าง QA/Critic Agent (ตรวจสอบ cross-check งานของ agent อื่น)
- [ ] เพิ่มระบบ feedback loop (agent แก้ไขงานตามคำแนะนำของ critic)
- [ ] เพิ่ม automated checks (tflint, checkov, tfsec)

## Phase 3 — Multi-Cloud

- [ ] ขยาย Architecture Agent ให้รองรับ Azure
- [ ] ขยาย Architecture Agent ให้รองรับ GCP
- [ ] ขยาย IaC Generator ให้สร้าง Bicep (Azure) และ Deployment Manager/Terraform (GCP)
- [ ] เปรียบเทียบ cost/architecture ข้าม provider

## Phase 4 — Documentation & Diagram Automation

- [ ] สร้าง Documentation Agent (สร้างเอกสารสรุปอัตโนมัติ)
- [ ] สร้าง diagram อัตโนมัติ (เช่น mermaid, draw.io format)

## Phase 5 — Production Readiness

- [ ] UI/Frontend สำหรับผู้ใช้งานจริง
- [ ] ระบบ authentication และ multi-user
- [ ] Monitoring และ logging ของ agent workflow
- [ ] Cost tracking สำหรับการเรียก LLM

## เอกสารที่เกี่ยวข้อง

- [README](../README.md)
- [Architecture](./architecture.md)
