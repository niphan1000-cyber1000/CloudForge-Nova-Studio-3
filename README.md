# CloudForge Nova Studio 3

> Multi-Agent AI Platform สำหรับออกแบบ วางแผน และสร้างสถาปัตยกรรมระบบคลาวด์แบบ Multi-Cloud (AWS, Azure, GCP)

## วิสัยทัศน์

CloudForge Nova Studio คือ "ทีมสถาปนิกคลาวด์เสมือน" ที่ทำงานร่วมกับมนุษย์ได้ตลอด 24 ชั่วโมง
ประกอบด้วย AI Agent หลายตัวที่ทำงานร่วมกัน ตรวจสอบงานของกันและกัน และรักษามาตรฐาน
security/compliance โดยไม่ต้องพึ่งพาความจำหรือประสบการณ์ส่วนบุคคลของสถาปนิกคนใดคนหนึ่ง

## เป้าหมาย

- ลดเวลาที่ทีมสถาปัตยกรรมใช้ในงานที่ทำซ้ำ ๆ
- ยกระดับความสม่ำเสมอ (consistency) ของคุณภาพงานออกแบบ
- ครอบคลุมตั้งแต่การรวบรวม requirement ไปจนถึงออกแบบสถาปัตยกรรม สร้าง Infrastructure-as-Code สร้างเอกสารประกอบ และสร้าง diagram โดยอัตโนมัติ

## สถานะโปรเจกต์

กำลังอยู่ระหว่างพัฒนา ดูรายละเอียดเพิ่มเติมที่ Roadmap

ตอนนี้ระบบมี Multi-Agent Pipeline ที่ทำงานได้จริง เวอร์ชัน mock logic และเชื่อมต่อกับ checkov เครื่องมือสแกน security มาตรฐานอุตสาหกรรมจริง ยังไม่ได้เชื่อมต่อ Claude API จริง ดู Phase 3 ใน roadmap

## Quick Start

ติดตั้งไลบรารีที่จำเป็นก่อน

pip install -r requirements.txt

รันตัวอย่างผ่าน Orchestrator Agent

from agents.orchestrator import run_cloudforge_pipeline

result = run_cloudforge_pipeline(
    "อยากทำระบบเว็บแอปสำหรับร้านค้าออนไลน์ รองรับผู้ใช้ประมาณ 5000 คน งบไม่เยอะ"
)

print(result["documentation"])

## ผลลัพธ์ที่คาดหวัง

เรียกฟังก์ชันเดียว ระบบจะรัน 6 Agent เรียงต่อกันให้อัตโนมัติ ได้แก่ Requirements Agent สรุป requirement เป็น structured spec, Architecture Agent ออกแบบสถาปัตยกรรม, IaC Generator Agent สร้างโค้ด Terraform, Security Reviewer Agent สแกนด้วย checkov จริง, Documentation Agent สรุปเป็นเอกสาร Markdown อ่านง่าย และ QA/Critic Agent ตัดสินใจว่า APPROVED หรือ REJECTED

ผลลัพธ์สุดท้ายคือเอกสารสรุปโครงการ โค้ด Terraform และผลตรวจสอบ security ทั้งหมดในคำสั่งเดียว

## โครงสร้างโปรเจกต์

โฟลเดอร์ docs เก็บเอกสารสถาปัตยกรรมและแผนงาน
โฟลเดอร์ agents เก็บโค้ดของ AI Agent แต่ละตัว ประกอบด้วย mock_pipeline.py ที่มี 6 Agent ครบพร้อม Generator-Critic Loop, checkov_pipeline.py ที่เชื่อมกับ checkov เครื่องมือสแกนจริง และ orchestrator.py ที่เป็นตัวคุมกลางเรียกครั้งเดียวจบ pipeline
โฟลเดอร์ templates เก็บเทมเพลต Infrastructure-as-Code ต่อ cloud provider
โฟลเดอร์ tests เก็บชุดทดสอบ

## เอกสารที่เกี่ยวข้อง

- Architecture: docs/architecture.md
- Roadmap: docs/roadmap.md
- Requirement Spec Schema: docs/requirement-spec-schema.json

## License

MIT ดูรายละเอียดที่ไฟล์ LICENSE
