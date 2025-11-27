"""
Create AgentCore Gateway for IoT Sensor Analysis
Adapted from device-management-agent
"""
import boto3
import os
import sys
from dotenv import load_dotenv, set_key
from bedrock_agentcore_starter_toolkit.operations.gateway import GatewayClient

# Load environment variables
# Look for .env in parent directory (project root)
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path)  # Load from project root
load_dotenv()  # Also try current directory

# Get environment variables
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
GATEWAY_NAME = os.getenv('GATEWAY_NAME', 'IoT-Sensor-Analysis-Gateway')
GATEWAY_DESCRIPTION = os.getenv('GATEWAY_DESCRIPTION', 'Gateway for IoT Sensor Data Analysis')
ROLE_ARN = os.getenv('ROLE_ARN')

print(f"AWS Region: {AWS_REGION}")
print(f"Gateway Name: {GATEWAY_NAME}")

if not ROLE_ARN:
    print("Error: ROLE_ARN not found in .env file")
    print("Please create an IAM role with AgentCore permissions and set ROLE_ARN in .env")
    sys.exit(1)

# Initialize the Bedrock Agent Core Control client
bedrock_agent_core_client = boto3.client(
    'bedrock-agentcore-control', 
    region_name=AWS_REGION
)

# For basic setup, we need to provide a customJWTAuthorizer
# Even if we're not using Cognito, the API requires this structure
# We'll create a minimal configuration that can be updated later
COGNITO_USERPOOL_ID = os.getenv('COGNITO_USERPOOL_ID')
COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')

if COGNITO_USERPOOL_ID and COGNITO_CLIENT_ID:
    # Use Cognito if available
    auth_config = {
        "customJWTAuthorizer": { 
            "allowedClients": [COGNITO_CLIENT_ID],
            "discoveryUrl": f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USERPOOL_ID}/.well-known/openid-configuration"
        }
    }
    authorizer_type = 'CUSTOM_JWT'
    print("Using Cognito JWT authentication")
else:
    # For basic setup without Cognito, we still need to provide the structure
    # This is a placeholder - you'll need to set up Cognito or use a different auth method
    print("⚠️  Warning: No Cognito configuration found")
    print("Creating gateway with placeholder JWT config (may need to update later)")
    # Use a dummy configuration - this may not work for actual requests
    # You should set up Cognito for production use
    auth_config = {
        "customJWTAuthorizer": {
            "allowedClients": ["placeholder-client-id"],
            "discoveryUrl": f"https://cognito-idp.{AWS_REGION}.amazonaws.com/placeholder/.well-known/openid-configuration"
        }
    }
    authorizer_type = 'CUSTOM_JWT'

# Check if gateway already exists and get its ID
gateway_id = None
gateway_arn = None

try:
    print(f"Checking if gateway '{GATEWAY_NAME}' already exists...")
    # List all gateways - API returns 'items' not 'gatewaySummaries'
    response = bedrock_agent_core_client.list_gateways()
    
    for gateway in response.get('items', []):
        if gateway.get('name') == GATEWAY_NAME:
            gateway_id = gateway.get('gatewayId')
            status = gateway.get('status', 'UNKNOWN')
            print(f"✅ Gateway '{GATEWAY_NAME}' already exists!")
            print(f"Gateway ID: {gateway_id}")
            print(f"Status: {status}")
            
            if status == 'FAILED':
                print("⚠️  Warning: Gateway is in FAILED status")
                print("Attempting to delete failed gateway and recreate...")
                try:
                    bedrock_agent_core_client.delete_gateway(gatewayIdentifier=gateway_id)
                    print("✅ Deleted failed gateway")
                    # Wait a moment for deletion to complete
                    import time
                    time.sleep(2)
                    gateway_id = None  # Reset to allow recreation
                except Exception as delete_error:
                    print(f"⚠️  Could not delete failed gateway: {delete_error}")
                    print("You may need to delete it manually from AWS Console")
                    print(f"Gateway ID to delete: {gateway_id}")
            
            # Get full gateway details - API uses gatewayIdentifier not gatewayId
            try:
                gateway_details = bedrock_agent_core_client.get_gateway(gatewayIdentifier=gateway_id)
                gateway_arn = gateway_details.get('gatewayArn')
                print(f"Gateway ARN: {gateway_arn}")
            except Exception as get_error:
                print(f"⚠️  Could not get gateway details: {get_error}")
                # Try to construct ARN manually
                account_id = boto3.client('sts').get_caller_identity()['Account']
                gateway_arn = f"arn:aws:bedrock-agentcore:{AWS_REGION}:{account_id}:gateway/{gateway_id}"
                print(f"Constructed Gateway ARN: {gateway_arn}")
            break
except Exception as list_error:
    print(f"⚠️  Could not list gateways: {list_error}")
    # Continue to try creating - if it exists, we'll catch that error

# If gateway not found, try to create it
if not gateway_id:
    print(f"Gateway not found. Creating new gateway: {GATEWAY_NAME}...")
    try:
        create_response = bedrock_agent_core_client.create_gateway(
            name=GATEWAY_NAME,
            roleArn=ROLE_ARN,
            protocolType='MCP',
            authorizerType=authorizer_type,
            authorizerConfiguration=auth_config,
            description=GATEWAY_DESCRIPTION
        )
        
        gateway_id = create_response.get('gatewayId')
        gateway_arn = create_response.get('gatewayArn')
        
        print("✅ Gateway created successfully!")
        print(f"Gateway ID: {gateway_id}")
        print(f"Gateway ARN: {gateway_arn}")
        print(f"Creation Time: {create_response.get('creationTime')}")
    except Exception as create_error:
        if "already exists" in str(create_error) or "ConflictException" in str(type(create_error).__name__):
            print(f"⚠️  Gateway already exists but couldn't retrieve via list: {create_error}")
            print("Trying alternative method to find gateway...")
            
            # Try to find it by attempting to get gateway with a common pattern
            # Or we can use AWS CLI to get it
            import subprocess
            try:
                result = subprocess.run(
                    ['aws', 'bedrock-agentcore-control', 'list-gateways', '--region', AWS_REGION, '--output', 'json'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    import json
                    gateways = json.loads(result.stdout)
                    for gw in gateways.get('gatewaySummaries', []):
                        if gw.get('gatewayName') == GATEWAY_NAME:
                            gateway_id = gw.get('gatewayId')
                            print(f"✅ Found gateway via AWS CLI: {gateway_id}")
                            break
            except Exception as cli_error:
                print(f"⚠️  AWS CLI method also failed: {cli_error}")
            
            if not gateway_id:
                print("❌ Could not retrieve existing gateway ID")
                print("Please run this command manually to get the Gateway ID:")
                print(f"  aws bedrock-agentcore-control list-gateways --region {AWS_REGION}")
                print("Then add to .env:")
                print("  GATEWAY_ID=<your-gateway-id>")
                sys.exit(1)
        else:
            print(f"❌ Error creating gateway: {create_error}")
            sys.exit(1)

# Update the .env file with the gateway information
# Use parent directory .env file (project root)
env_file_path = env_path if os.path.exists(env_path) else '.env'
try:
    if gateway_id:
        set_key(env_file_path, 'GATEWAY_ID', gateway_id)
        print(f"✅ Updated .env file with GATEWAY_ID: {gateway_id}")
    
    if gateway_arn:
        set_key(env_file_path, 'GATEWAY_ARN', gateway_arn)
        print(f"✅ Updated .env file with GATEWAY_ARN: {gateway_arn}")
        
    # Also set GATEWAY_IDENTIFIER for backward compatibility
    if gateway_id:
        set_key(env_file_path, 'GATEWAY_IDENTIFIER', gateway_id)
        print(f"✅ Updated .env file with GATEWAY_IDENTIFIER: {gateway_id}")
        
except Exception as e:
    print(f"⚠️  Warning: Failed to update .env file: {e}")
    print(f"Please manually add to .env:")
    print(f"GATEWAY_ID={gateway_id}")
    print(f"GATEWAY_ARN={gateway_arn}")

