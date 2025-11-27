# ESP32 AWS IoT Setup Guide

## 📋 Hardware Requirements

### Required Components
- **ESP32 Development Board** (ESP32-WROOM-32 or similar)
- **USB Cable** for programming and power
- **Breadboard** and jumper wires (optional, for sensors)

### Optional Sensors
- **DHT22** - Temperature and Humidity Sensor
- **BMP280** - Barometric Pressure Sensor
- **Other I2C/SPI sensors** as needed

### Wiring Diagram

#### DHT22 Connection
```
DHT22    ESP32
------   -----
VCC   -> 3.3V
GND   -> GND
DATA  -> GPIO 4
```

#### BMP280 Connection (I2C)
```
BMP280   ESP32
------   -----
VCC   -> 3.3V
GND   -> GND
SCL   -> GPIO 22
SDA   -> GPIO 21
```

## 🔧 Software Setup

### Step 1: Install Arduino IDE

1. Download Arduino IDE from [arduino.cc](https://www.arduino.cc/en/software)
2. Install the IDE

### Step 2: Install ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add this URL to **Additional Board Manager URLs**:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to **Tools → Board → Boards Manager**
5. Search for "ESP32" and install **esp32 by Espressif Systems**

### Step 3: Install Required Libraries

Go to **Sketch → Include Library → Manage Libraries** and install:

1. **PubSubClient** by Nick O'Leary (version 2.8.0+)
2. **ArduinoJson** by Benoit Blanchon (version 6.19.0+)
3. **DHT sensor library** by Adafruit (if using DHT22)
4. **Adafruit BMP280 Library** (if using BMP280)
5. **Adafruit Unified Sensor** (dependency for BMP280)

### Step 4: Configure the Sketch

1. Open `esp32_aws_iot.ino` in Arduino IDE
2. Update the following in the code:

```cpp
// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// AWS IoT Core Configuration
const char* aws_iot_endpoint = "YOUR_ENDPOINT.iot.REGION.amazonaws.com";
const char* thing_name = "ESP32_Device";
const char* client_id = "ESP32_Device";
```

3. **Add your certificates** (see Step 5)

### Step 5: Add AWS IoT Certificates

#### Option A: Direct Certificate Embedding

1. Get your certificates from AWS IoT Console:
   - Root CA: `certificates/AmazonRootCA1.pem`
   - Device Certificate: `certificates/certificate.pem.crt`
   - Private Key: `certificates/private.pem.key`

2. Convert certificates to PROGMEM format:
   - Open each certificate file
   - Copy the entire content including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`
   - Replace the placeholder strings in the sketch

3. Update the certificate constants:
```cpp
const char* root_ca = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF\n" \
"... (your actual certificate) ...\n" \
"-----END CERTIFICATE-----\n";
```

#### Option B: Use SPIFFS (Recommended for Production)

For production, store certificates in SPIFFS filesystem:

1. Install **Arduino ESP32 filesystem uploader** plugin
2. Create a `data` folder in your sketch directory
3. Place certificate files in the `data` folder
4. Use `SPIFFS.begin()` and file reading functions

### Step 6: Configure Board Settings

1. Select your board: **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
2. Set upload speed: **Tools → Upload Speed → 115200**
3. Set CPU frequency: **Tools → CPU Frequency → 240MHz (WiFi/BT)**
4. Set Flash frequency: **Tools → Flash Frequency → 80MHz**
5. Set Partition Scheme: **Tools → Partition Scheme → Default 4MB with spiffs**

### Step 7: Enable Sensor Support (Optional)

If using sensors, uncomment the defines at the top:

```cpp
#define USE_DHT22    // Uncomment if using DHT22
#define USE_BMP280   // Uncomment if using BMP280
```

## 📤 Uploading the Sketch

1. Connect ESP32 to your computer via USB
2. Select the correct port: **Tools → Port → (your ESP32 port)**
3. Click **Upload** button
4. Wait for compilation and upload to complete
5. Open **Serial Monitor** (Tools → Serial Monitor) at 115200 baud

## ✅ Verification

After uploading, you should see in Serial Monitor:

```
========================================
ESP32 AWS IoT Core Integration
========================================

WiFi connected!
IP address: 192.168.1.xxx
Signal strength (RSSI): -45 dBm

NTP time synchronized
Current time: ...

Connecting to AWS IoT Core...
Connected to AWS IoT Core!
Subscribed to: devices/ESP32_Device/commands

Setup complete! Starting main loop...

📤 Published: {"device_id":"ESP32_Device",...}
```

## 🔍 Troubleshooting

### WiFi Connection Issues
- Verify SSID and password are correct
- Check WiFi signal strength
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)

### AWS IoT Connection Issues
- Verify endpoint is correct
- Check certificates are properly formatted
- Ensure certificates match the Thing in AWS
- Verify IoT Policy allows Connect, Publish, Subscribe

### Certificate Issues
- Ensure certificates include `\n` characters
- Check for proper `-----BEGIN-----` and `-----END-----` markers
- Verify certificate hasn't expired

### Memory Issues
- If sketch is too large, consider using SPIFFS for certificates
- Reduce JSON buffer sizes if needed
- Disable unused sensor libraries

## 📚 Additional Resources

- [ESP32 Arduino Core Documentation](https://github.com/espressif/arduino-esp32)
- [PubSubClient Library](https://github.com/knolleary/pubsubclient)
- [ArduinoJson Documentation](https://arduinojson.org/)
- [AWS IoT Device SDK](https://docs.aws.amazon.com/iot/latest/developerguide/iot-device-sdk.html)







