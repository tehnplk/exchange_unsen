#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับสร้างไฟล์ version.json จาก config.py
"""

import json
import os
import sys
from datetime import datetime

# เพิ่ม path ปัจจุบันเพื่อ import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import APP_CONFIG
except ImportError:
    print("❌ ไม่สามารถ import config.py ได้")
    sys.exit(1)

def generate_version_json():
    """สร้างไฟล์ version.json จากข้อมูลใน config.py"""
    
    version_data = {
        "name": APP_CONFIG.get('name', 'ExchangeUnsen'),
        "version": APP_CONFIG.get('version', '1.0.0'),
        "description": APP_CONFIG.get('description', ''),
        "author": APP_CONFIG.get('author', ''),
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "download_url": "https://github.com/tehnplk/exchange_unsen/raw/master/ExchangeUnsen.exe",
        "backup_url": "https://github.com/tehnplk/exchange_unsen/raw/master/dist/ExchangeUnsen.exe",
        "changelog_url": "https://github.com/tehnplk/exchange_unsen/blob/master/CHANGELOG.md",
        "repository_url": "https://github.com/tehnplk/exchange_unsen",
        "minimum_version": "1.0.0",
        "update_required": False,
        "notes": [
            "ระบบอัปเดตอัตโนมัติ",
            "ตรวจสอบเวอร์ชันเมื่อเปิดโปรแกรม",
            "ดาวน์โหลดและติดตั้งอัตโนมัติ"
        ]
    }
    
    # เขียนไฟล์ version.json
    try:
        with open('version.json', 'w', encoding='utf-8') as f:
            json.dump(version_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ สร้างไฟล์ version.json สำเร็จ!")
        print(f"📦 เวอร์ชัน: {version_data['version']}")
        print(f"📅 วันที่: {version_data['release_date']}")
        print(f"🔗 URL: {version_data['download_url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างไฟล์: {e}")
        return False

def validate_version_json():
    """ตรวจสอบความถูกต้องของไฟล์ version.json"""
    
    try:
        with open('version.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_fields = ['name', 'version', 'download_url']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"❌ ไฟล์ version.json ขาดข้อมูล: {missing_fields}")
            return False
        
        print("✅ ไฟล์ version.json ถูกต้อง")
        return True
        
    except FileNotFoundError:
        print("❌ ไม่พบไฟล์ version.json")
        return False
    except json.JSONDecodeError:
        print("❌ ไฟล์ version.json มีรูปแบบไม่ถูกต้อง")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    print("🚀 กำลังสร้างไฟล์ version.json...")
    print("="*50)
    
    if generate_version_json():
        print("="*50)
        validate_version_json()
    else:
        print("❌ การสร้างไฟล์ล้มเหลว")
        sys.exit(1)
