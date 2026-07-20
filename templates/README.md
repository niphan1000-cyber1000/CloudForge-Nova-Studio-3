# Templates

โฟลเดอร์นี้เก็บเทมเพลต Infrastructure-as-Code (IaC) แยกตาม cloud provider
สำหรับให้ IaC Generator Agent ใช้เป็นฐานในการสร้างโค้ดจริง

## โครงสร้าง

```
templates/
└── terraform/
    ├── aws/     เทมเพลต Terraform สำหรับ AWS
    ├── azure/   เทมเพลต Terraform สำหรับ Azure
    └── gcp/     เทมเพลต Terraform สำหรับ GCP
```

เริ่มต้นที่ AWS ก่อนตาม [Roadmap](../docs/roadmap.md) แล้วค่อยขยายไปยัง provider อื่น
