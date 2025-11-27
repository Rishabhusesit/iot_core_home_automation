# 🛒 ESP32 Hardware Shopping List

## Essential Components

### Microcontroller
- [ ] **ESP32 Development Board** (ESP32-WROOM-32)
  - Price: ~$5-10
  - Where: Amazon, AliExpress, Adafruit, SparkFun
  - Example: "ESP32 DevKit V1" or "ESP32-WROOM-32"

### Breadboard & Wires
- [ ] **Breadboard** (830 points / half-size)
  - Price: ~$5-8
  - Where: Any electronics store
- [ ] **Jumper Wires** (Male-to-Male, Male-to-Female)
  - Price: ~$5-10
  - Where: Amazon, electronics stores
  - Need: 20-30 wires

### Sensors
- [ ] **DHT22 Temperature/Humidity Sensor**
  - Price: ~$5-8
  - Where: Amazon, AliExpress
  - Alternative: DHT11 (cheaper but less accurate)
  
- [ ] **PIR Motion Sensor (HC-SR501)**
  - Price: ~$3-5
  - Where: Amazon, AliExpress
  - Note: Very common, easy to find

### Actuators
- [ ] **4-Channel Relay Module (5V)**
  - Price: ~$5-8
  - Where: Amazon, AliExpress
  - Note: Make sure it's 5V compatible

- [ ] **LEDs (5mm, various colors)**
  - Price: ~$2-5 for pack of 20
  - Where: Any electronics store
  - Need: At least 3 LEDs

### Resistors
- [ ] **220Ω Resistors** (for LEDs)
  - Price: ~$1-3 for pack of 100
  - Where: Amazon, electronics stores
  - Need: 3-5 pieces
  
- [ ] **10kΩ Resistor** (for DHT22 pull-up)
  - Price: ~$1-3 for pack of 100
  - Where: Amazon, electronics stores
  - Need: 1 piece

### Power & Cables
- [ ] **USB Cable** (Micro-USB or USB-C, depending on ESP32)
  - Price: ~$3-5
  - Where: Any electronics store
  - Note: For programming and power

- [ ] **5V Power Supply** (optional, for relay module)
  - Price: ~$5-10
  - Where: Amazon, electronics stores
  - Note: Only needed if relay draws too much current

## Total Estimated Cost: $40-70

## Where to Buy

### Online (Recommended):
- **Amazon** - Fast shipping, good selection
- **AliExpress** - Cheaper, longer shipping
- **Adafruit** - Quality components, US-based
- **SparkFun** - Good documentation, US-based
- **DigiKey** - Professional components
- **Mouser** - Professional components

### Local Stores:
- **RadioShack** (if available)
- **Micro Center** (if nearby)
- **Fry's Electronics** (if available)
- **Local electronics/hobby shops**

## Starter Kits (Easiest Option)

Many vendors sell "ESP32 Starter Kits" that include:
- ESP32 board
- Breadboard
- Jumper wires
- LEDs
- Resistors
- Sensors (sometimes)

**Price:** ~$30-50
**Where:** Amazon, AliExpress

## Quick Links (Examples)

### Amazon US:
- ESP32 DevKit: Search "ESP32 Development Board"
- DHT22: Search "DHT22 Temperature Sensor"
- Relay Module: Search "4 Channel Relay Module 5V"
- Breadboard: Search "830 Point Breadboard"

### AliExpress:
- Usually 30-50% cheaper
- Shipping takes 2-4 weeks
- Good for bulk orders

## Notes

1. **Quality Matters:**
   - Cheaper ESP32 boards may have issues
   - Stick to well-reviewed products
   - ESP32-WROOM-32 is the standard

2. **Relay Module:**
   - Make sure it's 5V compatible
   - Some modules have optocouplers (better isolation)
   - Check if it's active HIGH or LOW

3. **DHT22 vs DHT11:**
   - DHT22: More accurate, more expensive
   - DHT11: Less accurate, cheaper
   - Code works with both (just change type)

4. **Power Supply:**
   - ESP32 can run on USB power
   - Relay module might need external supply
   - Check current requirements

