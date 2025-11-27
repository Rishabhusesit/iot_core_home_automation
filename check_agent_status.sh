#!/bin/bash
# Quick script to check agent deployment status

echo "============================================================"
echo "Checking AgentCore Runtime Agent Status"
echo "============================================================"
echo ""

cd agentcore

python3 -c "
from bedrock_agentcore_starter_toolkit import Runtime
try:
    r = Runtime()
    status = r.status()
    print(f'✅ Agent Found!')
    print(f'   Agent Name: {status.agent_name}')
    print(f'   Status: {status.endpoint.get(\"status\", \"UNKNOWN\")}')
    print(f'   Endpoint URL: {status.endpoint.get(\"endpointUrl\", \"N/A\")}')
    
    endpoint_status = status.endpoint.get('status', 'UNKNOWN')
    if endpoint_status == 'READY':
        print('')
        print('🎉 Agent is READY! You can now use AI analysis.')
    elif endpoint_status in ['CREATING', 'UPDATING']:
        print('')
        print(f'⏳ Agent is {endpoint_status} - please wait 2-5 minutes...')
    else:
        print('')
        print(f'⚠️  Agent status: {endpoint_status}')
except Exception as e:
    print(f'❌ Agent not configured: {e}')
    print('')
    print('Deploy agent with:')
    print('  ./deploy_agent_quick.sh')
    print('')
    print('Or manually:')
    print('  cd agentcore')
    print('  python3 strands_agent_runtime_deploy.py --gateway_id iot-sensor-analysis-gateway-vcyqiyewsa')
"




