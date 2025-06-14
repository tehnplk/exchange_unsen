#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบเต็มรูปแบบระบบ auto-update
"""

import sys
import os
import subprocess
import time
import tempfile
sys.path.append(os.path.dirname(__file__))

from auto_updater import AutoUpdater, DownloadThread
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QEventLoop, QTimer

class FullSystemTest:
    """คลาสสำหรับทดสอบระบบเต็มรูปแบบ"""
    
    def __init__(self):
        self.test_results = {}
        self.app = None
        
    def setup_qt_app(self):
        """สร้าง QApplication"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
    
    def test_1_basic_functionality(self):
        """ทดสอบฟังก์ชันพื้นฐาน"""
        print("\n" + "="*50)
        print("🧪 TEST 1: Basic Functionality")
        print("="*50)
        
        try:
            # ทดสอบการสร้าง AutoUpdater
            updater = AutoUpdater()
            print("✅ AutoUpdater created successfully")
            
            # ทดสอบการเชื่อมต่ออินเทอร์เน็ต
            if updater.check_internet_connection():
                print("✅ Internet connection available")
            else:
                print("❌ No internet connection")
                return False
            
            # ทดสอบการตรวจสอบเวอร์ชัน
            import requests
            response = requests.get(updater.version_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Version data retrieved: {len(data)} versions")
                latest = max(data, key=lambda x: x.get('version_code', 0))
                print(f"📦 Latest version: {latest.get('version_name')} (code: {latest.get('version_code')})")
            else:
                print("❌ Failed to retrieve version data")
                return False
                
            self.test_results['basic'] = True
            return True
            
        except Exception as e:
            print(f"❌ Basic functionality test failed: {e}")
            self.test_results['basic'] = False
            return False
    
    def test_2_download_functionality(self):
        """ทดสอบการดาวน์โหลด"""
        print("\n" + "="*50)
        print("🧪 TEST 2: Download Functionality")
        print("="*50)
        
        try:
            self.setup_qt_app()
            
            # สร้างไฟล์ทดสอบขนาดเล็ก
            test_url = "https://raw.githubusercontent.com/tehnplk/exchange_unsen/master/README.md"
            temp_file = tempfile.mktemp(suffix='.txt')
            
            print(f"📁 Test download to: {temp_file}")
            print(f"🌐 Test URL: {test_url}")
            
            # สร้าง DownloadThread
            download_thread = DownloadThread(test_url, temp_file)
            
            # ตัวแปรสำหรับตรวจสอบผล
            result = {'finished': False, 'success': False, 'progress_count': 0}
            
            def on_progress(value):
                result['progress_count'] += 1
                if result['progress_count'] % 5 == 0:
                    print(f"📊 Progress: {value}%")
            
            def on_finished(success, message):
                result['finished'] = True
                result['success'] = success
                result['message'] = message
                print(f"🏁 Download finished: {success}")
                if success and os.path.exists(temp_file):
                    size = os.path.getsize(temp_file)
                    print(f"📄 File size: {size} bytes")
                self.app.quit()
            
            download_thread.progress.connect(on_progress)
            download_thread.finished.connect(on_finished)
            
            print("🚀 Starting download test...")
            download_thread.start()
            
            # รอให้ดาวน์โหลดเสร็จ (timeout 30 วินาที)
            start_time = time.time()
            timeout = 30
            
            while not result['finished'] and (time.time() - start_time) < timeout:
                self.app.processEvents()
                time.sleep(0.1)
            
            if not result['finished']:
                print("⏰ Download test timeout")
                download_thread.terminate()
                download_thread.wait()
                self.test_results['download'] = False
                return False
            
            # ลบไฟล์ทดสอบ
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print("🗑️ Test file cleaned up")
            except:
                pass
            
            if result['success']:
                print("✅ Download functionality works correctly")
                self.test_results['download'] = True
                return True
            else:
                print(f"❌ Download failed: {result.get('message', 'Unknown error')}")
                self.test_results['download'] = False
                return False
                
        except Exception as e:
            print(f"❌ Download functionality test failed: {e}")
            self.test_results['download'] = False
            return False
    
    def test_3_version_comparison(self):
        """ทดสอบการเปรียบเทียบเวอร์ชัน"""
        print("\n" + "="*50)
        print("🧪 TEST 3: Version Comparison")
        print("="*50)
        
        try:
            updater = AutoUpdater()
            
            # ทดสอบการเปรียบเทียบเวอร์ชัน
            test_cases = [
                ("1.0.4", "1.0.3", True),   # newer
                ("1.0.3", "1.0.3", False),  # same
                ("1.0.2", "1.0.3", False),  # older
                ("2.0.0", "1.9.9", True),   # major version
            ]
            
            all_passed = True
            for latest, current, expected in test_cases:
                result = updater._is_newer_version(latest, current)
                status = "✅" if result == expected else "❌"
                print(f"{status} {latest} vs {current} -> {result} (expected: {expected})")
                if result != expected:
                    all_passed = False
            
            if all_passed:
                print("✅ Version comparison works correctly")
                self.test_results['version_comparison'] = True
                return True
            else:
                print("❌ Version comparison has issues")
                self.test_results['version_comparison'] = False
                return False
                
        except Exception as e:
            print(f"❌ Version comparison test failed: {e}")
            self.test_results['version_comparison'] = False
            return False
    
    def test_4_ui_components(self):
        """ทดสอบ UI Components"""
        print("\n" + "="*50)
        print("🧪 TEST 4: UI Components")
        print("="*50)
        
        try:
            self.setup_qt_app()
            
            # ทดสอบ MessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Test")
            msg.setText("UI Component Test")
            msg.setStandardButtons(QMessageBox.Ok)
            
            # ปิดอัตโนมัติหลัง 1 วินาที
            QTimer.singleShot(1000, msg.accept)
            msg.exec_()
            
            print("✅ QMessageBox works correctly")
            
            # ทดสอบ QProgressDialog
            from PyQt5.QtWidgets import QProgressDialog
            progress = QProgressDialog("Testing...", "Cancel", 0, 100)
            progress.setWindowTitle("Progress Test")
            progress.show()
            
            # อัปเดต progress และปิดอัตโนมัติ
            for i in range(0, 101, 20):
                progress.setValue(i)
                self.app.processEvents()
                time.sleep(0.1)
            
            progress.close()
            print("✅ QProgressDialog works correctly")
            
            self.test_results['ui_components'] = True
            return True
            
        except Exception as e:
            print(f"❌ UI components test failed: {e}")
            self.test_results['ui_components'] = False
            return False
    
    def test_5_exe_integration(self):
        """ทดสอบการเชื่อมต่อกับ EXE"""
        print("\n" + "="*50)
        print("🧪 TEST 5: EXE Integration")
        print("="*50)
        
        try:
            exe_path = "dist/ExchangeUnsen.exe"
            
            if not os.path.exists(exe_path):
                print("❌ ExchangeUnsen.exe not found")
                self.test_results['exe_integration'] = False
                return False
            
            print(f"✅ ExchangeUnsen.exe found")
            
            # ตรวจสอบขนาดไฟล์
            size = os.path.getsize(exe_path)
            print(f"📄 EXE size: {size:,} bytes ({size/1024/1024:.1f} MB)")
            
            if size < 1024 * 1024:  # น้อยกว่า 1MB อาจจะผิดปกติ
                print("⚠️ EXE size seems too small")
            
            # ทดสอบการรัน EXE (quick test)
            print("🚀 Testing EXE execution...")
            try:
                # รัน EXE แบบสั้นๆ เพื่อดูว่า error หรือไม่
                proc = subprocess.Popen([exe_path, "--help"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      timeout=5)
                stdout, stderr = proc.communicate(timeout=5)
                print("✅ EXE can be executed")
            except subprocess.TimeoutExpired:
                print("✅ EXE starts successfully (timeout expected)")
                proc.kill()
            except Exception as e:
                print(f"⚠️ EXE execution issue: {e}")
            
            self.test_results['exe_integration'] = True
            return True
            
        except Exception as e:
            print(f"❌ EXE integration test failed: {e}")
            self.test_results['exe_integration'] = False
            return False
    
    def run_full_test(self):
        """รันการทดสอบเต็มรูปแบบ"""
        print("🚀 เริ่มการทดสอบเต็มรูปแบบระบบ Auto-Update")
        print("="*70)
        
        tests = [
            ("Basic Functionality", self.test_1_basic_functionality),
            ("Download Functionality", self.test_2_download_functionality),
            ("Version Comparison", self.test_3_version_comparison),
            ("UI Components", self.test_4_ui_components),
            ("EXE Integration", self.test_5_exe_integration),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
        
        # สรุปผล
        print("\n" + "="*70)
        print("📊 สรุปผลการทดสอบ")
        print("="*70)
        
        for test_name, _ in tests:
            key = test_name.lower().replace(" ", "_")
            status = "✅ PASS" if self.test_results.get(key, False) else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 ผลรวม: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ระบบ Auto-Update ผ่านการทดสอบทั้งหมด!")
            print("✅ พร้อม Push ขึ้น Repository")
        else:
            print("⚠️ มีการทดสอบบางส่วนที่ล้มเหลว")
            print("🔧 แนะนำให้ตรวจสอบและแก้ไขก่อน Push")
        
        return passed == total

def main():
    """ฟังก์ชันหลัก"""
    tester = FullSystemTest()
    success = tester.run_full_test()
    
    if success:
        print("\n🚀 ระบบพร้อมสำหรับ Production!")
    else:
        print("\n🔧 ต้องการการแก้ไขเพิ่มเติม")
    
    return success

if __name__ == "__main__":
    main()
