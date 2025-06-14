# คู่มือการตั้งค่าตาราง MySQL สำหรับฟีเจอร์ค้นหาประชากร

## โครงสร้างตาราง person ที่ใช้งานจริง

แอปพลิเคชันใช้ตาราง `person` ที่มีโครงสร้างดังนี้:

### รายการคอลัมน์ทั้งหมด (87 คอลัมน์)

| ชื่อคอลัมน์ | ประเภทข้อมูล | รายละเอียด |
|------------|-------------|-----------|
| person_id | int | รหัสประจำตัวบุคคล (Primary Key) |
| house_id | int | รหัสบ้าน |
| **cid** | varchar | **เลขบัตรประจำตัวประชาชน** |
| pname | varchar | คำนำหน้า |
| **fname** | varchar | **ชื่อ** |
| **lname** | varchar | **นามสกุล** |
| pcode | char | รหัสคนไทย/ต่างชาติ |
| sex | char | เพศ |
| nationality | varchar | สัญชาติ |
| citizenship | varchar | ความเป็นพลเมือง |
| education | char | การศึกษา |
| occupation | varchar | อาชีพ |
| religion | char | ศาสนา |
| marrystatus | char | สถานภาพสมรส |
| house_regist_type_id | int | ประเภททะเบียนบ้าน |
| birthdate | date | วันเกิด |
| has_house_regist | char | มีทะเบียนบ้าน |
| chronic_disease_list | varchar | รายการโรคเรื้อรัง |
| club_list | varchar | รายการกลุ่ม/ชมรม |
| village_id | int | รหัสหมู่บ้าน |
| blood_group | varchar | หมู่เลือด |
| current_age | int | อายุปัจจุบัน |
| death_date | date | วันที่เสียชีวิต |
| hos_guid | varchar | รหัส GUID โรงพยาบาล |
| income_per_year | int | รายได้ต่อปี |
| home_position_id | int | ตำแหน่งในบ้าน |
| family_position_id | int | ตำแหน่งในครอบครัว |
| drug_allergy | varchar | ยาที่แพ้ |
| last_update | datetime | วันที่อัปเดตล่าสุด |
| death | char | สถานะการเสียชีวิต |
| pttype | char | ประเภทผู้ป่วย |
| pttype_begin_date | date | วันเริ่มสิทธิ |
| pttype_expire_date | date | วันหมดอายุสิทธิ |
| pttype_hospmain | char | โรงพยาบาลหลัก |
| pttype_hospsub | char | โรงพยาบาลรอง |
| father_person_id | int | รหัสบิดา |
| mother_person_id | int | รหัสมารดา |
| pttype_no | varchar | เลขที่สิทธิ |
| sps_person_id | int | รหัสคู่สมรส |
| birthtime | time | เวลาเกิด |
| age_y | int | อายุ (ปี) |
| age_m | int | อายุ (เดือน) |
| age_d | int | อายุ (วัน) |
| family_id | int | รหัสครอบครัว |
| person_house_position_id | int | ตำแหน่งในบ้าน |
| couple_person_id | int | รหัสคู่สมรส |
| person_guid | varchar | รหัส GUID บุคคล |
| house_guid | varchar | รหัส GUID บ้าน |
| last_update_pttype | datetime | วันที่อัปเดตสิทธิล่าสุด |
| patient_link | char | การเชื่อมโยงผู้ป่วย |
| **patient_hn** | varchar | **หมายเลข HN** |
| found_dw_emr | char | พบใน EMR |
| person_discharge_id | int | รหัสการย้ายออก |
| movein_date | date | วันย้ายเข้า |
| discharge_date | date | วันย้ายออก |
| person_labor_type_id | int | ประเภทแรงงาน |
| father_name | varchar | ชื่อบิดา |
| mother_name | varchar | ชื่อมารดา |
| sps_name | varchar | ชื่อคู่สมรส |
| father_cid | varchar | เลขบัตรบิดา |
| mother_cid | varchar | เลขบัตรมารดา |
| sps_cid | varchar | เลขบัตรคู่สมรส |
| bloodgroup_rh | varchar | หมู่เลือดและ Rh |
| home_phone | varchar | โทรศัพท์บ้าน |
| old_code | varchar | รหัสเดิม |
| deformed_status | char | สถานะความพิการ |
| ncd_dm_history_type_id | int | ประวัติเบาหวาน |
| ncd_ht_history_type_id | int | ประวัติความดันโลหิตสูง |
| agriculture_member_type_id | int | ประเภทสมาชิกเกษตร |
| senile | char | ผู้สูงอายุ |
| in_region | char | อยู่ในเขต |
| plkcode | varchar | รหัส PLK |
| body_weight_kg | double | น้ำหนัก (กก.) |
| height_cm | double | ส่วนสูง (ซม.) |
| nutrition_level | int | ระดับโภชนาการ |
| height_nutrition_level | int | ระดับโภชนาการส่วนสูง |
| bw_ht_nutrition_level | int | ระดับโภชนาการน้ำหนัก/ส่วนสูง |
| hometel | varchar | โทรศัพท์บ้าน |
| worktel | varchar | โทรศัพท์ที่ทำงาน |
| register_conflict | char | ขัดแย้งการลงทะเบียน |
| care_person_name | varchar | ชื่อผู้ดูแล |
| work_addr | varchar | ที่อยู่ที่ทำงาน |
| person_dm_screen_status_id | int | สถานะตรวจเบาหวาน |
| person_ht_screen_status_id | int | สถานะตรวจความดัน |
| person_stroke_screen_status_id | int | สถานะตรวจโรคหลอดเลือดสมอง |
| person_obesity_screen_status_id | int | สถานะตรวจความอ้วน |
| person_dmht_manage_type_id | int | ประเภทการจัดการเบาหวาน/ความดัน |
| last_screen_dmht_bdg_year | int | ปีตรวจล่าสุด |
| dw_chronic_register | char | ลงทะเบียนโรคเรื้อรัง |
| **mobile_phone** | varchar | **เบอร์โทรศัพท์มือถือ** |
| pttype_nhso_valid | char | สิทธิ NHSO ใช้ได้ |
| pttype_nhso_valid_datetime | datetime | วันเวลาตรวจสิทธิ NHSO |
| clinic_code_list | varchar | รายการรหัสคลินิก |
| addr_1 | varchar | ที่อยู่ 1 |
| addr_2 | varchar | ที่อยู่ 2 |

### คอลัมน์ที่แนะนำสำหรับการค้นหา

คอลัมน์ที่เหมาะสำหรับใช้เป็น search key (ขีดเส้นใต้คือแนะนำมากที่สุด):
- **cid** - เลขบัตรประจำตัวประชาชน
- **fname** - ชื่อ  
- **lname** - นามสกุล
- **patient_hn** - หมายเลข HN
- **mobile_phone** - เบอร์โทรศัพท์มือถือ
- person_id - รหัสประจำตัวบุคคล
- pname - คำนำหน้า
- birthdate - วันเกิด

### ตัวอย่างข้อมูล

```sql
INSERT INTO person (cid, fname, lname) VALUES
('1234567890123', 'สมชาย', 'ใจดี'),
('9876543210987', 'สมหญิง', 'รักเรียน'),
('5555555555555', 'ทดสอบ', 'ระบบ');
```

## การทำงานของฟีเจอร์

### 1. ขั้นตอนการค้นหา

1. ผู้ใช้เลือกคอลัมน์ที่ต้องการค้นหาจากไฟล์ Excel
2. คลิกปุ่ม "ค้นหา"
3. แอปพลิเคชันจะ query ข้อมูลด้วย:
   ```sql
   SELECT cid, fname, lname FROM person WHERE [ชื่อคอลัมน์ที่เลือก] = ? LIMIT 1
   ```
   ตัวอย่าง: หากเลือกคอลัมน์ `citizen_id` จะกลายเป็น:
   ```sql
   SELECT cid, fname, lname FROM person WHERE citizen_id = ? LIMIT 1
   ```

### 2. ผลลัพธ์ที่ได้

แอปพลิเคชันจะเพิ่มคอลัมน์ใหม่ในตาราง Excel:

| คอลัมน์เดิม | คอลัมน์ใหม่ที่เพิ่ม | ความหมาย |
|-------------|-------------------|----------|
| (คอลัมน์ที่เลือก) | `cid2` | รหัสประชาชนจาก MySQL |
| | `fname2` | ชื่อจาก MySQL |
| | `lname2` | นามสกุลจาก MySQL |

### 3. การจัดการกรณีพิเศษ

- **พบข้อมูล:** แสดงข้อมูลจริงจาก MySQL
- **ไม่พบข้อมูล:** แสดง "ไม่พบ" ในคอลัมน์ใหม่
- **เกิดข้อผิดพลาด:** แสดง "Error" ในคอลัมน์ใหม่

## การตั้งค่าฐานข้อมูล

### สคริปต์สร้างฐานข้อมูลตัวอย่าง

```sql
-- สร้างฐานข้อมูล
CREATE DATABASE excel_reader_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- ใช้ฐานข้อมูล
USE excel_reader_db;

-- สร้างตาราง person
CREATE TABLE person (
    cid VARCHAR(13) PRIMARY KEY COMMENT 'รหัสประชาชน 13 หลัก',
    fname VARCHAR(100) NOT NULL COMMENT 'ชื่อ',
    lname VARCHAR(100) NOT NULL COMMENT 'นามสกุล',
    birthdate DATE COMMENT 'วันเกิด',
    address TEXT COMMENT 'ที่อยู่',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_fname (fname),
    INDEX idx_lname (lname)
) ENGINE=InnoDB COMMENT='ตารางข้อมูลประชากร';

-- เพิ่มข้อมูลตัวอย่าง
INSERT INTO person (cid, fname, lname, birthdate, address) VALUES
('1100100000001', 'สมชาย', 'ใจดี', '1990-01-15', '123 ถ.สุขุมวิท กรุงเทพ'),
('1100100000002', 'สมหญิง', 'รักเรียน', '1985-05-20', '456 ถ.รัชดา กรุงเทพ'),
('1100100000003', 'ทดสอบ', 'ระบบ', '1995-12-10', '789 ถ.เพชรบุรี กรุงเทพ'),
('2100100000001', 'อนุชา', 'วิชาการ', '1988-03-25', '111 ถ.งามวงศ์วาน นนทบุรี'),
('2100100000002', 'สุดา', 'เก่งมาก', '1992-08-05', '222 ถ.ติวานนท์ ปทุมธานี');
```

### การตั้งค่าสิทธิ์ผู้ใช้

```sql
-- สร้างผู้ใช้สำหรับแอปพลิเคชัน
CREATE USER 'excel_reader'@'localhost' IDENTIFIED BY 'secure_password';

-- ให้สิทธิ์ SELECT เท่านั้น (เพื่อความปลอดภัย)
GRANT SELECT ON excel_reader_db.person TO 'excel_reader'@'localhost';

-- รีเฟรชสิทธิ์
FLUSH PRIVILEGES;
```

## การทดสอบ

### ทดสอบการเชื่อมต่อ

```sql
-- ทดสอบ query ที่แอปพลิเคชันจะใช้
SELECT cid, fname, lname FROM person WHERE cid = '1100100000001' LIMIT 1;
```

### ผลลัพธ์ที่คาดหวัง

```
+---------------+---------+---------+
| cid           | fname   | lname   |
+---------------+---------+---------+
| 1100100000001 | สมชาย   | ใจดี     |
+---------------+---------+---------+
```

## การแก้ไขปัญหา

### ปัญหาที่อาจพบ

1. **ตารางไม่พบ:** ตรวจสอบชื่อตารางและฐานข้อมูล
2. **ไม่มีสิทธิ์:** ตรวจสอบสิทธิ์ของผู้ใช้
3. **ข้อมูลไม่ตรงกัน:** ตรวจสอบรูปแบบรหัสประชาชน
4. **การเชื่อมต่อล้มเหลว:** ตรวจสอบการตั้งค่า MySQL ในแอปพลิเคชัน

### การตรวจสอบข้อมูล

```sql
-- ตรวจสอบจำนวนรายการทั้งหมด
SELECT COUNT(*) as total_records FROM person;

-- ตรวจสอบรูปแบบรหัสประชาชน
SELECT cid, LENGTH(cid) as cid_length 
FROM person 
WHERE LENGTH(cid) != 13;

-- ตรวจสอบข้อมูลซ้ำ
SELECT cid, COUNT(*) as duplicate_count 
FROM person 
GROUP BY cid 
HAVING COUNT(*) > 1;
```

---

**หมายเหตุ:** ควรสำรองข้อมูลก่อนดำเนินการใดๆ และทดสอบในสภาพแวดล้อม development ก่อนใช้งานจริง
