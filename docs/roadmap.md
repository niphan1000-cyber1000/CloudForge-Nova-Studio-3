# Roadmap — CloudForge Nova Studio 3

แผนการพัฒนาแบ่งเป็นเฟส เพื่อให้ทำทีละขั้น เห็นผลเร็ว และไม่ over-engineer ตั้งแต่ต้น

## Phase 0 — Foundation ✅ เสร็จสมบูรณ์

- [x] กำหนดวิสัยทัศน์และเป้าหมาย (README)
- [x] ร่างสถาปัตยกรรมระดับ high-level (architecture.md)
- [x] ออกแบบ Requirement Spec Schema แบบละเอียด (requirement-spec-schema.json)
- [x] ตั้งค่าโครงสร้าง repo (โฟลเดอร์ agents/, templates/, tests/ ฯลฯ)

## Phase 1 — Single-Agent MVP ✅ เสร็จสมบูรณ์ (เวอร์ชัน Mock)

เป้าหมาย: ทำ 1 use case ให้จบ end-to-end ก่อนขยายเป็น multi-agent

- [x] สร้าง Requirements Agent ตัวแรก (รับ input แบบข้อความ → สรุปเป็น structured spec)
- [x] สร้าง Architecture Agent (ออกแบบ high-level architecture สำหรับ AWS เท่านั้น)
- [x] สร้าง IaC Generator Agent (สร้าง Terraform สำหรับ AWS)
- [x] ทดสอบ flow แบบ end-to-end: requirement → spec → architecture → Terraform

> พัฒนาและทดสอบบน Google Colab เป็นเวอร์ชัน mock (ยังไม่เชื่อมต่อ Claude API จริง)
> ดูโค้ดได้ที่ `agents/mock_pipeline.py`

## Phase 2 — Multi-Agent Review Loop ✅ เสร็จสมบูรณ์

เป้าหมาย: เพิ่มการตรวจสอบงานระหว่าง agent (generator–critic pattern)

- [x] สร้าง Security Reviewer Agent (ตรวจ IaC ที่สร้างขึ้น)
- [x] เพิ่มระบบ feedback loop (agent แก้ไขงานตามคำแนะนำของ critic) — ทดสอบแล้ว: APPROVED ภายใน 2 รอบ
- [x] สร้าง QA/Critic Agent แยกต่างหาก (ตรวจสอบความสอดคล้องกันทั้งระบบในภาพรวม เช่น budget vs cost, data residency)
- [x] เพิ่ม automated checks จริง (checkov) แทนการเช็คแบบ hardcode

> เชื่อมต่อกับ checkov (เครื่องมือสแกน security มาตรฐานอุตสาหกรรมจริง) สำเร็จแล้ว
> ระบบเขียนไฟล์ Terraform ลงดิสก์จริง แล้วให้ checkov สแกนจริง พบปัญหาจริง เช่น
> S3 bucket ไม่ได้เข้ารหัสด้วย KMS, Public ALB ไม่มี WAF ป้องกัน ฯลฯ
> ดูโค้ดได้ที่ `agents/checkov_pipeline.py`

## Phase 2.5 — Documentation Automation ✅ เสร็จสมบูรณ์ (เวอร์ชัน Mock)

- [x] สร้าง Documentation Agent (สร้างเอกสารสรุปอัตโนมัติจากผลลัพธ์ทุก Agent)

## Phase 3 — เชื่อมต่อ AI จริง (ถัดไป)

เป้าหมาย: เปลี่ยนทุก Agent จาก mock logic ให้เรียก Claude API จริง

- [ ] สมัคร Anthropic API Key
- [ ] เปลี่ยน Requirements Agent ให้เรียก Claude API จริง
- [ ] เปลี่ยน Architecture Agent ให้เรียก Claude API จริง
- [ ] เปลี่ยน IaC Generator Agent ให้เรียก Claude API จริง
- [ ] เปลี่ยน Security Reviewer Agent ให้อ่านผล checkov จริง แล้วให้ AI แนะนำวิธีแก้ (แทน hardcoded fix)
- [ ] เปลี่ยน Documentation Agent ให้เรียก Claude API จริง

## Phase 4 — Orchestrator Agent

- [ ] สร้าง Orchestrator Agent ที่คุมทั้งหมด agent ให้ทำงานเป็นระบบเดียวอัตโนมัติ
- [ ] ผู้ใช้พิมพ์ requirement ครั้งเดียว ระบบรันจนจบ pipeline เอง (รวม checkov scan)
- [ ] รวม mock_pipeline.py และ checkov_pipeline.py เป็นระบบเดียวที่สมบูรณ์

## Phase 5 — Multi-Cloud

- [ ] ขยาย Architecture Agent ให้รองรับ Azure
- [ ] ขยาย Architecture Agent ให้รองรับ GCP
- [ ] ขยาย IaC Generator ให้สร้าง Bicep (Azure) และ Deployment Manager/Terraform (GCP)
- [ ] เปรียบเทียบ cost/architecture ข้าม provider

## Phase 6 — Production Readiness

- [ ] UI/Frontend สำหรับผู้ใช้งานจริง
- [ ] ระบบ authentication และ multi-user
- [ ] Monitoring และ logging ของ agent workflow
- [ ] Cost tracking สำหรับการเรียก LLM

## เอกสารที่เกี่ยวข้อง

- [README](../README.md)
- [Architecture](./architecture.md)
- [Agent Pipeline — เวอร์ชัน Mock ทั้งหมด](../agents/mock_pipeline.py)
- [Agent Pipeline — เวอร์ชันเชื่อม Checkov จริง](../agents/checkov_pipeline.py)
