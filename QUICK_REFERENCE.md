# Quick Reference Card

## 🚀 Quick Start Commands

### Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup AWS IoT
./setup_aws_iot.sh

# Setup Bedrock & Lambda
./setup_bedrock.sh

# Verify setup
python verify_setup.py
```

### ESP32 Setup
```bash
# Convert certificates for ESP32
cd esp32
python convert_certificates.py ../certificates/AmazonRootCA1.pem root_ca
python convert_certificates.py ../certificates/certificate.pem.crt device_cert
python convert_certificates.py ../certificates/private.pem.key device_key
```

### Testing
```bash
# Test Python publisher
python device_publisher.py

# Test Python subscriber
python device_subscriber.py

# Test Bedrock integration
python bedrock/bedrock_integration.py

# Monitor Lambda logs
aws logs tail /aws/lambda/bedrock-iot-handler --follow
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `COMPLETE_EXECUTABLE_PLAN.md` | **START HERE** - Full step-by-step guide |
| `esp32/esp32_aws_iot.ino` | ESP32 Arduino sketch |
| `lambda/bedrock_iot_handler.py` | Lambda function for Bedrock |
| `setup_aws_iot.sh` | Automated AWS IoT setup |
| `setup_bedrock.sh` | Automated Bedrock setup |
| `.env` | Your configuration (create from env.example) |

## 🔧 Configuration Checklist

- [ ] AWS CLI configured (`aws configure`)
- [ ] Python dependencies installed
- [ ] AWS IoT Thing created
- [ ] Certificates downloaded to `certificates/`
- [ ] `.env` file configured
- [ ] ESP32 sketch configured with WiFi & certificates
- [ ] Bedrock model access enabled
- [ ] Lambda function deployed
- [ ] IoT Rule created

## 🔍 Troubleshooting Quick Fixes

### ESP32 Won't Connect
```bash
# Check Serial Monitor at 115200 baud
# Verify WiFi credentials
# Check certificates include \n characters
```

### Lambda Not Triggering
```bash
# Check IoT Rule is active
aws iot get-topic-rule --rule-name bedrock-analysis-rule

# Check Lambda logs
aws logs tail /aws/lambda/bedrock-iot-handler --follow
```

### Bedrock Access Denied
```bash
# Enable in AWS Console
# Go to: AWS Console → Bedrock → Model access
# Request access to Claude models
```

## 📊 Architecture Overview

```
ESP32 → AWS IoT → Lambda → Bedrock → Lambda → AWS IoT → ESP32
```

## 🎯 Common Topics

| Topic | Direction | Purpose |
|-------|-----------|---------|
| `devices/ESP32_Device/data` | ESP32 → Cloud | Sensor data |
| `devices/ESP32_Device/commands` | Cloud → ESP32 | Device commands |
| `devices/ESP32_Device/ai_responses` | Cloud → ESP32 | AI analysis |

## 📚 Documentation

- **Full Guide**: `COMPLETE_EXECUTABLE_PLAN.md`
- **ESP32 Setup**: `esp32/README_ESP32.md`
- **Main README**: `README.md`







