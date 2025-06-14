#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ExchangeUnsen Downloader - โปรแกรมดาวน์โหลดและอัปเดตไฟล์
"""

import sys
import os
import requests
import shutil
import time
import subprocess
from pathlib import Path

def print_with_delay(message, delay=0.5):
    """แสดงข้อความพร้อม delay"""
    print(message)
    time.sleep(delay)

def download_file(url, output_path, backup_path=None):
    """ดาวน์โหลดไฟล์พร้อมแสดง progress"""
    try:
        print_with_delay("🔗 เชื่อมต่อกับเซิร์ฟเวอร์...")
        
        # ตรวจสอบการเชื่อมต่อ
        response = requests.head(url, timeout=10)
        response.raise_for_status()
        
        file_size = int(response.headers.get('content-length', 0))
        print_with_delay(f"📦 ขนาดไฟล์: {file_size // (1024*1024):.1f} MB")
        
        # สำรองไฟล์เก่า
        if backup_path and os.path.exists(output_path):
            print_with_delay("💾 สำรองไฟล์เก่า...")
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.copy2(output_path, backup_path)
            print_with_delay("✅ สำรองไฟล์เก่าเสร็จสิ้น")
        
        # ดาวน์โหลด
        print_with_delay("⬇️ เริ่มดาวน์โหลด...")
        temp_path = output_path + ".tmp"
        
        response = requests.get(url, stream=True, timeout=30,
                              headers={'User-Agent': 'ExchangeUnsen-Downloader/1.0'})
        response.raise_for_status()
        
        downloaded = 0
        with open(temp_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    
                    if file_size > 0:
                        percent = (downloaded / file_size) * 100
                        # แสดง progress ทุก 10%
                        if int(percent) % 10 == 0 and int(percent) != 0:
                            print(f"📊 Progress: {int(percent)}%")
        
        print_with_delay("✅ ดาวน์โหลดเสร็จสิ้น")
        
        # แทนที่ไฟล์เก่า
        print_with_delay("🔄 ติดตั้งไฟล์ใหม่...")
        if os.path.exists(output_path):
            os.remove(output_path)
        shutil.move(temp_path, output_path)
        
        print_with_delay("🎉 อัปเดตสำเร็จ!")
        return True
        
    except requests.exceptions.RequestException as e:
        print_with_delay(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return False
    except Exception as e:
        print_with_delay(f"❌ เกิดข้อผิดพลาด: {e}")
        
        # กู้คืนไฟล์เก่าหากมี
        if backup_path and os.path.exists(backup_path):
            print_with_delay("🔧 กำลังกู้คืนไฟล์เก่า...")
            if os.path.exists(output_path):
                os.remove(output_path)
            shutil.move(backup_path, output_path)
            print_with_delay("✅ กู้คืนไฟล์เก่าสำเร็จ")
        
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("="*50)
    print("  ExchangeUnsen Downloader v1.0")
    print("="*50)
    print()
    
    # ตรวจสอบ arguments
    if len(sys.argv) < 3:
        print("❌ Usage: downloader.exe <download_url> <output_file>")
        print("📝 Example: downloader.exe https://github.com/.../ExchangeUnsen.exe ExchangeUnsen.exe")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    download_url = sys.argv[1]
    output_file = sys.argv[2]
    backup_file = output_file.replace('.exe', '_backup.exe')
    
    print(f"🎯 Target: {output_file}")
    print(f"🌐 URL: {download_url}")
    print(f"💾 Backup: {backup_file}")
    print()
    
    # เริ่มดาวน์โหลด
    success = download_file(download_url, output_file, backup_file)
    
    if success:
        print()
        print("="*50)
        print("  🎉 การอัปเดตเสร็จสมบูรณ์!")
        print("="*50)
        print()
        
        # ถามว่าต้องการเปิดโปรแกรมใหม่หรือไม่
        try:
            choice = input("ต้องการเปิดโปรแกรมใหม่หรือไม่? (Y/n): ").strip().lower()
            if choice in ['', 'y', 'yes']:
                print_with_delay("🚀 กำลังเปิดโปรแกรมใหม่...")
                subprocess.Popen([output_file])
                print_with_delay("✅ เปิดโปรแกรมใหม่แล้ว")
        except KeyboardInterrupt:
            print("\n👋 ยกเลิกการเปิดโปรแกรม")
    else:
        print()
        print("="*50)
        print("  ❌ การอัปเดตล้มเหลว")
        print("="*50)
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print()
    print("👋 ขอบคุณที่ใช้ ExchangeUnsen Downloader")
    time.sleep(2)

if __name__ == "__main__":
    main()
