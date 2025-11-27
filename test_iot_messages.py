#!/usr/bin/env python3
"""
Test script to verify ESP32 messages are being published to AWS IoT Core
"""
import boto3
import json
import time
from datetime import datetime

# AWS IoT Core client
iot_client = boto3.client('iot', region_name='us-east-1')
iot_data_client = boto3.client('iot-data', region_name='us-east-1', endpoint_url='https://aka6dphv0mv57-ats.iot.us-east-1.amazonaws.com')

THING_NAME = "ESP32_SmartDevice"
TOPIC_DATA = "devices/ESP32_SmartDevice/data"
TOPIC_STATUS = "devices/ESP32_SmartDevice/status"
TOPIC_ALERTS = "devices/ESP32_SmartDevice/alerts"

print("=" * 60)
print("AWS IoT Core Message Diagnostic Tool")
print("=" * 60)
print(f"\nThing Name: {THING_NAME}")
print(f"Endpoint: aka6dphv0mv57-ats.iot.us-east-1.amazonaws.com")
print(f"\nTopics to check:")
print(f"  - {TOPIC_DATA}")
print(f"  - {TOPIC_STATUS}")
print(f"  - {TOPIC_ALERTS}")

# Check thing status
print("\n" + "=" * 60)
print("1. Checking Thing Configuration...")
print("=" * 60)
try:
    thing_info = iot_client.describe_thing(thingName=THING_NAME)
    print(f"✅ Thing exists: {thing_info['thingName']}")
    
    principals = iot_client.list_thing_principals(thingName=THING_NAME)
    print(f"✅ Certificates attached: {len(principals['principals'])}")
    for cert in principals['principals']:
        cert_id = cert.split('/')[-1]
        policies = iot_client.list_principal_policies(principal=cert)
        policy_names = [p['policyName'] for p in policies['policies']]
        print(f"   - Certificate {cert_id[:16]}... has policies: {', '.join(policy_names)}")
except Exception as e:
    print(f"❌ Error checking thing: {e}")

# Check policy permissions
print("\n" + "=" * 60)
print("2. Checking IoT Policy Permissions...")
print("=" * 60)
try:
    policy = iot_client.get_policy(policyName='ESP32_SmartDevice_Policy')
    policy_doc = json.loads(policy['policyDocument'])
    print("✅ Policy found: ESP32_SmartDevice_Policy")
    print("\nPolicy statements:")
    for stmt in policy_doc['Statement']:
        print(f"   - {stmt['Effect']}: {', '.join(stmt['Action'])}")
        print(f"     Resource: {stmt['Resource']}")
except Exception as e:
    print(f"❌ Error checking policy: {e}")

# Test publishing a message
print("\n" + "=" * 60)
print("3. Testing Message Publishing...")
print("=" * 60)
try:
    test_message = {
        "device_id": THING_NAME,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "test": True,
        "message": "Test message from diagnostic script"
    }
    
    response = iot_data_client.publish(
        topic=TOPIC_DATA,
        qos=0,
        payload=json.dumps(test_message)
    )
    print(f"✅ Test message published to {TOPIC_DATA}")
    print(f"   Message: {json.dumps(test_message, indent=2)}")
except Exception as e:
    print(f"❌ Error publishing test message: {e}")

# Instructions for MQTT Test Client
print("\n" + "=" * 60)
print("4. MQTT Test Client Instructions")
print("=" * 60)
print("\nTo see messages in AWS IoT Console MQTT Test Client:")
print("\n1. Go to AWS IoT Console → Test → MQTT test client")
print("2. Subscribe to these topics:")
print(f"   - {TOPIC_DATA}")
print(f"   - {TOPIC_STATUS}")
print(f"   - {TOPIC_ALERTS}")
print("   OR use wildcard: devices/ESP32_SmartDevice/*")
print("\n3. Make sure you click 'Subscribe' and see the subscription active")
print("4. Check that the connection status shows 'Connected'")
print("\n5. If messages still don't appear:")
print("   - Check Serial Monitor on ESP32 - are messages being published?")
print("   - Verify the ESP32 is actually connected (check Serial Monitor)")
print("   - Try subscribing to the exact topic: devices/ESP32_SmartDevice/data")
print("   - Check CloudWatch Logs for IoT Core errors")

print("\n" + "=" * 60)
print("Diagnostic Complete!")
print("=" * 60)




