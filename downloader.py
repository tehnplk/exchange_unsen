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
import psutil
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
        
        # ข้าม backup เนื่องจากเราไม่เขียนทับไฟล์เดิม
        if os.path.exists(output_path):
            print_with_delay(f"ℹ️ ไฟล์ใหม่จะถูกดาวน์โหลดเป็น: {output_path}")
            print_with_delay("ℹ️ ไฟล์เดิมจะไม่ถูกลบ")
        
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
        
        print_with_delay("✅ ดาวน์โหลดเสร็จสิ้น")        # บันทึกไฟล์ใหม่ (ไม่เขียนทับไฟล์เดิม)
        print_with_delay("� บันทึกไฟล์ใหม่...")
        
        # ตรวจสอบว่าไฟล์เป้าหมายมีอยู่แล้วหรือไม่
        if os.path.exists(output_path):
            print_with_delay(f"⚠️ ไฟล์ {output_path} มีอยู่แล้ว กำลังเขียนทับ...")
            
            # ลบไฟล์เดิมถ้ามี (เฉพาะไฟล์ที่มี version code ใหม่)
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    os.remove(output_path)
                    break
                except (OSError, PermissionError) as e:
                    if attempt == max_attempts - 1:
                        # ถ้าลบไม่ได้ ให้เปลี่ยนชื่อไฟล์ใหม่
                        import time
                        timestamp = int(time.time())
                        new_output_path = output_path.replace('.exe', f'_{timestamp}.exe')
                        print_with_delay(f"⚠️ ไม่สามารถลบไฟล์เดิมได้ เปลี่ยนชื่อเป็น: {new_output_path}")
                        output_path = new_output_path
                        break
                    print_with_delay(f"⚠️ ลองลบไฟล์อีกครั้ง... ({attempt + 1}/{max_attempts})")
                    time.sleep(1)
        
        shutil.move(temp_path, output_path)        
        print_with_delay("🎉 อัปเดตสำเร็จ!")
        return True
        
    except requests.exceptions.RequestException as e:
        print_with_delay(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return False
    except Exception as e:
        print_with_delay(f"❌ เกิดข้อผิดพลาด: {e}")
        
        # ลบไฟล์ temp หากมี
        temp_path = output_path + ".tmp"
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                print_with_delay("🧹 ลบไฟล์ชั่วคราวแล้ว")
            except:
                pass
        
        return False

def wait_for_file_release(file_path, max_wait=30):
    """รอให้ไฟล์ถูกปล่อยจาก process อื่น"""
    print_with_delay(f"⏳ รอให้ไฟล์ {file_path} ถูกปล่อย...")
    
    for attempt in range(max_wait):
        try:
            # ลองเปิดไฟล์เพื่อทดสอบว่าถูกใช้งานอยู่หรือไม่
            with open(file_path, 'r+b'):
                pass
            print_with_delay("✅ ไฟล์พร้อมสำหรับการแก้ไข")
            return True
        except (IOError, OSError, PermissionError):
            # ไฟล์ยังถูกใช้งานอยู่
            if attempt == 0:
                print_with_delay("⚠️ ไฟล์ยังถูกใช้งานอยู่ กำลังรอ...")
            
            # ลองหา process ที่ใช้ไฟล์นี้และปิด
            try:
                file_absolute = os.path.abspath(file_path)
                killed_any = False
                
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        if proc.info['exe'] and os.path.abspath(proc.info['exe']) == file_absolute:
                            print_with_delay(f"🔧 ปิด process: {proc.info['name']} (PID: {proc.info['pid']})")
                            proc.terminate()
                            killed_any = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                if killed_any:
                    time.sleep(2)  # รอให้ process ปิดจริง
                    
            except Exception as e:
                print_with_delay(f"⚠️ ไม่สามารถหา process ที่ใช้ไฟล์: {e}")
            
            time.sleep(1)
            print(f"⏳ รอครั้งที่ {attempt + 1}/{max_wait}...")
    
    print_with_delay("❌ หมดเวลารอ ไฟล์ยังถูกใช้งานอยู่")
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
    # ไม่ต้องใช้ backup_file เนื่องจากเราไม่เขียนทับไฟล์เดิม
    
    print(f"🎯 Target: {output_file}")
    print(f"🌐 URL: {download_url}")
    print("ℹ️ ไฟล์ใหม่จะถูกดาวน์โหลดโดยไม่เขียนทับไฟล์เดิม")
    print()
    
    # เริ่มดาวน์โหลด (ไม่ส่ง backup_file)
    success = download_file(download_url, output_file)
    
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
