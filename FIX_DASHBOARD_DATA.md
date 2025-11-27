# Fix Dashboard Data Issues

## Problems Identified

1. **No Sensor Data Showing** - Dashboard shows "--" for temperature and humidity
2. **AI Insights Empty** - No AI analysis results displayed

## Root Causes

1. **ESP32 publishes to MQTT topics** but backend queries **IoT Shadow**
2. **ESP32 doesn't update shadow**, so backend gets no data
3. **AI analysis not triggered** - needs BEARER_TOKEN and user action

## Solutions

### Solution 1: Quick Fix - Add Test Data (For Testing Dashboard)

Temporarily add test data to see dashboard working:

```python
# In backend/app.py, in get_device_status(), add before return:
if not device_data.get('sensor_data') or not device_data['sensor_data'].get('temperature'):
    device_data['sensor_data'] = {
        'temperature': 27.5,
        'humidity': 70.3,
        'motion_detected': False
    }
    device_data['status'] = 'online'
    device_data['uptime_seconds'] = 641
    device_data['wifi_rssi'] = -38
    device_data['last_update'] = datetime.utcnow()
```

### Solution 2: Set Up ESP32 to Update Shadow (Recommended)

Update ESP32 code to also update IoT Shadow:

```cpp
// In esp32_complete_hardware.ino, add shadow update function
void updateShadow() {
    StaticJsonDocument<512> shadow;
    shadow["state"]["reported"]["sensor_data"]["temperature"] = temperature;
    shadow["state"]["reported"]["sensor_data"]["humidity"] = humidity;
    shadow["state"]["reported"]["sensor_data"]["motion_detected"] = pirState;
    shadow["state"]["reported"]["relays"]["relay_1"] = relayStates[0];
    shadow["state"]["reported"]["uptime_seconds"] = deviceUptime;
    shadow["state"]["reported"]["wifi_rssi"] = WiFi.RSSI();
    
    char shadowBuffer[512];
    serializeJson(shadow, shadowBuffer);
    
    String shadowTopic = "$aws/things/" + String(thing_name) + "/shadow/update";
    client.publish(shadowTopic.c_str(), shadowBuffer);
}
```

### Solution 3: Use IoT Rules (Alternative)

Create IoT Rule that forwards messages to DynamoDB or Lambda.

## Get Cognito Token

Run this script to get the token:

```bash
python3 get_cognito_token.py
```

It will:
1. Ask for username and password
2. Authenticate with Cognito
3. Get IdToken
4. Save to .env as BEARER_TOKEN

**Cognito Details:**
- User Pool: `us-east-1_EtqvdS9H0`
- Client ID: `4247na9kdsrnl1704jc8coi6t2`

## Test AI Analysis

Once BEARER_TOKEN is set:

```bash
# Restart backend to load token
cd backend
python3 app.py

# In another terminal, trigger AI analysis
curl -X POST http://localhost:5000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"sensor_data": {"temperature": 27.5, "humidity": 70.3}}'
```

Then refresh dashboard - AI insights should appear!

## Quick Commands

```bash
# 1. Get Cognito token
python3 get_cognito_token.py

# 2. Restart backend (to load token)
cd backend
python3 app.py

# 3. Test API
curl http://localhost:5000/api/device/status
curl http://localhost:5000/api/ai/insights
```




