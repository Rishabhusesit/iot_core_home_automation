# Complete Integration Guide
## Hardware to Web Interface - End-to-End Setup

This guide covers **everything** from hardware assembly to web dashboard, AI integration, and backend services.

---

## 📋 Table of Contents

1. [Hardware Setup](#1-hardware-setup)
2. [ESP32 Programming](#2-esp32-programming)
3. [AWS IoT Core Setup](#3-aws-iot-core-setup)
4. [AWS Bedrock AI Setup](#4-aws-bedrock-ai-setup)
5. [Backend API Setup](#5-backend-api-setup)
6. [Web Dashboard Setup](#6-web-dashboard-setup)
7. [Complete Integration](#7-complete-integration)
8. [Testing & Verification](#8-testing--verification)

---

## 1. Hardware Setup

### 1.1 Gather Components

**Essential:**
- ESP32 Development Board
- Breadboard (830 points)
- Jumper Wires (Male-to-Male, Male-to-Female)
- USB Cable

**Sensors:**
- DHT22 Temperature/Humidity Sensor
- PIR Motion Sensor (HC-SR501)

**Actuators:**
- 4-Channel Relay Module (5V)
- LEDs (5mm, various colors)
- Resistors (220Ω, 10kΩ)

**Power:**
- 5V Power Supply (for relay module)

### 1.2 Wiring

Follow the detailed wiring guide: [`hardware/HARDWARE_SETUP.md`](hardware/HARDWARE_SETUP.md)

**Quick Reference:**
```
DHT22 DATA  → GPIO 4
PIR OUT     → GPIO 5
Relay IN1   → GPIO 18
Relay IN2   → GPIO 19
Relay IN3   → GPIO 21
Relay IN4   → GPIO 22
LED 1       → GPIO 25
LED 2       → GPIO 26
LED Motion  → GPIO 27
```

### 1.3 Test Hardware

1. **Test DHT22:**
   - Upload simple test code
   - Verify temperature/humidity readings

2. **Test PIR:**
   - Wave hand in front of sensor
   - Verify motion detection

3. **Test Relays:**
   - Toggle each relay
   - Verify clicking sound
   - Test with connected devices

4. **Test LEDs:**
   - Toggle each LED
   - Verify they light up

---

## 2. ESP32 Programming

### 2.1 Install Arduino IDE & ESP32 Support

1. **Download Arduino IDE:**
   - Visit: https://www.arduino.cc/en/software
   - Install Arduino IDE 2.x

2. **Install ESP32 Board Support:**
   - File → Preferences
   - Add URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager
   - Search "ESP32" and install

3. **Install Libraries:**
   - Sketch → Include Library → Manage Libraries
   - Install:
     - PubSubClient (v2.8.0+)
     - ArduinoJson (v6.19.0+)
     - DHT sensor library

### 2.2 Configure ESP32 Sketch

1. **Open Sketch:**
   ```bash
   # Open in Arduino IDE
   esp32/esp32_complete_hardware.ino
   ```

2. **Update WiFi:**
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```

3. **Update AWS IoT:**
   ```cpp
   const char* aws_iot_endpoint = "YOUR_ENDPOINT.iot.REGION.amazonaws.com";
   const char* thing_name = "ESP32_SmartDevice";
   ```

4. **Add Certificates:**
   - Use certificate converter:
     ```bash
     cd esp32
     python convert_certificates.py ../certificates/AmazonRootCA1.pem root_ca
     python convert_certificates.py ../certificates/certificate.pem.crt device_cert
     python convert_certificates.py ../certificates/private.pem.key device_key
     ```
   - Copy output into sketch

### 2.3 Upload to ESP32

1. **Select Board:**
   - Tools → Board → ESP32 Dev Module

2. **Select Port:**
   - Tools → Port → (your ESP32 port)

3. **Upload:**
   - Click Upload button
   - Wait for completion

4. **Open Serial Monitor:**
   - Tools → Serial Monitor (115200 baud)
   - Verify connection messages

---

## 3. AWS IoT Core Setup

### 3.1 Automated Setup

```bash
# Run setup script
chmod +x setup_aws_iot.sh
./setup_aws_iot.sh
```

**Provide:**
- AWS Region (e.g., `us-east-1`)
- Thing Name (e.g., `ESP32_SmartDevice`)

**What it creates:**
- IoT Thing
- Certificates
- IoT Policy
- Downloads Root CA

### 3.2 Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env
nano .env
```

**Update:**
```env
AWS_IOT_ENDPOINT=your-endpoint-ats.iot.region.amazonaws.com
THING_NAME=ESP32_SmartDevice
AWS_REGION=us-east-1
```

### 3.3 Verify Connection

1. **Check ESP32 Serial Monitor:**
   - Should show "Connected to AWS IoT Core!"

2. **Check AWS IoT Console:**
   - Go to Test → MQTT test client
   - Subscribe to: `devices/ESP32_SmartDevice/data`
   - Should see messages every 5 seconds

---

## 4. AWS Bedrock AI Setup

### 4.1 Enable Bedrock Access

1. **Go to AWS Console:**
   - Navigate to: https://console.aws.amazon.com/bedrock/
   - Select your region

2. **Request Model Access:**
   - Click "Model access"
   - Click "Request model access"
   - Select: Claude 3 Sonnet (or Haiku)
   - Click "Save requests"
   - Wait for approval (usually instant)

### 4.2 Automated Setup

```bash
# Run Bedrock setup script
chmod +x setup_bedrock.sh
./setup_bedrock.sh
```

**Provide:**
- AWS Region (same as IoT)
- Thing Name (same as IoT)
- Model choice (1-4)

**What it creates:**
- IAM Role for Lambda
- Lambda function
- IoT Rule
- Lambda permissions

### 4.3 Verify Bedrock

```bash
# Test Bedrock integration
python bedrock/bedrock_integration.py
```

**Expected:** AI analysis of sample sensor data

---

## 5. Backend API Setup

### 5.1 Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5.2 Configure Backend

Update `.env`:
```env
AWS_REGION=us-east-1
AWS_IOT_ENDPOINT=your-endpoint-ats.iot.region.amazonaws.com
THING_NAME=ESP32_SmartDevice
```

### 5.3 Start Backend Server

**Option A: Direct Flask Server**
```bash
cd backend
python app.py
```

**Option B: With IoT Subscriber (Recommended)**
```bash
# Terminal 1: Start IoT subscriber
cd backend
python iot_subscriber.py

# Terminal 2: Start Flask API
python app.py
```

**Expected Output:**
```
============================================================
ESP32 IoT Backend API Server
============================================================
Device: ESP32_SmartDevice
IoT Endpoint: xxxxx-ats.iot.us-east-1.amazonaws.com
Command Topic: devices/ESP32_SmartDevice/commands
============================================================

Starting server on http://localhost:5000
Dashboard: http://localhost:5000
```

### 5.4 Test API

```bash
# Test device status endpoint
curl http://localhost:5000/api/device/status

# Test relay control
curl -X POST http://localhost:5000/api/device/relay \
  -H "Content-Type: application/json" \
  -d '{"relay": 1, "state": true}'
```

---

## 6. Web Dashboard Setup

### 6.1 Access Dashboard

1. **Open Browser:**
   - Navigate to: http://localhost:5000
   - Dashboard should load automatically

2. **Verify Connection:**
   - Check device status (should show "Online" if ESP32 connected)
   - Verify sensor data appears
   - Check charts update

### 6.2 Dashboard Features

**Real-time Monitoring:**
- Temperature & Humidity charts
- Motion detection alerts
- Device status and uptime
- WiFi signal strength

**Control:**
- Toggle relays (4 channels)
- Send custom commands
- View activity log

**AI Insights:**
- Real-time AI analysis
- Recommendations
- Anomaly detection

### 6.3 Customize Dashboard

Edit `web/dashboard.html`:
- Change colors/styling
- Add more charts
- Customize layout
- Add new features

---

## 7. Complete Integration

### 7.1 Data Flow

```
ESP32 Hardware
    ↓ (MQTT/TLS)
AWS IoT Core
    ↓ (IoT Rules)
AWS Lambda → AWS Bedrock
    ↓ (AI Analysis)
AWS Lambda → AWS IoT Core
    ↓ (MQTT)
Backend API (IoT Subscriber)
    ↓ (WebSocket/HTTP)
Web Dashboard
```

### 7.2 Start All Services

**Terminal 1: IoT Subscriber**
```bash
cd backend
python iot_subscriber.py
```

**Terminal 2: Flask API**
```bash
cd backend
python app.py
```

**Terminal 3: Monitor ESP32**
```bash
# Use Serial Monitor in Arduino IDE
# Or use: screen /dev/ttyUSB0 115200
```

### 7.3 Verify Integration

1. **ESP32 → AWS IoT:**
   - Check Serial Monitor: "Published sensor data"
   - Check AWS Console: Messages in MQTT test client

2. **AWS IoT → Lambda → Bedrock:**
   - Check Lambda logs:
     ```bash
     aws logs tail /aws/lambda/bedrock-iot-handler --follow
     ```
   - Should see Bedrock invocations

3. **Bedrock → AWS IoT → Backend:**
   - Check IoT subscriber terminal
   - Should see AI responses

4. **Backend → Web Dashboard:**
   - Open http://localhost:5000
   - Should see real-time updates
   - AI insights should appear

---

## 8. Testing & Verification

### 8.1 Hardware Tests

**Test 1: Sensor Reading**
- Wave hand in front of PIR
- Check dashboard: Motion alert should appear
- Check Serial Monitor: Motion detected message

**Test 2: Relay Control**
- Toggle relay in dashboard
- Check ESP32: Relay should click
- Check connected device: Should turn on/off
- Check Serial Monitor: Relay state message

**Test 3: Temperature/Humidity**
- Check dashboard: Real-time values
- Check charts: Historical data
- Verify values are reasonable

### 8.2 Integration Tests

**Test 1: End-to-End Flow**
1. ESP32 publishes sensor data
2. AWS IoT receives message
3. Lambda triggers Bedrock
4. AI analysis published back
5. Backend receives AI response
6. Dashboard shows AI insights

**Test 2: Relay Control from Dashboard**
1. Toggle relay in dashboard
2. Command sent to backend API
3. Backend publishes to AWS IoT
4. ESP32 receives command
5. Relay toggles
6. ESP32 publishes state update
7. Dashboard updates

### 8.3 Troubleshooting

**ESP32 Not Connecting:**
- ✅ Check WiFi credentials
- ✅ Verify certificates
- ✅ Check IoT endpoint
- ✅ Verify IoT Policy

**Dashboard Not Updating:**
- ✅ Check backend API is running
- ✅ Check IoT subscriber is running
- ✅ Verify ESP32 is publishing
- ✅ Check browser console for errors

**AI Insights Not Appearing:**
- ✅ Check Bedrock access enabled
- ✅ Verify Lambda function deployed
- ✅ Check Lambda logs
- ✅ Verify IoT Rule is active

**Relay Not Responding:**
- ✅ Check wiring
- ✅ Verify relay module power
- ✅ Check GPIO pins
- ✅ Test relay manually

---

## 🎯 Quick Start Checklist

- [ ] Hardware assembled and tested
- [ ] ESP32 programmed and connected
- [ ] AWS IoT Core setup complete
- [ ] Certificates configured
- [ ] ESP32 connects to AWS IoT
- [ ] Bedrock access enabled
- [ ] Lambda function deployed
- [ ] Backend API running
- [ ] IoT subscriber running
- [ ] Web dashboard accessible
- [ ] All components communicating
- [ ] End-to-end flow working

---

## 📊 Architecture Diagram

```
┌─────────────────┐
│   ESP32 Device  │
│  - DHT22        │
│  - PIR Sensor   │
│  - Relays       │
│  - LEDs         │
└────────┬────────┘
         │ MQTT/TLS
         ↓
┌─────────────────┐
│  AWS IoT Core   │
│  - Message      │
│    Routing      │
│  - Rules Engine │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐  ┌──────────┐
│ Lambda │  │ Backend │
│Function│  │   API   │
└───┬────┘  └────┬────┘
    │            │
    ↓            ↓
┌────────┐  ┌──────────┐
│Bedrock │  │   Web    │
│   AI   │  │Dashboard │
└────────┘  └──────────┘
```

---

## 🚀 Production Deployment

### Deploy Backend to AWS

1. **Use AWS Elastic Beanstalk:**
   ```bash
   # Install EB CLI
   pip install awsebcli
   
   # Initialize
   eb init
   
   # Create environment
   eb create
   
   # Deploy
   eb deploy
   ```

2. **Or Use AWS App Runner:**
   - Containerize Flask app
   - Deploy to App Runner

3. **Or Use EC2:**
   - Launch EC2 instance
   - Install dependencies
   - Run with systemd

### Deploy Web Dashboard

1. **Use S3 + CloudFront:**
   - Upload HTML/CSS/JS to S3
   - Configure CloudFront
   - Enable HTTPS

2. **Or Use AWS Amplify:**
   - Connect GitHub repo
   - Auto-deploy on push

### Database Integration

1. **Use DynamoDB:**
   - Store device data
   - Query historical data
   - Real-time updates

2. **Or Use TimeStream:**
   - Time-series data
   - IoT analytics
   - Long-term storage

---

## 📚 Additional Resources

- **Hardware Guide**: [`hardware/HARDWARE_SETUP.md`](hardware/HARDWARE_SETUP.md)
- **ESP32 Code**: [`esp32/esp32_complete_hardware.ino`](esp32/esp32_complete_hardware.ino)
- **Backend API**: [`backend/app.py`](backend/app.py)
- **Web Dashboard**: [`web/dashboard.html`](web/dashboard.html)

---

## 🎉 Success!

You now have a **complete IoT system** with:
- ✅ Real hardware (ESP32 + sensors + actuators)
- ✅ Cloud connectivity (AWS IoT Core)
- ✅ AI intelligence (AWS Bedrock)
- ✅ Web dashboard (Real-time monitoring & control)
- ✅ Backend API (RESTful services)
- ✅ End-to-end integration

**Your smart home/office system is ready! 🚀**

---

**Next Steps:**
- Add more sensors
- Implement device shadow
- Add user authentication
- Set up alerts/notifications
- Deploy to production
- Scale to multiple devices







