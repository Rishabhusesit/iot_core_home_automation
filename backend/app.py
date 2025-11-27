"""
Backend API Server for ESP32 IoT Dashboard
Provides REST API for web interface and manages IoT data
Includes Cognito authentication support
"""
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import boto3
import json
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import threading
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = Flask(__name__, 
            static_folder='../web', 
            static_url_path='/static',
            template_folder='../web')
# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/healthz', methods=['GET'])
def healthcheck():
    """Simple health endpoint for container orchestration."""
    return jsonify({'status': 'ok'}), 200

# Initialize Cognito auth (optional)
try:
    from auth.cognito_auth import CognitoAuth
    cognito_auth = CognitoAuth()
    AUTH_ENABLED = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'
except ImportError:
    cognito_auth = None
    AUTH_ENABLED = False

# AWS IoT Core client
iot_client = boto3.client('iot-data', region_name=os.getenv('AWS_REGION', 'us-east-1'))
iot_endpoint = os.getenv('AWS_IOT_ENDPOINT', '')

# Device configuration
THING_NAME = os.getenv('THING_NAME', 'ESP32_SmartDevice')
COMMAND_TOPIC = f'devices/{THING_NAME}/commands'
DATA_TOPIC = f'devices/{THING_NAME}/data'
STATUS_TOPIC = f'devices/{THING_NAME}/status'
ALERTS_TOPIC = f'devices/{THING_NAME}/alerts'

# In-memory data store (in production, use database)
# This will be updated by iot_subscriber.py
try:
    from iot_subscriber import get_device_data
    device_data = get_device_data()
except:
    device_data = {
        'sensor_data': {},
        'relays': {},
        'status': 'offline',
        'last_update': None,
        'uptime_seconds': 0,
        'wifi_rssi': 0
    }

ai_insights = []

def invoke_bedrock_model(prompt, max_tokens=1500):
    """Invoke the configured Bedrock model and return the completion text."""
    bedrock_runtime = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    bedrock_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = bedrock_runtime.invoke_model(
        modelId=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-haiku-20240307-v1:0'),
        body=json.dumps(bedrock_payload)
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

def fetch_latest_device_state():
    """Fetch the latest device state from DynamoDB, IoT Shadow, or cached data."""
    global device_data
    
    # Try to get latest data from DynamoDB (if IoT Rule is set up)
    try:
        table_name = os.getenv('DYNAMODB_TABLE', f'ESP32_{THING_NAME}_Data')
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        table = dynamodb.Table(table_name)
        
        response = table.query(
            KeyConditionExpression='device_id = :device_id',
            ExpressionAttributeValues={
                ':device_id': THING_NAME
            },
            ScanIndexForward=False,
            Limit=1
        )
        
        if response.get('Items'):
            item = response['Items'][0]
            
            if 'sensor_data' in item:
                if isinstance(item['sensor_data'], dict):
                    device_data['sensor_data'] = item['sensor_data']
                else:
                    device_data['sensor_data'] = json.loads(item['sensor_data'])
            
            if 'relays' in item:
                if isinstance(item['relays'], dict):
                    device_data['relays'] = item['relays']
                else:
                    device_data['relays'] = json.loads(item['relays'])
            
            if 'uptime_seconds' in item:
                device_data['uptime_seconds'] = int(item['uptime_seconds'])
            if 'wifi_rssi' in item:
                device_data['wifi_rssi'] = int(item['wifi_rssi'])
            if 'timestamp' in item:
                timestamp_str = item['timestamp']
                try:
                    device_data['last_update'] = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except Exception:
                    device_data['last_update'] = datetime.utcnow()
            
            device_data['status'] = 'online'
    except Exception:
        pass
    
    # Try to get latest data from IoT Shadow (real-time)
    try:
        if iot_endpoint:
            shadow_client = boto3.client(
                'iot-data',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                endpoint_url=f"https://{iot_endpoint}"
            )
            
            try:
                response = shadow_client.get_thing_shadow(thingName=THING_NAME)
                shadow_payload = json.loads(response['payload'].read())
                
                if 'state' in shadow_payload and 'reported' in shadow_payload['state']:
                    reported = shadow_payload['state']['reported']
                    
                    if 'sensor_data' in reported:
                        device_data['sensor_data'] = reported['sensor_data']
                    if 'relays' in reported:
                        device_data['relays'] = reported['relays']
                    if 'uptime_seconds' in reported:
                        device_data['uptime_seconds'] = reported['uptime_seconds']
                    if 'wifi_rssi' in reported:
                        device_data['wifi_rssi'] = reported['wifi_rssi']
                    
                    device_data['status'] = 'online'
                    device_data['last_update'] = datetime.utcnow()
                    
            except shadow_client.exceptions.ResourceNotFoundException:
                if device_data.get('last_update'):
                    try:
                        last_update = device_data['last_update']
                        now = datetime.utcnow()
                        if isinstance(last_update, str):
                            last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                            if last_update.tzinfo is not None:
                                last_update = last_update.replace(tzinfo=None)
                        elif hasattr(last_update, 'tzinfo') and last_update.tzinfo is not None:
                            last_update = last_update.replace(tzinfo=None)
                        
                        time_diff = (now - last_update).total_seconds()
                        if time_diff > 30:
                            device_data['status'] = 'offline'
                    except Exception:
                        pass
            except Exception as e:
                print(f"Shadow query failed: {e}")
    except Exception:
        pass
    
    # Also try IoT subscriber if available
    try:
        from iot_subscriber import get_device_data
        current_data = get_device_data()
        if current_data:
            device_data.update(current_data)
    except Exception:
        pass
    
    # Determine status based on last update
    if device_data.get('last_update'):
        try:
            if isinstance(device_data['last_update'], str):
                last_update = datetime.fromisoformat(device_data['last_update'].replace('Z', '+00:00'))
                if last_update.tzinfo is not None:
                    last_update = last_update.replace(tzinfo=None)
                now = datetime.utcnow()
                time_diff = (now - last_update).total_seconds()
            else:
                last_update = device_data['last_update']
                now = datetime.utcnow()
                if hasattr(last_update, 'tzinfo') and last_update.tzinfo is not None:
                    last_update = last_update.replace(tzinfo=None)
                time_diff = (now - last_update).total_seconds()
        except Exception as e:
            print(f"Error calculating time difference: {e}")
            time_diff = 999
        
        if time_diff > 30:
            device_data['status'] = 'offline'
        else:
            device_data['status'] = 'online'
    
    if not device_data.get('sensor_data') or not device_data['sensor_data'].get('temperature'):
        pass
    
    return device_data

@app.route('/')
def index():
    """Serve dashboard HTML"""
    import os
    # Try multiple paths for dashboard (local dev vs container)
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web', 'dashboard.html'),
        '/web/dashboard.html',
        os.path.join(os.path.dirname(__file__), '..', 'web', 'dashboard.html')
    ]
    
    for dashboard_path in possible_paths:
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                return f.read()
    
    # Fallback: return a simple message
    return """
    <html>
        <head><title>ESP32 IoT Dashboard</title></head>
        <body>
            <h1>ESP32 IoT Dashboard</h1>
            <p>Dashboard file not found. Please check the deployment configuration.</p>
            <p>API is available at <a href="/api/device/status">/api/device/status</a></p>
        </body>
    </html>
    """

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user with Cognito"""
    if not AUTH_ENABLED or not cognito_auth:
        return jsonify({
            'success': False,
            'error': 'Authentication not enabled'
        }), 400
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password required'
            }), 400
        
        result = cognito_auth.authenticate_user(username, password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'access_token': result['access_token'],
                'id_token': result.get('id_token', ''),
                'expires_in': result['expires_in']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """Verify access token"""
    if not AUTH_ENABLED or not cognito_auth:
        return jsonify({
            'success': False,
            'error': 'Authentication not enabled'
        }), 400
    
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({
            'success': False,
            'error': 'Missing authorization header'
        }), 401
    
    token = auth_header.replace('Bearer ', '')
    result = cognito_auth.verify_token(token)
    
    if result['success']:
        return jsonify({
            'success': True,
            'username': result['username'],
            'user_attributes': result['user_attributes']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 401

@app.route('/api/device/status', methods=['GET'])
def get_device_status():
    """Get current device status and sensor data"""
    try:
        current_state = fetch_latest_device_state()
        return jsonify({
            'success': True,
            'device_id': THING_NAME,
            'status': current_state.get('status', 'offline'),
            'sensor_data': current_state.get('sensor_data', {}),
            'relays': current_state.get('relays', {}),
            'uptime_seconds': current_state.get('uptime_seconds', 0),
            'wifi_rssi': current_state.get('wifi_rssi', 0),
            'last_update': str(current_state.get('last_update')) if current_state.get('last_update') else None
        })
    except Exception as e:
        print(f"Error in get_device_status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'device_id': THING_NAME,
            'status': 'error',
            'sensor_data': {},
            'relays': {},
            'uptime_seconds': 0,
            'wifi_rssi': 0,
            'last_update': None
        }), 500

def publish_relay_command(relay_num, state):
    """Publish relay command to IoT Core and update local cache."""
    global device_data
    command = {
        'command': 'relay_control',
        'relay': relay_num,
        'state': state,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    iot_client.publish(
        topic=COMMAND_TOPIC,
        qos=1,
        payload=json.dumps(command)
    )
    
    if 'relays' not in device_data:
        device_data['relays'] = {}
    device_data['relays'][f'relay_{relay_num}'] = state
    
    return command

def detect_command_from_question(question):
    """Infer relay command intent from a natural language question."""
    text = (question or '').lower()
    desired_state = None
    
    if any(phrase in text for phrase in ['turn on', 'switch on', 'activate', 'power on']):
        desired_state = True
    elif any(phrase in text for phrase in ['turn off', 'switch off', 'deactivate', 'power off']):
        desired_state = False
    else:
        return None
    
    relay_num = 1
    label = 'relay 1'
    
    if 'relay 2' in text or 'second relay' in text or 'living room' in text:
        relay_num = 2
        label = 'relay 2'
    elif 'relay 3' in text or 'third relay' in text:
        relay_num = 3
        label = 'relay 3'
    elif 'relay 4' in text or 'fourth relay' in text:
        relay_num = 4
        label = 'relay 4'
    elif 'bedroom' in text:
        relay_num = 1
        label = 'bedroom relay'
    
    return {
        'relay': relay_num,
        'state': desired_state,
        'label': label
    }

@app.route('/api/device/relay', methods=['POST'])
def control_relay():
    """Control relay via MQTT command"""
    try:
        data = request.json
        relay_num = data.get('relay')
        state = data.get('state')
        
        if not relay_num or state is None:
            return jsonify({'success': False, 'error': 'Missing relay or state'}), 400
        
        command = publish_relay_command(relay_num, state)
        
        return jsonify({
            'success': True,
            'message': f'Relay {relay_num} command sent',
            'relay': relay_num,
            'state': state,
            'timestamp': command['timestamp']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device/command', methods=['POST'])
def send_command():
    """Send custom command to device"""
    try:
        data = request.json
        command = data.get('command')
        
        if not command:
            return jsonify({'success': False, 'error': 'Missing command'}), 400
        
        mqtt_command = {
            'command': command,
            'timestamp': datetime.utcnow().isoformat(),
            **data.get('params', {})
        }
        
        response = iot_client.publish(
            topic=COMMAND_TOPIC,
            qos=1,
            payload=json.dumps(mqtt_command)
        )
        
        return jsonify({
            'success': True,
            'message': 'Command sent successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def _perform_ai_analysis(sensor_data):
    """Internal function to perform AI analysis on sensor data"""
    try:
        # Prepare prompt for Bedrock analysis
        enhanced_prompt = f"""You are an AI assistant analyzing IoT sensor data from an ESP32 device.

Sensor Data:
- Temperature: {sensor_data.get('temperature', 'N/A')}°C
- Humidity: {sensor_data.get('humidity', 'N/A')}%
- Motion Detected: {sensor_data.get('motion_detected', False)}
- Device Uptime: {device_data.get('uptime_seconds', 0)} seconds
- WiFi Signal Strength: {device_data.get('wifi_rssi', 'N/A')} dBm

Please provide a comprehensive analysis including:
1. **Environmental Assessment**: Current conditions and what they mean
2. **Anomalies**: Any unusual readings or patterns
3. **Recommendations**: Actionable advice for optimization
4. **Risk Level**: Low/Medium/High based on current readings
5. **Suggested Actions**: Specific steps if intervention is needed

Format your response in a clear, structured way that's easy to read."""
        
        completion = invoke_bedrock_model(enhanced_prompt)
        
        # Store insight
        insight = {
            'timestamp': datetime.utcnow().isoformat(),
            'sensor_data': sensor_data,
            'analysis': completion
        }
        ai_insights.append(insight)
        if len(ai_insights) > 20:
            ai_insights.pop(0)
        
        return completion, None  # Return analysis and None for error
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"AI Analysis error: {error_details}")
        return None, f'AI Analysis failed: {str(e)}'

@app.route('/api/ai/analyze', methods=['POST'])
def analyze_sensor_data():
    """Send sensor data to AgentCore for AI analysis"""
    try:
        data = request.json or {}
        sensor_data = data.get('sensor_data', device_data.get('sensor_data', {}))
        
        # Perform AI analysis
        completion, error = _perform_ai_analysis(sensor_data)
        
        if error:
            return jsonify({
                'success': False,
                'error': error,
                'hint': 'Check AWS credentials and Bedrock model access'
            }), 500
        
        return jsonify({
            'success': True,
            'analysis': completion,
            'timestamp': datetime.utcnow().isoformat(),
            'sensor_data': sensor_data,
            'method': 'bedrock_direct'
        })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"AI Analysis outer error: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai/trigger', methods=['POST'])
def trigger_ai_analysis():
    """Trigger AI analysis with current sensor data"""
    try:
        # Use current device data
        sensor_data = device_data.get('sensor_data', {})
        
        if not sensor_data or not sensor_data.get('temperature'):
            return jsonify({
                'success': False,
                'error': 'No sensor data available. Wait for ESP32 to send data first.'
            }), 400
        
        # Perform AI analysis using the internal function
        completion, error = _perform_ai_analysis(sensor_data)
        
        if error:
            return jsonify({
                'success': False,
                'error': error,
                'hint': 'Check AWS credentials and Bedrock model access'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'AI analysis triggered successfully',
            'analysis': completion
        })
                
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Trigger AI analysis error: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai/insights', methods=['GET'])
def get_ai_insights():
    """Get AI insights and recommendations"""
    # Format insights for frontend
    formatted_insights = []
    for insight in ai_insights:
        formatted_insights.append({
            'title': f"Analysis - {insight.get('timestamp', 'Unknown time')[:19]}",
            'description': insight.get('analysis', 'No analysis available'),
            'timestamp': insight.get('timestamp'),
            'sensor_data': insight.get('sensor_data', {})
        })
    
    return jsonify({
        'success': True,
        'insights': formatted_insights
    })

@app.route('/api/ai/query', methods=['POST'])
def handle_natural_language_query():
    """Handle natural language queries via AgentCore"""
    try:
        data = request.json or {}
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Get AgentCore Gateway URL
        gateway_url = os.getenv('GATEWAY_URL', '')
        bearer_token = os.getenv('BEARER_TOKEN', '')
        
        if not gateway_url:
            # Fallback: Use direct Bedrock for simple queries
            return handle_direct_query(query)
        
        # Use AgentCore Gateway for natural language queries
        import requests
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }
        
        # AgentCore Gateway expects MCP-style request
        gateway_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "natural_language_query",
                "arguments": {
                    "query": query,
                    "context": {
                        "device_id": THING_NAME,
                        "sensor_data": device_data.get('sensor_data', {})
                    }
                }
            }
        }
        
        try:
            response = requests.post(
                f"{gateway_url}/invoke",
                json=gateway_payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    answer = result['result'].get('content', '') or str(result['result'])
                elif 'response' in result:
                    answer = result['response']
                else:
                    answer = str(result)
                
                return jsonify({
                    'success': True,
                    'response': answer,
                    'method': 'agentcore_gateway'
                })
            else:
                raise Exception(f'Gateway returned {response.status_code}: {response.text}')
                
        except Exception as gateway_error:
            # Fallback to direct query handling
            print(f"Gateway invocation failed: {gateway_error}, using direct query...")
            return handle_direct_query(query)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def handle_direct_query(query):
    """Handle query directly using Bedrock (fallback when AgentCore not available)"""
    try:
        import boto3
        
        query_lower = query.lower()
        
        # Simple pattern matching for common queries
        if 'temperature' in query_lower or 'temp' in query_lower:
            sensor_data = device_data.get('sensor_data', {})
            temp = sensor_data.get('temperature', 'N/A')
            return jsonify({
                'success': True,
                'response': f"The current temperature is {temp}°C",
                'method': 'direct_pattern'
            })
        
        elif 'humidity' in query_lower:
            sensor_data = device_data.get('sensor_data', {})
            humidity = sensor_data.get('humidity', 'N/A')
            return jsonify({
                'success': True,
                'response': f"The current humidity is {humidity}%",
                'method': 'direct_pattern'
            })
        
        elif 'device' in query_lower and ('all' in query_lower or 'list' in query_lower or 'show' in query_lower):
            return jsonify({
                'success': True,
                'response': f"Device: {THING_NAME}\nStatus: {device_data.get('status', 'unknown')}\nTemperature: {device_data.get('sensor_data', {}).get('temperature', 'N/A')}°C\nHumidity: {device_data.get('sensor_data', {}).get('humidity', 'N/A')}%",
                'method': 'direct_pattern'
            })
        
        elif 'turn on' in query_lower or 'turn off' in query_lower:
            # Extract relay number if mentioned
            relay_num = 1
            if 'relay 1' in query_lower or 'one' in query_lower:
                relay_num = 1
            elif 'relay 2' in query_lower or 'two' in query_lower:
                relay_num = 2
            elif 'relay 3' in query_lower or 'three' in query_lower:
                relay_num = 3
            elif 'relay 4' in query_lower or 'four' in query_lower:
                relay_num = 4
            
            state = 'on' in query_lower
            command = {
                'relay': relay_num,
                'state': state
            }
            
            # Publish command
            iot_client.publish(
                topic=COMMAND_TOPIC,
                qos=1,
                payload=json.dumps({
                    'command': 'relay_control',
                    'relay': relay_num,
                    'state': state,
                    'timestamp': datetime.utcnow().isoformat()
                })
            )
            
            return jsonify({
                'success': True,
                'response': f"Command sent: Turn {'ON' if state else 'OFF'} Relay {relay_num}",
                'method': 'direct_pattern'
            })
        
        else:
            # Use Bedrock for complex queries
            bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            model_id = os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-haiku-20240307-v1:0')
            
            prompt = f"""You are an AI assistant for IoT smart home devices.

Current device data:
- Device: {THING_NAME}
- Status: {device_data.get('status', 'unknown')}
- Temperature: {device_data.get('sensor_data', {}).get('temperature', 'N/A')}°C
- Humidity: {device_data.get('sensor_data', {}).get('humidity', 'N/A')}%
- Motion: {device_data.get('sensor_data', {}).get('motion_detected', False)}

User query: {query}

Provide a helpful response based on the device data. If the user wants to control something, explain that you can help with that."""
            
            bedrock_payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            bedrock_response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(bedrock_payload)
            )
            
            result = json.loads(bedrock_response['body'].read())
            answer = result['content'][0]['text']
            
            return jsonify({
                'success': True,
                'response': answer,
                'method': 'bedrock_direct'
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data/history', methods=['GET'])
def get_data_history():
    """Get historical sensor data (mock - in production, query database)"""
    # In production, query DynamoDB or TimeStream
    return jsonify({
        'success': True,
        'data': [],
        'message': 'Historical data not implemented. Use AWS IoT Analytics or TimeStream.'
    })

@app.route('/api/device/alerts', methods=['GET'])
def get_alerts():
    """Get recent alerts"""
    # In production, query from database
    return jsonify({
        'success': True,
        'alerts': []
    })

# Simulate IoT message processing (in production, use IoT Rules → Lambda → API)
def process_iot_message():
    """Process incoming IoT messages (simulated)"""
    # In production, this would be triggered by IoT Rules → Lambda → API Gateway
    # or use IoT Core MQTT subscription
    pass

# Simulated data generation for demo purposes
def start_simulated_data_feed():
    """Generate simulated sensor data when no real IoT feed is available"""
    import random
    
    def generate_simulated_data():
        """Generate realistic sensor data"""
        global device_data
        
        if not device_data.get('sensor_data') or not device_data['sensor_data'].get('temperature'):
            # Initialize with simulated data
            device_data['sensor_data'] = {
                'temperature': round(random.uniform(22.0, 29.0), 2),
                'humidity': round(random.uniform(40.0, 65.0), 2),
                'pressure': round(random.uniform(995.0, 1015.0), 2),
                'motion_detected': random.choice([True, False])
            }
            device_data['relays'] = {
                'relay_1': random.choice([True, False]),
                'relay_2': random.choice([True, False]),
                'relay_3': random.choice([True, False]),
                'relay_4': random.choice([True, False])
            }
            device_data['uptime_seconds'] = random.randint(1000, 100000)
            device_data['wifi_rssi'] = random.randint(-75, -45)
            device_data['status'] = 'online'
            device_data['last_update'] = datetime.utcnow()
        else:
            # Update existing data with small variations
            current_temp = device_data['sensor_data'].get('temperature', 25.0)
            current_humidity = device_data['sensor_data'].get('humidity', 50.0)
            
            device_data['sensor_data']['temperature'] = round(
                max(20.0, min(30.0, current_temp + random.uniform(-0.5, 0.5))), 2
            )
            device_data['sensor_data']['humidity'] = round(
                max(35.0, min(70.0, current_humidity + random.uniform(-2.0, 2.0))), 2
            )
            device_data['sensor_data']['pressure'] = round(random.uniform(995.0, 1015.0), 2)
            device_data['sensor_data']['motion_detected'] = random.choice([True, False])
            device_data['uptime_seconds'] += 5
            device_data['wifi_rssi'] = random.randint(-75, -45)
            device_data['last_update'] = datetime.utcnow()
            device_data['status'] = 'online'
    
    def simulated_data_loop():
        """Background thread to continuously update simulated data"""
        while True:
            try:
                # Check if we have real data from DynamoDB or Shadow
                fetch_latest_device_state()
                
                # Only generate simulated data if no real data exists
                if not device_data.get('sensor_data') or not device_data['sensor_data'].get('temperature'):
                    generate_simulated_data()
                elif device_data.get('last_update'):
                    # Check if data is stale (older than 60 seconds)
                    try:
                        last_update = device_data['last_update']
                        if isinstance(last_update, str):
                            last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                            if last_update.tzinfo is not None:
                                last_update = last_update.replace(tzinfo=None)
                        elif hasattr(last_update, 'tzinfo') and last_update.tzinfo is not None:
                            last_update = last_update.replace(tzinfo=None)
                        
                        time_diff = (datetime.utcnow() - last_update).total_seconds()
                        if time_diff > 60:  # Data is stale, use simulated
                            generate_simulated_data()
                    except Exception:
                        generate_simulated_data()
                else:
                    generate_simulated_data()
            except Exception as e:
                print(f"Error in simulated data loop: {e}")
            
            time.sleep(5)  # Update every 5 seconds
    
    # Start simulated data thread
    threading.Thread(target=simulated_data_loop, daemon=True).start()
    print("✅ Simulated data feed started")

# Background thread to poll IoT for latest data
def update_device_data():
    """Periodically query IoT Shadow and DynamoDB for latest device data"""
    while True:
        try:
            # First, try to fetch from DynamoDB (most reliable)
            fetch_latest_device_state()
            
            # Query IoT Shadow for latest data
            if iot_endpoint:
                shadow_client = boto3.client(
                    'iot-data',
                    region_name=os.getenv('AWS_REGION', 'us-east-1'),
                    endpoint_url=f"https://{iot_endpoint}"
                )
                
                try:
                    response = shadow_client.get_thing_shadow(thingName=THING_NAME)
                    shadow_payload = json.loads(response['payload'].read())
                    
                    if 'state' in shadow_payload and 'reported' in shadow_payload['state']:
                        reported = shadow_payload['state']['reported']
                        
                        # Update device_data with shadow data
                        if 'sensor_data' in reported:
                            device_data['sensor_data'] = reported['sensor_data']
                        if 'relays' in reported:
                            device_data['relays'] = reported['relays']
                        if 'uptime_seconds' in reported:
                            device_data['uptime_seconds'] = reported['uptime_seconds']
                        if 'wifi_rssi' in reported:
                            device_data['wifi_rssi'] = reported['wifi_rssi']
                        
                        device_data['status'] = 'online'
                        device_data['last_update'] = datetime.utcnow()
                        
                except shadow_client.exceptions.ResourceNotFoundException:
                    # Shadow doesn't exist - ESP32 may not be updating shadow
                    # Try to get data from recent MQTT messages via IoT Data API
                    # For now, mark as offline if no recent update
                    if device_data.get('last_update'):
                        try:
                            last_update = device_data['last_update']
                            now = datetime.utcnow()
                            
                            # Handle timezone-aware or naive datetimes
                            if isinstance(last_update, str):
                                last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                                if last_update.tzinfo is not None:
                                    last_update = last_update.replace(tzinfo=None)
                            elif hasattr(last_update, 'tzinfo') and last_update.tzinfo is not None:
                                last_update = last_update.replace(tzinfo=None)
                            
                            time_diff = (now - last_update).total_seconds()
                            if time_diff > 30:
                                device_data['status'] = 'offline'
                        except Exception as e:
                            print(f"Error calculating time difference in update_device_data: {e}")
                            pass
                except Exception as e:
                    # Shadow query failed, continue with existing data
                    pass
        except Exception as e:
            # IoT client setup failed
            pass
        
        # Also check if we have recent data
        if device_data.get('last_update'):
            try:
                last_update = device_data['last_update']
                now = datetime.utcnow()
                
                # Handle timezone-aware or naive datetimes
                if isinstance(last_update, str):
                    last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                    if last_update.tzinfo is not None:
                        last_update = last_update.replace(tzinfo=None)
                elif hasattr(last_update, 'tzinfo') and last_update.tzinfo is not None:
                    last_update = last_update.replace(tzinfo=None)
                
                time_diff = (now - last_update).total_seconds()
                if time_diff > 30:
                    device_data['status'] = 'offline'
            except Exception as e:
                print(f"Error calculating time difference in update_device_data: {e}")
                pass
        
        time.sleep(5)  # Poll every 5 seconds

# Start background thread
threading.Thread(target=update_device_data, daemon=True).start()

# Check if simulated data should be enabled
SIMULATED_DATA_ENABLED = os.getenv('ENABLE_SIMULATED_DATA', 'true').lower() == 'true'

if __name__ == '__main__':
    print("=" * 60)
    print("ESP32 IoT Backend API Server")
    print("=" * 60)
    print(f"Device: {THING_NAME}")
    print(f"IoT Endpoint: {iot_endpoint}")
    print(f"Command Topic: {COMMAND_TOPIC}")
    print(f"Simulated Data: {'Enabled' if SIMULATED_DATA_ENABLED else 'Disabled'}")
    print("=" * 60)
    print("\nStarting server on http://localhost:5000")
    print("Dashboard: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    # Start simulated data feed if enabled
    if SIMULATED_DATA_ENABLED:
        start_simulated_data_feed()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

