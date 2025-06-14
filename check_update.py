#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ExchangeUnsen Update Checker
ตรวจสอบเวอร์ชันใหม่จาก GitHub
"""

import requests
import re
import sys
import os
from packaging import version

# กำหนดค่าคงที่
GITHUB_API_URL = "https://api.github.com/repos/tehnplk/exchange_unsen/commits/master"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/tehnplk/exchange_unsen/master/config.py"
CURRENT_VERSION = "1.0.0"  # เวอร์ชันปัจจุบัน

def get_remote_version():
    """ดึงเวอร์ชันล่าสุดจาก GitHub"""
    try:
        print("🔍 กำลังตรวจสอบเวอร์ชันล่าสุด...")
        response = requests.get(GITHUB_RAW_URL, timeout=10)
        response.raise_for_status()
        
        # หาเวอร์ชันจาก config.py
        content = response.text
        version_match = re.search(r"'version':\s*'([^']+)'", content)
        
        if version_match:
            remote_version = version_match.group(1)
            print(f"📦 เวอร์ชันล่าสุดจาก GitHub: v{remote_version}")
            return remote_version
        else:
            print("❌ ไม่พบข้อมูลเวอร์ชันใน config.py")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ GitHub ได้: {e}")
        return None
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

def compare_versions(current, remote):
    """เปรียบเทียบเวอร์ชัน"""
    try:
        current_v = version.parse(current)
        remote_v = version.parse(remote)
        
        if remote_v > current_v:
            return "update_available"
        elif remote_v == current_v:
            return "up_to_date"
        else:
            return "newer_local"
    except Exception as e:
        print(f"❌ ไม่สามารถเปรียบเทียบเวอร์ชันได้: {e}")
        return "error"

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 50)
    print("🚀 ExchangeUnsen Update Checker")
    print("=" * 50)
    print(f"📱 เวอร์ชันปัจจุบัน: v{CURRENT_VERSION}")
    print()
    
    # ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
    try:
        requests.get("https://github.com", timeout=5)
        print("✅ การเชื่อมต่ออินเทอร์เน็ตปกติ")
    except:
        print("❌ ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้")
        print("กรุณาตรวจสอบการเชื่อมต่อแล้วลองใหม่")
        return 1
    
    # ดึงเวอร์ชันล่าสุด
    remote_version = get_remote_version()
    if not remote_version:
        print("❌ ไม่สามารถตรวจสอบเวอร์ชันล่าสุดได้")
        return 1
    
    # เปรียบเทียบเวอร์ชัน
    comparison = compare_versions(CURRENT_VERSION, remote_version)
    
    print()
    print("=" * 50)
    
    if comparison == "update_available":
        print("🎉 มีเวอร์ชันใหม่พร้อมให้อัปเดต!")
        print(f"📦 เวอร์ชันใหม่: v{remote_version}")
        print()
        print("💡 วิธีการอัปเดต:")
        print("1. รันไฟล์ update_app.bat (แนะนำ)")
        print("2. หรือดาวน์โหลดด้วยตนเองจาก:")
        print("   https://github.com/tehnplk/exchange_unsen/tree/master/dist")
        print()
        
        # ถามว่าต้องการอัปเดตหรือไม่
        try:
            choice = input("ต้องการเรียกใช้ update_app.bat เพื่ออัปเดตเลยหรือไม่? (y/N): ").strip().lower()
            if choice in ['y', 'yes']:
                if os.path.exists('update_app.bat'):
                    print("🚀 กำลังเรียกใช้ update_app.bat...")
                    os.system('update_app.bat')
                else:
                    print("❌ ไม่พบไฟล์ update_app.bat")
                    print("กรุณาดาวน์โหลดด้วยตนเองจาก GitHub")
        except KeyboardInterrupt:
            print("\n❌ ยกเลิกการอัปเดต")
            
    elif comparison == "up_to_date":
        print("✅ คุณใช้เวอร์ชันล่าสุดอยู่แล้ว!")
        print("ไม่จำเป็นต้องอัปเดต")
        
    elif comparison == "newer_local":
        print("🔬 เวอร์ชันในเครื่องใหม่กว่าบน GitHub")
        print("คุณอาจกำลังใช้เวอร์ชัน development")
        
    else:
        print("❌ ไม่สามารถเปรียบเทียบเวอร์ชันได้")
        
    print("=" * 50)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n❌ ยกเลิกการทำงาน")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
        sys.exit(1)
