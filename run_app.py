#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel Reader Application
รันแอปพลิเคชันอ่านไฟล์ Excel
"""

import sys
import os

# เพิ่ม path ของโปรเจกต์
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import และรันแอปพลิเคชัน
try:
    from exchange_unsen import main
    
    if __name__ == "__main__":
        print("กำลังเริ่มต้นแอปพลิเคชัน Exchange Unsen...")
        print("กรุณารอสักครู่...")
        main()
        
except ImportError as e:
    print(f"ข้อผิดพลาด: ไม่สามารถ import module ได้ - {e}")
    print("กรุณาตรวจสอบว่าได้ติดตั้ง dependencies ครบถ้วนแล้ว")
    print("รัน: pip install -r requirements.txt")
    
except Exception as e:
    print(f"ข้อผิดพลาดในการรันแอปพลิเคชัน: {e}")
    input("กด Enter เพื่อปิดโปรแกรม...")
