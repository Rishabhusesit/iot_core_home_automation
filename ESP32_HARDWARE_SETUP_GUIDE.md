# 🔧 ESP32 Hardware Setup - Step by Step

## 📦 Step 1: Gather Components

### Essential Components:
- [ ] **ESP32 Development Board** (ESP32-WROOM-32 or similar)
- [ ] **Breadboard** (830 points recommended)
- [ ] **Jumper Wires** (Male-to-Male, Male-to-Female)
- [ ] **USB Cable** (for ESP32 programming and power)

### Sensors:
- [ ] **DHT22 Temperature/Humidity Sensor**
- [ ] **PIR Motion Sensor** (HC-SR501)

### Actuators:
- [ ] **4-Channel Relay Module** (5V)
- [ ] **LEDs** (5mm, various colors - at least 3)
- [ ] **Resistors**:
  - 220Ω (for LEDs)
  - 10kΩ (for DHT22 pull-up)

### Power:
- [ ] **5V Power Supply** (for relay module if needed)
- [ ] **3.3V/5V Power Supply** (optional, ESP32 can use USB)

### Tools:
- [ ] **Multimeter** (optional, for testing)
- [ ] **Wire strippers** (optional)

---

## 🔌 Step 2: Pin Connections

### ESP32 Pinout Reference:
```
┌─────────────────────────────────┐
│         ESP32 Dev Board         │
│                                 │
│  [3.3V] [GND] [EN] [GPIO36]    │
│  [GPIO39] [GPIO34] [GPIO35]    │
│  [GPIO32] [GPIO33] [GPIO25]    │
│  [GPIO26] [GPIO27] [GPIO14]    │
│  [GPIO12] [GND] [GPIO13]       │
│  [GPIO9] [GPIO10] [GPIO11]     │
│  [GPIO6] [GPIO7] [GPIO8]       │
│  [GPIO5] [GPIO4] [GPIO0]       │
│  [GPIO2] [GPIO15] [GPIO16]     │
│  [GPIO17] [GPIO5] [GPIO18]     │
│  [GPIO19] [GPIO21] [GPIO22]    │
│  [GPIO23] [GND] [GPIO1]        │
│  [GPIO3] [RX] [TX]             │
└─────────────────────────────────┘
```

### Component Connections:

#### DHT22 Temperature/Humidity Sensor:
```
DHT22 Pin 1 (VCC)  → ESP32 3.3V
DHT22 Pin 2 (DATA) → ESP32 GPIO 4
DHT22 Pin 3 (NC)   → Not connected
DHT22 Pin 4 (GND)  → ESP32 GND
10kΩ Resistor      → Between DATA and VCC (pull-up)
```

#### PIR Motion Sensor (HC-SR501):
```
PIR VCC  → ESP32 5V (or 3.3V if module supports it)
PIR OUT  → ESP32 GPIO 5
PIR GND  → ESP32 GND
```

#### 4-Channel Relay Module:
```
Relay VCC  → ESP32 5V (or external 5V supply)
Relay GND  → ESP32 GND
Relay IN1  → ESP32 GPIO 18
Relay IN2  → ESP32 GPIO 19
Relay IN3  → ESP32 GPIO 21
Relay IN4  → ESP32 GPIO 22
```

#### LEDs:
```
LED 1 (Status)     → ESP32 GPIO 25 (via 220Ω resistor) → GND
LED 2 (Status)     → ESP32 GPIO 26 (via 220Ω resistor) → GND
LED 3 (Motion)     → ESP32 GPIO 27 (via 220Ω resistor) → GND
```

---

## 📐 Step 3: Wiring Diagram

### Visual Layout:
```
                    ESP32
                     │
        ┌────────────┼────────────┐
        │            │            │
     [3.3V]       [GPIO4]      [GND]
        │            │            │
        │            │            │
     DHT22         DHT22       DHT22
    (VCC)        (DATA)       (GND)
        │            │            │
        └────────────┴────────────┘
             10kΩ pull-up
             (DATA to VCC)

                    ESP32
                     │
        ┌────────────┼────────────┐
        │            │            │
     [5V]        [GPIO5]       [GND]
        │            │            │
        │            │            │
      PIR          PIR          PIR
     (VCC)        (OUT)        (GND)

                    ESP32
                     │
     ┌───────────────┼───────────────┐
     │               │               │
  [5V/GND]      [GPIO18-22]      [GND]
     │               │               │
     │               │               │
   Relay          Relay            Relay
   (VCC)         (IN1-4)          (GND)

                    ESP32
                     │
     ┌───────────────┼───────────────┐
     │               │               │
  [GPIO25]      [GPIO26]        [GPIO27]
     │               │               │
     │               │               │
   LED1            LED2            LED3
  (Anode)         (Anode)         (Anode)
     │               │               │
   [220Ω]         [220Ω]         [220Ω]
     │               │               │
    GND             GND             GND
```

---

## 🔍 Step 4: Detailed Wiring Instructions

### 4.1 Power Connections
1. **Connect ESP32 GND to breadboard ground rail**
2. **Connect ESP32 3.3V to breadboard power rail** (for sensors)
3. **Connect ESP32 5V to breadboard power rail** (for relay/PIR if needed)
4. **Connect all component GNDs to ground rail**

### 4.2 DHT22 Sensor
1. Place DHT22 on breadboard
2. Connect VCC (pin 1) to 3.3V rail
3. Connect GND (pin 4) to GND rail
4. Connect DATA (pin 2) to ESP32 GPIO 4
5. Add 10kΩ resistor between DATA and VCC (pull-up resistor)

### 4.3 PIR Motion Sensor
1. Place PIR sensor on breadboard
2. Connect VCC to 5V rail (or 3.3V if module supports)
3. Connect GND to GND rail
4. Connect OUT to ESP32 GPIO 5

### 4.4 Relay Module
1. Place relay module on breadboard
2. Connect VCC to 5V rail (or external 5V supply)
3. Connect GND to GND rail
4. Connect IN1 to ESP32 GPIO 18
5. Connect IN2 to ESP32 GPIO 19
6. Connect IN3 to ESP32 GPIO 21
7. Connect IN4 to ESP32 GPIO 22

### 4.5 LEDs
1. **LED 1 (Status):**
   - Connect anode (long leg) to 220Ω resistor
   - Connect resistor to ESP32 GPIO 25
   - Connect cathode (short leg) to GND

2. **LED 2 (Status):**
   - Connect anode to 220Ω resistor
   - Connect resistor to ESP32 GPIO 26
   - Connect cathode to GND

3. **LED 3 (Motion Indicator):**
   - Connect anode to 220Ω resistor
   - Connect resistor to ESP32 GPIO 27
   - Connect cathode to GND

---

## ✅ Step 5: Testing Each Component

### 5.1 Test DHT22
```cpp
// Simple test code (upload to ESP32)
#include <DHT.h>
#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  Serial.print("Temperature: ");
  Serial.print(temp);
  Serial.print("°C, Humidity: ");
  Serial.print(humidity);
  Serial.println("%");
  delay(2000);
}
```

**Expected:** Serial monitor shows temperature and humidity readings

### 5.2 Test PIR Sensor
```cpp
// Simple test code
#define PIR_PIN 5

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
}

void loop() {
  int motion = digitalRead(PIR_PIN);
  if (motion == HIGH) {
    Serial.println("Motion detected!");
  }
  delay(100);
}
```

**Expected:** Serial monitor shows "Motion detected!" when you wave hand

### 5.3 Test Relays
```cpp
// Test each relay
#define RELAY1 18
#define RELAY2 19
#define RELAY3 21
#define RELAY4 22

void setup() {
  Serial.begin(115200);
  pinMode(RELAY1, OUTPUT);
  pinMode(RELAY2, OUTPUT);
  pinMode(RELAY3, OUTPUT);
  pinMode(RELAY4, OUTPUT);
}

void loop() {
  // Toggle relay 1
  digitalWrite(RELAY1, HIGH);
  Serial.println("Relay 1 ON");
  delay(1000);
  digitalWrite(RELAY1, LOW);
  Serial.println("Relay 1 OFF");
  delay(1000);
  
  // Repeat for other relays...
}
```

**Expected:** Hear clicking sound from relay, LED on relay module lights up

### 5.4 Test LEDs
```cpp
// Test LEDs
#define LED1 25
#define LED2 26
#define LED3 27

void setup() {
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
}

void loop() {
  digitalWrite(LED1, HIGH);
  delay(500);
  digitalWrite(LED1, LOW);
  
  digitalWrite(LED2, HIGH);
  delay(500);
  digitalWrite(LED2, LOW);
  
  digitalWrite(LED3, HIGH);
  delay(500);
  digitalWrite(LED3, LOW);
}
```

**Expected:** LEDs blink in sequence

---

## 🎯 Step 6: Complete Wiring Checklist

Before proceeding to programming, verify:

- [ ] All GND connections are connected to ESP32 GND
- [ ] DHT22 has pull-up resistor (10kΩ)
- [ ] All LEDs have current-limiting resistors (220Ω)
- [ ] Relay module has proper power supply
- [ ] No loose connections
- [ ] All components are properly seated in breadboard
- [ ] ESP32 can be powered via USB

---

## ⚠️ Important Notes

1. **Power Supply:**
   - ESP32 can be powered via USB (5V)
   - Relay module may need external 5V supply if drawing too much current
   - Never exceed ESP32 GPIO voltage limits (3.3V)

2. **Relay Module:**
   - Most relay modules are active LOW (LOW = ON, HIGH = OFF)
   - Check your module's documentation
   - Some modules have optocouplers for isolation

3. **PIR Sensor:**
   - May need warm-up time (30-60 seconds)
   - Has sensitivity and delay potentiometers
   - Adjust as needed

4. **DHT22:**
   - Requires pull-up resistor
   - Can be slow (2 seconds between readings)
   - Check wiring if readings are -999 or NaN

---

## 🚀 Next Steps

Once hardware is tested and working:
1. ✅ Proceed to ESP32 programming
2. ✅ Configure WiFi credentials
3. ✅ Add AWS IoT certificates
4. ✅ Upload complete code
5. ✅ Connect to AWS IoT Core

See: `esp32/README_ESP32.md` for programming guide

