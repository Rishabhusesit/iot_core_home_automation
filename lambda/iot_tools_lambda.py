"""
IoT Sensor Data Analysis - Lambda Function for AgentCore Tools
Provides MCP (Model Context Protocol) tools for IoT Core operations
Adapted from device-management-agent pattern for IoT sensor data
"""
import json
import logging
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
# AWS_REGION is available from Lambda context, but we can also get it from environment
# If not set, boto3 will use the region from the Lambda execution environment
aws_region = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
iot_client = boto3.client('iot-data', region_name=aws_region)
iot_core = boto3.client('iot', region_name=aws_region)

# Configuration
THING_NAME = os.getenv('THING_NAME', 'ESP32_SmartDevice')
RESPONSE_TOPIC = os.getenv('RESPONSE_TOPIC', 'devices/ESP32_SmartDevice/ai_responses')

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling DynamoDB Decimal types"""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def json_dumps(obj):
    """JSON serialize object with Decimal handling"""
    return json.dumps(obj, cls=DecimalEncoder)

# IoT Core Tool Implementations

def tool_analyze_sensor_data(sensor_data):
    """
    Analyze IoT sensor data and provide insights
    
    Args:
        sensor_data: Dictionary containing sensor readings
            - temperature: float
            - humidity: float
            - pressure: float
            - motion: bool
            - timestamp: str (ISO format)
            
    Returns:
        Analysis result with insights and recommendations
    """
    try:
        # Extract sensor values
        temp = sensor_data.get('temperature')
        humidity = sensor_data.get('humidity')
        pressure = sensor_data.get('pressure')
        motion = sensor_data.get('motion', False)
        timestamp = sensor_data.get('timestamp', datetime.utcnow().isoformat())
        
        # Basic analysis
        analysis = {
            'timestamp': timestamp,
            'sensor_readings': {
                'temperature_c': temp,
                'humidity_percent': humidity,
                'pressure_hpa': pressure,
                'motion_detected': motion
            },
            'insights': [],
            'recommendations': []
        }
        
        # Temperature analysis
        if temp is not None:
            if temp < 15:
                analysis['insights'].append('Temperature is below normal range')
                analysis['recommendations'].append('Check heating system')
            elif temp > 30:
                analysis['insights'].append('Temperature is above normal range')
                analysis['recommendations'].append('Check cooling system')
            else:
                analysis['insights'].append('Temperature is within normal range')
        
        # Humidity analysis
        if humidity is not None:
            if humidity < 30:
                analysis['insights'].append('Humidity is low - may cause discomfort')
                analysis['recommendations'].append('Consider using a humidifier')
            elif humidity > 70:
                analysis['insights'].append('Humidity is high - may cause mold growth')
                analysis['recommendations'].append('Consider using a dehumidifier')
            else:
                analysis['insights'].append('Humidity is within comfortable range')
        
        # Pressure analysis
        if pressure is not None:
            if pressure < 1000:
                analysis['insights'].append('Low atmospheric pressure - possible storm approaching')
            elif pressure > 1025:
                analysis['insights'].append('High atmospheric pressure - clear weather expected')
            else:
                analysis['insights'].append('Atmospheric pressure is normal')
        
        # Motion detection
        if motion:
            analysis['insights'].append('Motion detected in the area')
        else:
            analysis['insights'].append('No motion detected')
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in analyze_sensor_data: {str(e)}")
        return {"error": str(e)}

def tool_get_device_status(thing_name=None):
    """
    Get status of an IoT device
    
    Args:
        thing_name: Name of the IoT thing (defaults to THING_NAME)
        
    Returns:
        Device status information
    """
    try:
        thing = thing_name or THING_NAME
        
        # Get thing details
        try:
            thing_info = iot_core.describe_thing(thingName=thing)
        except iot_core.exceptions.ResourceNotFoundException:
            return {"error": f"Thing {thing} not found"}
        
        # Get thing shadow (if available)
        shadow_data = None
        try:
            shadow_response = iot_client.get_thing_shadow(
                thingName=thing
            )
            shadow_payload = json.loads(shadow_response['payload'].read())
            shadow_data = shadow_payload.get('state', {})
        except Exception as e:
            logger.info(f"Could not get shadow for {thing}: {str(e)}")
        
        result = {
            "thing_name": thing,
            "thing_arn": thing_info.get('thingArn'),
            "attributes": thing_info.get('attributes', {}),
            "shadow": shadow_data,
            "status": "online" if shadow_data else "unknown"
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_device_status: {str(e)}")
        return {"error": str(e)}

def tool_publish_command(thing_name, command, value=None):
    """
    Publish a command to an IoT device
    
    Args:
        thing_name: Name of the IoT thing
        command: Command to send (e.g., 'set_temperature', 'toggle_relay')
        value: Optional value for the command
        
    Returns:
        Result of the command publication
    """
    try:
        topic = f"devices/{thing_name}/commands"
        
        payload = {
            "command": command,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if value is not None:
            payload["value"] = value
        
        # Publish to IoT Core
        iot_client.publish(
            topic=topic,
            qos=1,
            payload=json.dumps(payload)
        )
        
        return {
            "status": "success",
            "thing_name": thing_name,
            "command": command,
            "topic": topic,
            "timestamp": payload["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error in publish_command: {str(e)}")
        return {"error": str(e)}

def tool_list_things(limit=25):
    """
    List all IoT things in the account
    
    Args:
        limit: Maximum number of things to return
        
    Returns:
        List of IoT things
    """
    try:
        things = []
        paginator = iot_core.get_paginator('list_things')
        
        for page in paginator.paginate(maxResults=min(limit, 250)):
            for thing in page.get('things', []):
                things.append({
                    'thing_name': thing.get('thingName'),
                    'thing_arn': thing.get('thingArn'),
                    'attributes': thing.get('attributes', {})
                })
                if len(things) >= limit:
                    break
            if len(things) >= limit:
                break
        
        return things
        
    except Exception as e:
        logger.error(f"Error in list_things: {str(e)}")
        return {"error": str(e)}

# Lambda handler
def lambda_handler(event, context):
    """
    AWS Lambda handler function for AgentCore MCP tools
    
    Args:
        event: Lambda event data with action_name and parameters
        context: Lambda context
        
    Returns:
        Lambda response with tool result
    """
    try:
        # Parse the incoming request
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract the tool name from the event
        tool_name = event.get('action_name') or event.get('tool_name')
        result = None
        
        # Call the appropriate function based on tool_name
        if tool_name == 'analyze_sensor_data':
            sensor_data = event.get('sensor_data', {})
            result = tool_analyze_sensor_data(sensor_data)
        
        elif tool_name == 'get_device_status':
            thing_name = event.get('thing_name') or event.get('device_id')
            result = tool_get_device_status(thing_name)
        
        elif tool_name == 'publish_command':
            thing_name = event.get('thing_name') or event.get('device_id')
            command = event.get('command')
            value = event.get('value')
            result = tool_publish_command(thing_name, command, value)
        
        elif tool_name == 'list_things':
            limit = event.get('limit', 25)
            result = tool_list_things(limit)
        
        else:
            available_tools = [
                'analyze_sensor_data',
                'get_device_status',
                'publish_command',
                'list_things'
            ]
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f"Unknown tool: {tool_name}",
                    'available_tools': available_tools
                })
            }
        
        # Return the result
        return {
            'statusCode': 200,
            'body': json_dumps(result)
        }
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"Internal server error: {str(e)}"
            })
        }

