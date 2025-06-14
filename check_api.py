#!/usr/bin/env python3
import requests
import json

print("🔍 Checking API versions...")
try:
    response = requests.get('https://script.google.com/macros/s/AKfycbyzveWCcGt4GOQgVF8CUVF6I2Fzmz8x7Ds4BASTXPSh6VC1ErxTxv_KGjsaG7q4rNTLAw/exec', timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 Available versions:")
        for i, version_info in enumerate(data):
            print(f"  {i+1}. Version: {version_info.get('version_name')} (Code: {version_info.get('version_code')}) - {version_info.get('release', 'No date')}")
        
        print(f"\n🎯 Latest version from API: {data[0]['version_name']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")
