# คู่มือการใช้งาน - MySQL Configuration

## การตั้งค่า MySQL Connection

### 1. เปิดหน้าต่างตั้งค่า

**วิธีที่ 1: ใช้เมนู**
- เมนู ตั้งค่า > ตั้งค่า MySQL

**วิธีที่ 2: ใช้ Keyboard Shortcut**
- กด `Ctrl + M`

### 2. กรอกข้อมูลการเชื่อมต่อ

#### ข้อมูลที่จำเป็น:
- **Host**: ที่อยู่ของ MySQL Server (เช่น localhost หรือ IP Address)
- **Port**: พอร์ตของ MySQL (ปกติ 3306)
- **Database**: ชื่อฐานข้อมูล (เช่น hos)
- **Username**: ชื่อผู้ใช้ MySQL
- **Password**: รหัสผ่าน MySQL

#### ตัวเลือกเพิ่มเติม:
- **เชื่อมต่ออัตโนมัติเมื่อเปิดโปรแกรม**: เช็คถ้าต้องการให้เชื่อมต่ออัตโนมัติ

### 3. ทดสอบการเชื่อมต่อ

- คลิกปุ่ม "ทดสอบการเชื่อมต่อ" (สีน้ำเงิน)
- รอผลการทดสอบ
- ถ้าเชื่อมต่อสำเร็จ จะแสดงเวอร์ชันของ MySQL

### 4. บันทึกการตั้งค่า

- คลิกปุ่ม "บันทึก" (สีเขียว)
- การตั้งค่าจะถูกบันทึกลง Windows Registry
- ปิดหน้าต่างตั้งค่า

## การจัดการการเชื่อมต่อ

### เชื่อมต่อ MySQL
**วิธีที่ 1: ใช้เมนู**
- เมนู ตั้งค่า > เชื่อมต่อ MySQL

**วิธีที่ 2: ใช้ Keyboard Shortcut**
- กด `F6`

### ตัดการเชื่อมต่อ MySQL
**วิธีที่ 1: ใช้เมนู**
- เมนู ตั้งค่า > ตัดการเชื่อมต่อ MySQL

**วิธีที่ 2: ใช้ Keyboard Shortcut**
- กด `F7`

## Windows Registry

### ตำแหน่งการบันทึก
```
HKEY_CURRENT_USER\SOFTWARE\ExcelReaderApp
```

### ข้อมูลที่บันทึก
- `host`: ที่อยู่ MySQL Server
- `port`: พอร์ต MySQL
- `database`: ชื่อฐานข้อมูล
- `username`: ชื่อผู้ใช้
- `password`: รหัสผ่าน (เข้ารหัส)
- `auto_connect`: เชื่อมต่ออัตโนมัติ (true/false)

### การลบการตั้งค่า
1. เปิด Registry Editor (regedit)
2. ไปที่ `HKEY_CURRENT_USER\SOFTWARE\ExcelReaderApp`
3. ลบ key ทั้งหมดหรือ key ที่ต้องการ

## การแก้ไขปัญหา

### 1. ไม่สามารถเชื่อมต่อได้

**ตรวจสอบ:**
- MySQL Server ทำงานอยู่หรือไม่
- Host และ Port ถูกต้องหรือไม่
- Username และ Password ถูกต้องหรือไม่
- Firewall บล็อกการเชื่อมต่อหรือไม่

**แก้ไข:**
```sql
-- ตรวจสอบผู้ใช้ MySQL
SELECT User, Host FROM mysql.user WHERE User = 'your_username';

-- สร้างผู้ใช้ใหม่ (ถ้าจำเป็น)
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

### 2. ไม่สามารถบันทึกการตั้งค่าได้

**สาเหตุ:**
- ไม่มีสิทธิ์เขียน Registry
- UAC (User Account Control) บล็อก

**แก้ไข:**
- รันโปรแกรมในฐานะ Administrator
- ตรวจสอบสิทธิ์ Registry

### 3. การเชื่อมต่ออัตโนมัติไม่ทำงาน

**ตรวจสอบ:**
- เช็คบ็อกส์ "เชื่อมต่ออัตโนมัติ" เลือกไว้หรือไม่
- การตั้งค่าบันทึกใน Registry หรือไม่
- ข้อมูลการเชื่อมต่อถูกต้องหรือไม่

## ตัวอย่างการตั้งค่า

### การตั้งค่าพื้นฐาน (Local MySQL)
```
Host: localhost
Port: 3306
Database: hos
Username: root
Password: your_password
Auto Connect: ☑
```

### การตั้งค่าสำหรับ Remote MySQL
```
Host: 192.168.1.100
Port: 3306
Database: hospital_db
Username: app_user
Password: secure_password
Auto Connect: ☐
```

## Security Notes

### ความปลอดภัย
- รหัสผ่านถูกบันทึกใน Registry แบบ plain text
- รหัสผ่านจะแสดงในช่องกรอกแบบปกติ (ไม่มี *)
- ควรใช้ MySQL user ที่มีสิทธิ์จำกัด
- ไม่ควรใช้ root user สำหรับแอปพลิเคชัน

### คำแนะนำ
- สร้าง MySQL user เฉพาะสำหรับแอปพลิเคชัน
- ให้สิทธิ์เฉพาะที่จำเป็น (SELECT, INSERT, UPDATE, DELETE)
- ใช้รหัสผ่านที่แข็งแรง
- เปลี่ยนรหัสผ่านเป็นระยะ
- ระวังการแสดงหน้าจอเมื่อมีคนอื่นมองเห็น
