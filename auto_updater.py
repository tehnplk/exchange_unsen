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
import time
import psutil
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
                            progress_value = int((downloaded / total_size) * 100)
                            self.progress.emit(progress_value)
                            
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
        self.progress_dialog = None
        self.download_thread = None
        
    def check_internet_connection(self):
        """ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต"""
        try:
            socket.create_connection(("github.com", 80), timeout=5)
            return True
        except OSError:
            return False
    
    def download_update(self):
        """ดาวน์โหลดและติดตั้งอัปเดต (เวอร์ชันเก่า - ไม่ใช้แล้ว)"""
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
            
            # เก็บข้อมูลเวอร์ชันใหม่ไว้ใน parent
            if self.parent:
                self.parent.update_available_data = latest_version_data
            
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
    
    def check_for_updates_background(self, callback=None):
        """
        ตรวจสอบการอัปเดตแบบเบื้องหลัง (ไม่แสดง popup)
        
        Args:
            callback (function): ฟังก์ชันที่จะเรียกเมื่อพบเวอร์ชันใหม่
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
                return False
            
            # หาเวอร์ชันล่าสุดจาก version_code ที่สูงสุด
            latest_version_data = max(version_data_list, key=lambda x: x.get('version_code', 0))
            latest_version = latest_version_data.get('version_name', '1.0.0')
            
            # เก็บข้อมูลเวอร์ชันใหม่ไว้ใน parent
            if self.parent:
                self.parent.update_available_data = latest_version_data
            
            # เปรียบเทียบเวอร์ชัน
            if self._is_newer_version(latest_version, self.current_version):
                # พบเวอร์ชันใหม่ - เรียก callback
                if callback:
                    callback(latest_version_data)
                elif self.parent and hasattr(self.parent, 'on_update_available'):
                    self.parent.on_update_available(latest_version_data)
                return True
            else:
                # ไม่มีเวอร์ชันใหม่ - ไม่ต้องแจ้งเตือน
                return False
                
        except requests.exceptions.RequestException:
            # ข้อผิดพลาดการเชื่อมต่อ - ไม่แจ้งเตือน
            return False
        except Exception as e:
            # ข้อผิดพลาดอื่นๆ - ไม่แจ้งเตือน
            print(f"Background update check error: {e}")
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

หมายเหตุ: ไฟล์จะถูกดาวน์โหลดด้วยชื่อใหม่ (ไม่เขียนทับไฟล์เดิม)"""
        
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
            # ดึงข้อมูลเวอร์ชันใหม่
            if hasattr(self.parent, 'update_available_data') and self.parent.update_available_data:
                latest_version_code = self.parent.update_available_data.get('version_code', 999)
                latest_version_name = self.parent.update_available_data.get('version_name', 'unknown')
            else:
                self._show_error_message("ไม่พบข้อมูลเวอร์ชันใหม่\nกรุณาตรวจสอบการอัปเดตใหม่อีกครั้ง")
                return False
                
            target_exe = f"ExchangeUnsen{latest_version_code}.exe"
            
            # แสดงข้อความยืนยัน
            reply = QMessageBox.question(
                self.parent,
                "เริ่มการอัปเดต",
                f"จะเริ่มดาวน์โหลดเวอร์ชันใหม่ {latest_version_name}\n\nไฟล์ใหม่จะถูกบันทึกเป็น: {target_exe}\nไฟล์เดิมจะไม่ถูกลบ\n\nต้องการดำเนินการต่อหรือไม่?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply != QMessageBox.Yes:
                return False
            
            # เริ่มดาวน์โหลดด้วย progress dialog
            return self._download_with_progress(self.download_url, target_exe, latest_version_name)
                
        except Exception as e:
            self._show_error_message(f"เกิดข้อผิดพลาดในการอัปเดต: {str(e)}")
            return False
    
    def _download_with_progress(self, download_url, target_exe_name, version_name):
        """
        ดาวน์โหลดไฟล์อัปเดตพร้อมแสดง QProgressDialog (Flow ใหม่)
        """
        if not self.check_internet_connection():
            self._show_error_message("ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้\nกรุณาตรวจสอบการเชื่อมต่อแล้วลองใหม่")
            return False

        # Determine output directory (same as current executable or a 'downloads' subfolder)
        try:
            if getattr(sys, 'frozen', False):  # PyInstaller
                output_dir = Path(sys.executable).parent
            else:  # Running as script
                output_dir = Path(__file__).parent
        except Exception:
            output_dir = Path(".")  # Fallback to current working directory

        # Ensure output_dir exists (it should, but good practice)
        output_dir.mkdir(parents=True, exist_ok=True)
        downloaded_file_path = output_dir / target_exe_name

        self.progress_dialog = QProgressDialog(f"กำลังดาวน์โหลด {version_name}...", "ยกเลิก", 0, 100, self.parent)
        self.progress_dialog.setWindowTitle(f"ดาวน์โหลด ExchangeUnsen {version_name}")
        self.progress_dialog.setModal(True)
        self.progress_dialog.setAutoClose(False)  # We will close it manually
        self.progress_dialog.setAutoReset(False)  # We will reset it manually
        self.progress_dialog.show()

        self.download_thread = DownloadThread(download_url, str(downloaded_file_path))

        def update_progress(value):
            if self.progress_dialog:
                self.progress_dialog.setValue(value)
                if self.progress_dialog.wasCanceled():
                    if hasattr(self, 'download_thread') and self.download_thread.isRunning():
                        self.download_thread.terminate()
                        self.progress_dialog.setLabelText("การดาวน์โหลดถูกยกเลิก...")
                        if downloaded_file_path.exists():
                            try:
                                os.remove(downloaded_file_path)
                                print(f"ลบไฟล์ที่ดาวน์โหลดไม่สมบูรณ์: {downloaded_file_path}")
                            except Exception as e:
                                print(f"ไม่สามารถลบไฟล์ที่ดาวน์โหลดไม่สมบูรณ์: {e}")
                        
        def download_finished(success, message):
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
                
            if not success:
                self._show_error_message(f"ดาวน์โหลดล้มเหลว: {message}")
                if downloaded_file_path.exists():
                    try:
                        os.remove(downloaded_file_path)
                    except Exception:
                        pass
                return
            
            # แสดงข้อความสำเร็จและตำแหน่งไฟล์
            self._show_download_success(target_exe_name, str(downloaded_file_path), version_name)
        
        self.download_thread.progress.connect(update_progress)
        self.download_thread.finished.connect(download_finished)
        self.download_thread.start()
        
        return True
    
    def _show_download_success(self, filename, filepath, version_name):
        """แสดงข้อความเมื่อดาวน์โหลดสำเร็จ"""
        message = f"""✅ ดาวน์โหลดสำเร็จ!

เวอร์ชัน: {version_name}
ชื่อไฟล์: {filename}
ตำแหน่งไฟล์: {filepath}

ไฟล์ใหม่พร้อมใช้งานแล้ว
คุณสามารถปิดโปรแกรมเก่าและเปิดไฟล์ใหม่ได้เลย

ต้องการปิดโปรแกรมตอนนี้หรือไม่?"""
        
        reply = QMessageBox.question(
            self.parent,
            "ดาวน์โหลดสำเร็จ",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self._close_main_application()
    
    def _close_main_application(self):
        """ปิดโปรแกรมหลักอย่างสมบูรณ์"""
        try:
            current_pid = os.getpid()
            print(f"🔄 Attempting to close application (PID: {current_pid})")
            
            # ลองใช้ parent method ก่อน (graceful shutdown)
            if self.parent and hasattr(self.parent, 'close_for_update'):
                print("Calling parent.close_for_update()")
                self.parent.close_for_update()  # Parent should handle its own cleanup and QApplication.quit()
                # Give parent a moment to close gracefully
                QTimer.singleShot(500, lambda: self._force_exit_if_not_closed(current_pid))
                return  # Parent will handle exit
            elif self.parent and hasattr(self.parent, 'close'):
                print("Calling parent.close()")
                self.parent.close()
                QTimer.singleShot(500, lambda: self._force_exit_if_not_closed(current_pid))
                return

            # If no parent method, try direct psutil termination
            self._force_exit_if_not_closed(current_pid)

        except Exception as e_outer:
            print(f"🛑 Outer error in _close_main_application: {e_outer}")
            print("🛑 Forcing exit due to error in closing sequence.")
            sys.exit(1)  # Force exit with error code

    def _force_exit_if_not_closed(self, pid_to_check):
        """Helper to force exit if process is still running."""
        try:
            if psutil.pid_exists(pid_to_check):
                current_process = psutil.Process(pid_to_check)
                print(f"⏳ Process {pid_to_check} still running. Attempting terminate/kill.")
                current_process.terminate()
                try:
                    current_process.wait(timeout=0.5)  # Wait for termination
                except psutil.TimeoutExpired:
                    print(f"⚠️ Process {pid_to_check} did not terminate gracefully. Forcing kill...")
                    current_process.kill()
                    try:
                        current_process.wait(timeout=0.2)  # Wait for kill
                    except psutil.TimeoutExpired:
                        print(f"🛑 Process {pid_to_check} could not be killed.")
                    else:
                        print(f"✅ Process {pid_to_check} killed.")
                else:
                    print(f"✅ Process {pid_to_check} terminated.")
            else:
                print(f"✅ Process {pid_to_check} already closed.")
        except psutil.NoSuchProcess:
            print(f"✅ Process {pid_to_check} not found (already closed).")
        except Exception as e:
            print(f"🛑 Error during force exit for PID {pid_to_check}: {e}")
        finally:
            print("Exiting application now.")
            if QApplication.instance():  # Ensure Qt app quits
                QApplication.instance().quit()
            sys.exit(0)  # Ensure Python interpreter exits
    
    def _show_no_update_message(self):
        """แสดงข้อความเมื่อไม่มีอัปเดต"""
        QMessageBox.information(
            self.parent,
            "ไม่มีอัปเดต",
            f"คุณกำลังใช้เวอร์ชันล่าสุดอยู่แล้ว ({self.current_version})"
        )
    
    def _show_connection_error(self):
        """แสดงข้อความเมื่อเชื่อมต่อไม่ได้"""
        QMessageBox.warning(
            self.parent,
            "เชื่อมต่อไม่ได้",
            "ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์เพื่อตรวจสอบอัปเดตได้\nกรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ต"
        )
    
    def _show_error_message(self, message):
        """แสดงข้อความ error"""
        QMessageBox.critical(
            self.parent,
            "เกิดข้อผิดพลาด", 
            message
        )
