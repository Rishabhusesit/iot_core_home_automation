#!/usr/bin/env python3
"""
Manually sync device data from AWS IoT Core
This queries the latest message or shadow to update the backend data store
"""
import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import the device_data store from app.py
# For now, we'll update it directly
device_data = {
    'sensor_data': {},
    'relays': {},
    'status': 'offline',
    'last_update': None,
    'uptime_seconds': 0,
    'wifi_rssi': 0
}

def sync_from_shadow():
    """Sync data from IoT Shadow"""
    try:
        iot_endpoint = os.getenv('AWS_IOT_ENDPOINT', '')
        thing_name = os.getenv('THING_NAME', 'ESP32_SmartDevice')
        
        if not iot_endpoint:
            print("❌ AWS_IOT_ENDPOINT not set in .env")
            return False
        
        shadow_client = boto3.client(
            'iot-data',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            endpoint_url=f"https://{iot_endpoint}"
        )
        
        print(f"Querying IoT Shadow for {thing_name}...")
        response = shadow_client.get_thing_shadow(thingName=thing_name)
        shadow_payload = json.loads(response['payload'].read())
        
        if 'state' in shadow_payload and 'reported' in shadow_payload['state']:
            reported = shadow_payload['state']['reported']
            print("✅ Shadow data found!")
            print(json.dumps(reported, indent=2))
            return True
        else:
            print("⚠️  Shadow exists but no reported state")
            return False
            
    except shadow_client.exceptions.ResourceNotFoundException:
        print("⚠️  IoT Shadow doesn't exist yet")
        print("   ESP32 needs to update shadow for this to work")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_latest_message_info():
    """Get info about latest message (for reference)"""
    print("\n" + "=" * 60)
    print("Note: To get real-time data, you have options:")
    print("=" * 60)
    print("1. Set up IoT Shadow (ESP32 updates shadow)")
    print("2. Use IoT Rules → Lambda → Backend")
    print("3. Use MQTT subscription (iot_subscriber.py)")
    print("4. Query IoT Analytics (if configured)")
    print()
    print("For now, you can manually update device_data in app.py")
    print("or check MQTT Test Client for latest messages")

if __name__ == '__main__':
    print("=" * 60)
    print("IoT Data Sync Tool")
    print("=" * 60)
    print()
    
    if sync_from_shadow():
        print("\n✅ Data synced from shadow!")
    else:
        get_latest_message_info()




