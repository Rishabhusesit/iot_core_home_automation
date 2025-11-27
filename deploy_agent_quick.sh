#!/bin/bash
# Quick script to deploy AgentCore Runtime agent

echo "============================================================"
echo "Deploying AgentCore Runtime Agent"
echo "============================================================"
echo ""

cd agentcore

GATEWAY_ID="iot-sensor-analysis-gateway-vcyqiyewsa"

echo "Gateway ID: $GATEWAY_ID"
echo ""

# Check if agent is already deployed
echo "Checking if agent is already deployed..."
python3 -c "from bedrock_agentcore_starter_toolkit import Runtime; r = Runtime(); print(r.status())" 2>&1 | grep -q "READY" && {
    echo "✅ Agent is already deployed and READY!"
    echo ""
    echo "You can now test AI analysis in the dashboard."
    exit 0
}

echo "Agent not found or not ready. Deploying..."
echo ""

# Deploy agent
python3 strands_agent_runtime_deploy.py --gateway_id "$GATEWAY_ID"

echo ""
echo "============================================================"
echo "Deployment Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Wait 1-2 minutes for agent to be READY"
echo "2. Restart backend: cd backend && python3 app.py"
echo "3. Test AI analysis: python3 test_ai_analysis.py"
echo ""




