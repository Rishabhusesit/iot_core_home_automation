# 🚀 Quick Start: Complete the Integration

## ✅ Current Status
- ESP32 publishing to AWS IoT Core ✅
- Messages visible in MQTT Test Client ✅
- Backend API exists ✅
- AgentCore Gateway deployed ✅

## 🎯 Next Steps (Choose One Path)

### Path 1: Quick Test (5 minutes)
**Goal:** See sensor data in dashboard immediately

```bash
# 1. Start backend server
cd backend
python3 app.py

# 2. Open dashboard
# Open http://localhost:5000 in browser
# OR open web/dashboard.html directly
```

**What this does:**
- Backend serves dashboard
- Dashboard can query `/api/device/status` 
- You can manually trigger AI analysis

**Limitation:** Backend won't automatically receive new IoT messages (needs IoT Rule or MQTT subscription)

---

### Path 2: Full Integration (15 minutes)
**Goal:** Complete end-to-end flow with automatic AI analysis

#### Step 1: Create IoT Rule to Forward Messages

```bash
# Create IoT Rule that forwards messages to a Lambda
aws iot create-topic-rule \
  --rule-name ESP32DataForwarder \
  --topic-pattern "devices/ESP32_SmartDevice/data" \
  --sql "SELECT * FROM 'devices/ESP32_SmartDevice/data'" \
  --actions '[{"lambda":{"functionArn":"arn:aws:lambda:us-east-1:YOUR_ACCOUNT:function:iot-handler"}}]'
```

**OR** use IoT Shadow (simpler):
- ESP32 updates shadow
- Backend queries shadow for latest state

#### Step 2: Configure AgentCore Gateway

```bash
# Get your gateway URL
cd agentcore
python3 create_gateway.py --gateway_name iot-sensor-analysis-gateway

# Add to .env:
# GATEWAY_URL=https://your-gateway-url.execute-api.us-east-1.amazonaws.com
# BEARER_TOKEN=your-cognito-id-token
```

#### Step 3: Start Backend

```bash
cd backend
python3 app.py
```

#### Step 4: Test AI Analysis

```bash
# Get latest sensor data
curl http://localhost:5000/api/device/status

# Trigger AI analysis
curl -X POST http://localhost:5000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"sensor_data": {"temperature": 27.5, "humidity": 70.3, "motion_detected": false}}'
```

---

### Path 3: Use IoT Shadow (Recommended)
**Goal:** Simple, reliable state synchronization

#### Step 1: Update ESP32 to Use Shadow

The ESP32 can update its shadow instead of (or in addition to) publishing to topics.

#### Step 2: Backend Queries Shadow

```python
# In backend/app.py, add:
@app.route('/api/device/shadow', methods=['GET'])
def get_device_shadow():
    """Get device state from IoT Shadow"""
    iot = boto3.client('iot-data', region_name='us-east-1',
                      endpoint_url=f"https://{iot_endpoint}")
    
    response = iot.get_thing_shadow(
        thingName=THING_NAME
    )
    shadow = json.loads(response['payload'].read())
    return jsonify(shadow['state']['reported'])
```

#### Step 3: Poll Shadow Periodically

Backend can poll shadow every few seconds to get latest state.

---

## 🧪 Test Commands

```bash
# 1. Check if backend is running
curl http://localhost:5000/api/device/status

# 2. Test relay control
curl -X POST http://localhost:5000/api/device/relay \
  -H "Content-Type: application/json" \
  -d '{"relay": 1, "state": true}'

# 3. Test AI analysis (if AgentCore configured)
curl -X POST http://localhost:5000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"sensor_data": {"temperature": 27.5, "humidity": 70.3}}'

# 4. Get AI insights history
curl http://localhost:5000/api/ai/insights
```

---

## 📋 What You Need

### For Basic Dashboard:
- ✅ Backend running (`python3 app.py`)
- ✅ Dashboard HTML file
- ⚠️ Backend needs to get data somehow (Shadow, IoT Rule, or manual)

### For Full Integration:
- ✅ Backend running
- ✅ AgentCore Gateway URL in `.env`
- ✅ Bearer token (Cognito IdToken) in `.env`
- ✅ IoT Rule or Shadow setup
- ✅ Dashboard pointing to backend

---

## 🎯 Recommended Next Action

**Start with Path 1 (Quick Test):**
1. Run `python3 app.py` in backend directory
2. Open `http://localhost:5000` in browser
3. Check if dashboard loads
4. Test `/api/device/status` endpoint

**Then move to Path 3 (IoT Shadow):**
1. Set up ESP32 to update shadow
2. Backend queries shadow for latest state
3. Dashboard displays real-time data

**Finally add AI:**
1. Configure AgentCore Gateway URL
2. Test `/api/ai/analyze` endpoint
3. Add automatic analysis triggers

---

## ❓ Questions?

- **Backend won't start?** Check if port 5000 is in use
- **Dashboard shows no data?** Check browser console, verify API_URL
- **AI analysis fails?** Check GATEWAY_URL and BEARER_TOKEN in .env
- **ESP32 not updating?** Check Serial Monitor for connection status

---

**Ready?** Start with: `cd backend && python3 app.py`




