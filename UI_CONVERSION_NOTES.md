# UI Conversion Documentation

## การแปลงไฟล์ UI จาก XML เป็น Python Code

### ไฟล์ที่เกี่ยวข้อง:

- **ui_components.py** - ไฟล์ UI แบบ Python code ใหม่
- **excel_reader.ui** - ไฟล์ UI แบบ XML เดิม (ยังคงไว้สำรอง)
- **excel_reader.ui.backup** - สำรองไฟล์ UI เดิม

### ข้อดีของการใช้ Python UI:

1. **ไม่ต้องพึ่งไฟล์ภายนอก** - UI รวมอยู่ในโค้ด Python
2. **ควบคุมได้มากขึ้น** - สามารถปรับแต่ง UI แบบ dynamic ได้ง่าย
3. **การแจกจ่าย (Distribution)** - ง่ายกว่าเพราะไม่ต้องแนบไฟล์ .ui
4. **Performance** - เร็วกว่าเล็กน้อยเพราะไม่ต้องโหลดไฟล์ XML
5. **IDE Support** - IDE สามารถ autocomplete และ check syntax ได้

### ส่วนประกอบของ UI:

#### 1. Top Frame (File Selection)
- Label: "เลือกไฟล์ Excel"
- LineEdit: แสดง path ไฟล์
- Button: "Browse..." (สีเขียว)

#### 2. Button Frame (Controls)
- Label: "เชื่อมโยงโดย:" (ซ่อนไว้)
- ComboBox: เลือกคอลัมน์ (ซ่อนไว้)
- Button: "เชื่อมโยงข้อมูล" (สีส้ม, ซ่อนไว้)
- Spacer: เว้นระยะ
- Button: "ล้างข้อมูล" (สีแดง)
- Button: "Export" (สีส้ม)

#### 3. Status Label
- แสดงสถานะการทำงานของโปรแกรม

#### 4. Table View
- แสดงข้อมูล Excel และผลลัพธ์การค้นหา

#### 5. Menu Bar
- **ไฟล์:** เปิดไฟล์, Export, ออก
- **มุมมอง:** รีเฟรช
- **ตั้งค่า:** MySQL settings, เชื่อมต่อ/ตัดการเชื่อมต่อ
- **ช่วยเหลือ:** เกี่ยวกับ

### การใช้งาน:

```python
from ui_components import ExchangeUnsenUI

class MyApp(ExchangeUnsenUI):
    def __init__(self):
        super().__init__()
        self.setupUi()  # เรียกใช้เพื่อสร้าง UI
```

### Color Scheme:

- **เขียว (#4CAF50):** Browse button
- **ส้ม (#FF9800):** Export และ Search buttons  
- **แดง (#F44336):** Clear button
- **เทา (#CCCCCC):** Disabled buttons
- **ฟ้า (#2196F3):** Hover effects

### Font Settings:

- **หัวข้อ:** Tahoma 12pt Bold
- **ปุ่ม:** Tahoma 9-10pt Bold
- **ตาราง:** Tahoma 9pt
- **สถานะ:** Tahoma 10pt

### สรุป:

การแปลง UI จาก XML เป็น Python code ทำให้โปรแกรมมีความยืดหยุ่นมากขึ้น สามารถปรับแต่งและแจกจ่ายได้ง่ายขึ้น โดยยังคงรูปลักษณ์และการทำงานเดิมไว้ทั้งหมด
