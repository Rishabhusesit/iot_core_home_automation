# Fix: Gateway UnknownOperationException

## Problem
The Gateway endpoint returns `UnknownOperationException` because:
- Gateway is for **MCP protocol**, not direct HTTP REST calls
- We need to use **Agent Runtime API** via boto3 instead

## Solution Applied
Updated `backend/app.py` to use boto3 `bedrock-agent-runtime` client directly instead of HTTP calls to Gateway.

## What Changed
- Removed HTTP calls to Gateway endpoint
- Added boto3 `bedrock-agent-runtime` client
- Uses `invoke_agent()` method to call the agent directly

## Required Configuration
Set in `.env`:
```bash
AGENT_RUNTIME_ID=iot_sensor_analysis_agent  # Or your actual agent runtime ID
```

## If Agent Not Deployed
If you get "Agent not found" error, deploy the agent first:

```bash
cd agentcore
python3 strands_agent_runtime_deploy.py --gateway_id <your-gateway-id>
```

## Test Again
After restarting backend:
```bash
python3 test_ai_analysis.py
```

This should now work correctly!




