# Complete Hardware Setup Guide

## 📦 Required Components

### Essential Components
- **ESP32 Development Board** (ESP32-WROOM-32 or similar)
- **Breadboard** (830 points or larger)
- **Jumper Wires** (Male-to-Male, Male-to-Female)
- **USB Cable** (for programming and power)

### Sensors
- **DHT22** - Temperature & Humidity Sensor
- **PIR Sensor** (HC-SR501) - Motion Detection Sensor

### Actuators
- **4-Channel Relay Module** (5V) - Control AC/DC devices
- **LEDs** (5mm, various colors) - Status indicators
- **Resistors** (220Ω for LEDs, 10kΩ for DHT22)

### Power Supply
- **5V Power Supply** (for relay module)
- **3.3V/5V Power Supply** (for sensors)

### Optional Components
- **Push Button** (for manual control)
- **Buzzer** (for alerts)
- **OLED Display** (0.96" I2C) - For local display

---

## 🔌 Complete Wiring Diagram

### Pin Connections

```
Component          ESP32 Pin    Notes
-----------        ---------    -----
DHT22 DATA         GPIO 4       Pull-up resistor (10kΩ to 3.3V)
DHT22 VCC          3.3V
DHT22 GND          GND

PIR OUT            GPIO 5
PIR VCC            5V
PIR GND            GND

Relay Module IN1   GPIO 18
Relay Module IN2   GPIO 19
Relay Module IN3   GPIO 21
Relay Module IN4   GPIO 22
Relay Module VCC   5V
Relay Module GND   GND

LED Status         GPIO 2       (Built-in LED)
LED Relay 1        GPIO 25
LED Relay 2        GPIO 26
LED Motion        GPIO 27

Button             GPIO 0       (Built-in button, optional)
```

---

## 📐 Detailed Wiring Instructions

### Step 1: Power Distribution

1. **Create Power Rails on Breadboard**
   - Connect 3.3V from ESP32 to one power rail
   - Connect 5V from ESP32 to another power rail
   - Connect GND from ESP32 to ground rail

### Step 2: DHT22 Temperature & Humidity Sensor

```
DHT22 Pin    Connection
---------    ----------
Pin 1 (VCC)  → 3.3V power rail
Pin 2 (DATA) → GPIO 4 (with 10kΩ pull-up to 3.3V)
Pin 3 (NC)   → Not connected
Pin 4 (GND)  → GND rail
```

**Pull-up Resistor:**
- Connect 10kΩ resistor between DATA pin and 3.3V

### Step 3: PIR Motion Sensor (HC-SR501)

```
PIR Sensor Pin    Connection
---------------    ----------
VCC                → 5V power rail
OUT                → GPIO 5
GND                → GND rail
```

**PIR Sensor Settings:**
- **Sensitivity**: Adjust potentiometer (usually 50% is good)
- **Time Delay**: Adjust potentiometer (2-5 seconds recommended)
- **Mode**: Set jumper to "H" (repeatable trigger)

### Step 4: 4-Channel Relay Module

```
Relay Module Pin    Connection
----------------    ----------
IN1                 → GPIO 18
IN2                 → GPIO 19
IN3                 → GPIO 21
IN4                 → GPIO 22
VCC                 → 5V power rail
GND                → GND rail
```

**Important Notes:**
- Most relay modules are **active-low** (LOW = ON, HIGH = OFF)
- Connect relay outputs to your devices (lights, fans, etc.)
- **Safety**: Use proper AC wiring practices for high-voltage devices

### Step 5: Status LEDs

```
LED Component       Connection
-------------       ----------
LED 1 (Status)      → GPIO 2 (Built-in, no external LED needed)
LED 2 (Relay 1)     → GPIO 25 → 220Ω resistor → GND
LED 3 (Relay 2)     → GPIO 26 → 220Ω resistor → GND
LED 4 (Motion)      → GPIO 27 → 220Ω resistor → GND
```

**LED Wiring:**
- **Anode (long leg)** → GPIO pin → 220Ω resistor → GND
- **Cathode (short leg)** → GND directly

### Step 6: Optional Components

**Push Button:**
- One side → GPIO 0 (built-in button)
- Other side → GND
- ESP32 has internal pull-up, so no external resistor needed

**Buzzer:**
- Positive → GPIO pin (via transistor for higher current)
- Negative → GND

---

## 🔧 Component Specifications

### DHT22 Sensor
- **Operating Voltage**: 3.3V - 5V
- **Temperature Range**: -40°C to 80°C
- **Humidity Range**: 0% to 100% RH
- **Accuracy**: ±0.5°C, ±1% RH
- **Update Rate**: 2 seconds

### PIR Sensor (HC-SR501)
- **Operating Voltage**: 5V - 20V
- **Detection Range**: 3-7 meters
- **Detection Angle**: 110°
- **Output**: Digital (HIGH/LOW)
- **Time Delay**: Adjustable (0.3s - 300s)

### 4-Channel Relay Module
- **Operating Voltage**: 5V
- **Relay Type**: SPDT (Single Pole Double Throw)
- **Max Current**: 10A per channel
- **Max Voltage**: 250V AC / 30V DC
- **Control Signal**: 3.3V/5V TTL

### LEDs
- **Type**: Standard 5mm LEDs
- **Forward Voltage**: 2.0V - 3.4V (depending on color)
- **Forward Current**: 20mA
- **Resistor Value**: 220Ω (for 3.3V supply)

---

## 🛠️ Assembly Steps

### Step 1: Prepare Breadboard
1. Place ESP32 on breadboard (straddle the center gap)
2. Connect power rails (3.3V, 5V, GND)

### Step 2: Install DHT22
1. Place DHT22 on breadboard
2. Connect VCC to 3.3V rail
3. Connect GND to GND rail
4. Connect DATA to GPIO 4
5. Add 10kΩ pull-up resistor (DATA to 3.3V)

### Step 3: Install PIR Sensor
1. Place PIR sensor on breadboard
2. Connect VCC to 5V rail
3. Connect GND to GND rail
4. Connect OUT to GPIO 5

### Step 4: Install Relay Module
1. Place relay module on breadboard
2. Connect VCC to 5V rail
3. Connect GND to GND rail
4. Connect IN1-IN4 to GPIO pins (18, 19, 21, 22)

### Step 5: Install LEDs
1. For each LED:
   - Insert LED (long leg = anode)
   - Connect anode to GPIO pin via 220Ω resistor
   - Connect cathode to GND

### Step 6: Final Connections
1. Double-check all connections
2. Verify power connections (no shorts!)
3. Connect USB cable to ESP32
4. Power on

---

## ⚠️ Safety Warnings

### High Voltage Safety
- **NEVER** touch relay outputs when connected to AC power
- Use proper wire gauge for AC connections
- Install fuses for AC circuits
- Use proper enclosures for high-voltage components
- Follow local electrical codes

### Low Voltage Safety
- Check polarity before connecting components
- Don't exceed component voltage ratings
- Use appropriate current-limiting resistors
- Double-check connections before powering on

### General Safety
- Work in a well-lit area
- Keep workspace clean and organized
- Use proper tools
- Test with low voltage first
- Have a fire extinguisher nearby when testing AC circuits

---

## 🧪 Testing Each Component

### Test 1: DHT22 Sensor
```cpp
// Upload test code
float temp = dht.readTemperature();
float hum = dht.readHumidity();
Serial.println("Temperature: " + String(temp) + "°C");
Serial.println("Humidity: " + String(hum) + "%");
```
**Expected**: Valid temperature and humidity readings

### Test 2: PIR Sensor
```cpp
// Upload test code
int pirValue = digitalRead(PIR_PIN);
Serial.println("PIR: " + String(pirValue));
```
**Expected**: 0 when no motion, 1 when motion detected

### Test 3: Relay Module
```cpp
// Upload test code
digitalWrite(RELAY_1_PIN, LOW);  // Turn ON
delay(1000);
digitalWrite(RELAY_1_PIN, HIGH); // Turn OFF
```
**Expected**: Relay clicks, connected device turns on/off

### Test 4: LEDs
```cpp
// Upload test code
digitalWrite(LED_PIN, HIGH);
delay(500);
digitalWrite(LED_PIN, LOW);
```
**Expected**: LED lights up

---

## 📸 Component Layout Example

```
Breadboard Layout (Top View):

     Power Rails
  ┌─────────────────┐
  │ 3.3V │ 5V │ GND │
  ├─────────────────┤
  │                 │
  │  ESP32          │
  │  (Center)       │
  │                 │
  │  DHT22          │
  │  PIR            │
  │  Relay Module   │
  │  LEDs           │
  │                 │
  └─────────────────┘
```

---

## 🔍 Troubleshooting

### DHT22 Not Reading
- ✅ Check connections (VCC, GND, DATA)
- ✅ Verify pull-up resistor (10kΩ)
- ✅ Check DATA pin connection (GPIO 4)
- ✅ Wait 2 seconds between readings

### PIR Not Detecting Motion
- ✅ Check power (5V)
- ✅ Adjust sensitivity potentiometer
- ✅ Check time delay setting
- ✅ Verify OUT pin connection (GPIO 5)
- ✅ Wait for PIR to stabilize (30-60 seconds)

### Relay Not Working
- ✅ Check power supply (5V)
- ✅ Verify control pins (GPIO 18-22)
- ✅ Check relay module type (active-low vs active-high)
- ✅ Test with multimeter
- ✅ Verify relay connections to devices

### LEDs Not Lighting
- ✅ Check polarity (anode/cathode)
- ✅ Verify resistor value (220Ω)
- ✅ Check GPIO pin connections
- ✅ Test with multimeter

---

## 📚 Additional Resources

- [ESP32 Pinout Reference](https://randomnerdtutorials.com/esp32-pinout-reference-gpios/)
- [DHT22 Datasheet](https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf)
- [PIR Sensor Guide](https://learn.adafruit.com/pir-passive-infrared-proximity-motion-sensor)
- [Relay Module Guide](https://randomnerdtutorials.com/guide-for-relay-module-with-arduino/)

---

**Your hardware is now ready for integration! 🎉**







