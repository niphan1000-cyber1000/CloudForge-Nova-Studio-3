# ตัวอย่าง Architecture Diagram (สร้างอัตโนมัติ)

เอกสารนี้แสดงตัวอย่างผลลัพธ์ของฟังก์ชัน `generate_architecture_diagram()`
ที่แปลงผลลัพธ์จาก Architecture Agent เป็นแผนภาพ Mermaid โดยอัตโนมัติ
GitHub จะ render โค้ดด้านล่างเป็นรูปภาพให้เองทันที

```mermaid
flowchart TD
    Internet(["🌐 Internet"])
    LB["Load Balancer<br/>AWS Application Load Balancer (ALB)"]
    Internet --> LB
    Compute["Compute<br/>Amazon EC2 Auto Scaling Group"]
    LB --> Compute
    DB[("Database<br/>Amazon RDS (PostgreSQL)")]
    Compute --> DB
    Cache[("Cache<br/>Amazon ElastiCache (Redis)")]
    Compute --> Cache
    Storage[("Storage<br/>Amazon S3")]
    Compute --> Storage
    subgraph VPC[" AWS VPC "]
        Compute
        DB
        Cache
    end
```

## เอกสารที่เกี่ยวข้อง

- [Architecture](./architecture.md)
- [Agent Pipeline (โค้ด)](../agents/orchestrator.py)
