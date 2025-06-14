@echo off
echo ===============================================
echo    Excel Reader Application - Windows Batch
echo ===============================================
echo.

:: ตรวจสอบว่ามี Python หรือไม่
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python ไม่ได้ติดตั้งในระบบ
    echo กรุณาติดตั้ง Python ก่อนใช้งาน
    pause
    exit /b 1
)

:: เปลี่ยนไปยังโฟลเดอร์โปรเจกต์
cd /d "%~dp0"

:: ตรวจสอบว่ามี virtual environment หรือไม่
if not exist ".venv" (
    echo กำลังสร้าง virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: ไม่สามารถสร้าง virtual environment ได้
        pause
        exit /b 1
    )
)

:: เปิดใช้งาน virtual environment
echo กำลังเปิดใช้งาน virtual environment...
call .venv\Scripts\activate.bat

:: ตรวจสอบและติดตั้ง dependencies
if exist "requirements.txt" (
    echo กำลังตรวจสอบ dependencies...
    pip install -r requirements.txt --quiet
)

:: รันแอปพลิเคชัน
echo.
echo กำลังเริ่มต้นแอปพลิเคชัน...
echo.
python run_app.py

:: หยุดรอก่อนปิดหน้าต่าง
echo.
pause
