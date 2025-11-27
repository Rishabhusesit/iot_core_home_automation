# Troubleshooting: ESP32 Messages Not Appearing in MQTT Test Client

## ✅ What's Working
Based on diagnostics:
- ✅ Thing `ESP32_SmartDevice` exists
- ✅ Certificates are attached and have correct policy
- ✅ Policy allows publishing to `devices/ESP32_SmartDevice/*`
- ✅ ESP32 Serial Monitor shows successful publishes

## 🔍 Common Issues & Solutions

### Issue 1: MQTT Test Client Not Connected
**Symptoms:** No messages appear, subscription shows as inactive

**Solution:**
1. In AWS IoT Console → Test → MQTT test client
2. Check the top banner - it should say "Connected"
3. If it says "Disconnected", click "Connect" button
4. Wait for connection to establish (green indicator)

### Issue 2: Wrong Topic Subscription
**Symptoms:** Subscription exists but no messages

**Solution:**
1. **Remove existing subscription** (click X next to `devices/ESP32_SmartDevice/*`)
2. **Subscribe to exact topic:**
   - Topic filter: `devices/ESP32_SmartDevice/data`
   - Click "Subscribe"
3. **OR use wildcard correctly:**
   - Topic filter: `devices/ESP32_SmartDevice/#` (note: `#` not `*`)
   - `#` matches all subtopics, `*` matches single level

### Issue 3: Messages Arriving But Not Displayed
**Symptoms:** Subscription active, but message panel is empty

**Solution:**
1. Click "Clear" button in the message panel
2. Click "Pause" then "Resume" to refresh
3. Check if messages are being filtered (look for filter options)
4. Try "Export" to download messages as JSON

### Issue 4: ESP32 Not Actually Publishing
**Symptoms:** Serial Monitor shows "Published" but messages don't arrive

**Check Serial Monitor for:**
- ✅ "✅ Connected to AWS IoT Core!"
- ✅ "✅ Subscribed to: devices/ESP32_SmartDevice/commands"
- ✅ "📤 Published sensor data (XXX bytes): ..."

**If you see errors:**
- ❌ "❌ MQTT client not connected!" → Connection issue
- ❌ "❌ Publish failed!" → Check certificates or policy
- ❌ "Failed to connect after 5 attempts!" → Certificate/policy mismatch

### Issue 5: Certificate Mismatch
**Symptoms:** ESP32 connects but publishes fail

**Solution:**
1. Verify the certificate in ESP32 code matches the one attached to the thing
2. Check certificate is ACTIVE (not revoked)
3. Verify policy is attached to the certificate (not just the thing)

## 🧪 Testing Steps

### Step 1: Verify ESP32 Connection
Check Serial Monitor for:
```
✅ WiFi connected!
✅ NTP time synchronized
✅ Connected to AWS IoT Core!
✅ Subscribed to: devices/ESP32_SmartDevice/commands
📤 Published sensor data (273 bytes): T=27.90°C, H=67.80%, Motion=NO
```

### Step 2: Test with AWS CLI
Run this command to publish a test message:
```bash
aws iot-data publish \
  --topic "devices/ESP32_SmartDevice/data" \
  --payload '{"test":true,"message":"CLI test"}' \
  --region us-east-1 \
  --endpoint-url https://aka6dphv0mv57-ats.iot.us-east-1.amazonaws.com
```

Then check if it appears in MQTT test client.

### Step 3: Subscribe to Exact Topic
In MQTT test client:
1. Remove all subscriptions
2. Subscribe to: `devices/ESP32_SmartDevice/data` (exact match)
3. Wait 5-10 seconds
4. Check message panel

### Step 4: Check CloudWatch Logs
1. Go to CloudWatch → Log groups
2. Look for `/aws/iot/` log groups
3. Check for errors or connection issues

## 📋 Quick Checklist

- [ ] ESP32 Serial Monitor shows "✅ Connected to AWS IoT Core!"
- [ ] ESP32 Serial Monitor shows "📤 Published sensor data..."
- [ ] MQTT Test Client shows "Connected" (green)
- [ ] Subscription is active (not grayed out)
- [ ] Topic filter matches: `devices/ESP32_SmartDevice/data` or `devices/ESP32_SmartDevice/#`
- [ ] Message panel is not paused
- [ ] Certificates are active (not revoked)
- [ ] Policy is attached to certificate

## 🎯 Most Likely Fix

**Try this first:**
1. In MQTT Test Client, click "Disconnect"
2. Wait 2 seconds
3. Click "Connect"
4. Remove subscription `devices/ESP32_SmartDevice/*`
5. Add new subscription: `devices/ESP32_SmartDevice/data`
6. Click "Subscribe"
7. Wait 10 seconds and check message panel

If still not working, the ESP32 might not be publishing. Check Serial Monitor for actual publish confirmations.




