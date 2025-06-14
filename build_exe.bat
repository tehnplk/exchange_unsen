@echo off
echo ========================================
echo        ExchangeUnsen Build Script
echo ========================================
echo.

echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [2/3] Building executable with PyInstaller...
pyinstaller ExchangeUnsen.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [3/3] Build completed successfully!
    echo ========================================
    echo Output file: dist\ExchangeUnsen.exe
    echo File size: 
    dir dist\ExchangeUnsen.exe | find "ExchangeUnsen.exe"
    echo ========================================
    echo.
    echo Press any key to exit...
    pause >nul
) else (
    echo.
    echo [ERROR] Build failed!
    echo ========================================
    pause
)
