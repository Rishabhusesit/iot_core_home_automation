#!/usr/bin/env python3
"""
Simple IoT Data Poller
Uses AWS IoT Data Plane API to query recent messages
No MQTT subscription needed - simpler for quick testing
"""
import boto3
import json
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# AWS IoT Data client
iot_data = boto3.client(
    'iot-data',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    endpoint_url=f"https://{os.getenv('AWS_IOT_ENDPOINT', 'aka6dphv0mv57-ats.iot.us-east-1.amazonaws.com')}"
)

THING_NAME = os.getenv('THING_NAME', 'ESP32_SmartDevice')
DATA_TOPIC = f'devices/{THING_NAME}/data'

# In-memory data store (shared with app.py)
device_data_store = {
    'sensor_data': {},
    'relays': {},
    'status': 'offline',
    'last_update': None,
    'uptime_seconds': 0,
    'wifi_rssi': 0
}

def get_device_data():
    """Get latest device data from store"""
    return device_data_store.copy()

def poll_iot_messages():
    """
    Poll IoT Core for recent messages
    Note: This is a simplified approach. For real-time updates,
    use IoT Rules → Lambda or MQTT subscription.
    """
    print("📡 Polling IoT Core for messages...")
    print(f"   Topic: {DATA_TOPIC}")
    print("   (Note: For real-time updates, use IoT Rules or MQTT subscription)")
    print()

if __name__ == '__main__':
    print("=" * 60)
    print("Simple IoT Data Poller")
    print("=" * 60)
    print()
    print("This script demonstrates how to access IoT data.")
    print("For real-time updates, use one of these approaches:")
    print()
    print("1. IoT Rules → Lambda → Backend")
    print("2. MQTT Subscription (iot_subscriber.py)")
    print("3. IoT Shadow (device state)")
    print()
    print("Current device data store:")
    print(json.dumps(device_data_store, indent=2, default=str))
    print()
    print("To get real-time data, the backend should:")
    print("- Use IoT Rules to forward messages to a Lambda")
    print("- Or use MQTT subscription (requires AWSIoTPythonSDK)")
    print("- Or query IoT Shadow for device state")
    print()




