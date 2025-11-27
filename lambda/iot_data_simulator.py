"""
Periodic IoT data simulator Lambda.
Publishes synthetic readings to AWS IoT Core so downstream services receive data.
"""

import json
import os
import random
from datetime import datetime, timezone

import boto3

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
THING_NAME = os.environ.get("THING_NAME", "ESP32_SmartDevice")
IOT_TOPIC = os.environ.get("IOT_TOPIC", f"devices/{THING_NAME}/data")

iot_data = boto3.client("iot-data", region_name=AWS_REGION)


def _payload():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "device_id": THING_NAME,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "sensor_data": {
            "temperature": round(random.uniform(22.0, 29.0), 2),
            "humidity": round(random.uniform(40.0, 65.0), 2),
            "pressure": round(random.uniform(995.0, 1015.0), 2),
            "motion": random.choice([True, False]),
        },
        "relays": {
            "relay1": random.choice(["on", "off"]),
            "relay2": random.choice(["on", "off"]),
            "relay3": random.choice(["on", "off"]),
            "relay4": random.choice(["on", "off"]),
        },
        "uptime_seconds": random.randint(0, 86400),
        "wifi_rssi": random.randint(-78, -45),
    }


def lambda_handler(event, context):
    payload = _payload()
    iot_data.publish(topic=IOT_TOPIC, qos=0, payload=json.dumps(payload))
    return {"statusCode": 200, "message": "Published IoT payload", "payload": payload}

