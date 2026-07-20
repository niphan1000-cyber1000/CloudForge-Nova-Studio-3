# Agents

โฟลเดอร์นี้เก็บโค้ดของ AI Agent แต่ละตัวในระบบ CloudForge Nova Studio

## โครงสร้างที่วางแผนไว้

- `orchestrator/` — Agent หลักที่วางแผนงานและมอบหมายงานให้ agent อื่น
- `requirements/` — รวบรวมและสรุป requirement จากผู้ใช้
- `architecture/` — ออกแบบ high-level architecture
- `iac_generator/` — สร้าง Infrastructure-as-Code
- `security_reviewer/` — ตรวจสอบ security/compliance
- `docs_generator/` — สร้างเอกสารและ diagram

ดูรายละเอียดเพิ่มเติมที่ [Architecture](../docs/architecture.md)
