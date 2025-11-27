# 🔧 Manual IoT Rule Setup (5 minutes)

## ✅ What's Already Done
- ✅ DynamoDB table created: `ESP32_ESP32_SmartDevice_Data`
- ✅ IAM role created: `IoT_DynamoDB_Role`

## 📋 Step-by-Step: Create IoT Rule via AWS Console

### Step 1: Open AWS IoT Console
1. Go to: https://console.aws.amazon.com/iot/
2. Make sure you're in region: **us-east-1** (N. Virginia)

### Step 2: Create Rule
1. Click **"Rules"** in the left sidebar
2. Click **"Create rule"** button

### Step 3: Configure Rule
1. **Rule name:** `ESP32_SmartDevice_DataForwarder`
2. **Rule description:** `Forward ESP32 sensor data to DynamoDB`

### Step 4: SQL Statement
In the **"Rule query statement"** section, paste:
```sql
SELECT * FROM 'devices/ESP32_SmartDevice/data'
```

### Step 5: Add Action
1. Scroll down to **"Set one or more actions"**
2. Click **"Add action"**
3. Select **"Insert a message into a DynamoDB table"**
4. Click **"Configure action"**

### Step 6: Configure DynamoDB Action
1. **Table name:** `ESP32_ESP32_SmartDevice_Data`
2. **Partition key:** `device_id`
3. **Partition key value:** `${device_id}`
4. **Sort key:** `timestamp`
5. **Sort key value:** `${timestamp}`
6. **IAM role name:** `IoT_DynamoDB_Role`
7. Click **"Add action"**

### Step 7: Create Rule
1. Scroll to bottom
2. Click **"Create rule"**

## ✅ Verify It's Working

### Check Rule Status
1. Go to Rules → `ESP32_SmartDevice_DataForwarder`
2. Verify status is **"Active"**

### Test with ESP32
1. Wait for ESP32 to publish a message (every 3 seconds)
2. Go to DynamoDB Console → Tables → `ESP32_ESP32_SmartDevice_Data`
3. Click **"Explore table items"**
4. You should see new items appearing!

## 🚀 Alternative: Use AWS CLI

If you prefer CLI, run:

```bash
aws iot create-topic-rule \
  --rule-name ESP32_SmartDevice_DataForwarder \
  --topic-pattern "devices/ESP32_SmartDevice/data" \
  --sql "SELECT device_id, timestamp, sensor_data, relays, uptime_seconds, wifi_rssi FROM 'devices/ESP32_SmartDevice/data'" \
  --actions '[{
    "dynamoDBv2": {
      "roleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/IoT_DynamoDB_Role",
      "putItem": {
        "tableName": "ESP32_ESP32_SmartDevice_Data"
      }
    }
  }]'
```

**Replace `YOUR_ACCOUNT_ID`** with your AWS account ID:
```bash
aws sts get-caller-identity --query Account --output text
```

## 🎯 Next Steps

Once the rule is created:
1. ✅ ESP32 messages will automatically be stored in DynamoDB
2. ✅ Backend will query DynamoDB for latest data
3. ✅ Dashboard will show real-time sensor readings

**Restart backend:**
```bash
cd backend
python3 app.py
```

**Open dashboard:**
```
http://localhost:5000
```


