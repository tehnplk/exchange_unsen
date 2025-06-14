@echo off
echo ========================================
echo  ExchangeUnsen Auto Update
echo ========================================
echo.

echo ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต...
ping -n 1 github.com >nul 2>&1
if errorlevel 1 (
    echo ❌ ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้
    echo กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ตแล้วลองใหม่
    pause
    exit /b 1
)
echo ✅ การเชื่อมต่ออินเทอร์เน็ตปกติ

echo.
echo กำลังสำรองไฟล์เก่า...
if exist "ExchangeUnsen.exe" (
    copy "ExchangeUnsen.exe" "ExchangeUnsen_backup.exe" >nul 2>&1
    echo ✅ สำรองไฟล์เก่าเป็น ExchangeUnsen_backup.exe
)

echo.
echo กำลังดาวน์โหลดเวอร์ชันใหม่...
powershell -Command "try { Invoke-WebRequest -Uri 'https://github.com/tehnplk/exchange_unsen/raw/master/dist/ExchangeUnsen.exe' -OutFile 'ExchangeUnsen_new.exe' -UserAgent 'Mozilla/5.0' } catch { Write-Host 'Error downloading file'; exit 1 }"

if not exist "ExchangeUnsen_new.exe" (
    echo ❌ ไม่สามารถดาวน์โหลดไฟล์ใหม่ได้
    echo กรุณาตรวจสอบการเชื่อมต่อหรือลองอีกครั้งในภายหลัง
    pause
    exit /b 1
)

echo ✅ ดาวน์โหลดเสร็จสิ้น

echo.
echo กำลังติดตั้งเวอร์ชันใหม่...
if exist "ExchangeUnsen.exe" (
    del "ExchangeUnsen.exe" >nul 2>&1
)
move "ExchangeUnsen_new.exe" "ExchangeUnsen.exe" >nul 2>&1

if exist "ExchangeUnsen.exe" (
    echo ✅ อัปเดตสำเร็จ!
    echo.
    echo คุณสามารถลบไฟล์สำรอง ExchangeUnsen_backup.exe ได้หากต้องการ
    echo.
    echo ต้องการเรียกใช้แอปพลิเคชันหรือไม่? (Y/N)
    set /p choice=กรุณาเลือก: 
    if /i "%choice%"=="Y" (
        start "" "ExchangeUnsen.exe"
    )
) else (
    echo ❌ เกิดข้อผิดพลาดในการติดตั้ง
    if exist "ExchangeUnsen_backup.exe" (
        echo กำลังกู้คืนไฟล์เก่า...
        move "ExchangeUnsen_backup.exe" "ExchangeUnsen.exe" >nul 2>&1
        echo ✅ กู้คืนไฟล์เก่าสำเร็จ
    )
)

echo.
pause
