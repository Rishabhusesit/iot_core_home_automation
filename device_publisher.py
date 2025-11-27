"""
AWS IoT Device Publisher
Publishes sensor data to AWS IoT Core
"""
import json
import time
import random
from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config

class IoTDevicePublisher:
    def __init__(self):
        self.client = None
        self.setup_client()
    
    def setup_client(self):
        """Initialize and configure AWS IoT MQTT Client"""
        self.client = AWSIoTMQTTClient(config.CLIENT_ID)
        self.client.configureEndpoint(config.AWS_IOT_ENDPOINT, config.AWS_IOT_PORT)
        self.client.configureCredentials(
            config.ROOT_CA_PATH,
            config.PRIVATE_KEY_PATH,
            config.CERTIFICATE_PATH
        )
        
        # Configure connection settings
        self.client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
    
    def connect(self):
        """Connect to AWS IoT Core"""
        try:
            print(f"Connecting to AWS IoT Core at {config.AWS_IOT_ENDPOINT}...")
            self.client.connect()
            print("Connected successfully!")
            return True
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from AWS IoT Core"""
        if self.client:
            self.client.disconnect()
            print("Disconnected from AWS IoT Core")
    
    def publish_sensor_data(self, temperature=None, humidity=None, pressure=None):
        """Publish sensor data to AWS IoT Core"""
        if not temperature:
            temperature = round(random.uniform(20.0, 30.0), 2)
        if not humidity:
            humidity = round(random.uniform(40.0, 60.0), 2)
        if not pressure:
            pressure = round(random.uniform(980.0, 1020.0), 2)
        
        message = {
            "device_id": config.THING_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_data": {
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure
            }
        }
        
        try:
            self.client.publish(
                config.TOPIC_PUBLISH,
                json.dumps(message),
                config.QOS_LEVEL
            )
            print(f"Published: {json.dumps(message, indent=2)}")
            return True
        except Exception as e:
            print(f"Publish failed: {str(e)}")
            return False
    
    def publish_custom_message(self, topic, message):
        """Publish a custom message to a specific topic"""
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            self.client.publish(topic, message, config.QOS_LEVEL)
            print(f"Published to {topic}: {message}")
            return True
        except Exception as e:
            print(f"Publish failed: {str(e)}")
            return False


def main():
    """Main function to run the device publisher"""
    publisher = IoTDevicePublisher()
    
    if not publisher.connect():
        print("Failed to connect. Please check your configuration.")
        return
    
    try:
        print(f"Publishing sensor data to topic: {config.TOPIC_PUBLISH}")
        print("Press Ctrl+C to stop...\n")
        
        # Publish data every 5 seconds
        while True:
            publisher.publish_sensor_data()
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nStopping publisher...")
    finally:
        publisher.disconnect()


if __name__ == "__main__":
    main()







