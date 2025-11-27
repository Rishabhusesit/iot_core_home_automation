# Next Steps: Complete End-to-End Integration

## ✅ What's Working Now

1. **ESP32 Hardware** ✅
   - DHT22 sensor reading temperature (27.5°C) and humidity (70.3%)
   - PIR motion sensor working
   - Relays configured
   - WiFi connected
   - **Publishing to AWS IoT Core successfully!** 🎉

2. **AWS IoT Core** ✅
   - Thing `ESP32_SmartDevice` configured
   - Certificates attached with correct policy
   - Messages arriving on `devices/ESP32_SmartDevice/data`
   - MQTT Test Client receiving messages

## 🎯 Next Steps to Complete Integration

### Step 1: Set Up Backend to Receive IoT Messages

The backend needs to subscribe to IoT topics to receive ESP32 data. You have two options:

#### Option A: Use IoT Rules (Recommended for Production)
Create an IoT Rule that forwards messages to a Lambda function or directly to your backend.

#### Option B: Run IoT Subscriber Locally (Quick Testing)
Run the IoT subscriber script to receive messages and update the backend data store.

**Quick Start - Option B:**
```bash
cd backend
python3 iot_subscriber.py
```

This will:
- Subscribe to `devices/ESP32_SmartDevice/data`
- Update the backend data store with latest sensor readings
- Keep running in the background

### Step 2: Connect Backend to AgentCore for AI Analysis

The backend needs to send sensor data to your AgentCore gateway for AI analysis.

**Check your AgentCore Gateway:**
```bash
cd agentcore
python3 create_gateway.py --gateway_name iot-sensor-analysis-gateway
```

**Add to backend/app.py:**
Add an endpoint that forwards sensor data to AgentCore:

```python
@app.route('/api/ai/analyze', methods=['POST'])
def analyze_sensor_data():
    """Send sensor data to AgentCore for AI analysis"""
    import requests
    
    data = request.json
    sensor_data = data.get('sensor_data', {})
    
    # Get AgentCore Gateway URL from .env
    gateway_url = os.getenv('AGENTCORE_GATEWAY_URL', '')
    if not gateway_url:
        return jsonify({'error': 'AgentCore Gateway URL not configured'}), 500
    
    # Prepare prompt for AgentCore
    prompt = f"""Analyze this IoT sensor data:
- Temperature: {sensor_data.get('temperature', 'N/A')}°C
- Humidity: {sensor_data.get('humidity', 'N/A')}%
- Motion: {sensor_data.get('motion_detected', False)}
- Uptime: {data.get('uptime_seconds', 0)} seconds

Provide analysis and recommendations."""
    
    # Call AgentCore Gateway
    try:
        response = requests.post(
            f"{gateway_url}/invoke",
            json={"prompt": prompt},
            headers={"Authorization": f"Bearer {os.getenv('BEARER_TOKEN', '')}"}
        )
        
        if response.status_code == 200:
            ai_response = response.json()
            return jsonify({
                'success': True,
                'analysis': ai_response.get('response', ''),
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({'error': 'AgentCore request failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Step 3: Start Backend Server

```bash
cd backend
python3 app.py
```

The backend will run on `http://localhost:5000`

**Test endpoints:**
- `GET http://localhost:5000/api/device/status` - Get latest sensor data
- `POST http://localhost:5000/api/device/relay` - Control relays
- `POST http://localhost:5000/api/ai/analyze` - Get AI analysis

### Step 4: Update Dashboard to Connect to Backend

The dashboard needs to point to your backend API.

**Check dashboard.html:**
- Look for `API_URL` variable
- Should be: `const API_URL = 'http://localhost:5000/api';` for local testing
- Or: `const API_URL = 'https://your-backend-url.com/api';` for production

**Test the dashboard:**
1. Open `web/dashboard.html` in a browser
2. Or serve it via the backend: `http://localhost:5000/`
3. Check browser console for API calls
4. Verify sensor data appears on dashboard

### Step 5: Set Up Automatic AI Analysis (Optional)

To automatically analyze sensor data when it arrives:

**Option A: IoT Rule → Lambda → AgentCore**
1. Create IoT Rule that triggers on `devices/ESP32_SmartDevice/data`
2. Rule action: Invoke Lambda function
3. Lambda calls AgentCore Gateway
4. Lambda publishes AI response back to IoT topic
5. ESP32 subscribes to AI response topic

**Option B: Backend Polling**
1. Backend periodically calls `/api/ai/analyze` with latest sensor data
2. Store AI insights
3. Dashboard displays AI insights

### Step 6: Test End-to-End Flow

**Complete Flow:**
1. ESP32 publishes sensor data → AWS IoT Core ✅
2. Backend receives data (via IoT subscriber or IoT Rule) → **TODO**
3. Backend sends to AgentCore for analysis → **TODO**
4. AgentCore returns AI insights → **TODO**
5. Backend stores insights → **TODO**
6. Dashboard displays data + AI insights → **TODO**

**Test Commands:**
```bash
# Terminal 1: Start IoT Subscriber
cd backend
python3 iot_subscriber.py

# Terminal 2: Start Backend Server
cd backend
python3 app.py

# Terminal 3: Test API
curl http://localhost:5000/api/device/status
```

## 🚀 Quick Start Commands

```bash
# 1. Start IoT Subscriber (receives ESP32 messages)
cd backend
python3 iot_subscriber.py &

# 2. Start Backend API
cd backend
python3 app.py

# 3. Open Dashboard
# Open http://localhost:5000 in browser
# Or open web/dashboard.html directly
```

## 📋 Checklist

- [ ] ESP32 publishing to IoT Core ✅
- [ ] IoT Subscriber running and receiving messages
- [ ] Backend API running on localhost:5000
- [ ] Dashboard connecting to backend API
- [ ] AgentCore Gateway configured and accessible
- [ ] AI analysis endpoint working
- [ ] End-to-end flow tested

## 🔧 Troubleshooting

**If IoT Subscriber can't connect:**
- Check certificates in `certificates/` directory
- Verify `AWS_IOT_ENDPOINT` in `.env`
- Check IoT policy allows Subscribe

**If Backend can't reach AgentCore:**
- Verify `AGENTCORE_GATEWAY_URL` in `.env`
- Check `BEARER_TOKEN` is set (Cognito IdToken)
- Test gateway URL directly: `curl -X POST $GATEWAY_URL/invoke -H "Authorization: Bearer $BEARER_TOKEN" -d '{"prompt":"test"}'`

**If Dashboard shows no data:**
- Check browser console for API errors
- Verify `API_URL` in dashboard.html
- Test backend API directly: `curl http://localhost:5000/api/device/status`

## 🎉 Success Criteria

You'll know it's working when:
1. ESP32 publishes sensor data every 5 seconds
2. Backend receives and stores the data
3. Dashboard displays real-time sensor readings
4. AI analysis appears when requested
5. Relay control works from dashboard

---

**Ready to start?** Begin with Step 1 (IoT Subscriber) and work through each step!




