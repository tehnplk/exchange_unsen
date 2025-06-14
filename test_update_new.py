#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบระบบ auto-update ที่ปรับปรุงใหม่
- แจ้งเตือนที่ status bar เมื่อมีเวอร์ชันใหม่
- ไม่แจ้งเตือนเมื่อไม่มีเวอร์ชันใหม่  
- ตรวจสอบแบบ background
"""

import sys
import os
import time
sys.path.append(os.path.dirname(__file__))

from auto_updater import AutoUpdater
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import QTimer

class TestNewAutoUpdater(QMainWindow):
    """UI สำหรับทดสอบระบบ auto-update ใหม่"""
    
    def __init__(self):
        super().__init__()
        self.update_available_data = None
        self.initUI()
        
    def initUI(self):
        """สร้าง UI"""
        self.setWindowTitle("ทดสอบระบบ Auto-Update ใหม่")
        self.setGeometry(100, 100, 700, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("🧪 ทดสอบระบบ Auto-Update ที่ปรับปรุงใหม่")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; color: #2196F3;")
        layout.addWidget(title)
        
        # คำอธิบายการปรับปรุง
        desc = QLabel("""
📋 การปรับปรุงใหม่:
✅ 1. แจ้งเตือนว่ามี version ใหม่ที่ status bar (ไม่ใช่ popup)
✅ 2. ถ้าไม่มีเวอร์ชันใหม่ ไม่แจ้งเตือนอะไร
✅ 3. การตรวจสอบ version ทำแบบ background (ไม่บล็อค UI)
        """)
        desc.setStyleSheet("font-size: 12px; padding: 10px; background-color: #F5F5F5; border-radius: 5px;")
        layout.addWidget(desc)
        
        # ปุ่มทดสอบ
        self.btn_background_check = QPushButton("🔍 ทดสอบตรวจสอบแบบ Background")
        self.btn_background_check.clicked.connect(self.test_background_check)
        layout.addWidget(self.btn_background_check)
        
        self.btn_manual_check = QPushButton("🖱️ ทดสอบตรวจสอบแบบ Manual (แสดง dialog)")
        self.btn_manual_check.clicked.connect(self.test_manual_check)
        layout.addWidget(self.btn_manual_check)
        
        self.btn_reset_status = QPushButton("🔄 รีเซ็ต Status")
        self.btn_reset_status.clicked.connect(self.reset_status)
        layout.addWidget(self.btn_reset_status)
        
        # Status Bar (จำลอง)
        status_label_title = QLabel("📊 Status Bar (จำลอง):")
        status_label_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(status_label_title)
        
        self.statusLabel = QLabel("พร้อมใช้งาน")
        self.statusLabel.setStyleSheet("""
        QLabel {
            color: #4CAF50;
            padding: 8px;
            background-color: #E8F5E8;
            border: 1px solid #4CAF50;
            border-radius: 5px;
            font-size: 12px;
        }
        """)
        layout.addWidget(self.statusLabel)
        
        # Log
        log_title = QLabel("📝 Log:")
        log_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        self.log("✅ UI ทดสอบพร้อมใช้งาน")
        self.log("📝 กดปุ่มเพื่อทดสอบระบบ auto-update ใหม่")
        
    def log(self, message):
        """แสดงข้อความใน log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        print(f"[{timestamp}] {message}")
        
    def update_status(self, message):
        """อัปเดต status (จำลอง statusbar ของโปรแกรมจริง)"""
        self.statusLabel.setText(message)
        self.log(f"📊 Status: {message}")
        
    def reset_status(self):
        """รีเซ็ต status กลับเป็นปกติ"""
        self.update_status("พร้อมใช้งาน")
        self.statusLabel.setStyleSheet("""
        QLabel {
            color: #4CAF50;
            padding: 8px;
            background-color: #E8F5E8;
            border: 1px solid #4CAF50;
            border-radius: 5px;
            font-size: 12px;
        }
        """)
        self.log("🔄 รีเซ็ต status เรียบร้อย")
        
    def test_background_check(self):
        """ทดสอบการตรวจสอบแบบ background"""
        self.log("🚀 เริ่มทดสอบการตรวจสอบแบบ Background")
        self.log("   - ถ้ามีเวอร์ชันใหม่: จะแสดงการแจ้งเตือนที่ status bar")
        self.log("   - ถ้าไม่มีเวอร์ชันใหม่: จะไม่แจ้งเตือนอะไร")
        
        try:
            updater = AutoUpdater(parent=self)
            result = updater.check_for_updates_background(callback=self.on_update_available)
            self.log(f"✅ Background check เสร็จสิ้น: มีเวอร์ชันใหม่ = {result}")
            
            if not result:
                self.log("ℹ️ ไม่มีเวอร์ชันใหม่ - ไม่แสดงการแจ้งเตือน (ถูกต้องตามที่ต้องการ)")
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            
    def test_manual_check(self):
        """ทดสอบการตรวจสอบแบบ manual (แสดง dialog)"""
        self.log("🖱️ เริ่มทดสอบการตรวจสอบแบบ Manual")
        self.log("   - จะแสดง dialog ว่ามีหรือไม่มีเวอร์ชันใหม่")
        
        try:
            updater = AutoUpdater(parent=self)
            result = updater.check_for_updates(silent=False)
            self.log(f"✅ Manual check เสร็จสิ้น: {result}")
        except Exception as e:
            self.log(f"❌ Error: {e}")
    
    def on_update_available(self, version_data):
        """เมื่อพบเวอร์ชันใหม่ - แสดงการแจ้งเตือนที่ status bar"""
        self.update_available_data = version_data
        latest_version = version_data.get('version_name', 'unknown')
        version_code = version_data.get('version_code', 0)
        
        # อัปเดตสถานะให้แสดงข้อความแจ้งเตือน
        update_message = f"🚀 มีเวอร์ชันใหม่ {latest_version} (รหัส: {version_code}) - คลิก 'Manual Check' เพื่ออัปเดต"
        self.update_status(update_message)
        
        # เปลี่ยนสีสถานะให้เด่นขึ้น (สีส้มสะดุดตา)
        self.statusLabel.setStyleSheet("""
        QLabel {
            color: #FF6600;
            padding: 8px;
            background-color: #FFF3E0;
            border: 2px solid #FF9800;
            border-radius: 8px;
            font-weight: bold;
            font-size: 12px;
        }
        """)
        
        # Log การแจ้งเตือน
        self.log(f"🆕 พบเวอร์ชันใหม่: {latest_version} (รหัส: {version_code})")
        self.log("🎨 เปลี่ยนสี status bar เป็นสีส้มเพื่อให้เด่น")

def main():
    """ฟังก์ชันหลัก"""
    app = QApplication(sys.argv)
    
    window = TestNewAutoUpdater()
    window.show()
    
    print("🚀 เริ่มต้น UI ทดสอบระบบ auto-update ใหม่")
    print("📝 ใช้ UI เพื่อทดสอบการปรับปรุงใหม่")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
