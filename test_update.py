#!/usr/bin/env python3
import requests
from packaging import version

print("🔍 Testing auto-update logic...")

try:
    # ดึงข้อมูลจาก API
    response = requests.get('https://script.google.com/macros/s/AKfycbyzveWCcGt4GOQgVF8CUVF6I2Fzmz8x7Ds4BASTXPSh6VC1ErxTxv_KGjsaG7q4rNTLAw/exec', timeout=10)
    data = response.json()
    
    # หาเวอร์ชันล่าสุด
    latest_data = max(data, key=lambda x: x.get('version_code', 0))
    latest_version = latest_data['version_name']
    
    # เปรียบเทียบ
    current_version = '1.0.2'
    need_update = version.parse(latest_version) > version.parse(current_version)
    
    print(f"Current version: {current_version}")
    print(f"Latest version: {latest_version}")
    print(f"Update needed: {need_update}")
    
    if need_update:
        print(f"✅ Update available! {current_version} → {latest_version}")
    else:
        print("✅ You are using the latest version.")
        
except Exception as e:
    print(f"❌ Error: {e}")
