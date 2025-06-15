"""
Configuration file สำหรับ Excel Reader Application
"""

# การตั้งค่าแอปพลิเคชัน
APP_CONFIG = {
    'name': 'ExchangeUnsen',
    'version': '1.0.1',
    'version_code': 101,
    'release': '2025-06-15',
    'description': 'แอปพลิเคชันสำหรับอ่านไฟล์ Excel และเชื่อมโยงข้อมูลกับ MySQL',
    'author': 'Python Developer',
    'window_title': 'Excel File Reader',
    'window_size': (1000, 700),
    'min_window_size': (800, 600)
}

# การตั้งค่าไฟล์
FILE_CONFIG = {
    'supported_excel_formats': ['.xlsx', '.xls'],
    'excel_filter': "Excel Files (*.xlsx *.xls);;All Files (*)",
    'csv_filter': "CSV Files (*.csv);;All Files (*)",
    'default_export_name': 'exported_data.csv',
    'encoding': 'utf-8-sig'
}

# การตั้งค่า UI
UI_CONFIG = {
    'font_family': 'Tahoma',
    'font_size': 9,
    'menu_font_size': 10,
    'button_font_size': 10,
    'status_font_size': 10,
    'enable_sorting': True,
    'enable_alternating_colors': True,
    'selection_behavior': 'rows'  # 'rows' or 'items'
}

# การตั้งค่าสี
COLOR_CONFIG = {
    'primary': '#4CAF50',
    'primary_hover': '#45a049',
    'primary_pressed': '#3d8b40',
    'secondary': '#2196F3',
    'secondary_hover': '#1976D2',
    'secondary_pressed': '#1565C0',
    'warning': '#FF9800',
    'warning_hover': '#F57C00',
    'warning_pressed': '#E65100',
    'danger': '#F44336',
    'danger_hover': '#D32F2F',
    'danger_pressed': '#B71C1C',
    'disabled': '#CCCCCC',
    'disabled_text': '#666666',
    'background': '#F5F5F5',
    'border': '#DDDDDD'
}

# ข้อความภาษาไทย
MESSAGES = {
    'ready': 'พร้อมใช้งาน - กรุณาเลือกไฟล์ Excel',
    'file_selected': 'เลือกไฟล์: {}',
    'loading': 'กำลังโหลดข้อมูล...',
    'load_success': 'โหลดข้อมูลสำเร็จ - {} แถว, {} คอลัมน์',
    'load_error': 'เกิดข้อผิดพลาดในการโหลดไฟล์',
    'export_success': 'Export สำเร็จ: {}',
    'export_error': 'เกิดข้อผิดพลาดในการ export',
    'clear_success': 'ล้างข้อมูลเรียบร้อย - พร้อมใช้งาน',
    'no_file_warning': 'กรุณาเลือกไฟล์ Excel ก่อน',
    'no_data_warning': 'ไม่มีข้อมูลสำหรับ export',
    'clear_confirm': 'คุณต้องการล้างข้อมูลทั้งหมดหรือไม่?'
}

# การตั้งค่า pandas
PANDAS_CONFIG = {
    'max_rows': 10000,  # จำนวนแถวสูงสุดที่แสดง    'max_columns': 100,  # จำนวนคอลัมน์สูงสุดที่แสดง
    'excel_engine_xlsx': 'openpyxl',
    'excel_engine_xls': 'xlrd'
}
