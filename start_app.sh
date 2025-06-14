#!/bin/bash

echo "==============================================="
echo "    Excel Reader Application - Linux/Mac"
echo "==============================================="
echo

# ตรวจสอบว่ามี Python หรือไม่
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 ไม่ได้ติดตั้งในระบบ"
    echo "กรุณาติดตั้ง Python3 ก่อนใช้งาน"
    exit 1
fi

# เปลี่ยนไปยังโฟลเดอร์โปรเจกต์
cd "$(dirname "$0")"

# ตรวจสอบว่ามี virtual environment หรือไม่
if [ ! -d ".venv" ]; then
    echo "กำลังสร้าง virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: ไม่สามารถสร้าง virtual environment ได้"
        exit 1
    fi
fi

# เปิดใช้งาน virtual environment
echo "กำลังเปิดใช้งาน virtual environment..."
source .venv/bin/activate

# ตรวจสอบและติดตั้ง dependencies
if [ -f "requirements.txt" ]; then
    echo "กำลังตรวจสอบ dependencies..."
    pip install -r requirements.txt --quiet
fi

# รันแอปพลิเคชัน
echo
echo "กำลังเริ่มต้นแอปพลิเคชัน..."
echo
python run_app.py

echo
read -p "กด Enter เพื่อปิดโปรแกรม..."
