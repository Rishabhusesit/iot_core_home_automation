#!/usr/bin/env python3
"""
Check AgentCore Runtime Agent Status
"""
from bedrock_agentcore_starter_toolkit import Runtime
import boto3
import json

print("=" * 60)
print("AgentCore Runtime Agent Status Check")
print("=" * 60)

# Initialize Runtime
runtime = Runtime()

try:
    status = runtime.status()
    print(f"\n✅ Agent Found!")
    print(f"Agent Name: {status.agent_name}")
    print(f"Status: {status.endpoint.get('status', 'UNKNOWN')}")
    print(f"Agent ARN: {status.endpoint.get('endpointArn', 'N/A')}")
    print(f"Endpoint URL: {status.endpoint.get('endpointUrl', 'N/A')}")
    
    endpoint_status = status.endpoint.get('status', 'UNKNOWN')
    if endpoint_status == 'READY':
        print("\n🎉 Agent is READY and operational!")
    elif endpoint_status in ['CREATING', 'UPDATING']:
        print(f"\n⏳ Agent is {endpoint_status} - please wait...")
    else:
        print(f"\n⚠️  Agent status: {endpoint_status}")
        
except Exception as e:
    print(f"\n❌ Could not get status: {e}")
    print("\nAgent may still be deploying or configuration is missing.")

# Check CloudWatch Logs
print("\n" + "=" * 60)
print("CloudWatch Log Groups:")
print("=" * 60)
try:
    logs = boto3.client('logs', region_name='us-east-1')
    log_groups = logs.describe_log_groups(
        logGroupNamePrefix='/aws/bedrock-agentcore/runtimes/iot_sensor'
    )
    for lg in log_groups.get('logGroups', []):
        print(f"  ✅ {lg['logGroupName']}")
        print(f"     Created: {lg.get('creationTime', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Console Location:")
print("=" * 60)
print("Go to: Amazon Bedrock AgentCore → Agent runtime")
print("Look for: 'iot_sensor_analysis_agent'")
print("Region: us-east-1")
print("\nIf not visible:")
print("  1. Refresh the page (F5 or Cmd+R)")
print("  2. Wait 1-2 minutes")
print("  3. Check you're in us-east-1 region")






