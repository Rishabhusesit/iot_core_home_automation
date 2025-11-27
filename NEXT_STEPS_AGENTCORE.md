# Next Steps: AgentCore Runtime Setup

## ✅ What's Been Created

1. **Lambda Function with IoT Tools** (`lambda/iot_tools_lambda.py`)
   - `analyze_sensor_data` - Analyze sensor readings
   - `get_device_status` - Get IoT device status
   - `publish_command` - Send commands to devices
   - `list_things` - List all IoT devices

2. **Agent Runtime Code** (`agentcore/strands_agent_runtime.py`)
   - Strands agent for IoT sensor analysis
   - MCP client integration
   - Streaming response support

3. **Supporting Files**
   - `agentcore/access_token.py` - Token management
   - `agentcore/utils.py` - Utility functions
   - `agentcore/requirements-runtime.txt` - Runtime dependencies
   - `setup_agentcore.sh` - Setup script

## 📋 Setup Steps

### Step 1: Install Dependencies

```bash
cd /Users/rishabhtiwari/aws_iot_project
source .venv/bin/activate
pip install -r requirements.txt
pip install -r agentcore/requirements-runtime.txt
```

### Step 2: Deploy Lambda Function

```bash
./setup_agentcore.sh
```

This will:
- Create IAM role for Lambda
- Deploy Lambda function with IoT tools
- Save Lambda ARN to .env

### Step 3: Create Gateway

You'll need to create an AgentCore Gateway. This requires:
- IAM role with AgentCore permissions
- Gateway creation via AWS Console or Python script

### Step 4: Deploy Agent Runtime

Once Gateway is created:
```bash
cd agentcore
python strands_agent_runtime_deploy.py --gateway_id <gateway-id>
```

### Step 5: Test

Test the agent with:
```bash
python agentcore/device_management_agent_exec.py --agent_arn <agent-arn>
```

## 🔧 Configuration Needed

Update `.env` with:
- `LAMBDA_ARN` - After Lambda deployment
- `GATEWAY_ID` - After Gateway creation
- `GATEWAY_ARN` - After Gateway creation
- `MCP_SERVER_URL` - Gateway endpoint URL
- `BEDROCK_MODEL_ID` - Model to use (default: claude-3-7-sonnet)

## 📚 Reference

Following: https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/02-use-cases/device-management-agent

