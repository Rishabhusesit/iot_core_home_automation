# ESP32 Quick Setup Guide

## Step 1: Install Arduino IDE & ESP32 Support

1. **Download Arduino IDE:**
   - Go to: https://www.arduino.cc/en/software
   - Download and install

2. **Add ESP32 Board Support:**
   - Open Arduino IDE
   - File → Preferences
   - Add to "Additional Board Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Tools → Board → Boards Manager
   - Search "ESP32" → Install "esp32 by Espressif Systems"

3. **Install Libraries:**
   - Sketch → Include Library → Manage Libraries
   - Install:
     - **PubSubClient** by Nick O'Leary
     - **ArduinoJson** by Benoit Blanchon
     - **DHT sensor library** by Adafruit

## Step 2: Configure ESP32 Code

1. **Open sketch:**
   - File → Open → `esp32/esp32_complete_hardware.ino`

2. **Update WiFi:**
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```

3. **Update AWS IoT:**
   ```cpp
   const char* aws_iot_endpoint = "aka6dphv0mv57-ats.iot.us-east-1.amazonaws.com";
   const char* thing_name = "ESP32_SmartDevice";
   ```

4. **Add Certificates:**
   - Run: `python3 esp32/convert_certificates.py certificates/AmazonRootCA1.pem root_ca`
   - Copy output to sketch (replace root_ca)
   - Do same for certificate.pem.crt and private.pem.key

## Step 3: Hardware Connections

**Minimal Setup (No Sensors - Simulated Data):**
- Just ESP32 via USB (no extra wiring needed)

**With Sensors:**
```
DHT22:
  VCC  → 3.3V
  GND  → GND
  DATA → GPIO 4

PIR Sensor:
  VCC  → 5V
  GND  → GND
  OUT  → GPIO 5

Relay Module:
  IN1  → GPIO 18
  IN2  → GPIO 19
  IN3  → GPIO 21
  IN4  → GPIO 22
  VCC  → 5V
  GND  → GND

LEDs (optional):
  LED1 → GPIO 25 (via 220Ω resistor)
  LED2 → GPIO 26 (via 220Ω resistor)
```

## Step 4: Upload Code

1. **Select Board:**
   - Tools → Board → ESP32 Dev Module

2. **Select Port:**
   - Tools → Port → (your ESP32 port)

3. **Upload:**
   - Click Upload button
   - Wait for "Done uploading"

4. **Open Serial Monitor:**
   - Tools → Serial Monitor (115200 baud)
   - Should see: "Connected to AWS IoT Core!"

## Step 5: Test

1. **Check Serial Monitor:**
   - Should show sensor data every 5 seconds
   - Should show "Published sensor data"

2. **Check AWS IoT Console:**
   - Go to: Test → MQTT test client
   - Subscribe to: `devices/ESP32_SmartDevice/data`
   - Should see messages appearing

3. **Check Dashboard:**
   - Open: http://localhost:5000
   - Should see sensor data updating

## Troubleshooting

**WiFi won't connect:**
- Check SSID/password
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)

**AWS IoT won't connect:**
- Verify certificates are correct
- Check endpoint matches
- Verify IoT Policy is attached

**No sensor data:**
- Check wiring
- Verify sensor libraries installed
- Check Serial Monitor for errors







