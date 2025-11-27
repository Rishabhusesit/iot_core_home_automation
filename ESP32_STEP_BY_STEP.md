# ESP32 Setup - Step by Step

## ✅ Already Done:
- AWS IoT endpoint configured: `aka6dphv0mv57-ats.iot.us-east-1.amazonaws.com`
- Certificates generated and saved
- ESP32 code updated with endpoint

## Step 1: Install Arduino IDE (5 min)

1. Download: https://www.arduino.cc/en/software
2. Install Arduino IDE
3. Open Arduino IDE

## Step 2: Add ESP32 Support (3 min)

1. **File → Preferences**
2. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. **Tools → Board → Boards Manager**
4. Search "ESP32"
5. Install "esp32 by Espressif Systems"

## Step 3: Install Libraries (2 min)

**Sketch → Include Library → Manage Libraries**

Install these:
- **PubSubClient** by Nick O'Leary
- **ArduinoJson** by Benoit Blanchon  
- **DHT sensor library** by Adafruit

## Step 4: Open & Configure ESP32 Code (5 min)

1. **File → Open** → `esp32/esp32_complete_hardware.ino`

2. **Update WiFi** (line 30-31):
   ```cpp
   const char* ssid = "YOUR_WIFI_NAME";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```

3. **Endpoint is already set** ✅ (line 36)

4. **Add Certificates** (lines 50-63):
   - Open `esp32/root_ca_code.txt` → Copy all → Paste in sketch (replace root_ca)
   - Open `esp32/device_cert_code.txt` → Copy all → Paste in sketch (replace device_cert)
   - Open `esp32/device_key_code.txt` → Copy all → Paste in sketch (replace device_key)

## Step 5: Hardware (Optional - Can Test Without)

**Minimal Test (No Sensors):**
- Just connect ESP32 via USB
- Code will use simulated sensor data

**With Sensors:**
```
DHT22:
  VCC → 3.3V
  GND → GND  
  DATA → GPIO 4

PIR:
  VCC → 5V
  GND → GND
  OUT → GPIO 5

Relays:
  IN1 → GPIO 18
  IN2 → GPIO 19
  IN3 → GPIO 21
  IN4 → GPIO 22
  VCC → 5V
  GND → GND
```

## Step 6: Upload Code (2 min)

1. **Connect ESP32** via USB
2. **Tools → Board → ESP32 Dev Module**
3. **Tools → Port → (select your ESP32 port)**
4. Click **Upload** button
5. Wait for "Done uploading"

## Step 7: Test (2 min)

1. **Tools → Serial Monitor** (115200 baud)
2. Should see:
   ```
   WiFi connected!
   Connected to AWS IoT Core!
   Published sensor data: T=25.5°C, H=50.2%
   ```

3. **Check AWS Console:**
   - Go to: AWS IoT Console → Test → MQTT test client
   - Subscribe to: `devices/ESP32_SmartDevice/data`
   - Should see messages every 5 seconds

4. **Check Dashboard:**
   - Open: http://localhost:5000
   - Should see sensor data updating

## Troubleshooting

**WiFi won't connect:**
- Check SSID/password
- Use 2.4GHz WiFi (ESP32 doesn't support 5GHz)

**AWS IoT won't connect:**
- Verify certificates copied correctly
- Check endpoint matches
- Verify Serial Monitor for error messages

**No data in dashboard:**
- Make sure backend is running: `cd backend && python app.py`
- Check Serial Monitor for connection status

## Quick Test Without Hardware

The code works without sensors! It will:
- Connect to WiFi ✅
- Connect to AWS IoT ✅
- Publish simulated sensor data ✅
- Receive commands ✅

You can add sensors later!







