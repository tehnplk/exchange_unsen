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
import shutil
import socket
from pathlib import Path
from packaging import version
from PyQt5.QtWidgets import QMessageBox, QProgressDialog, QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from config import APP_CONFIG

class DownloadThread(QThread):
    """Thread สำหรับดาวน์โหลดไฟล์"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, output_path):
        super().__init__()
        self.url = url
        self.output_path = output_path
        
    def run(self):
        """ดาวน์โหลดไฟล์พร้อมแสดง progress"""
        try:
            response = requests.get(self.url, stream=True, timeout=30,
                                  headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(self.output_path, 'wb') as file:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress.emit(progress)
                            
            self.finished.emit(True, "ดาวน์โหลดสำเร็จ")
            
        except Exception as e:
            self.finished.emit(False, f"เกิดข้อผิดพลาด: {str(e)}")

class AutoUpdater:
    """คลาสสำหรับจัดการการอัปเดตอัตโนมัติ"""
    
    # Class variable สำหรับป้องกันการเรียกซ้ำ
    _update_check_in_progress = False
    
    def __init__(self, parent=None):
        self.parent = parent
        self.current_version = APP_CONFIG.get('version', '1.0.0')
        self.version_url = "https://script.google.com/macros/s/AKfycbyzveWCcGt4GOQgVF8CUVF6I2Fzmz8x7Ds4BASTXPSh6VC1ErxTxv_KGjsaG7q4rNTLAw/exec"
        self.download_url = "https://github.com/tehnplk/exchange_unsen/raw/master/dist/ExchangeUnsen.exe"
        self.update_script = "update_app.bat"  # สำรอง fallback
        
    def check_internet_connection(self):
        """ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต"""
        try:
            socket.create_connection(("github.com", 80), timeout=5)
            return True
        except OSError:
            return False
    
    def download_update(self):
        """ดาวน์โหลดและติดตั้งอัปเดต"""
        if not self.check_internet_connection():
            self._show_error_message("ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้\nกรุณาตรวจสอบการเชื่อมต่อแล้วลองใหม่")
            return False
            
        # สร้าง progress dialog
        progress_dialog = QProgressDialog("กำลังดาวน์โหลดอัปเดต...", "ยกเลิก", 0, 100, self.parent)
        progress_dialog.setWindowTitle("อัปเดต ExchangeUnsen")
        progress_dialog.setModal(True)
        progress_dialog.show()
        
        try:
            # กำหนดเส้นทางไฟล์
            exe_path = "dist/ExchangeUnsen.exe"  # ดาวน์โหลดไปใน dist/
            backup_path = "dist/ExchangeUnsen_backup.exe"
            temp_path = "dist/ExchangeUnsen_new.exe"
            
            # สร้างโฟลเดอร์ dist หากไม่มี
            os.makedirs("dist", exist_ok=True)
            
            if os.path.exists(exe_path):
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.copy2(exe_path, backup_path)
                progress_dialog.setLabelText("สำรองไฟล์เก่าแล้ว\nกำลังดาวน์โหลดไฟล์ใหม่...")
            
            # เริ่มดาวน์โหลด
            self.download_thread = DownloadThread(self.download_url, temp_path)
            
            def update_progress(value):
                progress_dialog.setValue(value)
                if progress_dialog.wasCanceled():
                    self.download_thread.terminate()
                    
            def download_finished(success, message):
                progress_dialog.close()
                
                if not success:
                    self._show_error_message(f"ดาวน์โหลดล้มเหลว: {message}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return
                
                # ติดตั้งไฟล์ใหม่
                try:
                    if os.path.exists(exe_path):
                        os.remove(exe_path)
                    shutil.move(temp_path, exe_path)
                    
                    # แสดงข้อความสำเร็จ
                    reply = QMessageBox.question(
                        self.parent,
                        "อัปเดตสำเร็จ",
                        "อัปเดตเสร็จสิ้น!\n\nไฟล์ใหม่ถูกดาวน์โหลดไปที่ dist/ExchangeUnsen.exe\n\n(หมายเหตุ: คุณสามารถลบไฟล์สำรอง dist/ExchangeUnsen_backup.exe ได้หากต้องการ)",
                        QMessageBox.Ok,
                        QMessageBox.Ok
                    )
                        
                except Exception as e:
                    # กู้คืนไฟล์เก่าหากติดตั้งล้มเหลว
                    if os.path.exists(backup_path):
                        if os.path.exists(exe_path):
                            os.remove(exe_path)
                        shutil.move(backup_path, exe_path)
                        self._show_error_message(f"ติดตั้งล้มเหลว: {str(e)}\nกู้คืนไฟล์เก่าสำเร็จ")
                    else:
                        self._show_error_message(f"ติดตั้งล้มเหลว: {str(e)}")
            
            self.download_thread.progress.connect(update_progress)
            self.download_thread.finished.connect(download_finished)
            self.download_thread.start()
            
            return True
            
        except Exception as e:
            progress_dialog.close()
            self._show_error_message(f"เกิดข้อผิดพลาด: {str(e)}")
            return False
    
    def fallback_to_bat_update(self):
        """ใช้ bat file เป็น fallback หากระบบ Python ล้มเหลว"""
        if os.path.exists(self.update_script):
            try:
                subprocess.run([self.update_script], check=True)
                return True
            except subprocess.CalledProcessError:
                return False
        return False

    def check_for_updates(self, silent=False):
        """
        ตรวจสอบการอัปเดต
        
        Args:
            silent (bool): ถ้า True จะไม่แสดง popup เมื่อไม่มีอัปเดต
        """
        # ป้องกันการเรียกตรวจสอบซ้ำ
        if self.__class__._update_check_in_progress:
            print("⚠️ Auto-update check already in progress, skipping...")
            return False
        
        self.__class__._update_check_in_progress = True
        
        try:
            # ดาวน์โหลดข้อมูลเวอร์ชันจาก Google Apps Script
            response = requests.get(self.version_url, timeout=10)
            response.raise_for_status()
            
            # response เป็น array, หาเวอร์ชันล่าสุด
            version_data_list = response.json()
            if not version_data_list or not isinstance(version_data_list, list):
                if not silent:
                    self._show_error_message("ข้อมูลเวอร์ชันไม่ถูกต้อง")
                return False
            
            # หาเวอร์ชันล่าสุดจาก version_code ที่สูงสุด
            latest_version_data = max(version_data_list, key=lambda x: x.get('version_code', 0))
            latest_version = latest_version_data.get('version_name', '1.0.0')
            
            # เปรียบเทียบเวอร์ชัน
            if self._is_newer_version(latest_version, self.current_version):
                return self._show_update_dialog(latest_version_data)
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
        finally:
            self.__class__._update_check_in_progress = False
    
    def _is_newer_version(self, latest, current):
        """เปรียบเทียบเวอร์ชัน"""
        try:
            return version.parse(latest) > version.parse(current)
        except:
            return latest != current
    
    def _show_update_dialog(self, version_data):
        """แสดง dialog สำหรับถามการอัปเดต"""
        latest_version = version_data.get('version_name', 'unknown')
        release_date = version_data.get('release', 'unknown')
        version_code = version_data.get('version_code', 0)
        
        message = f"""🚀 พบเวอร์ชันใหม่!

เวอร์ชันปัจจุบัน: {self.current_version}
เวอร์ชันใหม่: {latest_version}
วันที่ปล่อย: {release_date}
รหัสเวอร์ชัน: {version_code}

ต้องการดาวน์โหลดเวอร์ชันใหม่หรือไม่?

หมายเหตุ: ไฟล์จะถูกดาวน์โหลดไปใน folder dist/"""
        
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
            # ตรวจสอบว่ามี downloader.exe หรือไม่
            downloader_path = "dist/downloader.exe"
            if not os.path.exists(downloader_path):
                # หาใน folder ปัจจุบัน
                downloader_path = "downloader.exe"
                if not os.path.exists(downloader_path):
                    self._show_error_message("ไม่พบโปรแกรมดาวน์โหลด (downloader.exe)\nกรุณาติดต่อผู้พัฒนา")
                    return False
            
            # เตรียม arguments สำหรับ downloader
            target_exe = "ExchangeUnsen.exe"
            
            # แสดงข้อความ
            reply = QMessageBox.question(
                self.parent,
                "เริ่มการอัปเดต",
                f"จะเริ่มดาวน์โหลดเวอร์ชันใหม่\n\nโปรแกรมหลักจะปิดลงชั่วคราว\nโปรแกรมดาวน์โหลดจะจัดการส่วนที่เหลือ\n\nต้องการดำเนินการต่อหรือไม่?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return False
            
            # รัน downloader.exe
            try:
                subprocess.Popen([
                    downloader_path,
                    self.download_url,
                    target_exe
                ])
                
                # ปิดโปรแกรมหลัก
                QTimer.singleShot(1000, self._close_main_application)
                
                return True
                
            except Exception as e:
                self._show_error_message(f"ไม่สามารถเรียกโปรแกรมดาวน์โหลดได้: {str(e)}")
                return False
                
        except Exception as e:
            self._show_error_message(f"เกิดข้อผิดพลาดในการอัปเดต: {str(e)}")
            return False
    
    def _close_main_application(self):
        """ปิดโปรแกรมหลัก"""
        try:
            if self.parent:
                self.parent.close()
            else:
                QApplication.quit()
        except:
            sys.exit(0)
    
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
        """แสดงข้อความข้อผิดพลาด"""
        QMessageBox.critical(
            self.parent,
            "ข้อผิดพลาด",
            message
        )

class UpdateCheckThread(QThread):
    """Thread สำหรับตรวจสอบอัปเดตแบบ async"""
    update_available = pyqtSignal(dict)
    
    def __init__(self, version_url, current_version):
        super().__init__()
        self.version_url = version_url
        self.current_version = current_version
        
    def run(self):
        """ตรวจสอบอัปเดตในพื้นหลัง"""
        try:
            response = requests.get(self.version_url, timeout=10)
            response.raise_for_status()
            
            version_data_list = response.json()
            if version_data_list and isinstance(version_data_list, list):
                # หาเวอร์ชันล่าสุด
                latest_version_data = max(version_data_list, key=lambda x: x.get('version_code', 0))
                latest_version = latest_version_data.get('version_name', '1.0.0')
                
                # เปรียบเทียบเวอร์ชัน
                try:
                    if version.parse(latest_version) > version.parse(self.current_version):
                        self.update_available.emit(latest_version_data)
                except:
                    if latest_version != self.current_version:
                        self.update_available.emit(latest_version_data)
                        
        except:
            pass  # เงียบๆ ไม่แสดง error หากตรวจสอบไม่ได้

def check_update_on_startup(parent=None, silent=True):
    """
    ฟังก์ชันสำหรับเรียกตรวจสอบอัปเดตเมื่อเปิดโปรแกรม
    
    Args:
        parent: Parent widget สำหรับ dialog
        silent: ถ้า True จะไม่แสดงข้อความเมื่อไม่มีอัปเดต
    """
    updater = AutoUpdater(parent)
    return updater.check_for_updates(silent=silent)
