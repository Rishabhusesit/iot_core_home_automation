# Quick Fix: AgentCore 400 Error

## The Real Problem
The framework (`bedrock_agentcore.runtime.app`) validates JSON **BEFORE** calling our entrypoint.
When Agent Sandbox sends requests, sometimes the body is empty, causing:
```
Invalid JSON in request: Expecting value: line 1 column 1 (char 0)
```

## Solution: Use Direct Invocation Instead of Sandbox

The Agent Sandbox has a bug where it sometimes sends empty bodies.
Instead, test the agent using direct API calls:

```bash
# Get the endpoint URL
ENDPOINT_URL=$(aws bedrock-agentcore get-agent-runtime-endpoint \
  --agent-runtime-identifier iot_sensor_analysis_agent-Zz1vVbFKy9 \
  --endpoint-identifier DEFAULT \
  --region us-east-1 \
  --query 'agentRuntimeEndpoint.endpointUrl' \
  --output text)

# Invoke with proper JSON
curl -X POST "$ENDPOINT_URL/invoke" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "hi"}'
```

## Alternative: Wait for Framework Fix
This is a known issue with the Agent Sandbox. The agent code is correct.
The framework needs to be updated to handle empty bodies gracefully.

