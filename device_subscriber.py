"""
AWS IoT Device Subscriber
Subscribes to topics and receives messages from AWS IoT Core
"""
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config

class IoTDeviceSubscriber:
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
            print(f"Topic: {message.topic}")
            print(f"QoS: {message.qos}")
            print(f"Message:")
            print(json.dumps(payload, indent=2))
            print(f"{'='*60}\n")
        except json.JSONDecodeError:
            print(f"\n{'='*60}")
            print(f"Topic: {message.topic}")
            print(f"QoS: {message.qos}")
            print(f"Message (raw): {message.payload.decode('utf-8')}")
            print(f"{'='*60}\n")
    
    def subscribe(self, topic=None):
        """Subscribe to a topic"""
        if not topic:
            topic = config.TOPIC_SUBSCRIBE
        
        try:
            self.client.subscribe(topic, config.QOS_LEVEL, self.message_callback)
            print(f"Subscribed to topic: {topic}")
            print("Waiting for messages... (Press Ctrl+C to stop)\n")
            return True
        except Exception as e:
            print(f"Subscribe failed: {str(e)}")
            return False
    
    def subscribe_multiple(self, topics):
        """Subscribe to multiple topics"""
        for topic in topics:
            try:
                self.client.subscribe(topic, config.QOS_LEVEL, self.message_callback)
                print(f"Subscribed to topic: {topic}")
            except Exception as e:
                print(f"Failed to subscribe to {topic}: {str(e)}")
        print("\nWaiting for messages... (Press Ctrl+C to stop)\n")


def main():
    """Main function to run the device subscriber"""
    subscriber = IoTDeviceSubscriber()
    
    if not subscriber.connect():
        print("Failed to connect. Please check your configuration.")
        return
    
    try:
        # Subscribe to the configured topic
        subscriber.subscribe()
        
        # Keep the script running
        import time
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping subscriber...")
    finally:
        subscriber.disconnect()


if __name__ == "__main__":
    main()







