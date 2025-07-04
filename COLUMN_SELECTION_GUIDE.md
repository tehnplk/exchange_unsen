# คู่มือการเลือกคอลัมน์สำหรับการเชื่อมโยงข้อมูล

## ภาพรวม

ฟีเจอร์ "ค้นหาประชากร" ในแอปพลิเคชัน Excel Reader ช่วยให้คุณสามารถเชื่อมโยงข้อมูลจากไฟล์ Excel กับฐานข้อมูล MySQL ตาราง `person` ได้

## คอลัมน์ที่รองรับ

ระบบรองรับเฉพาะ 3 คอลัมน์ดังนี้:

### 1. `pid` - รหัสประจำตัวบุคคล
- **เชื่อมโยงกับ**: `person_id` ในตาราง person
- **ประเภทข้อมูล**: ตัวเลข (int)
- **ตัวอย่าง**: 12345, 67890
- **เหมาะสำหรับ**: รหัสภายในของระบบ

### 2. `cid` - เลขบัตรประชาชน
- **เชื่อมโยงกับ**: `cid` ในตาราง person
- **ประเภทข้อมูล**: ข้อความ 13 หลัก
- **ตัวอย่าง**: 1234567890123
- **เหมาะสำหรับ**: เลขบัตรประชาชนไทย

### 3. `hn` - หมายเลข HN
- **เชื่อมโยงกับ**: `patient_hn` ในตาราง person
- **ประเภทข้อมูล**: ข้อความ
- **ตัวอย่าง**: HN001234, 987654
- **เหมาะสำหรับ**: หมายเลขผู้ป่วยในโรงพยาบาล

## วิธีใช้งาน

1. **โหลดไฟล์ Excel** ที่มีคอลัมน์ `pid`, `cid`, หรือ `hn`
2. **เลือกคอลัมน์** จาก dropdown ที่มี 3 ตัวเลือก:
   - `pid` - สำหรับค้นหาด้วยรหัสประจำตัวบุคคล
   - `cid` - สำหรับค้นหาด้วยเลขบัตรประชาชน  
   - `hn` - สำหรับค้นหาด้วยหมายเลข HN
3. **เชื่อมต่อ MySQL** และตั้งค่าฐานข้อมูล
4. **กดปุ่ม "ค้นหาประชากร"** เพื่อเริ่มค้นหา

**หมายเหตุ**: คอลัมน์ที่เลือกจาก dropdown ต้องมีอยู่จริงในไฟล์ Excel ของคุณ

## ผลลัพธ์ที่ได้

เมื่อค้นหาเสร็จสิ้น ระบบจะเพิ่มคอลัมน์ใหม่ในตาราง:

- `pid_found` - รหัสประจำตัวบุคคลที่พบ
- `cid_found` - เลขบัตรประชาชนที่พบ
- `fname_found` - ชื่อที่พบ
- `lname_found` - นามสกุลที่พบ  
- `hn_found` - หมายเลข HN ที่พบ

## ข้อกำหนดไฟล์ Excel

ไฟล์ Excel ของคุณควรมี:
- คอลัมน์ที่มีชื่อ `pid`, `cid`, หรือ `hn` (ตรงตัว)
- ข้อมูลที่ถูกต้องและสอดคล้องกับฐานข้อมูล
- ไม่มีค่าว่างมากเกินไป

## ตัวอย่างโครงสร้างไฟล์ Excel

| ชื่อ | นามสกุล | pid | cid | hn |
|-----|---------|-----|-----|-----|
| สมชาย | ใจดี | 12345 | 1234567890123 | HN001 |
| สมหญิง | รักเรียน | 67890 | 9876543210987 | HN002 |

## การแก้ไขปัญหา

**ข้อผิดพลาด "คอลัมน์ไม่รองรับ"**
- ตรวจสอบว่าชื่อคอลัมน์ในไฟล์ Excel เป็น `pid`, `cid`, หรือ `hn` (ตัวพิมพ์เล็ก)

**ข้อผิดพลาด "Unknown column"**
- ตรวจสอบการเชื่อมต่อฐานข้อมูล
- ยืนยันว่าตาราง `person` มีคอลัมน์ `person_id`, `cid`, และ `patient_hn`

### 5. การค้นหาประชากร

ปุ่ม "ค้นหา" จะค้นหาข้อมูลในฐานข้อมูล MySQL:

#### ข้อกำหนด:
- ต้องเชื่อมต่อ MySQL ก่อนใช้งาน
- ต้องมีตาราง `person` ใน MySQL
- ตารางต้องมีคอลัมน์: `cid`, `fname`, `lname`

#### การทำงาน:
1. **เลือกคอลัมน์:** เลือกคอลัมน์ที่ต้องการค้นหา (เช่น รหัสประชาชน, citizen_id, national_id)
2. **คลิกค้นหา:** ระบบจะใช้คอลัมน์ที่เลือกเป็นเงื่อนไขค้นหาในตาราง person
3. **เพิ่มคอลัมน์:** เพิ่มคอลัมน์ใหม่ในตาราง Excel:
   - `cid2`: รหัสประชาชนจาก MySQL
   - `fname2`: ชื่อจาก MySQL
   - `lname2`: นามสกุลจาก MySQL

#### SQL Query ที่ใช้:
```sql
SELECT cid, fname, lname FROM person WHERE [ชื่อคอลัมน์ที่เลือก] = ? LIMIT 1
```

**ตัวอย่าง:** หากเลือกคอลัมน์ `citizen_id` จะกลายเป็น:
```sql
SELECT cid, fname, lname FROM person WHERE citizen_id = ? LIMIT 1
```

#### ตัวอย่างผลลัพธ์:

```
การค้นหาประชากรเสร็จสิ้น!

🔍 รายละเอียดการค้นหา:
คอลัมน์ที่เลือก: cid
═════════════════════════════════
📊 สถิติข้อมูล:
• จำนวนรายการทั้งหมด: 1,250 รายการ
• จำนวนค่าไม่ซ้ำ: 1,250 ค่า
• จำนวนค่าว่าง: 0 รายการ
• ความสมบูรณ์: 100.0%

🎯 ผลการวิเคราะห์:
• ข้อมูลเป็น Unique (เหมาะสำหรับ Primary Key)
• ข้อมูลสมบูรณ์ 100% (ไม่มีค่าว่าง)

📋 ตัวอย่างข้อมูล 5 รายการแรก:
   1. CUST001
   2. CUST002
   3. CUST003
   4. CUST004
   5. CUST005
```

## ประโยชน์ของฟีเจอร์นี้

1. **การวิเคราะห์ข้อมูล:** ดูสถิติเบื้องต้นของแต่ละคอลัมน์
2. **การเตรียมข้อมูล:** เลือกคอลัมน์ที่เหมาะสมสำหรับการประมวลผลต่อไป
3. **การตรวจสอบคุณภาพ:** ตรวจสอบความสมบูรณ์ของข้อมูล (ค่าว่าง)
4. **การเชื่อมโยงระบบ:** เตรียมพร้อมสำหรับการส่งข้อมูลไป MySQL หรือระบบอื่น

## การซ่อน/แสดง UI

- **ซ่อน:** เมื่อยังไม่โหลดข้อมูล หรือเมื่อล้างข้อมูล
- **แสดง:** เมื่อโหลดข้อมูล Excel สำเร็จเท่านั้น

## การพัฒนาต่อในอนาคต

ฟีเจอร์นี้เป็นพื้นฐานสำหรับการพัฒนาฟีเจอร์ขั้นสูงต่อไป เช่น:
- การส่งข้อมูลคอลัมน์ที่เลือกไป MySQL
- การแปลงข้อมูลตามประเภทคอลัมน์
- การสร้าง mapping ระหว่างคอลัมน์ Excel กับตาราง MySQL
- การ validate ข้อมูลก่อนส่ง

## คำแนะนำการใช้งาน

1. **เลือกคอลัมน์ที่มีค่าไม่ซ้ำสูง** สำหรับ Primary Key
2. **ตรวจสอบค่าว่าง** ก่อนนำไปใช้งานจริง
3. **ใช้ข้อมูลสถิติ** ในการวางแผนการประมวลผลข้อมูล

---

**หมายเหตุ:** ฟีเจอร์นี้ยังอยู่ในขั้นพื้นฐาน การพัฒนาเพิ่มเติมจะขึ้นอยู่กับความต้องการการใช้งาน
