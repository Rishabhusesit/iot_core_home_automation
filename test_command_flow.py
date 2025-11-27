#!/usr/bin/env python3
"""
Test the command flow: Dashboard → Backend → AWS IoT → ESP32
"""
import requests
import time
import json

API_URL = "http://localhost:5000/api"

def test_relay_control():
    """Test relay control command flow"""
    print("=" * 60)
    print("Testing Command Flow: Dashboard → Backend → AWS IoT → ESP32")
    print("=" * 60)
    print()
    
    # Test 1: Turn Relay 1 ON
    print("Test 1: Turning Relay 1 ON...")
    try:
        response = requests.post(
            f"{API_URL}/device/relay",
            json={"relay": 1, "state": True},
            timeout=5
        )
        result = response.json()
        if result.get('success'):
            print(f"✅ Command sent successfully: {result.get('message')}")
        else:
            print(f"❌ Command failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    time.sleep(2)
    
    # Test 2: Turn Relay 1 OFF
    print("Test 2: Turning Relay 1 OFF...")
    try:
        response = requests.post(
            f"{API_URL}/device/relay",
            json={"relay": 1, "state": False},
            timeout=5
        )
        result = response.json()
        if result.get('success'):
            print(f"✅ Command sent successfully: {result.get('message')}")
        else:
            print(f"❌ Command failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("Next Steps:")
    print("1. Check AWS IoT MQTT Test Client for messages on:")
    print("   Topic: devices/ESP32_SmartDevice/commands")
    print("2. Check ESP32 Serial Monitor for command receipt")
    print("3. Verify relay physically toggles")
    print("=" * 60)

if __name__ == '__main__':
    test_relay_control()

