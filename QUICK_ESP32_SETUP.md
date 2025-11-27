# 🚀 Quick ESP32 Setup - What You Need

## ✅ Status Check

**Hardware:** ✅ Ready  
**Certificates:** ✅ Found (`certificates/` folder)  
**AWS IoT Endpoint:** ✅ `aka6dphv0mv57-ats.iot.us-east-1.amazonaws.com`  
**Thing Name:** ✅ `ESP32_SmartDevice`

---

## 📋 5 Steps to Get ESP32 Running

### STEP 1: Install Arduino IDE (5 min)

1. **Download:** https://www.arduino.cc/en/software
2. **Install** Arduino IDE 2.x
3. **Add ESP32 Board Support:**
   - File → Preferences
   - Add URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "ESP32" → Install

### STEP 2: Install Libraries (2 min)

**Sketch → Include Library → Manage Libraries:**
- **DHT sensor library** (by Adafruit)
- **PubSubClient** (by Nick O'Leary) - Version 2.8.0+
- **ArduinoJson** (by Benoit Blanchon) - Version 6.19.0+

### STEP 3: Configure Code (5 min)

**Open:** `esp32/esp32_complete_hardware.ino`

**Update 3 things:**

#### A. WiFi (Line ~30):
```cpp
const char* ssid = "YOUR_WIFI_SSID";        // ← Your WiFi name
const char* password = "YOUR_WIFI_PASSWORD"; // ← Your WiFi password
```

#### B. AWS IoT Endpoint (Line ~36):
```cpp
// ✅ Already configured! No change needed
const char* aws_iot_endpoint = "aka6dphv0mv57-ats.iot.us-east-1.amazonaws.com";
```

#### C. Certificates (Lines ~50-63):

**Option 1: Use Certificate Converter (Easiest)**
```bash
cd esp32
python3 convert_certificates.py ../certificates/AmazonRootCA1.pem root_ca
python3 convert_certificates.py ../certificates/certificate.pem.crt device_cert
python3 convert_certificates.py ../certificates/private.pem.key device_key
```

Then copy the output into the code.

**Option 2: Manual (if converter doesn't work)**
- Open each certificate file
- Copy content
- Replace in code, adding `\n` at end of each line

### STEP 4: Upload to ESP32 (2 min)

1. **Connect ESP32** via USB
2. **Select Board:** Tools → Board → ESP32 Dev Module
3. **Select Port:** Tools → Port → (your ESP32 port)
4. **Click Upload** (→ button)
5. **Wait** for "Done uploading"

### STEP 5: Test (1 min)

1. **Open Serial Monitor:** Tools → Serial Monitor (115200 baud)
2. **Should see:**
   ```
   WiFi connected!
   Connected to AWS IoT Core!
   Publishing sensor data...
   ```

---

## 🎯 What You Need to Provide

**Only 2 things:**
1. ✅ **WiFi SSID and password** (you know this)
2. ✅ **Certificates** (convert and paste into code)

**Everything else is already configured!**

---

## 🔧 Certificate Conversion

**Quick command:**
```bash
cd esp32
python3 convert_certificates.py ../certificates/AmazonRootCA1.pem root_ca
python3 convert_certificates.py ../certificates/certificate.pem.crt device_cert  
python3 convert_certificates.py ../certificates/private.pem.key device_key
```

**Then:**
1. Copy the output from each command
2. Paste into `esp32_complete_hardware.ino` at the appropriate sections
3. Replace the placeholder text

---

## ✅ Verification Checklist

After uploading, check:

- [ ] Serial Monitor shows "WiFi connected!"
- [ ] Serial Monitor shows "Connected to AWS IoT Core!"
- [ ] Serial Monitor shows "Publishing sensor data..."
- [ ] AWS IoT Console → Test → MQTT test client
- [ ] Subscribe to: `devices/ESP32_SmartDevice/data`
- [ ] See messages every 5 seconds

---

## 🆘 Quick Troubleshooting

**WiFi won't connect:**
- Check SSID/password
- Use 2.4GHz network (not 5GHz)

**AWS IoT won't connect:**
- Verify certificates are correctly formatted
- Check endpoint is correct (already set!)

**Can't find ESP32 port:**
- Install USB drivers (CH340 or CP2102)
- Try different USB cable/port

---

## 📚 Files You Need

- **Code:** `esp32/esp32_complete_hardware.ino`
- **Certificates:** `certificates/AmazonRootCA1.pem`, `certificates/certificate.pem.crt`, `certificates/private.pem.key`
- **Converter:** `esp32/convert_certificates.py`

---

**That's it! Once uploaded, your ESP32 will connect to AWS IoT and start sending sensor data!** 🎉

