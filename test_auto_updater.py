#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบระบบ auto_updater
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from auto_updater import AutoUpdater
import requests

def test_internet_connection():
    """ทดสอบการเชื่อมต่ออินเทอร์เน็ต"""
    print("=== ทดสอบการเชื่อมต่ออินเทอร์เน็ต ===")
    updater = AutoUpdater()
    if updater.check_internet_connection():
        print("✅ การเชื่อมต่ออินเทอร์เน็ตปกติ")
        return True
    else:
        print("❌ ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้")
        return False

def test_version_check():
    """ทดสอบการตรวจสอบเวอร์ชัน"""
    print("\n=== ทดสอบการตรวจสอบเวอร์ชัน ===")
    updater = AutoUpdater()
    print(f"🔍 เวอร์ชันปัจจุบัน: {updater.current_version}")
    print(f"🌐 URL สำหรับตรวจสอบเวอร์ชัน: {updater.version_url}")
    
    try:
        response = requests.get(updater.version_url, timeout=10)
        response.raise_for_status()
        version_data_list = response.json()
        print(f"✅ ดึงข้อมูลเวอร์ชันสำเร็จ: {len(version_data_list)} รายการ")
        
        # หาเวอร์ชันล่าสุด
        if version_data_list:
            latest_version_data = max(version_data_list, key=lambda x: x.get('version_code', 0))
            print(f"📦 เวอร์ชันล่าสุด: {latest_version_data.get('version_name', 'unknown')}")
            print(f"🔢 รหัสเวอร์ชัน: {latest_version_data.get('version_code', 0)}")
            print(f"📅 วันที่ปล่อย: {latest_version_data.get('release', 'unknown')}")
            
            # ทดสอบการเปรียบเทียบเวอร์ชัน
            is_newer = updater._is_newer_version(
                latest_version_data.get('version_name', '1.0.0'), 
                updater.current_version
            )
            print(f"🆕 มีเวอร์ชันใหม่หรือไม่: {'ใช่' if is_newer else 'ไม่'}")
            return True, latest_version_data
        else:
            print("❌ ไม่พบข้อมูลเวอร์ชัน")
            return False, None
            
    except Exception as e:
        print(f"❌ Error ในการดึงข้อมูลเวอร์ชัน: {e}")
        return False, None

def test_class_initialization():
    """ทดสอบการสร้าง class และ initialization"""
    print("\n=== ทดสอบการสร้าง Class ===")
    try:
        updater = AutoUpdater()
        print("✅ สร้าง AutoUpdater สำเร็จ")
        print(f"✅ current_version: {updater.current_version}")
        print(f"✅ version_url: {updater.version_url}")
        print(f"✅ download_url: {updater.download_url}")
        return True
    except Exception as e:
        print(f"❌ Error ในการสร้าง AutoUpdater: {e}")
        return False

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("🧪 เริ่มทดสอบระบบ auto_updater")
    print("=" * 50)
    
    # ทดสอบการสร้าง class
    if not test_class_initialization():
        print("❌ ทดสอบล้มเหลว: ไม่สามารถสร้าง AutoUpdater ได้")
        return
    
    # ทดสอบการเชื่อมต่ออินเทอร์เน็ต
    if not test_internet_connection():
        print("❌ ทดสอบล้มเหลว: ไม่มีการเชื่อมต่ออินเทอร์เน็ต")
        return
    
    # ทดสอบการตรวจสอบเวอร์ชัน
    success, version_data = test_version_check()
    if success:
        print("\n🎉 ทดสอบพื้นฐานสำเร็จทั้งหมด!")
        print("\n📝 หมายเหตุ: ระบบพร้อมทำงาน")
        print("   - สามารถเชื่อมต่ออินเทอร์เน็ตได้")
        print("   - สามารถดึงข้อมูลเวอร์ชันได้")
        print("   - ระบบ auto-update พร้อมใช้งาน")
    else:
        print("\n❌ ทดสอบล้มเหลว: ไม่สามารถตรวจสอบเวอร์ชันได้")

if __name__ == "__main__":
    main()
