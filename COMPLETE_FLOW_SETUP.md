# 🚀 Complete Flow Setup Guide

## Overview

This guide sets up the complete bidirectional IoT flow:

1. **ESP32 → AWS IoT Core** ✅ (Already working)
2. **User → Web App → AgentCore → Lambda → DynamoDB** (To be set up)
3. **User → Command → AgentCore → Lambda → AWS IoT Core → ESP32** (To be set up)

## What's Already Done ✅

- ✅ ESP32 publishing sensor data to AWS IoT Core
- ✅ IoT Rule forwarding to DynamoDB
- ✅ Backend API receiving data
- ✅ Dashboard displaying real-time data
- ✅ Basic AI analysis working

## What's Left 🔧

### Step 1: Deploy Lambda Function for AgentCore Tools

```bash
python3 setup_complete_flow.py
```

This will:
- Create Lambda function: `iot-agentcore-tools`
- Set up IAM role with permissions
- Add CloudWatch metrics to IoT Rule

### Step 2: Deploy AgentCore Agent with Tools

```bash
cd agentcore
python3 strands_agent_runtime_deploy.py \
  --gateway_id your-gateway-id \
  --lambda_arn arn:aws:lambda:us-east-1:ACCOUNT:function:iot-agentcore-tools
```

### Step 3: Update Backend with Natural Language Endpoint

The backend already has `/api/ai/query` endpoint added. Just restart:

```bash
cd backend
python3 app.py
```

### Step 4: Test Natural Language Queries

Open dashboard: http://localhost:5000

Try these queries in the "Ask AI Assistant" box:

1. **"Show me all devices"**
   - Should query DynamoDB and list devices

2. **"What is the temperature?"**
   - Should get latest temperature reading

3. **"Turn on bedroom light"**
   - Should send MQTT command to ESP32
   - ESP32 should turn on relay

4. **"What's the device status?"**
   - Should get comprehensive device summary

## Architecture

```
User Query → Dashboard → Backend (/api/ai/query)
                              ↓
                    AgentCore Gateway
                              ↓
                    AgentCore Agent (with tools)
                              ↓
                    Lambda Function (iot-agentcore-tools)
                              ↓
              ┌───────────────┴───────────────┐
              ↓                               ↓
        DynamoDB Query              IoT Core Publish
        (for queries)               (for commands)
              ↓                               ↓
        Return Results              ESP32 Receives
```

## Lambda Function Tools

The Lambda function (`lambda/agentcore_tools_lambda.py`) provides:

1. **query_devices** - Query DynamoDB for device data
2. **get_temperature** - Get temperature from specific device
3. **control_device** - Send commands to ESP32 via IoT Core
4. **get_device_summary** - Get comprehensive device status

## Testing

### Test Lambda Function Directly

```bash
aws lambda invoke \
  --function-name iot-agentcore-tools \
  --payload '{"tool_name":"get_temperature","parameters":{"device_id":"ESP32_SmartDevice"}}' \
  response.json
cat response.json
```

### Test Natural Language Query

```bash
curl -X POST http://localhost:5000/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the temperature?"}'
```

## Troubleshooting

### Lambda Function Not Found
- Run `setup_complete_flow.py` to create it
- Check IAM role permissions

### AgentCore Gateway Not Responding
- Verify `GATEWAY_URL` in `.env`
- Check `BEARER_TOKEN` is valid
- Fallback: Direct Bedrock will be used

### Commands Not Reaching ESP32
- Verify ESP32 is subscribed to `devices/ESP32_SmartDevice/commands`
- Check IoT Core permissions
- Verify MQTT topic matches

## Next Steps After Setup

1. **Add More Tools** - Extend Lambda with more capabilities
2. **Scheduled Queries** - Set up CloudWatch Events for periodic analysis
3. **Multi-Device Support** - Extend to multiple ESP32 devices
4. **Alerting** - Trigger notifications when thresholds are exceeded


