"""
MySQL Configuration Manager
จัดการการตั้งค่าการเชื่อมต่อ MySQL และบันทึกลง Registry
"""

import winreg
import json
import mysql.connector
from typing import Dict, Optional, Tuple
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QSpinBox, QPushButton, QLabel, 
                             QMessageBox, QCheckBox, QGroupBox, QTextEdit)
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QFont, QIcon


class MySQLConfigManager:
    """จัดการการตั้งค่า MySQL ใน Registry"""
    
    REGISTRY_KEY = r"SOFTWARE\ExcelReaderApp"
    
    @staticmethod
    def save_config(config: Dict[str, str]) -> bool:
        """บันทึกการตั้งค่าลง Registry"""
        try:
            # เปิดหรือสร้าง registry key
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, 
                                  MySQLConfigManager.REGISTRY_KEY) as key:
                
                # บันทึกการตั้งค่าแต่ละตัว
                for name, value in config.items():
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
                
                return True
                
        except Exception as e:
            print(f"Error saving config to registry: {e}")
            return False
    
    @staticmethod
    def load_config() -> Dict[str, str]:
        """โหลดการตั้งค่าจาก Registry"""
        config = {
            'host': 'localhost',
            'port': '3306',
            'database': 'hos',
            'username': '',
            'password': '',
            'auto_connect': 'false'
        }
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                              MySQLConfigManager.REGISTRY_KEY) as key:
                
                # อ่านการตั้งค่าแต่ละตัว
                for name in config.keys():
                    try:
                        value, _ = winreg.QueryValueEx(key, name)
                        config[name] = value
                    except FileNotFoundError:
                        # ใช้ค่าเริ่มต้นถ้าไม่พบ
                        pass
                        
        except FileNotFoundError:
            # ไม่มี registry key ใช้ค่าเริ่มต้น
            pass
        except Exception as e:
            print(f"Error loading config from registry: {e}")
        
        return config
    
    @staticmethod
    def test_connection(config: Dict[str, str]) -> Tuple[bool, str]:
        """ทดสอบการเชื่อมต่อ MySQL"""
        try:
            connection = mysql.connector.connect(
                host=config['host'],
                port=int(config['port']),
                database=config['database'],
                user=config['username'],
                password=config['password'],
                connection_timeout=5
            )
            
            if connection.is_connected():
                # ทดสอบ query
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()
                connection.close()
                
                return True, f"เชื่อมต่อสำเร็จ\nMySQL Version: {version}"
            else:
                return False, "ไม่สามารถเชื่อมต่อได้"
                
        except mysql.connector.Error as e:
            return False, f"MySQL Error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"


class MySQLConfigDialog(QDialog):
    """Dialog สำหรับตั้งค่า MySQL"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ตั้งค่าการเชื่อมต่อ MySQL")
        self.setModal(True)
        self.setFixedSize(450, 500)
        
        # โหลดการตั้งค่าปัจจุบัน
        self.config = MySQLConfigManager.load_config()
        
        self.setup_ui()
        self.load_current_config()
        
    def setup_ui(self):
        """สร้าง UI"""
        layout = QVBoxLayout(self)
        
        # หัวข้อ
        title_label = QLabel("การตั้งค่าการเชื่อมต่อ MySQL")
        title_label.setFont(QFont("Tahoma", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # กลุ่มการตั้งค่าการเชื่อมต่อ
        connection_group = QGroupBox("ข้อมูลการเชื่อมต่อ")
        connection_layout = QFormLayout(connection_group)
        
        # Host
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("localhost หรือ IP Address")
        connection_layout.addRow("Host:", self.host_edit)        # Port
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(3306)
        # บังคับให้ใช้ locale แบบอังกฤษสำหรับตัวเลข
        english_locale = QLocale(QLocale.English, QLocale.UnitedStates)
        self.port_spin.setLocale(english_locale)
        connection_layout.addRow("Port:", self.port_spin)
        
        # Database
        self.database_edit = QLineEdit()
        self.database_edit.setPlaceholderText("ชื่อฐานข้อมูล")
        connection_layout.addRow("Database:", self.database_edit)
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("ชื่อผู้ใช้")
        connection_layout.addRow("Username:", self.username_edit)
          # Password
        self.password_edit = QLineEdit()
        # ไม่ใช้ EchoMode.Password เพื่อให้แสดงข้อความปกติ
        self.password_edit.setEchoMode(QLineEdit.Normal)
        self.password_edit.setPlaceholderText("รหัสผ่าน")
        connection_layout.addRow("Password:", self.password_edit)
        
        # Auto connect
        self.auto_connect_check = QCheckBox("เชื่อมต่ออัตโนมัติเมื่อเปิดโปรแกรม")
        connection_layout.addRow("", self.auto_connect_check)
        
        layout.addWidget(connection_group)
        
        # ปุ่มทดสอบการเชื่อมต่อ
        test_button = QPushButton("ทดสอบการเชื่อมต่อ")
        test_button.clicked.connect(self.test_connection)
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(test_button)
        
        # พื้นที่แสดงผลการทดสอบ
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(80)
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("ผลการทดสอบจะแสดงที่นี่...")
        layout.addWidget(self.result_text)
        
        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("บันทึก")
        save_button.clicked.connect(self.save_config)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        cancel_button = QPushButton("ยกเลิก")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def load_current_config(self):
        """โหลดการตั้งค่าปัจจุบันลง UI"""
        self.host_edit.setText(self.config.get('host', 'localhost'))
        self.port_spin.setValue(int(self.config.get('port', '3306')))
        self.database_edit.setText(self.config.get('database', 'hos'))
        self.username_edit.setText(self.config.get('username', ''))
        self.password_edit.setText(self.config.get('password', ''))
        self.auto_connect_check.setChecked(self.config.get('auto_connect', 'false') == 'true')
        
    def get_current_config(self) -> Dict[str, str]:
        """ดึงการตั้งค่าปัจจุบันจาก UI"""
        return {
            'host': self.host_edit.text().strip(),
            'port': str(self.port_spin.value()),
            'database': self.database_edit.text().strip(),
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'auto_connect': 'true' if self.auto_connect_check.isChecked() else 'false'
        }
        
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ"""
        config = self.get_current_config()
        
        # ตรวจสอบข้อมูลที่จำเป็น
        if not all([config['host'], config['database'], config['username']]):
            self.result_text.setPlainText("กรุณากรอกข้อมูลให้ครบถ้วน (Host, Database, Username)")
            return
        
        self.result_text.setPlainText("กำลังทดสอบการเชื่อมต่อ...")
        
        # ทดสอบการเชื่อมต่อ
        success, message = MySQLConfigManager.test_connection(config)
        
        if success:
            self.result_text.setPlainText(f"✅ {message}")
            self.result_text.setStyleSheet("color: green;")
        else:
            self.result_text.setPlainText(f"❌ {message}")
            self.result_text.setStyleSheet("color: red;")
    
    def _show_silent_message(self, parent, icon, title, text, buttons=None, default_button=None):
        """แสดง message box แบบไม่มีเสียง"""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        
        if buttons:
            msg.setStandardButtons(buttons)
        else:
            msg.setStandardButtons(QMessageBox.Ok)
            
        if default_button:
            msg.setDefaultButton(default_button)
            
        # ปิดเสียง
        msg.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        
        return msg.exec_()
    
    def _info_silent(self, title, text):
        """แสดง information message แบบไม่มีเสียง"""
        self._show_silent_message(self, QMessageBox.Information, title, text)
    
    def _warning_silent(self, title, text):
        """แสดง warning message แบบไม่มีเสียง"""
        self._show_silent_message(self, QMessageBox.Warning, title, text)
    
    def _critical_silent(self, title, text):
        """แสดง critical message แบบไม่มีเสียง"""
        self._show_silent_message(self, QMessageBox.Critical, title, text)
            
    def save_config(self):
        """บันทึกการตั้งค่า"""
        config = self.get_current_config()
          # ตรวจสอบข้อมูลที่จำเป็น
        if not all([config['host'], config['database'], config['username']]):
            self._warning_silent("คำเตือน", 
                              "กรุณากรอกข้อมูลให้ครบถ้วน (Host, Database, Username)")
            return
        
        # บันทึกลง registry
        if MySQLConfigManager.save_config(config):
            self._info_silent("สำเร็จ", 
                                  "บันทึกการตั้งค่าเรียบร้อยแล้ว")
            self.accept()
        else:
            self._critical_silent("ข้อผิดพลาด", 
                               "ไม่สามารถบันทึกการตั้งค่าได้")


class MySQLConnection:
    """จัดการการเชื่อมต่อ MySQL"""
    
    def __init__(self):
        self.connection = None
        self.config = MySQLConfigManager.load_config()
        
    def connect(self) -> Tuple[bool, str]:
        """เชื่อมต่อฐานข้อมูล"""
        try:
            if self.connection and self.connection.is_connected():
                return True, "เชื่อมต่ออยู่แล้ว"
            
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                port=int(self.config['port']),
                database=self.config['database'],
                user=self.config['username'],
                password=self.config['password'],
                connection_timeout=10
            )
            
            return True, "เชื่อมต่อสำเร็จ"
            
        except mysql.connector.Error as e:
            return False, f"MySQL Error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def disconnect(self):
        """ตัดการเชื่อมต่อ"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            
    def is_connected(self) -> bool:
        """ตรวจสอบสถานะการเชื่อมต่อ"""
        return self.connection and self.connection.is_connected()
        
    def execute_query(self, query: str) -> Tuple[bool, any]:
        """ดำเนินการ query"""
        try:
            if not self.is_connected():
                success, message = self.connect()
                if not success:
                    return False, message
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                cursor.close()
                return True, (result, columns)
            else:
                self.connection.commit()
                cursor.close()
                return True, "Query executed successfully"
                
        except mysql.connector.Error as e:
            return False, f"MySQL Error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
