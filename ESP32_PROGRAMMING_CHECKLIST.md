# 🔧 ESP32 Programming Checklist - What You Need

## ✅ Hardware Status: COMPLETE
Your wiring and hardware are ready!

---

## 📋 What You Need Next:

### 1. SOFTWARE INSTALLATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#### Arduino IDE Setup:
- [ ] **Download Arduino IDE 2.x**
  - https://www.arduino.cc/en/software
  - Install on your computer

- [ ] **Install ESP32 Board Support**
  - Open Arduino IDE
  - File → Preferences
  - Add to "Additional Board Manager URLs":
    ```
    https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
    ```
  - Tools → Board → Boards Manager
  - Search "ESP32" → Install "esp32 by Espressif Systems"

- [ ] **Install Required Libraries**
  - Sketch → Include Library → Manage Libraries
  - Install these libraries:
    - **DHT sensor library** (by Adafruit)
    - **PubSubClient** (by Nick O'Leary) - Version 2.8.0+
    - **ArduinoJson** (by Benoit Blanchon) - Version 6.19.0+

---

### 2. AWS IOT CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You need these from AWS IoT Core:

- [ ] **AWS IoT Endpoint**
  - Format: `xxxxx-ats.iot.us-east-1.amazonaws.com`
  - Get from: AWS Console → IoT Core → Settings → Device data endpoint
  - Or run: `aws iot describe-endpoint --endpoint-type iot:Data-ATS --region us-east-1`

- [ ] **Thing Name**
  - Should be: `ESP32_SmartDevice`
  - Verify it exists: `aws iot describe-thing --thing-name ESP32_SmartDevice --region us-east-1`

- [ ] **Device Certificates**
  - Device certificate (`.pem.crt` file)
  - Private key (`.pem.key` file)
  - Root CA certificate (`AmazonRootCA1.pem`)
  - Location: `certificates/` folder in project

---

### 3. ESP32 CODE CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Open: `esp32/esp32_complete_hardware.ino`

Update these sections:

#### A. WiFi Credentials (Line ~30):
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

#### B. AWS IoT Endpoint (Line ~36):
```cpp
const char* aws_iot_endpoint = "YOUR_ENDPOINT.iot.us-east-1.amazonaws.com";
```

#### C. Certificates (Lines ~50-63):
Replace with your actual certificates:
- Root CA certificate
- Device certificate
- Private key

---

### 4. CERTIFICATE CONVERSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ESP32 needs certificates in Arduino format (with `\n` characters).

- [ ] **Convert certificates**
  - Use: `esp32/convert_certificates.py`
  - Or manually add `\n` at end of each line
  - Format: `"-----BEGIN CERTIFICATE-----\n" \`

---

### 5. UPLOAD TO ESP32
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- [ ] **Select Board**
  - Tools → Board → ESP32 Dev Module

- [ ] **Select Port**
  - Tools → Port → (your ESP32 port)
  - On Mac: Usually `/dev/cu.usbserial-*` or `/dev/cu.SLAB_USBtoUART`
  - On Windows: Usually `COM3`, `COM4`, etc.

- [ ] **Upload Settings**
  - Upload Speed: 115200
  - CPU Frequency: 240MHz
  - Flash Frequency: 80MHz
  - Flash Size: 4MB (or your board's size)

- [ ] **Upload Code**
  - Click Upload button (→)
  - Wait for compilation and upload
  - Should see "Done uploading"

---

### 6. TEST CONNECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- [ ] **Open Serial Monitor**
  - Tools → Serial Monitor
  - Baud rate: 115200
  - Should see:
    - WiFi connecting...
    - WiFi connected!
    - AWS IoT connecting...
    - Connected to AWS IoT Core!
    - Publishing sensor data...

- [ ] **Verify in AWS Console**
  - AWS IoT Console → Test → MQTT test client
  - Subscribe to: `devices/ESP32_SmartDevice/data`
  - Should see messages every 5 seconds

---

## 🚀 Quick Start Commands

### Check AWS IoT Endpoint:
```bash
aws iot describe-endpoint --endpoint-type iot:Data-ATS --region us-east-1
```

### Verify Thing Exists:
```bash
aws iot describe-thing --thing-name ESP32_SmartDevice --region us-east-1
```

### Check Certificates:
```bash
ls -la certificates/
```

### Convert Certificates (if needed):
```bash
cd esp32
python convert_certificates.py ../certificates/AmazonRootCA1.pem root_ca
python convert_certificates.py ../certificates/device-certificate.pem.crt device_cert
python convert_certificates.py ../certificates/private.pem.key device_key
```

---

## 📝 Configuration Summary

**What you need to provide:**
1. ✅ WiFi SSID and password
2. ✅ AWS IoT endpoint URL
3. ✅ Device certificates (3 files)
4. ✅ Thing name (ESP32_SmartDevice)

**What's already in the code:**
- ✅ Pin definitions (GPIO 4, 5, 18, 19, 21, 22, 25, 26, 27)
- ✅ MQTT topics
- ✅ Sensor reading logic
- ✅ Relay control logic
- ✅ AWS IoT connection code

---

## ⚠️ Common Issues

**Can't find ESP32 port:**
- Install USB drivers (CH340 or CP2102)
- Check USB cable (data cable, not just power)
- Try different USB port

**WiFi won't connect:**
- Check SSID and password
- Verify 2.4GHz network (ESP32 doesn't support 5GHz)
- Check signal strength

**AWS IoT won't connect:**
- Verify certificates are correct
- Check endpoint URL
- Verify Thing exists
- Check certificate policies

**Compilation errors:**
- Install all required libraries
- Check Arduino IDE version (2.x recommended)
- Verify ESP32 board support installed

---

## 🎯 Next Steps After Programming

Once ESP32 is connected:
1. ✅ Verify data publishing to AWS IoT
2. ✅ Test relay control from dashboard
3. ✅ Check AgentCore agent can query device
4. ✅ Test end-to-end flow

