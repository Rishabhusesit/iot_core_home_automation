"""
AWS IoT Bidirectional Device
Can both publish and subscribe to AWS IoT Core
"""
import json
import time
import random
from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config

class IoTBidirectionalDevice:
    def __init__(self):
        self.client = None
        self.setup_client()
        self.running = False
    
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
        self.client.configureOfflinePublishQueueing(-1)
        self.client.configureDrainingFrequency(2)
        self.client.configureConnectDisconnectTimeout(10)
        self.client.configureMQTTOperationTimeout(5)
    
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
    
    def message_callback(self, client, userdata, message):
        """Callback function for received messages"""
        try:
            payload = json.loads(message.payload.decode('utf-8'))
            print(f"\n{'='*60}")
            print(f"📨 Received Message")
            print(f"Topic: {message.topic}")
            print(f"QoS: {message.qos}")
            print(f"Payload:")
            print(json.dumps(payload, indent=2))
            print(f"{'='*60}\n")
            
            # Example: Respond to commands
            if 'command' in payload:
                self.handle_command(payload['command'], payload)
        except json.JSONDecodeError:
            print(f"\n{'='*60}")
            print(f"📨 Received Message (raw)")
            print(f"Topic: {message.topic}")
            print(f"Payload: {message.payload.decode('utf-8')}")
            print(f"{'='*60}\n")
    
    def handle_command(self, command, payload):
        """Handle incoming commands"""
        print(f"Executing command: {command}")
        # Add your command handling logic here
        if command == "get_status":
            self.publish_status()
        elif command == "set_interval":
            if 'interval' in payload:
                print(f"Setting publish interval to {payload['interval']} seconds")
    
    def subscribe(self, topic=None):
        """Subscribe to a topic"""
        if not topic:
            topic = config.TOPIC_SUBSCRIBE
        
        try:
            self.client.subscribe(topic, config.QOS_LEVEL, self.message_callback)
            print(f"Subscribed to topic: {topic}")
            return True
        except Exception as e:
            print(f"Subscribe failed: {str(e)}")
            return False
    
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
            print(f"📤 Published: Temperature={temperature}°C, Humidity={humidity}%, Pressure={pressure}hPa")
            return True
        except Exception as e:
            print(f"Publish failed: {str(e)}")
            return False
    
    def publish_status(self):
        """Publish device status"""
        status = {
            "device_id": config.THING_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "online",
            "uptime": "active"
        }
        self.client.publish(
            f"{config.TOPIC_PUBLISH}/status",
            json.dumps(status),
            config.QOS_LEVEL
        )
        print("📤 Published device status")
    
    def run(self, publish_interval=5):
        """Run the bidirectional device"""
        if not self.connect():
            print("Failed to connect. Please check your configuration.")
            return
        
        # Subscribe to commands
        self.subscribe()
        
        self.running = True
        try:
            print(f"\n{'='*60}")
            print("🚀 Device Running in Bidirectional Mode")
            print(f"📤 Publishing to: {config.TOPIC_PUBLISH}")
            print(f"📥 Subscribing to: {config.TOPIC_SUBSCRIBE}")
            print(f"⏱️  Publish interval: {publish_interval} seconds")
            print(f"{'='*60}\n")
            print("Press Ctrl+C to stop...\n")
            
            # Publish data periodically
            while self.running:
                self.publish_sensor_data()
                time.sleep(publish_interval)
        
        except KeyboardInterrupt:
            print("\nStopping device...")
        finally:
            self.disconnect()


def main():
    """Main function"""
    device = IoTBidirectionalDevice()
    device.run(publish_interval=5)


if __name__ == "__main__":
    main()







