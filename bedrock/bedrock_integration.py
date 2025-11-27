"""
AWS Bedrock Integration Service
Processes IoT sensor data using AWS Bedrock AI models
Supports both direct model invocation and Bedrock Agent Core
"""
import json
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Try to import Agent Core (optional)
try:
    from bedrock.bedrock_agent_core import BedrockAgentCore
    AGENT_CORE_AVAILABLE = True
except ImportError:
    AGENT_CORE_AVAILABLE = False

class BedrockIntegration:
    def __init__(self, use_agent_core=None):
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bedrock = boto3.client(
            'bedrock',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.iot_topic = os.getenv('BEDROCK_RESPONSE_TOPIC', 'devices/ESP32_Device/ai_responses')
        
        # Agent Core support
        self.use_agent_core = use_agent_core if use_agent_core is not None else os.getenv('USE_AGENT_CORE', 'false').lower() == 'true'
        self.agent_core = None
        
        if self.use_agent_core and AGENT_CORE_AVAILABLE:
            try:
                self.agent_core = BedrockAgentCore()
                print("✅ Bedrock Agent Core initialized")
            except Exception as e:
                print(f"⚠️  Agent Core initialization failed: {str(e)}, using direct invocation")
                self.use_agent_core = False
        
    def analyze_sensor_data(self, sensor_data, device_id=None):
        """
        Analyze sensor data using AWS Bedrock AI (with Agent Core support)
        
        Args:
            sensor_data: Dictionary containing sensor readings
            device_id: Device identifier for Agent Core session management
            
        Returns:
            AI-generated analysis and recommendations
        """
        try:
            # Use Agent Core if enabled and available
            if self.use_agent_core and self.agent_core:
                result = self.agent_core.analyze_sensor_data_with_agent(sensor_data, device_id)
                return {
                    'success': result.get('success', True),
                    'analysis': result.get('analysis', ''),
                    'timestamp': result.get('timestamp', datetime.utcnow().isoformat()),
                    'agent_core_used': result.get('agent_used', True),
                    'session_id': result.get('session_id')
                }
            else:
                # Fallback to direct model invocation
                prompt = self._create_analysis_prompt(sensor_data)
                response = self._invoke_bedrock(prompt)
                
                return {
                    'success': True,
                    'analysis': response,
                    'timestamp': datetime.utcnow().isoformat(),
                    'agent_core_used': False
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'agent_core_used': False
            }
    
    def _create_analysis_prompt(self, sensor_data):
        """Create a prompt for AI analysis"""
        prompt = f"""You are an IoT sensor data analyst. Analyze the following sensor readings and provide:
1. Current environmental assessment
2. Any anomalies or concerns
3. Recommendations for optimization

Sensor Data:
- Temperature: {sensor_data.get('temperature', 'N/A')}°C
- Humidity: {sensor_data.get('humidity', 'N/A')}%
- Pressure: {sensor_data.get('pressure', 'N/A')} hPa
- Timestamp: {sensor_data.get('timestamp', 'N/A')}

Provide a concise, actionable analysis in JSON format with the following structure:
{{
  "assessment": "brief environmental assessment",
  "anomalies": ["list of any anomalies"],
  "recommendations": ["list of recommendations"],
  "risk_level": "low|medium|high"
}}"""
        return prompt
    
    def _invoke_bedrock(self, prompt):
        """Invoke AWS Bedrock model"""
        # Prepare request body based on model type
        if 'claude' in self.model_id.lower():
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        elif 'llama' in self.model_id.lower():
            body = {
                "prompt": prompt,
                "max_gen_len": 512,
                "temperature": 0.7
            }
        else:
            # Default to Claude format
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        
        # Invoke model
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        if 'claude' in self.model_id.lower():
            return response_body['content'][0]['text']
        elif 'llama' in self.model_id.lower():
            return response_body['generation']
        else:
            return str(response_body)
    
    def process_iot_message(self, iot_message):
        """
        Process incoming IoT message and generate AI response
        
        Args:
            iot_message: MQTT message from IoT device
            
        Returns:
            Processed response with AI analysis
        """
        try:
            # Parse IoT message
            if isinstance(iot_message, str):
                data = json.loads(iot_message)
            else:
                data = iot_message
            
            # Extract sensor data
            sensor_data = data.get('sensor_data', {})
            device_id = data.get('device_id', 'unknown')
            
            # Analyze with Bedrock
            analysis = self.analyze_sensor_data(sensor_data)
            
            # Format response
            response = {
                'device_id': device_id,
                'original_timestamp': data.get('timestamp'),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'sensor_data': sensor_data,
                'ai_analysis': analysis,
                'model_used': self.model_id
            }
            
            return response
            
        except Exception as e:
            return {
                'error': f'Failed to process message: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def list_available_models(self):
        """List available Bedrock models"""
        try:
            response = self.bedrock.list_foundation_models()
            models = response.get('modelSummaries', [])
            
            print("Available Bedrock Models:")
            print("=" * 80)
            for model in models:
                print(f"Model ID: {model['modelId']}")
                print(f"Name: {model['modelName']}")
                print(f"Provider: {model['providerName']}")
                print("-" * 80)
            
            return models
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return []


def main():
    """Test Bedrock integration"""
    bedrock = BedrockIntegration()
    
    # Test with sample sensor data
    sample_data = {
        'temperature': 28.5,
        'humidity': 65.0,
        'pressure': 1013.25,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    print("Testing Bedrock Integration...")
    print("=" * 80)
    
    # List available models
    bedrock.list_available_models()
    
    print("\nAnalyzing sensor data...")
    result = bedrock.analyze_sensor_data(sample_data)
    
    if result['success']:
        print("\n✅ Analysis successful!")
        print("\nAI Response:")
        print(result['analysis'])
    else:
        print(f"\n❌ Analysis failed: {result['error']}")


if __name__ == "__main__":
    main()

