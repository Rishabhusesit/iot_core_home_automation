# AWS IoT Project - Complete Setup Guide

A comprehensive AWS IoT Core project with **ESP32 hardware integration** and **AWS Bedrock AI** for intelligent sensor data analysis.

## 🎯 What's Included

- ✅ **ESP32 Hardware Integration** - Real sensor data collection with Arduino
- ✅ **AWS IoT Core** - Secure device-to-cloud communication
- ✅ **AWS Bedrock AI** - Intelligent sensor data analysis using Claude/Llama
- ✅ **Lambda Functions** - Serverless processing pipeline
- ✅ **Bidirectional Communication** - Device commands and AI responses

## 📖 Documentation

- **🚀 START HERE**: [`COMPLETE_EXECUTABLE_PLAN.md`](COMPLETE_EXECUTABLE_PLAN.md) - Full step-by-step guide with ESP32 and Bedrock
- **⚡ Quick Reference**: [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) - Command cheat sheet
- **📱 ESP32 Setup**: [`esp32/README_ESP32.md`](esp32/README_ESP32.md) - Hardware setup guide
- **🔧 Original Plan**: [`EXECUTABLE_PLAN.md`](EXECUTABLE_PLAN.md) - Python-only setup

---

## Original Python-Only Setup (Below)

For the complete setup with ESP32 hardware and AWS Bedrock, see [`COMPLETE_EXECUTABLE_PLAN.md`](COMPLETE_EXECUTABLE_PLAN.md).

A comprehensive AWS IoT Core project for connecting devices, publishing sensor data, and receiving commands using MQTT protocol.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

Before you begin, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
   ```bash
   aws --version
   aws configure
   ```
3. **Python 3.7+** installed
   ```bash
   python3 --version
   ```
4. **pip** package manager
5. **jq** (for JSON parsing in setup script)
   ```bash
   # macOS
   brew install jq
   
   # Linux
   sudo apt-get install jq
   ```

## 📁 Project Structure

```
aws_iot_project/
├── certificates/              # AWS IoT certificates (created during setup)
│   ├── AmazonRootCA1.pem
│   ├── certificate.pem.crt
│   └── private.pem.key
├── config.py                 # Configuration module
├── device_publisher.py       # Device that publishes sensor data
├── device_subscriber.py      # Device that subscribes to commands
├── device_bidirectional.py   # Device that both publishes and subscribes
├── setup_aws_iot.sh          # Automated AWS IoT setup script
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your environment variables (create this)
├── .gitignore
└── README.md                 # This file
```

## 🚀 Step-by-Step Setup

### Step 1: Clone or Navigate to Project

```bash
cd aws_iot_project
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Up AWS IoT Core

You have two options:

#### Option A: Automated Setup (Recommended)

```bash
# Make the script executable
chmod +x setup_aws_iot.sh

# Run the setup script
./setup_aws_iot.sh
```

The script will:
- Create an IoT Thing
- Generate certificates and keys
- Download Amazon Root CA
- Create and attach an IoT Policy
- Get your IoT Endpoint

#### Option B: Manual Setup via AWS Console

1. **Go to AWS IoT Console**
   - Navigate to [AWS IoT Console](https://console.aws.amazon.com/iot/)
   - Select your region

2. **Create a Thing**
   - Go to "Manage" → "Things"
   - Click "Create things"
   - Choose "Create single thing"
   - Enter a name (e.g., "MyIoTDevice")
   - Click "Next" and then "Create thing"

3. **Create Certificates**
   - Go to "Secure" → "Certificates"
   - Click "Create certificate"
   - Choose "One-click certificate creation"
   - Download:
     - Device certificate (certificate.pem.crt)
     - Private key (private.pem.key)
     - Public key (optional)
   - Activate the certificate
   - Save certificates to `certificates/` directory

4. **Download Root CA**
   ```bash
   mkdir -p certificates
   curl -o certificates/AmazonRootCA1.pem \
     https://www.amazontrust.com/repository/AmazonRootCA1.pem
   ```

5. **Create IoT Policy**
   - Go to "Secure" → "Policies"
   - Click "Create policy"
   - Name: `MyIoTDevice_Policy`
   - Policy document:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": ["iot:Connect"],
         "Resource": "arn:aws:iot:*:*:client/${iot:ClientId}"
       },
       {
         "Effect": "Allow",
         "Action": ["iot:Publish"],
         "Resource": "arn:aws:iot:*:*:topic/devices/MyIoTDevice/*"
       },
       {
         "Effect": "Allow",
         "Action": ["iot:Subscribe"],
         "Resource": "arn:aws:iot:*:*:topicfilter/devices/MyIoTDevice/*"
       },
       {
         "Effect": "Allow",
         "Action": ["iot:Receive"],
         "Resource": "arn:aws:iot:*:*:topic/devices/MyIoTDevice/*"
       }
     ]
   }
   ```
   - Click "Create"

6. **Attach Policy to Certificate**
   - Go to "Secure" → "Certificates"
   - Click on your certificate
   - Go to "Policies" tab
   - Click "Attach policies"
   - Select your policy and attach

7. **Attach Certificate to Thing**
   - Go to "Manage" → "Things"
   - Click on your thing
   - Go to "Security" tab
   - Click "Attach certificate"
   - Select your certificate

8. **Get IoT Endpoint**
   - Go to "Settings"
   - Copy the "Device data endpoint" (e.g., `xxxxx-ats.iot.us-east-1.amazonaws.com`)

### Step 4: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

Update the following in `.env`:
```env
AWS_IOT_ENDPOINT=your-endpoint-ats.iot.region.amazonaws.com
AWS_IOT_PORT=8883
THING_NAME=MyIoTDevice
ROOT_CA_PATH=certificates/AmazonRootCA1.pem
PRIVATE_KEY_PATH=certificates/private.pem.key
CERTIFICATE_PATH=certificates/certificate.pem.crt
TOPIC_PUBLISH=devices/MyIoTDevice/data
TOPIC_SUBSCRIBE=devices/MyIoTDevice/commands
CLIENT_ID=MyIoTDevice
QOS_LEVEL=1
```

## 💻 Usage

### 1. Device Publisher (Publish Sensor Data)

Publishes simulated sensor data to AWS IoT Core:

```bash
python device_publisher.py
```

This will:
- Connect to AWS IoT Core
- Publish sensor data (temperature, humidity, pressure) every 5 seconds
- Display published messages

### 2. Device Subscriber (Receive Commands)

Subscribes to topics and receives messages:

```bash
python device_subscriber.py
```

This will:
- Connect to AWS IoT Core
- Subscribe to the configured topic
- Display received messages

### 3. Bidirectional Device (Publish & Subscribe)

Both publishes sensor data and receives commands:

```bash
python device_bidirectional.py
```

This will:
- Connect to AWS IoT Core
- Subscribe to commands topic
- Publish sensor data every 5 seconds
- Handle incoming commands

## 🧪 Testing

### Test 1: Publish and View in AWS Console

1. Run the publisher:
   ```bash
   python device_publisher.py
   ```

2. View messages in AWS IoT Console:
   - Go to "Test" → "MQTT test client"
   - Subscribe to topic: `devices/MyIoTDevice/data`
   - You should see messages appearing

### Test 2: Send Command from AWS Console

1. Run the subscriber:
   ```bash
   python device_subscriber.py
   ```

2. In AWS IoT Console:
   - Go to "Test" → "MQTT test client"
   - Publish to topic: `devices/MyIoTDevice/commands`
   - Message:
   ```json
   {
     "command": "get_status",
     "timestamp": "2024-01-01T00:00:00Z"
   }
   ```

3. You should see the message in your subscriber terminal

### Test 3: Bidirectional Communication

1. Run the bidirectional device:
   ```bash
   python device_bidirectional.py
   ```

2. In AWS IoT Console, publish a command to see it received
3. Watch the terminal for both published and received messages

## 🔍 Troubleshooting

### Connection Issues

**Error: "Connection failed"**
- Verify your `.env` file has correct endpoint
- Check certificate paths are correct
- Ensure certificates are in the `certificates/` directory
- Verify your IoT endpoint is correct (should end with `.iot.region.amazonaws.com`)

**Error: "Certificate not found"**
- Ensure all certificate files exist in `certificates/` directory
- Check file permissions: `chmod 644 certificates/*.pem*`

**Error: "Policy not attached"**
- Verify the policy is attached to your certificate in AWS Console
- Check policy permissions match your topics

### Permission Issues

**Error: "Not authorized to perform: iot:Connect"**
- Check your IoT Policy allows `iot:Connect` action
- Verify the policy is attached to your certificate

**Error: "Not authorized to perform: iot:Publish"**
- Check your IoT Policy allows `iot:Publish` action
- Verify the topic ARN in policy matches your topic pattern

### Network Issues

**Error: "Connection timeout"**
- Check your internet connection
- Verify AWS IoT endpoint is accessible
- Check firewall settings (port 8883 should be open)

### Certificate Issues

**Error: "SSL/TLS handshake failed"**
- Verify Root CA certificate is correct
- Check certificate and private key match
- Ensure certificates haven't expired

## 📚 Additional Resources

- [AWS IoT Core Documentation](https://docs.aws.amazon.com/iot/)
- [AWS IoT Python SDK](https://github.com/aws/aws-iot-device-sdk-python)
- [MQTT Protocol](https://mqtt.org/)
- [AWS IoT Best Practices](https://docs.aws.amazon.com/iot/latest/developerguide/best-practices.html)

## 🔐 Security Notes

1. **Never commit certificates to version control**
   - Certificates are in `.gitignore`
   - Keep certificates secure and private

2. **Use IAM roles when possible**
   - For production, consider using IAM roles instead of access keys

3. **Rotate certificates regularly**
   - Set up certificate rotation for production devices

4. **Use least privilege principle**
   - Only grant necessary permissions in IoT policies

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Happy IoT Development! 🚀**

