#!/usr/bin/env python3
"""
Update backend data store from AWS IoT Core
Queries IoT Shadow or recent messages to get latest ESP32 data
"""
import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# This will be imported by app.py
device_data_store = {
    'sensor_data': {},
    'relays': {},
    'status': 'offline',
    'last_update': None,
    'uptime_seconds': 0,
    'wifi_rssi': 0
}

def update_from_iot_shadow():
    """Update device data from IoT Shadow"""
    try:
        iot_endpoint = os.getenv('AWS_IOT_ENDPOINT', '')
        thing_name = os.getenv('THING_NAME', 'ESP32_SmartDevice')
        
        if not iot_endpoint:
            return False
        
        shadow_client = boto3.client(
            'iot-data',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            endpoint_url=f"https://{iot_endpoint}"
        )
        
        response = shadow_client.get_thing_shadow(thingName=thing_name)
        shadow_payload = json.loads(response['payload'].read())
        
        if 'state' in shadow_payload and 'reported' in shadow_payload['state']:
            reported = shadow_payload['state']['reported']
            
            if 'sensor_data' in reported:
                device_data_store['sensor_data'] = reported['sensor_data']
            if 'relays' in reported:
                device_data_store['relays'] = reported['relays']
            if 'uptime_seconds' in reported:
                device_data_store['uptime_seconds'] = reported['uptime_seconds']
            if 'wifi_rssi' in reported:
                device_data_store['wifi_rssi'] = reported['wifi_rssi']
            
            device_data_store['status'] = 'online'
            device_data_store['last_update'] = datetime.utcnow()
            return True
        
    except Exception as e:
        print(f"Shadow update failed: {e}")
        return False
    
    return False

if __name__ == '__main__':
    print("Updating device data from IoT Shadow...")
    if update_from_iot_shadow():
        print("✅ Updated successfully!")
        print(json.dumps(device_data_store, indent=2, default=str))
    else:
        print("⚠️  Update failed or shadow doesn't exist")
        print("Note: ESP32 needs to update shadow for this to work")




