#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์สำหรับส่งเวอร์ชันใหม่ไป Google Apps Script
"""

import sys
import requests
from config import APP_CONFIG

def post_version_to_api(version_name=None, version_code=None, release_date=None):
    """
    POST เวอร์ชันใหม่ไปยัง Google Apps Script API
    
    Args:
        version_name (str): ชื่อเวอร์ชัน (ถ้าไม่ระบุจะใช้จาก config.py)
        version_code (int): รหัสเวอร์ชัน (ถ้าไม่ระบุจะใช้จาก config.py)
        release_date (str): วันที่ปล่อย (ถ้าไม่ระบุจะใช้จาก config.py)
    """
    # ใช้ข้อมูลจาก config ถ้าไม่ระบุ
    if version_name is None:
        version_name = APP_CONFIG.get('version', '1.0.0')
    
    if version_code is None:
        version_code = APP_CONFIG.get('version_code')
        if version_code is None:
            # สร้าง version_code จากเวอร์ชัน ถ้าไม่มีใน config
            try:
                parts = version_name.split('.')
                version_code = int(''.join(parts))
            except:
                version_code = 1
    
    if release_date is None:
        release_date = APP_CONFIG.get('release', '')
    
    api_url = "https://script.google.com/macros/s/AKfycbyzveWCcGt4GOQgVF8CUVF6I2Fzmz8x7Ds4BASTXPSh6VC1ErxTxv_KGjsaG7q4rNTLAw/exec"
    
    try:
        print(f"📤 กำลังส่งเวอร์ชัน {version_name} (code: {version_code}) ไปยัง API...")
        
        data = {
            'version_name': version_name,
            'version_code': version_code,
            'release': release_date,
            'action': 'add'
        }
        
        response = requests.post(api_url, json=data, timeout=15)
        
        print(f"📋 Status Code: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ อัปเดตเวอร์ชัน {version_name} สำเร็จ!")
            return True
        else:
            print(f"❌ เกิดข้อผิดพลาด: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        return False

if __name__ == "__main__":
    # รองรับการใช้งานจาก command line
    if len(sys.argv) > 1:
        version_name = sys.argv[1]
        version_code = int(sys.argv[2]) if len(sys.argv) > 2 else None
        release_date = sys.argv[3] if len(sys.argv) > 3 else None
        post_version_to_api(version_name, version_code, release_date)
    else:
        # ใช้ข้อมูลจาก config.py
        post_version_to_api()
