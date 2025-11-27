# 🔗 Integrate ESP32 Data with Backend

## ✅ Current Status

**ESP32 is publishing successfully!** 🎉
- Temperature: 26.6°C
- Humidity: 65.7%
- Motion: false
- Topic: `devices/ESP32_SmartDevice/data`
- Messages visible in AWS IoT MQTT Test Client

## 🎯 Solution: IoT Rule → DynamoDB

Since ESP32 publishes to MQTT (not Shadow), we'll use an IoT Rule to forward messages to DynamoDB, then the backend queries DynamoDB for the latest data.

## 📋 Setup Steps

### Step 1: Create IoT Rule and DynamoDB Table

```bash
python3 setup_iot_rule.py
```

This script will:
1. ✅ Create DynamoDB table: `ESP32_ESP32_SmartDevice_Data`
2. ✅ Create IoT Rule: `ESP32_SmartDevice_DataForwarder`
3. ✅ Set up IAM role with DynamoDB write permissions

### Step 2: Verify IoT Rule is Active

1. Go to AWS IoT Console → Rules
2. Find rule: `ESP32_SmartDevice_DataForwarder`
3. Verify it's enabled and forwarding to DynamoDB

### Step 3: Restart Backend

```bash
cd backend
python3 app.py
```

The backend will now:
- Query DynamoDB for latest ESP32 data
- Fall back to IoT Shadow if DynamoDB fails
- Fall back to IoT subscriber if available

### Step 4: Test Dashboard

1. Open: http://localhost:5000
2. Check sensor readings (should show real ESP32 data)
3. Click "🔄 Analyze Now" for AI analysis

## 🔍 How It Works

```
ESP32 → AWS IoT Core (MQTT)
         ↓
    IoT Rule (forwards messages)
         ↓
    DynamoDB Table (stores messages)
         ↓
    Backend API (queries DynamoDB)
         ↓
    Dashboard (displays data)
```

## 🐛 Troubleshooting

### No data in dashboard?

1. **Check DynamoDB table:**
   ```bash
   aws dynamodb scan --table-name ESP32_ESP32_SmartDevice_Data --limit 5
   ```

2. **Check IoT Rule:**
   - AWS IoT Console → Rules → `ESP32_SmartDevice_DataForwarder`
   - Verify it's enabled
   - Check "Test" tab for recent executions

3. **Check ESP32 is publishing:**
   - AWS IoT Console → Test → MQTT test client
   - Subscribe to: `devices/ESP32_SmartDevice/data`
   - Verify messages are arriving

### Backend errors?

- Check `.env` has `AWS_REGION=us-east-1`
- Verify AWS credentials are configured
- Check backend logs for DynamoDB errors

## 🚀 Alternative: Use IoT Shadow (Simpler)

If you prefer, update ESP32 code to also update IoT Shadow:

```cpp
// In publishSensorData(), add:
String shadowUpdate = "{\"state\":{\"reported\":" + jsonPayload + "}}";
client.publish("$aws/things/ESP32_SmartDevice/shadow/update", shadowUpdate.c_str());
```

Then backend will automatically get data from Shadow (no DynamoDB needed).

## ✅ Success Indicators

- ✅ Dashboard shows real-time temperature/humidity
- ✅ Data updates every few seconds
- ✅ AI analysis works with real sensor data
- ✅ Device status shows "online"


