"""
Utility functions สำหรับ Excel Reader Application
"""

import os
import sys
import pandas as pd
from typing import Optional, Tuple, List
import logging
from datetime import datetime


def setup_logging():
    """ตั้งค่า logging สำหรับแอปพลิเคชัน"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = os.path.join(log_dir, f"excel_reader_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def validate_excel_file(file_path: str) -> Tuple[bool, str]:
    """
    ตรวจสอบความถูกต้องของไฟล์ Excel
    
    Args:
        file_path: เส้นทางไฟล์
        
    Returns:
        Tuple[bool, str]: (ถูกต้องหรือไม่, ข้อความ)
    """
    if not file_path:
        return False, "ไม่ได้ระบุไฟล์"
    
    if not os.path.exists(file_path):
        return False, "ไฟล์ไม่พบ"
    
    if not os.path.isfile(file_path):
        return False, "เส้นทางที่ระบุไม่ใช่ไฟล์"
    
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in ['.xlsx', '.xls']:
        return False, "รูปแบบไฟล์ไม่ถูกต้อง (รองรับเฉพาะ .xlsx และ .xls)"
    
    # ตรวจสอบขนาดไฟล์ (ไม่เกิน 100MB)
    file_size = os.path.getsize(file_path)
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        return False, f"ไฟล์ใหญ่เกินไป ({file_size / (1024*1024):.1f}MB > 100MB)"
    
    return True, "ไฟล์ถูกต้อง"


def read_excel_file(file_path: str, sheet_name: Optional[str] = None) -> Tuple[Optional[pd.DataFrame], str]:
    """
    อ่านไฟล์ Excel
    
    Args:
        file_path: เส้นทางไฟล์
        sheet_name: ชื่อ sheet (ถ้าไม่ระบุจะใช้ sheet แรก)
        
    Returns:
        Tuple[Optional[pd.DataFrame], str]: (DataFrame, ข้อความสถานะ)
    """
    try:
        # ตรวจสอบไฟล์ก่อน
        is_valid, message = validate_excel_file(file_path)
        if not is_valid:
            return None, message
        
        # อ่านไฟล์
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.xlsx':
            df = pd.read_excel(file_path, engine='openpyxl', sheet_name=sheet_name)
        else:  # .xls
            df = pd.read_excel(file_path, engine='xlrd', sheet_name=sheet_name)
        
        # ตรวจสอบข้อมูล
        if df.empty:
            return None, "ไฟล์ไม่มีข้อมูล"
        
        rows, cols = df.shape
        return df, f"อ่านไฟล์สำเร็จ: {rows} แถว, {cols} คอลัมน์"
        
    except FileNotFoundError:
        return None, "ไม่พบไฟล์ที่ระบุ"
    except PermissionError:
        return None, "ไม่มีสิทธิ์เข้าถึงไฟล์"
    except pd.errors.EmptyDataError:
        return None, "ไฟล์ไม่มีข้อมูล"
    except Exception as e:
        return None, f"เกิดข้อผิดพลาด: {str(e)}"


def export_to_csv(df: pd.DataFrame, file_path: str, encoding: str = 'utf-8-sig') -> Tuple[bool, str]:
    """
    Export DataFrame เป็นไฟล์ CSV
    
    Args:
        df: DataFrame ที่จะ export
        file_path: เส้นทางไฟล์ปลายทาง
        encoding: encoding ของไฟล์
        
    Returns:
        Tuple[bool, str]: (สำเร็จหรือไม่, ข้อความสถานะ)
    """
    try:
        if df is None or df.empty:
            return False, "ไม่มีข้อมูลสำหรับ export"
        
        # สร้างโฟลเดอร์ถ้าไม่มี
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Export ไฟล์
        df.to_csv(file_path, index=False, encoding=encoding)
        
        rows, cols = df.shape
        file_size = os.path.getsize(file_path)
        return True, f"Export สำเร็จ: {rows} แถว, {cols} คอลัมน์ ({file_size:,} bytes)"
        
    except PermissionError:
        return False, "ไม่มีสิทธิ์เขียนไฟล์ในตำแหน่งที่ระบุ"
    except Exception as e:
        return False, f"เกิดข้อผิดพลาดในการ export: {str(e)}"


def get_excel_sheets(file_path: str) -> Tuple[Optional[List[str]], str]:
    """
    ดึงรายชื่อ sheet ทั้งหมดในไฟล์ Excel
    
    Args:
        file_path: เส้นทางไฟล์
        
    Returns:
        Tuple[Optional[List[str]], str]: (รายชื่อ sheet, ข้อความสถานะ)
    """
    try:
        # ตรวจสอบไฟล์ก่อน
        is_valid, message = validate_excel_file(file_path)
        if not is_valid:
            return None, message
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.xlsx':
            excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        else:  # .xls
            excel_file = pd.ExcelFile(file_path, engine='xlrd')
        
        sheets = excel_file.sheet_names
        excel_file.close()
        
        return sheets, f"พบ {len(sheets)} sheet"
        
    except Exception as e:
        return None, f"เกิดข้อผิดพลาด: {str(e)}"


def format_file_size(size_bytes: int) -> str:
    """
    แปลงขนาดไฟล์เป็นรูปแบบที่อ่านง่าย
    
    Args:
        size_bytes: ขนาดไฟล์ในหน่วย bytes
        
    Returns:
        str: ขนาดไฟล์ในรูปแบบที่อ่านง่าย
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    ทำความสะอาดข้อมูลใน DataFrame
    
    Args:
        df: DataFrame ที่ต้องการทำความสะอาด
        
    Returns:
        pd.DataFrame: DataFrame ที่ทำความสะอาดแล้ว
    """
    if df is None or df.empty:
        return df
    
    # สำเนา DataFrame
    cleaned_df = df.copy()
    
    # ลบคอลัมน์ที่ว่างทั้งหมด
    cleaned_df = cleaned_df.dropna(axis=1, how='all')
    
    # ลบแถวที่ว่างทั้งหมด
    cleaned_df = cleaned_df.dropna(axis=0, how='all')
    
    # แทนที่ค่า NaN ด้วยสตริงว่าง
    cleaned_df = cleaned_df.fillna('')
    
    # ตัดช่องว่างหน้าและหลังในคอลัมน์ที่เป็นสตริง
    string_columns = cleaned_df.select_dtypes(include=['object']).columns
    for col in string_columns:
        cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
    
    return cleaned_df


def get_dataframe_info(df: pd.DataFrame) -> dict:
    """
    ดึงข้อมูลสถิติของ DataFrame
    
    Args:
        df: DataFrame ที่ต้องการดูข้อมูล
        
    Returns:
        dict: ข้อมูลสถิติ
    """
    if df is None or df.empty:
        return {"error": "ไม่มีข้อมูล"}
    
    info = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": dict(df.dtypes),
        "memory_usage": df.memory_usage(deep=True).sum(),
        "null_counts": dict(df.isnull().sum()),
        "has_duplicates": df.duplicated().any(),
        "duplicate_count": df.duplicated().sum()
    }
    
    return info
