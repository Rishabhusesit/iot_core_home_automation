# Complete Fix Guide: Dashboard Data & AI Analysis

## 🔍 Problems

1. **No sensor data showing** - Temperature and humidity show "--"
2. **AI Insights section empty** - No analysis displayed

## ✅ Solutions

### Fix 1: Get Real-Time Sensor Data

**Problem:** ESP32 publishes to MQTT but backend queries IoT Shadow (which doesn't exist yet).

**Quick Fix (For Testing):**
Add test data temporarily to see dashboard working:

```python
# In backend/app.py, line ~170, in get_device_status(), add:
if not device_data.get('sensor_data') or not device_data['sensor_data'].get('temperature'):
    # Temporary test data - remove once shadow is set up
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

**Permanent Fix:**
Update ESP32 to also update IoT Shadow (I can provide the code).

### Fix 2: Get Cognito Token for AI Analysis

**Step 1: Get the Token**
```bash
python3 get_cognito_token.py
```

Enter your Cognito username and password when prompted.

**Step 2: Restart Backend**
```bash
# Stop current backend (Ctrl+C)
cd backend
python3 app.py
```

**Step 3: Test AI Analysis**
1. Open dashboard: `http://localhost:5000`
2. Click "🔄 Analyze Now" button in AI Insights section
3. Wait a few seconds
4. AI insights should appear!

### Alternative: Test AI Analysis via API

```bash
curl -X POST http://localhost:5000/api/ai/trigger \
  -H "Content-Type: application/json"
```

Then check dashboard or:
```bash
curl http://localhost:5000/api/ai/insights
```

## 📋 Step-by-Step Instructions

### Step 1: Get Cognito Token
```bash
cd /Users/rishabhtiwari/aws_iot_project
python3 get_cognito_token.py
# Enter username and password
```

### Step 2: Add Test Data (Temporary)
Edit `backend/app.py` and add the test data code above.

### Step 3: Restart Backend
```bash
cd backend
python3 app.py
```

### Step 4: Test Dashboard
1. Open `http://localhost:5000`
2. You should see:
   - Temperature: 27.5°C
   - Humidity: 70.3%
   - Device: Online
3. Click "🔄 Analyze Now" in AI Insights
4. Wait for analysis to appear

## 🎯 Expected Results

After fixes:
- ✅ Dashboard shows sensor data
- ✅ Charts display temperature and humidity
- ✅ AI Insights section shows analysis when triggered
- ✅ "Analyze Now" button works

## 🔧 Troubleshooting

**If dashboard still shows "--":**
- Check browser console for errors
- Verify backend is running: `curl http://localhost:5000/api/device/status`
- Check if test data was added correctly

**If AI analysis fails:**
- Check if BEARER_TOKEN is in .env: `grep BEARER_TOKEN .env`
- Verify token is valid (not expired)
- Check backend logs for errors
- Test gateway directly: `curl -X POST $GATEWAY_URL/invoke -H "Authorization: Bearer $BEARER_TOKEN" -d '{"prompt":"test"}'`

**If "Analyze Now" button doesn't work:**
- Check browser console for errors
- Verify API_URL is set correctly in dashboard
- Check backend is running and accessible

## 📝 Files Modified

1. `backend/app.py` - Added AI trigger endpoint, improved insights formatting
2. `web/dashboard.html` - Added "Analyze Now" button, improved AI insights display
3. `get_cognito_token.py` - Script to get Cognito token

## 🚀 Next Steps

Once basic functionality works:
1. Set up ESP32 to update IoT Shadow (for real-time data)
2. Set up automatic AI analysis triggers
3. Add more AI insights features
4. Deploy to production

---

**Ready to fix?** Start with Step 1 (Get Cognito Token)!




