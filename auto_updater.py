#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
โมดูลสำหรับระบบอัปเดตอัตโนมัติ ExchangeUnsen
"""

import json
import requests
import subprocess
import os
import sys
from packaging import version
from PyQt5.QtWidgets import QMessageBox, QProgressDialog
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from config import APP_CONFIG

class AutoUpdater:
    """คลาสสำหรับจัดการการอัปเดตอัตโนมัติ"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.current_version = APP_CONFIG.get('version', '1.0.0')
        self.version_url = "https://raw.githubusercontent.com/tehnplk/exchange_unsen/master/version.json"
        self.update_script = "update_app.bat"
        
    def check_for_updates(self, silent=False):
        """
        ตรวจสอบการอัปเดต
        
        Args:
            silent (bool): ถ้า True จะไม่แสดง popup เมื่อไม่มีอัปเดต
        """
        try:
            # ดาวน์โหลดข้อมูลเวอร์ชันจาก GitHub
            response = requests.get(self.version_url, timeout=10)
            response.raise_for_status()
            
            version_data = response.json()
            latest_version = version_data.get('version', '1.0.0')
            
            # เปรียบเทียบเวอร์ชัน
            if self._is_newer_version(latest_version, self.current_version):
                return self._show_update_dialog(version_data)
            else:
                if not silent:
                    self._show_no_update_message()
                return False
                
        except requests.exceptions.RequestException:
            if not silent:
                self._show_connection_error()
            return False
        except Exception as e:
            if not silent:
                self._show_error_message(f"เกิดข้อผิดพลาด: {str(e)}")
            return False
    
    def _is_newer_version(self, latest, current):
        """เปรียบเทียบเวอร์ชัน"""
        try:
            return version.parse(latest) > version.parse(current)
        except:
            return latest != current
    
    def _show_update_dialog(self, version_data):
        """แสดง dialog สำหรับถามการอัปเดต"""
        latest_version = version_data.get('version', 'unknown')
        notes = version_data.get('notes', [])
        release_date = version_data.get('release_date', 'unknown')
        
        message = f"""🚀 พบเวอร์ชันใหม่!

เวอร์ชันปัจจุบัน: {self.current_version}
เวอร์ชันใหม่: {latest_version}
วันที่ปล่อย: {release_date}

ความเปลี่ยนแปลง:
{chr(10).join(f"• {note}" for note in notes)}

ต้องการอัปเดตเลยหรือไม่?"""
        
        reply = QMessageBox.question(
            self.parent,
            "อัปเดตโปรแกรม",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            return self._start_update()
        return False
    
    def _start_update(self):
        """เริ่มกระบวนการอัปเดต"""
        try:
            if os.path.exists(self.update_script):
                # แสดง progress dialog
                progress = QProgressDialog("กำลังอัปเดต...", "ยกเลิก", 0, 0, self.parent)
                progress.setWindowTitle("กำลังอัปเดต")
                progress.setModal(True)
                progress.show()
                
                # รันสคริปต์อัปเดต
                subprocess.Popen([self.update_script], shell=True)
                
                # ปิดโปรแกรมเพื่อให้อัปเดตได้
                if self.parent:
                    QTimer.singleShot(2000, self.parent.close)
                
                return True
            else:
                self._show_error_message(f"ไม่พบไฟล์อัปเดต: {self.update_script}")
                return False
                
        except Exception as e:
            self._show_error_message(f"เกิดข้อผิดพลาดในการอัปเดต: {str(e)}")
            return False
    
    def _show_no_update_message(self):
        """แสดงข้อความเมื่อไม่มีอัปเดต"""
        QMessageBox.information(
            self.parent,
            "ตรวจสอบอัปเดต",
            f"คุณใช้เวอร์ชันล่าสุดแล้ว (v{self.current_version})"
        )
    
    def _show_connection_error(self):
        """แสดงข้อความเมื่อเชื่อมต่ออินเทอร์เน็ตไม่ได้"""
        QMessageBox.warning(
            self.parent,
            "ข้อผิดพลาด",
            "ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้\nกรุณาตรวจสอบการเชื่อมต่อและลองใหม่"
        )
    
    def _show_error_message(self, message):
        """แสดงข้อความแสดงข้อผิดพลาด"""
        QMessageBox.critical(
            self.parent,
            "ข้อผิดพลาด",
            message
        )

class UpdateCheckThread(QThread):
    """Thread สำหรับตรวจสอบอัปเดตแบบไม่บล็อก UI"""
    
    update_available = pyqtSignal(dict)
    no_update = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, version_url, current_version):
        super().__init__()
        self.version_url = version_url
        self.current_version = current_version
        
    def run(self):
        """รันการตรวจสอบอัปเดตใน background"""
        try:
            response = requests.get(self.version_url, timeout=10)
            response.raise_for_status()
            
            version_data = response.json()
            latest_version = version_data.get('version', '1.0.0')
            
            if self._is_newer_version(latest_version, self.current_version):
                self.update_available.emit(version_data)
            else:
                self.no_update.emit()
                
        except requests.exceptions.RequestException:
            self.error_occurred.emit("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้")
        except Exception as e:
            self.error_occurred.emit(f"เกิดข้อผิดพลาด: {str(e)}")
    
    def _is_newer_version(self, latest, current):
        """เปรียบเทียบเวอร์ชัน"""
        try:
            return version.parse(latest) > version.parse(current)
        except:
            return latest != current

def check_update_on_startup(parent=None, silent=True):
    """
    ฟังก์ชันสำหรับเรียกตรวจสอบอัปเดตเมื่อเปิดโปรแกรม
    
    Args:
        parent: Parent widget สำหรับ dialog
        silent: ถ้า True จะไม่แสดงข้อความเมื่อไม่มีอัปเดต
    """
    updater = AutoUpdater(parent)
    return updater.check_for_updates(silent=silent)
