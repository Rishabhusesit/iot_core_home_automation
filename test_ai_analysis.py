#!/usr/bin/env python3
"""
Test AI Analysis with the retrieved token
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:5000"
API_BASE = f"{BACKEND_URL}/api"

print("=" * 60)
print("Testing AI Analysis")
print("=" * 60)
print()

# Check if backend is running
try:
    response = requests.get(f"{API_BASE}/device/status", timeout=5)
    if response.status_code == 200:
        print("✅ Backend is running")
    else:
        print(f"⚠️  Backend returned status {response.status_code}")
        exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Backend is not running!")
    print("   Start it with: cd backend && python3 app.py")
    exit(1)

# Test AI analysis
print("\n🤖 Testing AI Analysis...")
print("   Sending sensor data to AgentCore...")

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
        print("✅ AI Analysis successful!")
        print()
        print("Analysis result:")
        print("-" * 60)
        analysis = data.get('analysis', 'No analysis returned')
        # Print first 500 chars
        print(analysis[:500])
        if len(analysis) > 500:
            print(f"\n... (truncated, total {len(analysis)} chars)")
        print("-" * 60)
        print()
        print("✅ Token is working! AI analysis is functional.")
    else:
        error_data = response.json()
        error_msg = error_data.get('error', 'Unknown error')
        print(f"❌ AI Analysis failed: {error_msg}")
        
        if 'GATEWAY_URL' in error_msg:
            print("\n💡 Fix: Set GATEWAY_URL in .env")
        elif 'BEARER_TOKEN' in error_msg or 'token' in error_msg.lower():
            print("\n💡 Fix: BEARER_TOKEN may be missing or invalid")
            print("   Re-run: python3 get_cognito_token.py")
        else:
            print(f"\n💡 Check backend logs for more details")
            
except requests.exceptions.Timeout:
    print("⚠️  Request timed out (AgentCore may be slow)")
    print("   This is normal - AgentCore can take 10-30 seconds")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 60)
print("Next Steps:")
print("=" * 60)
print("1. Open dashboard: http://localhost:5000")
print("2. Click '🔄 Analyze Now' button in AI Insights section")
print("3. Wait a few seconds for analysis to appear")
print()
print("If backend is not running, start it:")
print("  cd backend")
print("  python3 app.py")




