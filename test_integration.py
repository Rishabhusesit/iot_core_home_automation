#!/usr/bin/env python3
"""
Quick Integration Test Script
Tests the complete flow: ESP32 → IoT → Backend → AgentCore
"""
import requests
import json
import time
import sys

BACKEND_URL = "http://localhost:5000"
API_BASE = f"{BACKEND_URL}/api"

def test_backend_running():
    """Test if backend is running"""
    print("1. Testing backend connection...")
    try:
        response = requests.get(f"{API_BASE}/device/status", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running!")
            data = response.json()
            print(f"   Device status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"   ⚠️  Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend is not running!")
        print("   Start it with: cd backend && python3 app.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_device_status():
    """Test device status endpoint"""
    print("\n2. Testing device status endpoint...")
    try:
        response = requests.get(f"{API_BASE}/device/status")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Device status retrieved!")
            print(f"   Status: {data.get('status')}")
            sensor_data = data.get('sensor_data', {})
            if sensor_data:
                print(f"   Temperature: {sensor_data.get('temperature', 'N/A')}°C")
                print(f"   Humidity: {sensor_data.get('humidity', 'N/A')}%")
            else:
                print("   ⚠️  No sensor data yet (ESP32 may not be connected)")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_ai_analysis():
    """Test AI analysis endpoint"""
    print("\n3. Testing AI analysis endpoint...")
    
    # Check if AgentCore is configured
    test_data = {
        "sensor_data": {
            "temperature": 27.5,
            "humidity": 70.3,
            "motion_detected": False
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/ai/analyze",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ AI analysis successful!")
            print(f"   Analysis: {data.get('analysis', 'N/A')[:100]}...")
            return True
        elif response.status_code == 500:
            error_data = response.json()
            error_msg = error_data.get('error', 'Unknown error')
            if 'GATEWAY_URL' in error_msg:
                print("   ⚠️  AgentCore Gateway not configured")
                print("   Set GATEWAY_URL in .env file")
            elif 'Bearer' in error_msg or 'token' in error_msg.lower():
                print("   ⚠️  Bearer token not configured")
                print("   Set BEARER_TOKEN in .env file")
            else:
                print(f"   ⚠️  AI analysis failed: {error_msg}")
            return False
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("   ⚠️  Request timed out (AgentCore may be slow)")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_relay_control():
    """Test relay control endpoint"""
    print("\n4. Testing relay control endpoint...")
    try:
        test_command = {
            "relay": 1,
            "state": True
        }
        response = requests.post(
            f"{API_BASE}/device/relay",
            json=test_command,
            timeout=5
        )
        
        if response.status_code == 200:
            print("   ✅ Relay command sent successfully!")
            print("   (Check ESP32 Serial Monitor to verify)")
            return True
        else:
            print(f"   ⚠️  Relay command returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("ESP32 IoT Integration Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Backend running
    results.append(("Backend Running", test_backend_running()))
    
    if not results[0][1]:
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd backend")
        print("   python3 app.py")
        sys.exit(1)
    
    # Test 2: Device status
    results.append(("Device Status", test_device_status()))
    
    # Test 3: AI Analysis
    results.append(("AI Analysis", test_ai_analysis()))
    
    # Test 4: Relay Control
    results.append(("Relay Control", test_relay_control()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nResults: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Integration is working!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nNext steps:")
        print("1. Ensure ESP32 is connected and publishing")
        print("2. Configure AgentCore Gateway URL in .env")
        print("3. Set BEARER_TOKEN in .env (Cognito IdToken)")

if __name__ == '__main__':
    main()




