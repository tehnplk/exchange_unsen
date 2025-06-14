#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบระบบ auto_updater ผ่าน UI จริง
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel
from PyQt5.QtCore import QTimer
from auto_updater import AutoUpdater

class TestAutoUpdaterUI(QMainWindow):
    """UI สำหรับทดสอบ auto_updater"""
    
    def __init__(self):
        super().__init__()
        self.updater = None
        self.update_available_data = None  # ข้อมูลเวอร์ชันใหม่
        self.initUI()
        
    def initUI(self):
        """สร้าง UI"""
        self.setWindowTitle("ทดสอบระบบ Auto Update")
        self.setGeometry(100, 100, 600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("🧪 ทดสอบระบบ Auto Update ExchangeUnsen")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # ปุ่มทดสอบ
        self.btn_check_update = QPushButton("🔍 ตรวจสอบการอัปเดต")
        self.btn_check_update.clicked.connect(self.check_for_updates)
        layout.addWidget(self.btn_check_update)
        
        self.btn_silent_check = QPushButton("🤐 ตรวจสอบแบบเงียบ (Silent)")
        self.btn_silent_check.clicked.connect(self.check_for_updates_silent)
        layout.addWidget(self.btn_silent_check)
        
        # กล่องแสดงผล
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Status bar
        self.status_label = QLabel("พร้อมทดสอบ")
        layout.addWidget(self.status_label)
        
        self.log("✅ UI ทดสอบพร้อมใช้งาน")
        self.log("📝 คลิกปุ่มเพื่อทดสอบระบบ auto-update")
        
    def log(self, message):
        """แสดงข้อความใน log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        print(f"[{timestamp}] {message}")
        
    def update_status(self, message):
        """อัปเดต status"""
        self.status_label.setText(message)
        self.log(f"📊 Status: {message}")
        
    def check_for_updates(self):
        """ทดสอบการตรวจสอบอัปเดต"""
        self.log("🚀 เริ่มทดสอบการตรวจสอบอัปเดต (แสดง dialog)")
        self.update_status("กำลังตรวจสอบ...")
        
        try:
            self.updater = AutoUpdater(parent=self)
            result = self.updater.check_for_updates(silent=False)
            self.log(f"✅ ผลการตรวจสอบ: {result}")
            self.update_status("พร้อมใช้งาน")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.update_status("เกิดข้อผิดพลาด")
            
    def check_for_updates_silent(self):
        """ทดสอบการตรวจสอบอัปเดตแบบเงียบ"""
        self.log("🤐 เริ่มทดสอบการตรวจสอบอัปเดต (silent mode)")
        self.update_status("กำลังตรวจสอบแบบเงียบ...")
        
        try:
            self.updater = AutoUpdater(parent=self)
            result = self.updater.check_for_updates(silent=True)
            self.log(f"✅ ผลการตรวจสอบ (silent): {result}")
            self.update_status("พร้อมใช้งาน")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.update_status("เกิดข้อผิดพลาด")
    
    def close_for_update(self):
        """ฟังก์ชันสำหรับปิดโปรแกรมเพื่ออัปเดต"""
        self.log("🔄 ได้รับคำสั่งปิดโปรแกรมเพื่ออัปเดต")
        self.update_status("กำลังปิดโปรแกรม...")
        
        # ปิดแบบ graceful
        QTimer.singleShot(1000, self.close)

def main():
    """ฟังก์ชันหลัก"""
    app = QApplication(sys.argv)
    
    window = TestAutoUpdaterUI()
    window.show()
    
    print("🚀 เริ่มต้น UI ทดสอบ auto_updater")
    print("📝 ใช้ UI เพื่อทดสอบระบบ auto-update")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
