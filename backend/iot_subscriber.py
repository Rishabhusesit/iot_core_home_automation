"""
IoT Message Subscriber
Subscribes to AWS IoT topics and updates backend data store
"""
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import threading
import time

load_dotenv()

# Import device_data from app (in production, use database)
# For now, we'll use a shared dictionary
device_data_store = {}

class IoTSubscriber:
    def __init__(self):
        self.client = None
        self.setup_client()
    
    def setup_client(self):
        """Initialize AWS IoT MQTT Client"""
        from config import (
            AWS_IOT_ENDPOINT, AWS_IOT_PORT,
            ROOT_CA_PATH, PRIVATE_KEY_PATH, CERTIFICATE_PATH,
            CLIENT_ID
        )
        
        self.client = AWSIoTMQTTClient(f"{CLIENT_ID}_subscriber")
        self.client.configureEndpoint(AWS_IOT_ENDPOINT, AWS_IOT_PORT)
        self.client.configureCredentials(
            ROOT_CA_PATH,
            PRIVATE_KEY_PATH,
            CERTIFICATE_PATH
        )
        
        self.client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.client.configureOfflinePublishQueueing(-1)
        self.client.configureDrainingFrequency(2)
        self.client.configureConnectDisconnectTimeout(10)
        self.client.configureMQTTOperationTimeout(5)
    
    def connect(self):
        """Connect to AWS IoT Core"""
        from config import AWS_IOT_ENDPOINT
        
        try:
            print(f"Connecting to AWS IoT Core at {AWS_IOT_ENDPOINT}...")
            self.client.connect()
            print("✅ Connected to AWS IoT Core!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def message_callback(self, client, userdata, message):
        """Handle incoming MQTT messages"""
        try:
            payload = json.loads(message.payload.decode('utf-8'))
            topic = message.topic
            
            print(f"\n📨 Message received on {topic}")
            
            # Update device data store based on topic
            if 'data' in topic:
                # Sensor data
                if 'sensor_data' in payload:
                    device_data_store['sensor_data'] = payload['sensor_data']
                if 'relays' in payload:
                    device_data_store['relays'] = payload['relays']
                device_data_store['last_update'] = datetime.utcnow()
                device_data_store['uptime_seconds'] = payload.get('uptime_seconds', 0)
                device_data_store['wifi_rssi'] = payload.get('wifi_rssi', 0)
                device_data_store['status'] = 'online'
                
            elif 'status' in topic:
                # Device status
                device_data_store['status'] = payload.get('status', 'unknown')
                
            elif 'alerts' in topic:
                # Alerts
                if 'alerts' not in device_data_store:
                    device_data_store['alerts'] = []
                device_data_store['alerts'].append(payload)
                # Keep only last 50 alerts
                if len(device_data_store['alerts']) > 50:
                    device_data_store['alerts'] = device_data_store['alerts'][-50:]
            
            print(f"✅ Updated device data store")
            
        except Exception as e:
            print(f"❌ Error processing message: {str(e)}")
    
    def subscribe(self, topics):
        """Subscribe to multiple topics"""
        from config import QOS_LEVEL
        
        for topic in topics:
            try:
                self.client.subscribe(topic, QOS_LEVEL, self.message_callback)
                print(f"✅ Subscribed to: {topic}")
            except Exception as e:
                print(f"❌ Failed to subscribe to {topic}: {str(e)}")
    
    def run(self):
        """Run subscriber"""
        from config import THING_NAME
        
        if not self.connect():
            return
        
        # Subscribe to all relevant topics
        topics = [
            f'devices/{THING_NAME}/data',
            f'devices/{THING_NAME}/status',
            f'devices/{THING_NAME}/alerts',
            f'devices/{THING_NAME}/data/relay',
        ]
        
        self.subscribe(topics)
        
        print("\n✅ IoT Subscriber running. Waiting for messages...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping subscriber...")
            self.client.disconnect()

def get_device_data():
    """Get current device data (for use by Flask app)"""
    return device_data_store

if __name__ == "__main__":
    subscriber = IoTSubscriber()
    subscriber.run()







