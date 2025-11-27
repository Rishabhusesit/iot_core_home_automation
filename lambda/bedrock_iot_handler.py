"""
AWS Lambda Function: IoT to Bedrock Strands Agent Integration
Processes IoT messages and invokes Bedrock Strands Agent for AI analysis
Publishes results back to IoT topic
"""
import json
import boto3
import os
import uuid
from datetime import datetime

# Initialize AWS clients
iot_client = boto3.client('iot-data')
bedrock_runtime = boto3.client('bedrock-runtime')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

# Configuration
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
BEDROCK_AGENT_ID = os.environ.get('BEDROCK_AGENT_ID', '')
BEDROCK_AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'TSTALIASID')
USE_AGENT_CORE = os.environ.get('USE_AGENT_CORE', 'true').lower() == 'true'
RESPONSE_TOPIC = os.environ.get('RESPONSE_TOPIC', 'devices/ESP32_Device/ai_responses')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Session storage (in production, use DynamoDB or ElastiCache)
sessions = {}

def lambda_handler(event, context):
    """
    Lambda handler for processing IoT messages
    
    Event structure:
    {
        "topic": "devices/ESP32_Device/data",
        "payload": {
            "device_id": "ESP32_Device",
            "timestamp": "...",
            "sensor_data": {...}
        }
    }
    """
    try:
        # Extract message data
        if 'topic' in event:
            topic = event['topic']
            payload = event.get('payload', {})
        else:
            # Direct payload (from IoT Rule)
            payload = event
            topic = payload.get('topic', 'unknown')
        
        # Extract sensor data
        sensor_data = payload.get('sensor_data', {})
        device_id = payload.get('device_id', 'unknown')
        
        print(f"Processing message from device: {device_id}")
        print(f"Sensor data: {json.dumps(sensor_data)}")
        print(f"Using Agent Core: {USE_AGENT_CORE}")
        
        # Use Bedrock Agent Core if configured, otherwise fallback to direct invocation
        if USE_AGENT_CORE and BEDROCK_AGENT_ID:
            ai_response = invoke_bedrock_agent(sensor_data, device_id)
            analysis = parse_ai_response(ai_response)
            agent_used = True
    else:
        # Fallback to direct model invocation
        prompt = create_analysis_prompt(sensor_data)
        ai_response = invoke_bedrock(prompt)
        analysis = parse_ai_response(ai_response)
        agent_used = False
        
        # Create response message
        response_message = {
            'device_id': device_id,
            'original_timestamp': payload.get('timestamp'),
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'sensor_data': sensor_data,
            'ai_response': analysis,
            'model_used': BEDROCK_MODEL_ID,
            'agent_core_used': agent_used
        }
        
        # Publish response to IoT topic
        publish_to_iot(RESPONSE_TOPIC, response_message)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully processed and analyzed sensor data',
                'device_id': device_id,
                'analysis': analysis
            })
        }
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

def create_analysis_prompt(sensor_data):
    """Create prompt for AI analysis"""
    temperature = sensor_data.get('temperature', 'N/A')
    humidity = sensor_data.get('humidity', 'N/A')
    pressure = sensor_data.get('pressure', 'N/A')
    
    prompt = f"""You are an IoT sensor data analyst. Analyze the following sensor readings and provide a concise JSON response.

Sensor Data:
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Pressure: {pressure} hPa

Provide your analysis in this JSON format:
{{
  "assessment": "brief environmental assessment",
  "anomalies": ["any anomalies detected"],
  "recommendations": ["actionable recommendations"],
  "risk_level": "low|medium|high",
  "summary": "one sentence summary"
}}

Be concise and actionable."""
    
    return prompt

def get_or_create_session(device_id):
    """Get or create a session for device conversation"""
    if device_id not in sessions:
        sessions[device_id] = str(uuid.uuid4())
    return sessions[device_id]

def invoke_bedrock_agent(sensor_data, device_id):
    """Invoke Bedrock Agent Core for analysis"""
    try:
        # Get or create session
        session_id = get_or_create_session(device_id)
        
        # Prepare input for agent
        input_text = f"""Analyze the following IoT sensor data and provide:
1. Current environmental assessment
2. Any anomalies or concerns
3. Recommendations for optimization
4. Suggested actions if needed

Sensor Data:
- Temperature: {sensor_data.get('temperature', 'N/A')}°C
- Humidity: {sensor_data.get('humidity', 'N/A')}%
- Pressure: {sensor_data.get('pressure', 'N/A')} hPa
- Motion Detected: {sensor_data.get('motion', False)}
- Timestamp: {sensor_data.get('timestamp', 'N/A')}

Provide a comprehensive analysis in JSON format:
{{
  "assessment": "brief environmental assessment",
  "anomalies": ["list of any anomalies"],
  "recommendations": ["actionable recommendations"],
  "risk_level": "low|medium|high",
  "actions": ["suggested actions if any"],
  "summary": "one sentence summary"
}}"""
        
        # Invoke agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=BEDROCK_AGENT_ID,
            agentAliasId=BEDROCK_AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=input_text,
            enableTrace=True
        )
        
        # Process streaming response
        completion = ""
        for event in response:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    chunk_data = json.loads(chunk['bytes'].decode('utf-8'))
                    if 'text' in chunk_data:
                        completion += chunk_data['text']
                elif 'text' in chunk:
                    completion += chunk['text']
        
        print(f"Agent response received (session: {session_id})")
        return completion
        
    except Exception as e:
        print(f"Agent invocation failed: {str(e)}, falling back to direct model")
        # Fallback to direct invocation
        prompt = create_analysis_prompt(sensor_data)
        return invoke_bedrock(prompt)

def invoke_bedrock(prompt):
    """Invoke AWS Bedrock model directly (fallback)"""
    # Prepare request body for Claude
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    # Invoke model
    response = bedrock_runtime.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body)
    )
    
    # Parse response
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

def parse_ai_response(ai_text):
    """Parse AI response text to extract JSON"""
    try:
        # Try to extract JSON from response
        # AI might wrap JSON in markdown code blocks
        if '```json' in ai_text:
            start = ai_text.find('```json') + 7
            end = ai_text.find('```', start)
            json_str = ai_text[start:end].strip()
        elif '```' in ai_text:
            start = ai_text.find('```') + 3
            end = ai_text.find('```', start)
            json_str = ai_text[start:end].strip()
        else:
            # Try to find JSON object
            start = ai_text.find('{')
            end = ai_text.rfind('}') + 1
            json_str = ai_text[start:end]
        
        return json.loads(json_str)
    except:
        # If parsing fails, return as text
        return {'raw_response': ai_text}

def publish_to_iot(topic, message):
    """Publish message to IoT topic"""
    iot_endpoint = os.environ.get('IOT_ENDPOINT')
    if not iot_endpoint:
        # Get endpoint from IoT Core
        iot = boto3.client('iot')
        response = iot.describe_endpoint(endpointType='iot:Data-ATS')
        iot_endpoint = response['endpointAddress']
    
    # Publish to IoT topic
    iot_client.publish(
        topic=topic,
        qos=1,
        payload=json.dumps(message)
    )
    
    print(f"Published response to topic: {topic}")

