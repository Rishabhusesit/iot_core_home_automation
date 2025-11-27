#!/usr/bin/env python3
"""
Test Lambda function for AgentCore tools
"""
import boto3
import json
import sys

lambda_client = boto3.client('lambda', region_name='us-east-1')
function_name = 'iot-agentcore-tools'

def test_lambda_tool(tool_name, parameters=None):
    """Test a Lambda tool"""
    payload = {
        'tool_name': tool_name,
        'parameters': parameters or {}
    }
    
    print(f"\n🧪 Testing tool: {tool_name}")
    print(f"   Parameters: {json.dumps(parameters or {})}")
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print(f"✅ Success!")
            print(f"   Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ Error: Status {response['StatusCode']}")
            print(f"   Response: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Lambda Tools")
    print("=" * 60)
    
    # Test 1: Get temperature
    test_lambda_tool('get_temperature', {'device_id': 'ESP32_SmartDevice'})
    
    # Test 2: Query devices
    test_lambda_tool('query_devices', {'query_type': 'latest', 'limit': 5})
    
    # Test 3: Get device summary
    test_lambda_tool('get_device_summary', {'device_id': 'ESP32_SmartDevice'})
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)


