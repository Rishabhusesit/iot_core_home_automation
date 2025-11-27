"""
AgentCore agent configuration with Lambda tools for IoT queries and control
"""
import json

# AgentCore tool definitions for IoT operations
IOT_AGENT_TOOLS = [
    {
        "name": "query_devices",
        "description": "Query IoT devices from DynamoDB. Use this when user asks to 'show all devices', 'list devices', or 'get device data'.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["all", "latest", "by_device"],
                    "description": "Type of query: 'all' for all devices, 'latest' for most recent data, 'by_device' for specific device"
                },
                "device_id": {
                    "type": "string",
                    "description": "Optional device ID to filter results"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10
                }
            }
        }
    },
    {
        "name": "get_temperature",
        "description": "Get temperature reading from an IoT device. Use this when user asks about temperature, 'what is the temperature', 'how hot is it', etc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID (defaults to ESP32_SmartDevice)"
                },
                "location": {
                    "type": "string",
                    "description": "Optional location name (e.g., 'bedroom', 'living room')"
                }
            }
        }
    },
    {
        "name": "control_device",
        "description": "Control IoT device actions like turning on/off lights or relays. Use this when user wants to 'turn on light', 'turn off bedroom light', 'toggle relay', etc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID to control"
                },
                "action": {
                    "type": "string",
                    "description": "Action to perform: 'turn_on_light', 'turn_off_light', 'toggle_relay', etc."
                },
                "value": {
                    "type": "integer",
                    "description": "Optional value (e.g., relay number 1-4)"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "get_device_summary",
        "description": "Get comprehensive summary of device status including all sensor readings. Use this when user asks for 'device status', 'device info', or 'what's the status'.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID (defaults to ESP32_SmartDevice)"
                }
            }
        }
    }
]

def get_lambda_tool_config(lambda_arn):
    """
    Generate AgentCore tool configuration that calls Lambda function
    
    Args:
        lambda_arn: ARN of the Lambda function
        
    Returns:
        List of tool configurations
    """
    tools = []
    
    for tool_def in IOT_AGENT_TOOLS:
        tool_config = {
            "name": tool_def["name"],
            "description": tool_def["description"],
            "inputSchema": tool_def["inputSchema"],
            "action": {
                "actionExecutor": "lambda",
                "lambda": {
                    "lambdaArn": lambda_arn,
                    "toolName": tool_def["name"]
                }
            }
        }
        tools.append(tool_config)
    
    return tools

def create_agent_instructions():
    """Create agent instructions for IoT device management"""
    return """You are an AI assistant for managing IoT smart home devices. 

Your capabilities:
1. Query device data from DynamoDB (temperature, humidity, motion, etc.)
2. Control devices (turn on/off lights, relays, etc.)
3. Provide device status summaries

When users ask questions:
- "Show me all devices" → Use query_devices tool with query_type="all"
- "What is the temperature?" → Use get_temperature tool
- "Turn on bedroom light" → Use control_device tool with action="turn_on_light"
- "Device status" → Use get_device_summary tool

Always provide clear, helpful responses with the actual sensor data and confirmations of actions taken."""


