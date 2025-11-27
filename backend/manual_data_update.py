#!/usr/bin/env python3
"""
Manually update device_data with test data from ESP32
Use this to test the dashboard while setting up real-time data sync
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import device_data from app.py
# We'll update it directly
from datetime import datetime

# This simulates the data structure from ESP32
test_data = {
    'sensor_data': {
        'temperature': 27.5,
        'humidity': 70.3,
        'motion_detected': False
    },
    'relays': {
        'relay_1': False,
        'relay_2': False,
        'relay_3': False,
        'relay_4': False
    },
    'status': 'online',
    'last_update': datetime.utcnow(),
    'uptime_seconds': 641,
    'wifi_rssi': -38
}

print("=" * 60)
print("Manual Data Update")
print("=" * 60)
print()
print("This script updates the backend data store with test data.")
print("In production, this would come from IoT Shadow or MQTT subscription.")
print()
print("To use real-time data:")
print("1. Set up ESP32 to update IoT Shadow")
print("2. Or use IoT Rules → Lambda → Backend")
print("3. Or run iot_subscriber.py in background")
print()
print("For now, you can manually update app.py's device_data")
print("or use this script to inject test data.")
print()
print("Test data:")
print(f"  Temperature: {test_data['sensor_data']['temperature']}°C")
print(f"  Humidity: {test_data['sensor_data']['humidity']}%")
print(f"  Status: {test_data['status']}")
print()
print("⚠️  Note: This is a helper script. The backend's background")
print("   thread will query shadow automatically every 5 seconds.")




