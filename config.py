"""
AWS IoT Core Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# AWS IoT Core Endpoint
AWS_IOT_ENDPOINT = os.getenv('AWS_IOT_ENDPOINT', '')
AWS_IOT_PORT = int(os.getenv('AWS_IOT_PORT', '8883'))

# Thing Configuration
THING_NAME = os.getenv('THING_NAME', 'MyIoTDevice')

# Certificate paths
ROOT_CA_PATH = os.getenv('ROOT_CA_PATH', 'certificates/AmazonRootCA1.pem')
PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH', 'certificates/private.pem.key')
CERTIFICATE_PATH = os.getenv('CERTIFICATE_PATH', 'certificates/certificate.pem.crt')

# MQTT Topics
TOPIC_PUBLISH = os.getenv('TOPIC_PUBLISH', f'devices/{THING_NAME}/data')
TOPIC_SUBSCRIBE = os.getenv('TOPIC_SUBSCRIBE', f'devices/{THING_NAME}/commands')

# Client ID
CLIENT_ID = os.getenv('CLIENT_ID', THING_NAME)

# Message settings
QOS_LEVEL = int(os.getenv('QOS_LEVEL', '1'))







