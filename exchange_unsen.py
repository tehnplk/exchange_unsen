import sys
import os
import time

import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QTableView,
    QHeaderView, QComboBox, QHBoxLayout, QWidget, QLabel, QDialog,
    QVBoxLayout, QLineEdit, QPushButton, QDialogButtonBox
)
from PyQt5.QtCore import (
    QAbstractTableModel, Qt, QVariant, QTimer, QThread, pyqtSignal
)
from PyQt5.QtGui import QFont

from ui_components import ExchangeUnsenUI

# Import configuration
try:
    from config import (APP_CONFIG, FILE_CONFIG, UI_CONFIG, 
                       COLOR_CONFIG, MESSAGES, PANDAS_CONFIG)
    from mysql_config import MySQLConfigDialog, MySQLConnection
except ImportError:
    # Default configuration if config.py is not available
    APP_CONFIG = {'name': 'Excel Reader', 'window_size': (1000, 700)}
    FILE_CONFIG = {'excel_filter': "Excel Files (*.xlsx *.xls);;All Files (*)"}
    UI_CONFIG = {'font_family': 'Tahoma', 'font_size': 9}
    MESSAGES = {'ready': 'พร้อมใช้งาน'}
    MySQLConfigDialog = None
    MySQLConnection = None


class FilterDialog(QDialog):
    """Dialog สำหรับตั้งค่า filter ของคอลัมน์"""
    
    def __init__(self, column_name, current_filter="", parent=None):
        super().__init__(parent)
        self.column_name = column_name
        self.filter_text = current_filter
        self.setupUI()
        
    def setupUI(self):
        """ตั้งค่า UI ของ dialog"""
        self.setWindowTitle(f"กรองข้อมูลคอลัมน์: {self.column_name}")
        self.setModal(True)
        self.resize(400, 150)
        
        layout = QVBoxLayout()
        
        # Label สำหรับคำอธิบาย
        info_label = QLabel(
            f"ใส่คำที่ต้องการค้นหาในคอลัมน์ '{self.column_name}':"
        )
        layout.addWidget(info_label)
        
        # Line edit สำหรับใส่เงื่อนไขการกรอง
        self.filter_input = QLineEdit()
        self.filter_input.setText(self.filter_text)
        self.filter_input.setPlaceholderText(
            "เช่น: ABC, 123, หรือเว้นว่างเพื่อแสดงทั้งหมด"
        )
        layout.addWidget(self.filter_input)
        
        # Label สำหรับคำอธิบายการใช้งาน
        help_label = QLabel(
            "หมายเหตุ: การค้นหาจะใช้รูปแบบ 'LIKE' (ค้นหาข้อความที่มีคำนี้อยู่)"
        )
        help_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(help_label)
        
        # ปุ่ม OK และ Cancel
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Focus ที่ input field
        self.filter_input.setFocus()
        self.filter_input.selectAll()
        
    def getFilterText(self):
        """ส่งคืนข้อความที่ใส่ใน filter"""
        return self.filter_input.text().strip()


class FilterableHeaderView(QHeaderView):
    """Custom Header View ที่มีปุ่ม filter"""
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.filter_buttons = {}  # เก็บปุ่ม filter สำหรับแต่ละคอลัมน์
        self.table_view = parent  # เก็บ reference ไปยัง table view
        
    def setModel(self, model):
        """ตั้งค่า model และสร้าง filter buttons"""
        super().setModel(model)
        if model:
            self.createFilterButtons()
    
    def createFilterButtons(self):
        """สร้างปุ่ม filter สำหรับแต่ละคอลัมน์"""
        if not self.model():
            return
            
        # ล้างปุ่มเก่า
        for button in self.filter_buttons.values():
            button.setParent(None)
            button.deleteLater()
        self.filter_buttons.clear()
        
        # สร้างปุ่มใหม่สำหรับแต่ละคอลัมน์
        for i in range(self.model().columnCount()):
            button = QPushButton("...", self.parent())
            button.setFixedSize(20, 20)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)
            
            # เชื่อมต่อ signal
            button.clicked.connect(
                lambda checked, col=i: self.openFilterDialog(col)
            )
            
            self.filter_buttons[i] = button
        
        # จัดตำแหน่งปุ่ม
        self.positionFilterButtons()
    
    def positionFilterButtons(self):
        """จัดตำแหน่งปุ่ม filter"""
        if not self.filter_buttons:
            return
            
        for i, button in self.filter_buttons.items():
            # คำนวณตำแหน่งของปุ่ม
            section_pos = self.sectionPosition(i)
            section_size = self.sectionSize(i)            # ตั้งตำแหน่งปุ่มให้อยู่ด้านขวาของหัวคอลัมน์
            button_x = section_pos + section_size - 25
            button_y = 5
            
            button.setGeometry(button_x, button_y, 20, 20)
            button.show()
    
    def openFilterDialog(self, column_index):
        """เปิด dialog สำหรับตั้งค่า filter"""
        if not self.model() or not self.table_view:
            return
            
        # ดึงชื่อคอลัมน์
        column_name = self.model().headerData(
            column_index, Qt.Horizontal, Qt.DisplayRole
        )
        
        # ดึง filter ปัจจุบัน
        current_filter = ""
        if hasattr(self.model(), 'getColumnFilter'):
            current_filter = self.model().getColumnFilter(column_index)
        
        # เปิด dialog
        dialog = FilterDialog(column_name, current_filter, self.parent())
        if dialog.exec_() == QDialog.Accepted:
            filter_text = dialog.getFilterText()
            
            # ใช้ filter กับ model
            if hasattr(self.model(), 'applyColumnFilter'):
                self.model().applyColumnFilter(column_index, filter_text)
                
                # อัปเดตสถานะปุ่ม
                self.updateButtonState(column_index, filter_text)
                
                # แจ้งเจ้าของเกี่ยวกับการเปลี่ยน filter
                if hasattr(self.table_view, 'on_filter_applied'):
                    self.table_view.on_filter_applied()
    
    def updateButtonState(self, column_index, filter_text):
        """อัปเดตสถานะของปุ่ม filter"""
        if column_index in self.filter_buttons:
            button = self.filter_buttons[column_index]
            if filter_text:
                # มี filter อยู่ - เปลี่ยนสีปุ่ม
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 1px solid #45a049;
                        border-radius: 3px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                button.setToolTip(f"กรอง: {filter_text}")
            else:
                # ไม่มี filter - กลับเป็นสีปกติ
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #ccc;
                        border-radius: 3px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                """)
                button.setToolTip("คลิกเพื่อกรองข้อมูล")
    
    def resizeEvent(self, event):
        """จัดตำแหน่งปุ่มใหม่เมื่อ resize"""
        super().resizeEvent(event)
        self.positionFilterButtons()
    
    def paintEvent(self, event):
        """วาด header และจัดตำแหน่งปุ่ม"""
        super().paintEvent(event)
        self.positionFilterButtons()
    
    def showEvent(self, event):
        """แสดงปุ่มเมื่อ header แสดง"""
        super().showEvent(event)
        # รอสักครู่แล้วจัดตำแหน่งปุ่ม
        QTimer.singleShot(100, self.positionFilterButtons)
    
    def getActiveFilters(self):
        """ส่งคืน filter ที่ active อยู่ทั้งหมด"""
        if hasattr(self.model(), 'getActiveFilters'):
            return self.model().getActiveFilters()
        return {}
    
    def clearAllFilters(self):
        """ล้าง filter ทั้งหมด"""
        if hasattr(self.model(), 'clearAllFilters'):
            self.model().clearAllFilters()
            
            # อัปเดตสถานะปุ่มทั้งหมด
            for i, button in self.filter_buttons.items():
                self.updateButtonState(i, "")


class ExcelLoaderThread(QThread):
    """Thread สำหรับโหลดไฟล์ Excel"""
    finished = pyqtSignal(object)  # ส่งข้อมูล DataFrame เมื่อเสร็จ
    error = pyqtSignal(str)  # ส่งข้อความ error
    progress = pyqtSignal(str)  # ส่งข้อความสถานะ
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        """ฟังก์ชันหลักที่รันใน thread"""
        try:
            self.progress.emit("กำลังอ่านไฟล์ Excel...")
            
            # อ่านไฟล์ Excel
            if self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
                data = pd.read_excel(self.file_path)
            else:
                raise ValueError("รูปแบบไฟล์ไม่ถูกต้อง กรุณาเลือกไฟล์ Excel (.xlsx หรือ .xls)")
            
            if data.empty:
                raise ValueError("ไฟล์ Excel ไม่มีข้อมูล")
            
            self.progress.emit("อ่านไฟล์สำเร็จ")
            self.finished.emit(data)
            
        except Exception as e:
            self.error.emit(f"ไม่สามารถอ่านไฟล์ Excel ได้: {str(e)}")


class MySQLSearchThread(QThread):
    """Thread สำหรับค้นหาข้อมูลใน MySQL"""
    finished = pyqtSignal(object, int, int)  # ส่งข้อมูล DataFrame, found_count, not_found_count
    error = pyqtSignal(str)  # ส่งข้อความ error
    progress = pyqtSignal(str, int, int)  # ส่งข้อความสถานะ, progress_value, max_value
    
    def __init__(self, data, selected_column, mysql_connection):
        super().__init__()
        self.data = data.copy()  # สำเนาข้อมูลเพื่อความปลอดภัย
        self.selected_column = selected_column
        self.mysql_connection = mysql_connection
    
    def run(self):
        """ฟังก์ชันหลักที่รันใน thread"""
        try:
            # เตรียมข้อมูล
            found_count = 0
            not_found_count = 0
            total_rows = len(self.data)
            
            # แมปคอลัมน์
            column_mapping = {
                'pid': 'person_id',
                'cid': 'cid', 
                'hn': 'patient_hn'
            }
            db_column = column_mapping[self.selected_column]
            
            # เพิ่มคอลัมน์ผลลัพธ์
            self.data['pid_found'] = ''
            self.data['cid_found'] = ''
            self.data['fname_found'] = ''
            self.data['lname_found'] = ''
            self.data['hn_found'] = ''
            
            self.progress.emit("เริ่มค้นหาข้อมูลใน MySQL...", 0, total_rows)
            
            # ค้นหาทีละแถว
            for idx, row in self.data.iterrows():
                if self.isInterruptionRequested():
                    break
                    
                search_value = row[self.selected_column]
                if pd.isna(search_value):
                    continue
                
                try:
                    # Query ข้อมูลจาก MySQL
                    query = f"SELECT person_id, cid, fname, lname, patient_hn FROM person WHERE {db_column} = %s LIMIT 1"
                    cursor = self.mysql_connection.connection.cursor()
                    cursor.execute(query, (str(search_value),))
                    result = cursor.fetchone()
                    cursor.close()
                    
                    if result:
                        # พบข้อมูล
                        self.data.at[idx, 'pid_found'] = result[0] if result[0] else ''
                        self.data.at[idx, 'cid_found'] = result[1] if result[1] else ''
                        self.data.at[idx, 'fname_found'] = result[2] if result[2] else ''
                        self.data.at[idx, 'lname_found'] = result[3] if result[3] else ''
                        self.data.at[idx, 'hn_found'] = result[4] if result[4] else ''
                        found_count += 1
                    else:
                        # ไม่พบข้อมูล
                        self.data.at[idx, 'pid_found'] = ''
                        self.data.at[idx, 'cid_found'] = ''
                        self.data.at[idx, 'fname_found'] = ''
                        self.data.at[idx, 'lname_found'] = ''
                        self.data.at[idx, 'hn_found'] = ''
                        not_found_count += 1
                        
                except Exception as query_error:
                    print(f"Error querying for {search_value}: {str(query_error)}")
                    # ใส่ค่าว่างเมื่อเกิด error
                    self.data.at[idx, 'pid_found'] = ''
                    self.data.at[idx, 'cid_found'] = ''
                    self.data.at[idx, 'fname_found'] = ''
                    self.data.at[idx, 'lname_found'] = ''
                    self.data.at[idx, 'hn_found'] = ''
                    not_found_count += 1
                
                # อัปเดต progress
                current_row = idx + 1
                self.progress.emit(f"ค้นหาแล้ว {current_row}/{total_rows} รายการ", current_row, total_rows)
            
            # จัดเรียงคอลัมน์ใหม่
            found_columns = ['pid_found', 'cid_found', 'fname_found', 'lname_found', 'hn_found']
            existing_columns = [col for col in self.data.columns if col not in found_columns]
            new_column_order = found_columns + existing_columns
            self.data = self.data[new_column_order]
            
            self.finished.emit(self.data, found_count, not_found_count)
            
        except Exception as e:
            self.error.emit(f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}")


class PandasModel(QAbstractTableModel):
    """Model สำหรับแสดงข้อมูล Pandas DataFrame ใน QTableView"""
    
    def __init__(self, data):
        super().__init__()
        self._original_data = data.copy()  # เก็บข้อมูลต้นฉบับ
        self._data = data  # ข้อมูลที่แสดงผล (หลังจากกรอง)
        self._filters = {}  # เก็บ filter ที่ active อยู่
    
    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]
    
    def applyFilters(self, filters):
        """ใช้ filter กับข้อมูลแบบ LIKE search"""
        self.layoutAboutToBeChanged.emit()
        
        # เริ่มจากข้อมูลต้นฉบับ
        filtered_data = self._original_data.copy()
        
        # ใช้ filter แต่ละตัว
        for column_index, filter_value in filters.items():
            if filter_value and column_index < len(filtered_data.columns):
                column_name = filtered_data.columns[column_index]
                # กรองข้อมูลโดยใช้ LIKE search (ค้นหาข้อความที่มีคำที่ระบุ)
                filtered_data = filtered_data[
                    filtered_data[column_name].astype(str).str.contains(
                        str(filter_value), case=False, na=False
                    )
                ]
        
        self._data = filtered_data.reset_index(drop=True)
        self._filters = filters
        
        self.layoutChanged.emit()
    
    def applyColumnFilter(self, column_index, filter_text):
        """ใช้ filter สำหรับคอลัมน์เดียว"""
        if filter_text.strip():
            # เพิ่ม/อัปเดต filter สำหรับคอลัมน์นี้
            self._filters[column_index] = filter_text.strip()
        else:
            # ลบ filter สำหรับคอลัมน์นี้
            self._filters.pop(column_index, None)
        
        # ใช้ filter ทั้งหมด
        self.applyFilters(self._filters)
    
    def getColumnFilter(self, column_index):
        """ส่งคืน filter ปัจจุบันของคอลัมน์"""
        return self._filters.get(column_index, "")
    
    def clearAllFilters(self):
        """ล้าง filter ทั้งหมด"""
        self._filters = {}
        self.applyFilters(self._filters)
    
    def getActiveFilters(self):
        """ส่งคืน filter ที่ active อยู่"""
        return self._filters.copy()
    
    def getUniqueValues(self, column_index):
        """ส่งคืนค่าที่ไม่ซ้ำในคอลัมน์"""
        if column_index < len(self._original_data.columns):
            column_name = self._original_data.columns[column_index]
            return self._original_data[column_name].dropna().unique()
        return []

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                value = self._data.iloc[index.row(), index.column()]
                return str(value)
            elif role == Qt.FontRole:
                # สร้าง font แบบ bold สำหรับข้อมูลในตาราง
                font = QFont()
                font.setBold(True)
                return font
        return QVariant()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(self._data.index[section])
        return QVariant()

    def sort(self, column, order=Qt.AscendingOrder):
        """เรียงลำดับข้อมูลตามคอลัมน์ที่ระบุ"""
        if 0 <= column < self.columnCount():
            self.layoutAboutToBeChanged.emit()
            
            try:
                # รับชื่อคอลัมน์
                column_name = self._data.columns[column]
                
                # แปลงข้อมูลทั้งคอลัมน์ให้เป็น string เพื่อหลีกเลี่ยงปัญหาการเปรียบเทียบ
                # ทำสำเนาของ DataFrame เพื่อไม่ให้กระทบข้อมูลต้นฉบับ
                temp_data = self._data.copy()
                temp_data[column_name] = temp_data[column_name].astype(str)
                
                # เรียงลำดับ DataFrame
                ascending = (order == Qt.AscendingOrder)
                sorted_data = temp_data.sort_values(by=column_name, ascending=ascending, na_position='last')
                
                # อัปเดต _data ด้วยข้อมูลที่เรียงแล้ว แต่คงประเภทข้อมูลเดิม
                self._data = self._data.loc[sorted_data.index]
                
                # รีเซ็ต index ให้เป็นลำดับใหม่
                self._data = self._data.reset_index(drop=True)
                
            except Exception as e:
                # หากเกิดข้อผิดพลาดในการเรียงลำดับ ให้แสดงข้อความแจ้งเตือน
                print(f"Warning: ไม่สามารถเรียงลำดับคอลัมน์ '{column_name}' ได้: {str(e)}")
            
            self.layoutChanged.emit()

    def flags(self, index):
        """กำหนด flags สำหรับ item ในตาราง"""
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.NoItemFlags


class ExchangeUnsenApp(ExchangeUnsenUI):
    """แอปพลิเคชันหลักสำหรับอ่านไฟล์ Excel"""
    
    def __init__(self):
        super().__init__()
        
        # ตั้งค่า UI
        self.setupUi()
        
        # ตัวแปรสำหรับเก็บข้อมูล
        self.current_data = None
        self.current_file_path = None
        
        # Threads
        self.excel_loader_thread = None
        self.mysql_search_thread = None # จะใช้ในภายหลัง

        # Timer สำหรับการกระพริบปุ่ม
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_load_button_style)
        self.is_blinking = False
        self.original_load_button_style = ""
        
        # MySQL connection
        self.mysql_connection = MySQLConnection() if MySQLConnection else None
        
        # เชื่อมต่อ signals กับ slots
        self.setup_connections()
        
        # ตั้งค่าเริ่มต้น
        self.setup_ui()
          # เชื่อมต่อ MySQL อัตโนมัติถ้าตั้งค่าไว้
        self.auto_connect_mysql()
        
        # ตั้งค่า tooltip เริ่มต้นสำหรับ status bar
        if hasattr(self, 'statusbar'):
            self.statusbar.setToolTip("📊 แถบแสดงสถานะการทำงานของโปรแกรม")
        
    def setup_connections(self):
        """เชื่อมต่อ signals กับ functions"""        # ปุ่มต่างๆ
        self.browseButton.clicked.connect(self.browse_file)
        self.exportButton.clicked.connect(self.export_to_excel)
        self.clearButton.clicked.connect(self.clear_data)
        self.searchPopulationButton.clicked.connect(self.start_mysql_search)
        
        # เพิ่มการจัดการ Double Click บนแถวข้อมูลในตาราง
        self.tableView.doubleClicked.connect(self.on_table_double_clicked)
        
        # เพิ่มปุ่ม clear filters ถ้ามี
        if hasattr(self, 'clearFiltersButton'):
            self.clearFiltersButton.clicked.connect(self.clear_filters)
        
        # Column combo box
        self.columnComboBox.currentTextChanged.connect(self.on_column_selected)
          # Menu actions
        self.actionOpen.triggered.connect(self.browse_file)
        self.actionExport.triggered.connect(self.export_to_excel)
        self.actionExit.triggered.connect(self.close)
        self.actionRefresh.triggered.connect(self.start_excel_load)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionMySQLSettings.triggered.connect(self.open_mysql_settings)
        self.actionConnectMySQL.triggered.connect(self.connect_mysql)
        self.actionDisconnectMySQL.triggered.connect(self.disconnect_mysql)
        
    def setup_ui(self):
        """ตั้งค่า UI เริ่มต้น"""
        # ตั้งค่าขนาดหน้าต่างให้กว้าง 65% ของหน้าจอ
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        window_width = int(screen.width() * 0.65)
        window_height = int(screen.height() * 0.8)  # สูง 80% เพื่อความสมดุล
          # คำนวณตำแหน่งให้อยู่กึ่งกลางหน้าจอ
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        
        # ตั้งค่าขนาดขั้นต่ำของหน้าต่าง
        self.setMinimumSize(800, 600)
        
        # ตั้งค่า window title และ icon
        self.setWindowTitle("ExchangeUnsen")
        
        # ตั้งค่า app icon
        icon_path = os.path.join(os.path.dirname(__file__), 'search-file.png')
        if os.path.exists(icon_path):
            app_icon = QtGui.QIcon(icon_path)
            self.setWindowIcon(app_icon)
            
        # ตั้งค่า table view
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSortingEnabled(True)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
          # ใช้ header แบบปกติเพื่อให้ชื่อคอลัมน์แสดงถูกต้อง
        header = self.tableView.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setStretchLastSection(True)
        header.sectionClicked.connect(self.on_header_clicked)
        
        # เพิ่ม context menu สำหรับ header
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_header_context_menu)
        
        # เปิดใช้งาน mouse tracking และ tooltip สำหรับ header
        header.setMouseTracking(True)
        header.sectionEntered.connect(self.update_header_tooltip)
        
        # ตั้งค่า tooltips สำหรับปุ่มต่างๆ
        self.setup_button_tooltips()
        
        # เพิ่ม context menu สำหรับ table rows
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.show_table_context_menu)
        
        # ตั้งค่า stylesheet สำหรับ selected row ให้ตัวอักษรเข้มขึ้น
        self.tableView.setStyleSheet("""
            QTableView::item:selected {
                background-color: #3daee9;
                color: white;
                font-weight: bold;
            }
            QTableView::item:selected:active {
                background-color: #2980b9;
                color: white;
                font-weight: bold;
            }
        """)
        
        # ซ่อน column selection UI เมื่อเริ่มต้น
        self.columnLabel.setVisible(False)
        self.columnComboBox.setVisible(False)
        self.searchPopulationButton.setVisible(False)
          # ตั้งค่า status
        self.update_status(MESSAGES.get('ready', 'พร้อมใช้งาน'))
        
    def on_header_clicked(self, logical_index):
        """จัดการเมื่อคลิกที่ header เพื่อเรียงลำดับ"""
        if self.current_data is not None:
            # อัปเดตสถานะให้แสดงว่าเรียงลำดับตามคอลัมน์ไหน
            column_name = self.current_data.columns[logical_index]
            self._update_status_and_progress(f"เรียงลำดับข้อมูลตามคอลัมน์: {column_name}")
    
    def on_filter_changed(self, column, filter_value):
        """จัดการเมื่อมีการเปลี่ยน filter (ปิดใช้งานชั่วคราว)"""
        # TODO: เปิดใช้งานเมื่อ filterable header พร้อม
        pass
        # if self.current_data is not None and hasattr(self.tableView.model(), 'applyFilters'):
        #     # รวบรวม filter ทั้งหมดที่ active อยู่
        #     active_filters = self.filterable_header.getActiveFilters()
        #     
        #     # ใช้ filter กับ model
        #     self.tableView.model().applyFilters(active_filters)
        #     
        #     # อัปเดตสถานะ
        #     if active_filters:
        #         filter_info = ", ".join([f"{self.current_data.columns[col]}='{val}'" 
        #                                for col, val in active_filters.items()])
        #         self._update_status_and_progress(f"กรองข้อมูล: {filter_info}")
        #     else:
        #         rows, cols = self.current_data.shape        #         self._update_status_and_progress(f"แสดงข้อมูลทั้งหมด - {rows} แถว, {cols} คอลัมน์")
        
    def browse_file(self):
        """เปิด dialog สำหรับเลือกไฟล์ Excel"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "เลือกไฟล์ Excel",
                "",
                "Excel Files (*.xlsx *.xls);;All Files (*)"
            )
            
            if file_path:
                self.current_file_path = file_path                # แสดง path แบบสั้นใน file path line edit
                display_path = self.get_shortened_path(file_path)
                self.filePathLineEdit.setText(display_path)
                # แสดง full path ใน tooltip
                self.filePathLineEdit.setToolTip(f"Full path: {file_path}")
                
                # เปิดใช้งานปุ่ม Clear เมื่อมีไฟล์
                self.clearButton.setEnabled(True)
                
                self.update_status(
                    f"เลือกไฟล์: {os.path.basename(file_path)} - กำลังเตรียมโหลด..."
                )
                  # โหลดข้อมูลอัตโนมัติหลัง delay 1 วินาที
                QTimer.singleShot(1000, self.start_excel_load)
            else:
                self.update_status("ยกเลิกการเลือกไฟล์")
                
        except Exception as e:
            QMessageBox.critical(
                self, "ข้อผิดพลาด", 
                f"เกิดข้อผิดพลาดในการเปิด dialog:\n{str(e)}"
            )
            self.update_status("เกิดข้อผิดพลาดในการเลือกไฟล์")
            
    def start_excel_load(self): # เปลี่ยนชื่อจาก load_data
        """เริ่มการโหลดข้อมูลจากไฟล์ Excel โดยใช้ Thread"""
        if not self.current_file_path:
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกไฟล์ Excel ก่อน")
            return

        if self.excel_loader_thread and self.excel_loader_thread.isRunning():
            QMessageBox.information(self, "แจ้งเตือน", "กำลังโหลดข้อมูลอยู่ กรุณารอสักครู่")
            return
            
        # หยุดการกระพริบปุ่มโหลดข้อมูล
        self.stop_load_button_blink()
        
        self.browseButton.setEnabled(False)
        self.exportButton.setEnabled(False)
        # self.clearButton.setEnabled(False) # อาจจะไม่ต้องปิด clear ขณะโหลด
        self.searchPopulationButton.setEnabled(False) # ปิดปุ่มค้นหาด้วย

        self.excel_loader_thread = ExcelLoaderThread(self.current_file_path)
        self.excel_loader_thread.finished.connect(self._on_excel_load_finished)
        self.excel_loader_thread.error.connect(self._on_excel_load_error)
        self.excel_loader_thread.progress.connect(self._update_status_and_progress)
        self.excel_loader_thread.start()
        
        self._update_status_and_progress("กำลังเริ่มต้นโหลดไฟล์ Excel...")
    
    def _on_excel_load_finished(self, data):
        """Slot เมื่อ ExcelLoaderThread โหลดข้อมูลเสร็จ"""
        self.current_data = data
        
        model = PandasModel(self.current_data)
        self.tableView.setModel(model)
        
        # ตั้งค่า header 
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # ตั้งค่า tooltip เริ่มต้นสำหรับ header
        self.setup_header_tooltips()
        
        self.exportButton.setEnabled(True)
        self.clearButton.setEnabled(True) 
        
        self.show_column_selection()
        self.update_column_dropdown()
        
        rows, cols = self.current_data.shape
        self._update_status_and_progress(f"โหลดข้อมูลสำเร็จ - {rows} แถว, {cols} คอลัมน์")
        
        # ไม่แสดง MessageBox เมื่อโหลดเสร็จ เพื่อให้ workflow ต่อเนื่อง
        # แสดงเฉพาะข้อมูลใน status bar เท่านั้น
        
        self.browseButton.setEnabled(True)
        if self.mysql_connection and self.mysql_connection.is_connected() and self.current_data is not None:
             self.searchPopulationButton.setEnabled(True) # เปิดปุ่มค้นหาถ้าเชื่อมต่อ MySQL และมีข้อมูล

        self.excel_loader_thread = None

    def _on_excel_load_error(self, error_message):
        """Slot เมื่อ ExcelLoaderThread เกิดข้อผิดพลาด"""
        QMessageBox.critical(self, "ข้อผิดพลาดในการโหลดไฟล์", error_message)
        self._update_status_and_progress(f"เกิดข้อผิดพลาดในการโหลดไฟล์: {error_message}")
        
        self.browseButton.setEnabled(True)
        self.excel_loader_thread = None

    def _update_status_and_progress(self, message, progress_value=None, max_value=None):
        """อัปเดต status bar และ (ในอนาคต) progress bar"""
        self.statusLabel.setText(f"สถานะ: {message}")
        # ส่วนของ QProgressBar จะเพิ่มทีหลังถ้าต้องการ
        # if progress_value is not None and max_value is not None and self.progressBar: # สมมติว่ามี self.progressBar
        #     self.progressBar.setMaximum(max_value)
        #     self.progressBar.setValue(progress_value)        # elif self.progressBar:
        #     self.progressBar.setValue(0) # Reset progress bar if no specific progress
    
    def export_to_excel(self):
        """Export ข้อมูลที่กรองแล้วเป็นไฟล์ Excel"""
        if self.current_data is None:
            QMessageBox.warning(self, "คำเตือน", "ไม่มีข้อมูลสำหรับ export")
            return
        if self.excel_loader_thread and self.excel_loader_thread.isRunning():
            QMessageBox.warning(self, "คำเตือน", "ไม่สามารถ export ได้ในขณะที่กำลังโหลดไฟล์อยู่")
            return
        if self.mysql_search_thread and self.mysql_search_thread.isRunning():
            QMessageBox.warning(self, "คำเตือน", "ไม่สามารถ export ได้ในขณะที่กำลังค้นหาข้อมูล")
            return
            
        try:
            # ดึงข้อมูลที่แสดงอยู่ในตาราง (หลังจากกรองแล้ว)
            model = self.tableView.model()
            if model and hasattr(model, '_data'):
                # ใช้ข้อมูลที่ผ่านการกรองแล้วจาก PandasModel
                export_data = model._data.copy()
                data_type = "ข้อมูลที่กรองแล้ว"
            else:
                # fallback ไปใช้ข้อมูลต้นฉบับ
                export_data = self.current_data.copy()
                data_type = "ข้อมูลทั้งหมด"
            
            # ตรวจสอบว่ามีข้อมูลสำหรับ export หรือไม่
            if export_data.empty:
                QMessageBox.warning(self, "คำเตือน", "ไม่มีข้อมูลสำหรับ export (อาจถูกกรองหมดแล้ว)")
                return
            
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(
                self,
                "บันทึกไฟล์ Excel",
                "exported_data.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if file_path:
                # ใช้ pandas.to_excel() เพื่อ export เป็น Excel
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    export_data.to_excel(writer, sheet_name='Data', index=False)
                
                QMessageBox.information(
                    self, 
                    "สำเร็จ", 
                    f"Export {data_type} เป็น Excel สำเร็จ!\n\n"
                    f"ไฟล์: {os.path.basename(file_path)}\n"
                    f"จำนวนแถว: {len(export_data):,} แถว\n"
                    f"จำนวนคอลัมน์: {len(export_data.columns)} คอลัมน์"
                )
                self._update_status_and_progress(f"Export สำเร็จ: {os.path.basename(file_path)} ({len(export_data):,} แถว)")
                
        except Exception as e:
            error_msg = f"เกิดข้อผิดพลาดในการ export:\n{str(e)}"
            QMessageBox.critical(self, "ข้อผิดพลาด", error_msg)
            self._update_status_and_progress("เกิดข้อผิดพลาดในการ export")
            
    def clear_data(self):
        """ล้างข้อมูลทั้งหมด"""
        if self.excel_loader_thread and self.excel_loader_thread.isRunning():
            QMessageBox.warning(self, "คำเตือน", "ไม่สามารถล้างข้อมูลได้ในขณะที่กำลังโหลดไฟล์อยู่")
            return
        if self.mysql_search_thread and self.mysql_search_thread.isRunning():
            QMessageBox.warning(self, "คำเตือน", "ไม่สามารถล้างข้อมูลได้ในขณะที่กำลังค้นหาข้อมูล")
            return

        reply = QMessageBox.question(
            self, 
            "ยืนยัน", 
            "คุณต้องการล้างข้อมูลทั้งหมดหรือไม่?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # หยุดการกระพริบปุ่มโหลดข้อมูล
            self.stop_load_button_blink()
            
            # ล้างข้อมูล
            self.current_data = None
            self.current_file_path = None            # ล้าง UI
            self.filePathLineEdit.clear()
            self.filePathLineEdit.setToolTip("")  # ล้าง tooltip ด้วย
            self.tableView.setModel(None)
            
            # ซ่อน column selection UI
            self.hide_column_selection()
            
            # ตรวจสอบให้แน่ใจว่าปุ่ม Browse ยังคงทำงานได้
            self.browseButton.setEnabled(True) # ปุ่ม Browse ควรทำงานได้เสมอ
            self.exportButton.setEnabled(False)
            self.clearButton.setEnabled(False) # ปิดปุ่ม clear จนกว่าจะเลือกไฟล์ใหม่
            self.searchPopulationButton.setEnabled(False)
            
            self.update_status("ล้างข้อมูลเรียบร้อย - พร้อมใช้งาน")
            
    def update_status(self, message): # ฟังก์ชันนี้อาจจะไม่ถูกใช้โดยตรงแล้ว จะใช้ _update_status_and_progress แทน
        """อัพเดทสถานะ"""
        self.statusLabel.setText(f"สถานะ: {message}")
    
    def show_about(self):
        """แสดงข้อมูลเกี่ยวกับแอปพลิเคชัน"""
        about_text = """
ExchangeUnsen - Excel Reader App

ฟีเจอร์หลัก:
• อ่านและแสดงไฟล์ Excel
• ค้นหาข้อมูลใน MySQL database
• กรองข้อมูลในตาราง
• ส่งออกข้อมูลเป็นไฟล์ Excel

การใช้งานระบบกรอง:
• คลิกขวาที่หัวคอลัมน์เพื่อเปิดเมนู
• เลือก "กรองคอลัมน์" เพื่อตั้งค่าการกรอง
• ใช้การค้นหาแบบ LIKE (ไม่คำนึงตัวพิมพ์ใหญ่-เล็ก)
• สามารถกรองหลายคอลัมน์พร้อมกัน

เคล็ดลับการใช้งาน:
• วางเมาส์บนปุ่มหรือหัวคอลัมน์เพื่อดู tooltip
• คลิกซ้ายที่หัวคอลัมน์เพื่อเรียงลำดับ
• คลิกขวาที่หัวคอลัมน์เพื่อกรองข้อมูล

Version: 1.0
        """
        QMessageBox.about(self, "เกี่ยวกับโปรแกรม", about_text.strip())
    
    def auto_connect_mysql(self):
        """เชื่อมต่อ MySQL อัตโนมัติถ้าตั้งค่าไว้"""
        if not self.mysql_connection:
            return
            
        try:
            from mysql_config import MySQLConfigManager
            config = MySQLConfigManager.load_config()
            if config.get('auto_connect', 'false') == 'true':
                success, message = self.mysql_connection.connect()
                if success:
                    self.update_status(f"เชื่อมต่อ MySQL สำเร็จ - {message}")
                else:
                    self.update_status(f"ไม่สามารถเชื่อมต่อ MySQL ได้ - {message}")
        except Exception as e:            self.update_status(f"ข้อผิดพลาดในการเชื่อมต่อ MySQL: {str(e)}")
    
    def open_mysql_settings(self):
        """เปิด dialog ตั้งค่า MySQL"""
        if not MySQLConfigDialog:
            QMessageBox.warning(self, "คำเตือน", "ไม่พบ MySQL configuration module")
            return
            
        dialog = MySQLConfigDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # รีโหลด connection หลังจากการตั้งค่าใหม่
            if self.mysql_connection:
                self.mysql_connection.disconnect()
                self.mysql_connection = MySQLConnection()
            self.update_status("อัปเดตการตั้งค่า MySQL แล้ว")
    
    def connect_mysql(self):
        """เชื่อมต่อ MySQL"""
        if not self.mysql_connection:
            QMessageBox.warning(self, "คำเตือน", "ไม่พบ MySQL connection module")
            return
            
        success, message = self.mysql_connection.connect()
        if success:
            QMessageBox.information(self, "สำเร็จ", f"เชื่อมต่อ MySQL สำเร็จ\n{message}")
            self.update_status("เชื่อมต่อ MySQL แล้ว")
        else:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ไม่สามารถเชื่อมต่อ MySQL ได้\n{message}")
            self.update_status("เชื่อมต่อ MySQL ไม่สำเร็จ")
    
    def disconnect_mysql(self):
        """ตัดการเชื่อมต่อ MySQL"""
        if not self.mysql_connection:
            return
            
        if self.mysql_connection.is_connected():
            self.mysql_connection.disconnect()
            QMessageBox.information(self, "สำเร็จ", "ตัดการเชื่อมต่อ MySQL แล้ว")
            self.update_status("ตัดการเชื่อมต่อ MySQL แล้ว")
        else:
            QMessageBox.information(self, "แจ้งเตือน", "ไม่ได้เชื่อมต่อ MySQL อยู่")

    def show_column_selection(self):
        """แสดง UI สำหรับเลือกคอลัมน์"""
        self.columnLabel.setVisible(True)
        self.columnComboBox.setVisible(True)
        self.searchPopulationButton.setVisible(True)
    
    def hide_column_selection(self):
        """ซ่อน UI สำหรับเลือกคอลัมน์"""
        self.columnLabel.setVisible(False)
        self.columnComboBox.setVisible(False)
        self.searchPopulationButton.setVisible(False)
        self.columnComboBox.clear()
    
    def update_column_dropdown(self):
        """อัปเดตรายการคอลัมน์ใน dropdown"""
        if self.current_data is not None:
            # ล้างรายการเก่า
            self.columnComboBox.clear()
              # เพิ่มตัวเลือก "ไม่เลือก" เป็นตัวเลือกแรก
            self.columnComboBox.addItem("-- ไม่เลือกคอลัมน์ --")
            
            # เพิ่มเฉพาะ 3 ตัวเลือกที่รองรับ
            supported_columns = ['pid', 'cid', 'hn']
            for column in supported_columns:
                self.columnComboBox.addItem(column)
                
            # ตั้งค่าให้เลือกตัวเลือกแรก (ไม่เลือก)            self.columnComboBox.setCurrentIndex(0)
    
    def on_column_selected(self, column_name):
        """จัดการเมื่อเลือกคอลัมน์"""
        if not column_name or column_name == "-- ไม่เลือกคอลัมน์ --":
            self._update_status_and_progress("ไม่ได้เลือกคอลัมน์สำหรับเชื่อมโยง") # เปลี่ยนไปใช้ _update_status_and_progress
            self.searchPopulationButton.setEnabled(False) # ปิดปุ่มค้นหาถ้าไม่เลือกคอลัมน์
            return
        
        # เปิดใช้งานปุ่มค้นหาถ้าเลือกคอลัมน์ที่ถูกต้อง และเชื่อมต่อ MySQL แล้ว และมีข้อมูล
        if self.mysql_connection and self.mysql_connection.is_connected() and self.current_data is not None:
            self.searchPopulationButton.setEnabled(True)
        else:
            self.searchPopulationButton.setEnabled(False)

        if self.current_data is not None and column_name in self.current_data.columns:
            # แสดงข้อมูลของคอลัมน์ที่เลือก
            column_data = self.current_data[column_name]
            unique_values = column_data.nunique()
            null_count = column_data.isnull().sum()
            
            self._update_status_and_progress(f"เลือกคอลัมน์: {column_name} (ค่าไม่ซ้ำ: {unique_values}, ค่าว่าง: {null_count})") # เปลี่ยนไปใช้ _update_status_and_progress
        elif self.current_data is not None:
            self._update_status_and_progress(f"เลือกคอลัมน์: {column_name} (ไม่พบในข้อมูลปัจจุบัน)") # เปลี่ยนไปใช้ _update_status_and_progress
            self.searchPopulationButton.setEnabled(False)
        else: # กรณี current_data is None
            self.searchPopulationButton.setEnabled(False)

    def start_mysql_search(self):
        """เริ่มการเชื่อมโยงข้อมูลกับฐานข้อมูล MySQL โดยใช้ Thread"""
        if self.current_data is None:
            QMessageBox.warning(self, "คำเตือน", "กรุณาโหลดข้อมูล Excel ก่อน")
            return

        # ตรวจสอบการเชื่อมต่อฐานข้อมูลก่อนทำงานอื่นๆ
        if not self.mysql_connection or not self.mysql_connection.is_connected():
            QMessageBox.warning(self, "คำเตือน", "กรุณาเชื่อมต่อฐานข้อมูลก่อน")
            self.searchPopulationButton.setEnabled(False)
            return

        selected_column = self.columnComboBox.currentText()
        if not selected_column or selected_column == "-- ไม่เลือกคอลัมน์ --":
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกคอลัมน์สำหรับค้นหา")
            return

        if self.mysql_search_thread and self.mysql_search_thread.isRunning():
            QMessageBox.information(self, "แจ้งเตือน", "กำลังค้นหาข้อมูลอยู่ กรุณารอสักครู่")
            return
        
        # ปิดการใช้งาน UI elements
        self.searchPopulationButton.setEnabled(False)
        self.browseButton.setEnabled(False)
        self.exportButton.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.columnComboBox.setEnabled(False)
        self.actionOpen.setEnabled(False)
        self.actionExport.setEnabled(False)
        self.actionRefresh.setEnabled(False)
        self.actionMySQLSettings.setEnabled(False)
        self.actionConnectMySQL.setEnabled(False)
        self.actionDisconnectMySQL.setEnabled(False)

        self.mysql_search_thread = MySQLSearchThread(self.current_data, selected_column, self.mysql_connection)
        self.mysql_search_thread.finished.connect(self._on_mysql_search_finished)
        self.mysql_search_thread.error.connect(self._on_mysql_search_error)
        self.mysql_search_thread.progress.connect(self._update_status_and_progress) # ใช้ slot เดิม
        self.mysql_search_thread.start()
        
        self._update_status_and_progress("กำลังเริ่มต้นค้นหาข้อมูลใน MySQL...")
    
    def _on_mysql_search_finished(self, updated_data, found_count, not_found_count):
        """Slot เมื่อ MySQLSearchThread ค้นหาข้อมูลเสร็จ"""
        self.current_data = updated_data
        model = PandasModel(self.current_data)
        self.tableView.setModel(model)
        
        # ตั้งค่า header
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
          # ตั้งค่า tooltip เริ่มต้นสำหรับ header
        self.setup_header_tooltips()
        
        self._update_status_and_progress(f"เชื่อมโยงข้อมูลสำเร็จ - พบ {found_count} รายการ, ไม่พบ {not_found_count} รายการ")
        
        # ไม่แสดง MessageBox เพื่อให้ workflow ต่อเนื่อง
        # แสดงผลลัพธ์เฉพาะใน status bar เท่านั้น
        
        # เปิดการใช้งาน UI elements
        self.browseButton.setEnabled(True)
        self.exportButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.columnComboBox.setEnabled(True)
        self.actionOpen.setEnabled(True)
        self.actionExport.setEnabled(True)
        self.actionRefresh.setEnabled(True)
        self.actionMySQLSettings.setEnabled(True)
        self.actionConnectMySQL.setEnabled(True)
        self.actionDisconnectMySQL.setEnabled(True)

        # เปิด/ปิดปุ่ม searchPopulationButton ตามเงื่อนไข
        enable_search_button = (self.mysql_connection and 
                                self.mysql_connection.is_connected() and 
                                self.current_data is not None and 
                                self.columnComboBox.currentText() != "-- ไม่เลือกคอลัมน์ --")
        self.searchPopulationButton.setEnabled(enable_search_button)
        
        self.mysql_search_thread = None

    def _on_mysql_search_error(self, error_message):
        """Slot เมื่อ MySQLSearchThread เกิดข้อผิดพลาด"""
        QMessageBox.critical(self, "ข้อผิดพลาดในการเชื่อมโยงข้อมูล", error_message)
        self._update_status_and_progress(f"เกิดข้อผิดพลาดในการเชื่อมโยงข้อมูล: {error_message}")
        
        # เปิดการใช้งาน UI elements (เหมือนใน _on_mysql_search_finished)
        self.browseButton.setEnabled(True)
        self.exportButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.columnComboBox.setEnabled(True)
        self.actionOpen.setEnabled(True)
        self.actionExport.setEnabled(True)
        self.actionRefresh.setEnabled(True)
        self.actionMySQLSettings.setEnabled(True)
        self.actionConnectMySQL.setEnabled(True)
        self.actionDisconnectMySQL.setEnabled(True)

        # เปิด/ปิดปุ่ม searchPopulationButton ตามเงื่อนไข
        enable_search_button = (self.mysql_connection and 
                                self.mysql_connection.is_connected() and 
                                self.current_data is not None and 
                                self.columnComboBox.currentText() != "-- ไม่เลือกคอลัมน์ --")
        self.searchPopulationButton.setEnabled(enable_search_button)
            
        self.mysql_search_thread = None

    def on_filter_applied(self):
        """จัดการเมื่อมีการใช้ filter"""
        if self.current_data is not None and hasattr(self.tableView.model(), 'getActiveFilters'):
            # รับ filter ที่ active อยู่
            active_filters = self.tableView.model().getActiveFilters()
            
            # นับจำนวนแถวที่แสดงหลังการกรอง
            current_rows = self.tableView.model().rowCount()
            total_rows = len(self.current_data)
            
            # อัปเดตสถานะ
            if active_filters:
                filter_count = len(active_filters)
                self._update_status_and_progress(f"✅ กรองข้อมูล: แสดง {current_rows}/{total_rows} แถว ({filter_count} คอลัมน์มีการกรอง)")
                  # ไม่แสดง popup เพื่อให้ workflow ต่อเนื่อง
                # แสดงเฉพาะข้อมูลใน status bar เท่านั้น
                self.last_filter_time = time.time()
            else:
                rows, cols = self.current_data.shape
                self._update_status_and_progress(f"📊 แสดงข้อมูลทั้งหมด: {rows} แถว, {cols} คอลัมน์")

    def clear_filters(self):
        """ล้าง filter ทั้งหมด"""
        if self.current_data is not None:
            # กรณีมี filterable_header
            if hasattr(self, 'filterable_header'):
                self.filterable_header.clearAllFilters()
                self.on_filter_applied()  # อัปเดตสถานะ
            # กรณีไม่มี filterable_header แต่มี model ที่สนับสนุนการ filter
            elif hasattr(self.tableView, 'model') and hasattr(self.tableView.model(), 'clearAllFilters'):
                self.tableView.model().clearAllFilters()
                self.on_filter_applied()  # อัปเดตสถานะ
            # กรณีไม่มีการ filter ให้โหลด model ใหม่จาก current_data
            else:
                model = PandasModel(self.current_data)
                self.tableView.setModel(model)
                self.on_filter_applied()  # อัปเดตสถานะ
                
            # ไม่แสดง MessageBox เพื่อให้ workflow ต่อเนื่อง

    def start_load_button_blink(self):
        """เริ่มการกระพริบปุ่มโหลดข้อมูลด้วยสีส้ม"""
        if not self.is_blinking:
            # เก็บ style เดิมของปุ่ม
            self.original_load_button_style = self.loadButton.styleSheet()
            self.is_blinking = True
            self.blink_timer.start(400)  # กระพริบทุก 400ms (เร็วขึ้นเล็กน้อย)
    
    def stop_load_button_blink(self):
        """หยุดการกระพริบปุ่มโหลดข้อมูล"""
        if self.is_blinking:
            self.blink_timer.stop()
            self.is_blinking = False            # คืนค่า style เดิม
            self.loadButton.setStyleSheet(self.original_load_button_style)
    
    def toggle_load_button_style(self):
        """สลับ style ของปุ่มโหลดข้อมูลเพื่อทำให้กระพริบ"""
        if self.is_blinking:
            current_style = self.loadButton.styleSheet()            # Style สำหรับการกระพริบ (สีส้มสว่าง)
            blink_style = """
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: 2px solid #FF6F00;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
                border-color: #E65100;
            }
            """
            
            # สลับระหว่าง style เดิมกับ style กระพริบ
            if "FF9800" in current_style:
                self.loadButton.setStyleSheet(self.original_load_button_style)
            else:
                self.loadButton.setStyleSheet(blink_style)

    def show_header_context_menu(self, position):
        """แสดง context menu สำหรับ header"""
        if self.current_data is None:
            return
            
        header = self.tableView.horizontalHeader()
        logical_index = header.logicalIndexAt(position)
        
        if logical_index >= 0:
            menu = QtWidgets.QMenu(self)
            
            column_name = self.current_data.columns[logical_index]
            filter_action = menu.addAction(f"🔍 กรองคอลัมน์ '{column_name}'")
            filter_action.setToolTip("เปิด dialog สำหรับตั้งค่าการกรองข้อมูล (LIKE search)")
            
            clear_filter_action = menu.addAction(f"🚫 ล้างการกรองคอลัมน์ '{column_name}'")
            clear_filter_action.setToolTip("ยกเลิกการกรองสำหรับคอลัมน์นี้")
            
            menu.addSeparator()
            clear_all_filters_action = menu.addAction("🗑️ ล้างการกรองทั้งหมด")
            clear_all_filters_action.setToolTip("ยกเลิกการกรองทุกคอลัมน์")
            
            action = menu.exec_(header.mapToGlobal(position))
            
            if action == filter_action:
                self.open_column_filter_dialog(logical_index)
            elif action == clear_filter_action:
                self.clear_column_filter(logical_index)
            elif action == clear_all_filters_action:
                self.clear_filters()
    
    def open_column_filter_dialog(self, logical_index):
        """เปิด dialog สำหรับ filter คอลัมน์"""
        column_name = self.current_data.columns[logical_index]
        
        # ดึง filter ปัจจุบัน
        current_filter = ""
        model = self.tableView.model()
        if model and hasattr(model, 'getColumnFilter'):
            current_filter = model.getColumnFilter(logical_index)
        
        # เปิด filter dialog
        dialog = FilterDialog(column_name, current_filter, self)
        if dialog.exec_() == QDialog.Accepted:
            filter_text = dialog.getFilterText()
            
            # ใช้ filter กับ model
            if model and hasattr(model, 'applyColumnFilter'):
                model.applyColumnFilter(logical_index, filter_text)
                self.on_filter_applied()
                
                # แสดงข้อความแจ้งเตือน
                if filter_text:
                    self._update_status_and_progress(f"กรองคอลัมน์ '{column_name}' ด้วย: {filter_text}")
                else:
                    self._update_status_and_progress(f"ยกเลิกการกรองคอลัมน์ '{column_name}'")
    
    def clear_column_filter(self, logical_index):
        """ล้างการกรองของคอลัมน์เดียว"""
        model = self.tableView.model()
        if model and hasattr(model, 'applyColumnFilter'):
            model.applyColumnFilter(logical_index, "")
            self.on_filter_applied()
            
            column_name = self.current_data.columns[logical_index]
            self._update_status_and_progress(f"ล้างการกรองคอลัมน์ '{column_name}'")

    def update_header_tooltip(self, logical_index):
        """อัปเดต tooltip สำหรับ header column"""
        if self.current_data is None or logical_index < 0:
            return
            
        try:
            column_name = self.current_data.columns[logical_index]
            
            # ข้อมูลพื้นฐานของคอลัมน์
            total_rows = len(self.current_data)
            non_null_count = self.current_data[column_name].count()
            null_count = total_rows - non_null_count;
            
            # ตรวจสอบว่ามี filter อยู่หรือไม่
            current_filter = ""
            model = self.tableView.model()
            if model and hasattr(model, 'getColumnFilter'):
                current_filter = model.getColumnFilter(logical_index)
            
            # สร้าง tooltip text
            tooltip_parts = [
                f"📊 คอลัมน์: {column_name}",
                f"📈 ข้อมูลทั้งหมด: {total_rows:,} แถว",
                f"✅ มีข้อมูล: {non_null_count:,} แถว",
            ]
            
            if null_count > 0:
                tooltip_parts.append(f"❌ ไม่มีข้อมูล: {null_count:,} แถว")
            
            if current_filter:
                tooltip_parts.append(f"🔍 กรองด้วย: '{current_filter}'")
            
            tooltip_parts.extend([
                "",
                "💡 เคล็ดลับ:",
                "• คลิกซ้าย = เรียงลำดับ",
                "• คลิกขวา = เปิดเมนูกรองข้อมูล"
            ])
            
            tooltip_text = "\n".join(tooltip_parts)
            
            # ตั้งค่า tooltip
            header = self.tableView.horizontalHeader()
            header.setToolTip(tooltip_text)
            
        except Exception as e:
            # หากเกิดข้อผิดพลาด ให้แสดง tooltip พื้นฐาน
            header = self.tableView.horizontalHeader()
            header.setToolTip("คลิกขวาเพื่อกรองข้อมูล | คลิกซ้ายเพื่อเรียงลำดับ")
    
    def setup_header_tooltips(self):
        """ตั้งค่า tooltip เริ่มต้นสำหรับ header ทุกคอลัมน์"""
        if self.current_data is None:
            return
            
        header = self.tableView.horizontalHeader()
        
        # ตั้งค่า tooltip ทั่วไปสำหรับ header
        general_tooltip = (
            "💡 คำแนะนำการใช้งาน:\n"
            "• คลิกซ้าย = เรียงลำดับข้อมูล\n"
            "• คลิกขวา = เปิดเมนูกรองข้อมูล\n"
            "• เลื่อนเมาส์ไปที่คอลัมน์ = ดูข้อมูลสถิติ"
        )
        
        # ตั้งค่า tooltip สำหรับ header widget หลัก
        header.setToolTip(general_tooltip)

    def setup_button_tooltips(self):
        """ตั้งค่า tooltips สำหรับปุ่มต่างๆ"""
        try:
            # tooltips สำหรับปุ่มหลัก
            if hasattr(self, 'browseButton'):
                self.browseButton.setToolTip("📂 เลือกไฟล์ Excel ที่ต้องการเปิด\n(สนับสนุนไฟล์ .xls, .xlsx, .xlsm)")
            
            if hasattr(self, 'exportButton'):
                self.exportButton.setToolTip("💾 ส่งออกข้อมูลที่กรองแล้วเป็นไฟล์ Excel\n(จะส่งออกเฉพาะข้อมูลที่แสดงในตารางเท่านั้น)")
            
            if hasattr(self, 'clearButton'):
                self.clearButton.setToolTip("🗑️ ล้างข้อมูลทั้งหมด")
            
            if hasattr(self, 'searchPopulationButton'):
                self.searchPopulationButton.setToolTip("🔗 เชื่อมโยงข้อมูลกับฐานข้อมูล MySQL")
            
            if hasattr(self, 'columnComboBox'):
                self.columnComboBox.setToolTip("📝 เลือกคอลัมน์สำหรับค้นหาใน MySQL")
                
        except Exception as e:
            print(f"Warning: ไม่สามารถตั้งค่า tooltips ได้: {e}")

    def show_table_context_menu(self, position):
        """แสดง context menu สำหรับ table rows"""
        if self.current_data is None:
            return
            
        # ตรวจสอบว่าคลิกที่แถวหรือไม่
        index = self.tableView.indexAt(position)
        if not index.isValid():
            return
            
        row = index.row()
        if row < 0 or row >= len(self.current_data):
            return
            
        menu = QtWidgets.QMenu(self)
        menu.setTitle(f"แถวที่ {row + 1}")
        
        # เพิ่ม actions
        check_action = menu.addAction("🔍 ตรวจสอบข้อมูล")
        check_action.setToolTip("แสดงข้อมูลในแถวนี้แบบละเอียด")
        
        menu.addSeparator()
        close_action = menu.addAction("❌ ปิด")
        close_action.setToolTip("ปิดเมนู")
          # แสดงเมนู
        action = menu.exec_(self.tableView.mapToGlobal(position))
        
        if action == check_action:
            self.check_row_data(row)
        elif action == close_action:
            pass

    def on_table_double_clicked(self, index):
        """จัดการเมื่อมีการ Double Click ที่แถวข้อมูล"""
        if not index.isValid() or self.current_data is None:
            return
        # เรียกใช้ฟังก์ชันตรวจสอบข้อมูลโดยส่งลำดับแถวที่คลิก
        self.check_row_data(index.row())
    
    def check_row_data(self, row):
        """ตรวจสอบข้อมูลในแถวที่เลือก"""
        if self.current_data is None or row < 0 or row >= len(self.current_data):
            QMessageBox.warning(self, "คำเตือน", "ไม่สามารถตรวจสอบข้อมูลได้")
            return
            
        # ดึงข้อมูลจากแถวที่เลือก
        row_data = self.current_data.iloc[row]
        
        # สร้างข้อความแสดงข้อมูล
        details = []
        details.append(f"📋 ข้อมูลแถวที่ {row + 1}:")
        details.append("=" * 50)
        
        # เรียงคอลัมน์ให้แสดงผลลัพธ์การค้นหาก่อน (ถ้ามี)
        found_columns = [col for col in row_data.index if col.endswith('_found')]
        other_columns = [col for col in row_data.index if not col.endswith('_found')]
        
        # แสดงคอลัมน์ผลลัพธ์ก่อน (ถ้ามี)
        if found_columns:
            details.append("🔍 ผลการค้นหา:")
            for column in found_columns:
                value = row_data[column]
                # จัดรูปแบบข้อมูล
                if pd.isna(value) or value == '':
                    formatted_value = "(ไม่มีข้อมูล)"
                elif isinstance(value, (int, float)):
                    formatted_value = f"{value:,}"
                else:
                    formatted_value = str(value)
                    
                # แปลงชื่อคอลัมน์ให้อ่านง่ายขึ้น
                display_name = column.replace('_found', '').replace('pid', 'รหัสบุคคล')
                display_name = display_name.replace('cid', 'เลขบัตรประชาชน')
                display_name = display_name.replace('fname', 'ชื่อ')
                display_name = display_name.replace('lname', 'นามสกุล')
                display_name = display_name.replace('hn', 'HN')
                
                details.append(f"• {display_name}: {formatted_value}")
            
            details.append("-" * 30)
        
        # แสดงคอลัมน์อื่นๆ
        details.append("📊 ข้อมูลที่เลือก:")
        for column in other_columns:
            value = row_data[column]
            # จัดรูปแบบข้อมูล
            if pd.isna(value):
                formatted_value = "(ไม่มีข้อมูล)"
            elif isinstance(value, (int, float)):
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
                
            details.append(f"• {column}: {formatted_value}")
        
        details.append("")
        details.append("💡 เคล็ดลับ:")
        details.append("• คลิกขวาที่หัวคอลัมน์เพื่อกรองข้อมูล")
        details.append("• คลิกซ้ายที่หัวคอลัมน์เพื่อเรียงลำดับ")
        
        # แสดง dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("ตรวจสอบข้อมูล")
        msg.setText("\n".join(details))
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        
        # ปรับขนาด dialog ให้เหมาะสม
        msg.setDetailedText("ข้อมูลแสดงจากแถวที่เลือกในตาราง")
        msg.exec_()
    
    def get_shortened_path(self, file_path, max_length=50):
        """สร้าง path แบบสั้นสำหรับแสดงใน UI"""
        if len(file_path) <= max_length:
            return file_path
            
        # แยกส่วนต่างๆ ของ path
        drive, path_without_drive = os.path.splitdrive(file_path)
        directory, filename = os.path.split(path_without_drive)
        
        # หากชื่อไฟล์ยาวเกินไป ให้ตัดให้สั้นลง
        if len(filename) > max_length - 10:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length-15] + "..." + ext
            return f"...{os.sep}{filename}"
        
        # หาค path ที่เหมาะสม
        parts = directory.strip(os.sep).split(os.sep)
        
        # เริ่มจาก directory สุดท้ายและชื่อไฟล์
        result = filename
        remaining_length = max_length - len(filename)
        
        # เพิ่ม directory ทีละตัวจากหลังไปหน้า
        for i in range(len(parts) - 1, -1, -1):
            part = parts[i]
            test_addition = os.sep + part
            
            if len(result) + len(test_addition) + 3 <= remaining_length:  # +3 สำหรับ "...":
                result = part + os.sep + result
            else:
                result = "..." + os.sep + result
                break
                
        # เพิ่ม drive letter ถ้ามี
        if drive and len(result) + len(drive) <= max_length:
            result = drive + result
        elif not result.startswith("..."):
            result = "..." + os.sep + result
            
        return result

def main():
    """ฟังก์ชันหลักสำหรับรันแอปพลิเคชัน"""
    app = QApplication(sys.argv)
    
    # ตั้งค่า app icon สำหรับ taskbar
    icon_path = os.path.join(os.path.dirname(__file__), 'search-file.png')
    if os.path.exists(icon_path):
        app_icon = QtGui.QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # ตั้งค่าฟอนต์ไทย
    font = QFont("Tahoma", 9)
    app.setFont(font)
    
    # สร้างและแสดงหน้าต่างหลัก
    window = ExchangeUnsenApp()
    window.show()
    
    # รันแอปพลิเคชัน
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
