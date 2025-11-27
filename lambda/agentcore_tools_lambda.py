"""
Lambda function for AgentCore tools
Provides natural language query capabilities for IoT devices
"""
import json
import boto3
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Configure logging
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
# AWS_REGION is automatically available in Lambda execution environment
# Use boto3 without explicit region - it will use Lambda's region
dynamodb = boto3.resource('dynamodb')
iot_data = boto3.client('iot-data')
iot_core = boto3.client('iot')

# Configuration
THING_NAME = os.getenv('THING_NAME', 'ESP32_SmartDevice')
TABLE_NAME = os.getenv('DYNAMODB_TABLE', f'ESP32_{THING_NAME}_Data')
COMMAND_TOPIC = f'devices/{THING_NAME}/commands'

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling DynamoDB Decimal types"""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def json_dumps(obj):
    """JSON serialize object with Decimal handling"""
    return json.dumps(obj, cls=DecimalEncoder)

def tool_query_devices(query_type="all", device_id=None, limit=10):
    """
    Query IoT devices from DynamoDB
    
    Args:
        query_type: "all", "latest", "by_device"
        device_id: Specific device ID to query
        limit: Maximum number of results
        
    Returns:
        List of device data
    """
    try:
        table = dynamodb.Table(TABLE_NAME)
        results = []
        
        if query_type == "all" or query_type == "latest":
            # Query for latest data from all devices or specific device
            if device_id:
                response = table.query(
                    KeyConditionExpression='device_id = :device_id',
                    ExpressionAttributeValues={':device_id': device_id},
                    ScanIndexForward=False,  # Most recent first
                    Limit=limit
                )
            else:
                # Scan for all devices (limited)
                response = table.scan(Limit=limit)
            
            for item in response.get('Items', []):
                # Convert DynamoDB item to regular dict
                device_data = {
                    'device_id': item.get('device_id', 'unknown'),
                    'timestamp': item.get('timestamp', ''),
                    'sensor_data': item.get('sensor_data', {}),
                    'relays': item.get('relays', {}),
                    'uptime_seconds': item.get('uptime_seconds', 0),
                    'wifi_rssi': item.get('wifi_rssi', 0)
                }
                results.append(device_data)
        
        return {
            'devices': results,
            'count': len(results),
            'query_type': query_type
        }
        
    except Exception as e:
        logger.error(f"Error querying devices: {str(e)}")
        return {"error": str(e)}

def tool_get_temperature(device_id=None, location=None):
    """
    Get temperature reading from device
    
    Args:
        device_id: Specific device ID (defaults to THING_NAME)
        location: Optional location filter (e.g., "bedroom")
        
    Returns:
        Temperature data
    """
    try:
        device = device_id or THING_NAME
        table = dynamodb.Table(TABLE_NAME)
        
        # Get latest reading
        response = table.query(
            KeyConditionExpression='device_id = :device_id',
            ExpressionAttributeValues={':device_id': device},
            ScanIndexForward=False,  # Most recent first
            Limit=1
        )
        
        if not response.get('Items'):
            return {"error": f"No data found for device {device}"}
        
        item = response['Items'][0]
        sensor_data = item.get('sensor_data', {})
        temperature = sensor_data.get('temperature')
        
        return {
            'device_id': device,
            'temperature_celsius': temperature,
            'temperature_fahrenheit': (temperature * 9/5 + 32) if temperature else None,
            'timestamp': item.get('timestamp', ''),
            'location': location or 'unknown'
        }
        
    except Exception as e:
        logger.error(f"Error getting temperature: {str(e)}")
        return {"error": str(e)}

def tool_control_device(device_id, action, value=None):
    """
    Control IoT device (e.g., turn on/off relay)
    
    Args:
        device_id: Device ID to control
        action: Action to perform (e.g., "turn_on_light", "turn_off_light", "toggle_relay")
        value: Optional value (e.g., relay number)
        
    Returns:
        Command result
    """
    try:
        device = device_id or THING_NAME
        topic = f'devices/{device}/commands'
        
        # Parse action to determine command
        command_payload = {
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if 'turn_on' in action.lower() or 'on' in action.lower():
            if 'light' in action.lower() or 'relay' in action.lower():
                relay_num = value if value else 1
                command_payload['command'] = 'relay_control'
                command_payload['relay'] = int(relay_num)
                command_payload['state'] = True
            else:
                command_payload['command'] = action
                command_payload['state'] = True
                
        elif 'turn_off' in action.lower() or 'off' in action.lower():
            if 'light' in action.lower() or 'relay' in action.lower():
                relay_num = value if value else 1
                command_payload['command'] = 'relay_control'
                command_payload['relay'] = int(relay_num)
                command_payload['state'] = False
            else:
                command_payload['command'] = action
                command_payload['state'] = False
                
        elif 'toggle' in action.lower():
            relay_num = value if value else 1
            command_payload['command'] = 'relay_control'
            command_payload['relay'] = int(relay_num)
            command_payload['state'] = 'toggle'
            
        else:
            command_payload['command'] = action
            if value:
                command_payload['value'] = value
        
        # Publish to IoT Core
        iot_data.publish(
            topic=topic,
            qos=1,
            payload=json.dumps(command_payload)
        )
        
        return {
            'status': 'success',
            'device_id': device,
            'action': action,
            'command': command_payload,
            'message': f'Command sent to {device}',
            'timestamp': command_payload['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Error controlling device: {str(e)}")
        return {"error": str(e)}

def tool_get_device_summary(device_id=None):
    """
    Get comprehensive summary of device status
    
    Args:
        device_id: Device ID (defaults to THING_NAME)
        
    Returns:
        Device summary with all sensor data
    """
    try:
        device = device_id or THING_NAME
        table = dynamodb.Table(TABLE_NAME)
        
        # Get latest reading
        response = table.query(
            KeyConditionExpression='device_id = :device_id',
            ExpressionAttributeValues={':device_id': device},
            ScanIndexForward=False,
            Limit=1
        )
        
        if not response.get('Items'):
            return {"error": f"No data found for device {device}"}
        
        item = response['Items'][0]
        sensor_data = item.get('sensor_data', {})
        
        # Get device info from IoT Core
        try:
            thing_info = iot_core.describe_thing(thingName=device)
            thing_arn = thing_info.get('thingArn', '')
        except:
            thing_arn = ''
        
        summary = {
            'device_id': device,
            'device_arn': thing_arn,
            'status': 'online',
            'last_update': item.get('timestamp', ''),
            'sensor_readings': {
                'temperature_celsius': sensor_data.get('temperature'),
                'humidity_percent': sensor_data.get('humidity'),
                'motion_detected': sensor_data.get('motion_detected', False)
            },
            'device_info': {
                'uptime_seconds': item.get('uptime_seconds', 0),
                'wifi_rssi': item.get('wifi_rssi', 0),
                'relays': item.get('relays', {})
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting device summary: {str(e)}")
        return {"error": str(e)}

def lambda_handler(event, context):
    """
    AWS Lambda handler for AgentCore tools
    
    Event structure (from AgentCore):
    {
        "tool_name": "query_devices",
        "parameters": {
            "query_type": "all",
            "device_id": "ESP32_SmartDevice"
        }
    }
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract tool name and parameters
        tool_name = event.get('tool_name') or event.get('action_name')
        params = event.get('parameters', {}) or event
        
        if not tool_name:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'tool_name is required',
                    'available_tools': [
                        'query_devices',
                        'get_temperature',
                        'control_device',
                        'get_device_summary'
                    ]
                })
            }
        
        result = None
        
        # Route to appropriate tool
        if tool_name == 'query_devices':
            result = tool_query_devices(
                query_type=params.get('query_type', 'all'),
                device_id=params.get('device_id'),
                limit=params.get('limit', 10)
            )
            
        elif tool_name == 'get_temperature':
            result = tool_get_temperature(
                device_id=params.get('device_id'),
                location=params.get('location')
            )
            
        elif tool_name == 'control_device':
            result = tool_control_device(
                device_id=params.get('device_id'),
                action=params.get('action'),
                value=params.get('value')
            )
            
        elif tool_name == 'get_device_summary':
            result = tool_get_device_summary(
                device_id=params.get('device_id')
            )
            
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Unknown tool: {tool_name}',
                    'available_tools': [
                        'query_devices',
                        'get_temperature',
                        'control_device',
                        'get_device_summary'
                    ]
                })
            }
        
        return {
            'statusCode': 200,
            'body': json_dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }

