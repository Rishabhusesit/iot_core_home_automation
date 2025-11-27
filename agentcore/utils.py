"""
Utility functions for AgentCore setup
"""
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def create_agentcore_client():
    """
    Create AgentCore client for control plane operations
    """
    region = os.getenv('AWS_REGION', 'us-east-1')
    boto_session = boto3.Session(region_name=region)
    agentcore_client = boto_session.client('bedrock-agentcore-control')
    return boto_session, agentcore_client

def get_gateway_endpoint(agentcore_client, gateway_id):
    """
    Get gateway endpoint URL from gateway ID
    """
    try:
        # API uses gatewayIdentifier not gatewayId
        response = agentcore_client.get_gateway(gatewayIdentifier=gateway_id)
        gateway_arn = response.get('gatewayArn')
        
        # Extract region and account from ARN
        # Format: arn:aws:bedrock-agentcore:region:account:gateway/gateway-id
        if gateway_arn:
            parts = gateway_arn.split(':')
            region = parts[3]
            gateway_id_from_arn = parts[5].split('/')[1]
            
            # Construct endpoint URL
            endpoint = f"https://{gateway_id_from_arn}.gateway.bedrock-agentcore.{region}.amazonaws.com"
            return endpoint
    except Exception as e:
        print(f"Error getting gateway endpoint: {e}")
        return None
    
    return None

