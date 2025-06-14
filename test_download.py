#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบระบบ download และ UI components
"""

import sys
import os
import tempfile
import time
sys.path.append(os.path.dirname(__file__))

from auto_updater import DownloadThread
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop

def test_download_thread():
    """ทดสอบ DownloadThread"""
    print("=== ทดสอบ DownloadThread ===")
    
    # สร้าง QApplication หาก่อนไม่มี
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # สร้างไฟล์ชั่วคราว
    temp_file = tempfile.mktemp(suffix='.exe')
    print(f"📁 จะดาวน์โหลดไปที่: {temp_file}")
    
    # URL ทดสอบ (ไฟล์เล็กๆ)
    test_url = "https://github.com/tehnplk/exchange_unsen/raw/master/dist/ExchangeUnsen.exe"
    
    # สร้าง download thread
    download_thread = DownloadThread(test_url, temp_file)
    
    # ตัวแปรสำหรับตรวจสอบผล
    download_result = {'success': False, 'message': '', 'progress_updates': 0}
    
    def on_progress(value):
        download_result['progress_updates'] += 1
        if download_result['progress_updates'] % 10 == 0:  # แสดงทุก 10 updates
            print(f"📊 Progress: {value}%")
    
    def on_finished(success, message):
        download_result['success'] = success
        download_result['message'] = message
        print(f"✅ Download finished: {success}, Message: {message}")
        app.quit()
    
    # เชื่อมต่อ signals
    download_thread.progress.connect(on_progress)
    download_thread.finished.connect(on_finished)
    
    print("🚀 เริ่มดาวน์โหลดทดสอบ...")
    download_thread.start()
    
    # รอให้ดาวน์โหลดเสร็จ (timeout 60 วินาที)
    start_time = time.time()
    timeout = 60
    
    while download_thread.isRunning() and (time.time() - start_time) < timeout:
        app.processEvents()
        time.sleep(0.1)
    
    if download_thread.isRunning():
        print("⏰ Timeout - ยกเลิกการดาวน์โหลด")
        download_thread.terminate()
        download_thread.wait()
        return False
    
    # ตรวจสอบผลลัพธ์
    if download_result['success']:
        file_size = os.path.getsize(temp_file) if os.path.exists(temp_file) else 0
        print(f"✅ ดาวน์โหลดสำเร็จ!")
        print(f"📊 ขนาดไฟล์: {file_size:,} bytes")
        print(f"📊 Progress updates: {download_result['progress_updates']}")
        
        # ลบไฟล์ทดสอบ
        try:
            os.remove(temp_file)
            print("🗑️ ลบไฟล์ทดสอบแล้ว")
        except:
            pass
        
        return True
    else:
        print(f"❌ ดาวน์โหลดล้มเหลว: {download_result['message']}")
        return False

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("🧪 ทดสอบระบบ Download และ UI")
    print("=" * 50)
    
    try:
        if test_download_thread():
            print("\n🎉 ทดสอบการดาวน์โหลดสำเร็จ!")
        else:
            print("\n❌ ทดสอบการดาวน์โหลดล้มเหลว!")
    except Exception as e:
        print(f"\n❌ Error ในการทดสอบ: {e}")

if __name__ == "__main__":
    main()
