# CloudForge Nova Studio 3

> Multi-Agent AI Platform สำหรับออกแบบ วางแผน และสร้างสถาปัตยกรรมระบบคลาวด์แบบ Multi-Cloud (AWS, Azure, GCP)

## วิสัยทัศน์

CloudForge Nova Studio คือ "ทีมสถาปนิกคลาวด์เสมือน" ที่ทำงานร่วมกับมนุษย์ได้ตลอด 24 ชั่วโมง
ประกอบด้วย AI Agent หลายตัวที่ทำงานร่วมกัน ตรวจสอบงานของกันและกัน และรักษามาตรฐาน
security/compliance โดยไม่ต้องพึ่งพาความจำหรือประสบการณ์ส่วนบุคคลของสถาปนิกคนใดคนหนึ่ง

## เป้าหมาย

- ลดเวลาที่ทีมสถาปัตยกรรมใช้ในงานที่ทำซ้ำ ๆ
- ยกระดับความสม่ำเสมอ (consistency) ของคุณภาพงานออกแบบ
- ครอบคลุมตั้งแต่การรวบรวม requirement → ออกแบบสถาปัตยกรรม → สร้าง Infrastructure-as-Code
  → สร้างเอกสารประกอบ → สร้าง diagram โดยอัตโนมัติ

## สถานะโปรเจกต์

🚧 อยู่ในช่วงเริ่มต้น (Planning / Phase 0)

## โครงสร้างโปรเจกต์

```
CloudForge-Nova-Studio-3/
├── docs/            เอกสารสถาปัตยกรรมและแผนงาน
├── agents/          โค้ดของ AI Agent แต่ละตัว
├── templates/       เทมเพลต Infrastructure-as-Code ต่อ cloud provider
└── tests/           ชุดทดสอบ
```

## เอกสารที่เกี่ยวข้อง

- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)

## License

TBD
