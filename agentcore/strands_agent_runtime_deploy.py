"""
Deploy IoT Sensor Analysis Agent to AgentCore Runtime
Adapted from device-management-agent deployment script
"""
from bedrock_agentcore_starter_toolkit import Runtime
import time
import utils
import os
import sys
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()
load_dotenv('.env.runtime')  # If you have a separate runtime env file

script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Python file directory: {script_dir}")

# Parse command line arguments
parser = argparse.ArgumentParser(
    prog='iot_sensor_agent_runtime_deploy',
    description='Deploy IoT Sensor Analysis Agent to AgentCore Runtime',
    epilog='Input Parameters'
)

parser.add_argument('--gateway_id', help="Gateway Id", required=True)
parser.add_argument('--agent_name', help="Name of the agent", default="iot_sensor_analysis_agent")
parser.add_argument('--execution_role', help="IAM execution role ARN")

args = parser.parse_args()

# Parameter validation
if args.gateway_id is None:
    raise Exception("Gateway Id is required")

if args.agent_name is None:
    args.agent_name = os.getenv("AGENT_NAME", "iot_sensor_analysis_agent")

print(f"Deploying agent: {args.agent_name}")
print(f"Gateway ID: {args.gateway_id}")

# Create AgentCore client
try:
    (boto_session, agentcore_client) = utils.create_agentcore_client()
except Exception as e:
    print(f"❌ Error creating AgentCore client: {e}")
    print("Make sure your AWS credentials are configured")
    sys.exit(1)

# Files to copy to container
FilesToCopy = [
    "strands_agent_runtime.py",
    "access_token.py",
    "utils.py", 
    "requirements-runtime.txt"
]

# Environment variables for the runtime
EnvVariables = {
    "AWS_DEFAULT_REGION": os.getenv("AWS_REGION", "us-east-1"),
    "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
    
    # MCP Server configuration
    "MCP_SERVER_URL": os.getenv("MCP_SERVER_URL"),
    
    # IAM Role configuration
    "ROLE_ARN": os.getenv("ROLE_ARN"),
    
    # Bedrock AgentCore Runtime configuration
    "ENDPOINT_URL": os.getenv("ENDPOINT_URL"),
    "AGENT_NAME": os.getenv("AGENT_NAME", "iot_sensor_analysis_agent"),
    "AGENT_DESCRIPTION": os.getenv("AGENT_DESCRIPTION", "IoT Sensor Data Analysis Agent"),
    
    # Model configuration - Use Haiku by default (broader access, no Marketplace subscription)
    "BEDROCK_MODEL_ID": os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-haiku-20240307-v1:0"),
}

# Get gateway endpoint
try:
    gatewayEndpoint = utils.get_gateway_endpoint(agentcore_client=agentcore_client, gateway_id=args.gateway_id)
    print(f"Gateway Endpoint: {gatewayEndpoint}")
    if gatewayEndpoint:
        EnvVariables["MCP_SERVER_URL"] = gatewayEndpoint
        EnvVariables["gateway_endpoint"] = gatewayEndpoint
    else:
        print("⚠️  Gateway endpoint is empty, using value from .env file")
except Exception as e:
    print(f"⚠️  Warning: Could not get gateway endpoint: {e}")
    print("Using value from .env file")

aws_region = boto_session.region_name
print(f"AWS region: {aws_region}")

print(f"Environment variables: {EnvVariables}")

# Exclusions for dockerignore file
excluded_prefixes = ('.venv', '.ipynb_checkpoints', '__pycache__', '.git', 'images')
dockerignoreappend = ['.venv/', '.ipynb_checkpoints/', '__pycache__/', '.git/', 'images/']

for root, dirs, files in os.walk(script_dir):
    dirs[:] = [d for d in dirs if not d.startswith(excluded_prefixes)]
    
    relativePathDir = os.path.split(root)[-1]
    
    if root != script_dir:
        if relativePathDir not in FilesToCopy:
            dockerignoreappend.append(f"{relativePathDir}/")
    else:
        for file in files:
            if file not in FilesToCopy:
                dockerignoreappend.append(f"{file}")

# Don't remove Dockerfile - let Runtime generate it
# The Runtime will generate Dockerfile and .dockerignore during configure()
print("Cleaning up old config files before configuration")
cleanup_files = [".bedrock_agentcore.yaml"]  # Only remove old config
for cleanup_file in cleanup_files:
    file_path = os.path.join(script_dir, cleanup_file)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed {cleanup_file}")

# Initialize AgentCore Runtime
agentcore_runtime = Runtime()

print("Configuring Agent Runtime...")
# Get execution role - use provided arg, or from env, or auto-create
execution_role = args.execution_role or os.getenv("ROLE_ARN") or os.getenv("AGENT_EXECUTION_ROLE_ARN")

if not execution_role:
    print("⚠️  No execution role provided. Will auto-create execution role...")
    auto_create_role = True
else:
    auto_create_role = False
    print(f"Using execution role: {execution_role}")

try:
    response = agentcore_runtime.configure(
        entrypoint="strands_agent_runtime.py",
        execution_role=execution_role if not auto_create_role else None,
        auto_create_execution_role=auto_create_role,
        auto_create_ecr=True,
        requirements_file="requirements-runtime.txt",
        region=aws_region,
        agent_name=args.agent_name,
    )
    print("✅ Configuration successful")
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    sys.exit(1)

print("Appending to .dockerignore file")
dockerignore_path = os.path.join(script_dir, ".dockerignore")
# Read current .dockerignore
with open(dockerignore_path, "r", encoding='utf-8') as f:
    content = f.read()

# Remove Dockerfile if it's in there (it shouldn't be excluded)
content = content.replace("Dockerfile\n", "").replace("Dockerfile", "")

# Write back with our additions
with open(dockerignore_path, "w", encoding='utf-8') as f:
    f.write(content)
    f.write("\n")
    f.write("# Auto-generated exclusions\n")
    for ignorefile in dockerignoreappend:
        f.write(ignorefile + "\n")
    
    # Ensure Dockerfile is NOT ignored
    f.write("!Dockerfile\n")

print("Launching Agent...")
# Filter out None values from environment variables
EnvVariablesFiltered = {k: v for k, v in EnvVariables.items() if v is not None}
try:
    # Use auto_update to update existing agent
    launch_result = agentcore_runtime.launch(env_vars=EnvVariablesFiltered, auto_update_on_conflict=True)
    print(f"✅ Agent created with ARN: {launch_result.agent_arn}")
except Exception as e:
    print(f"❌ Launch failed: {e}")
    sys.exit(1)

# Monitor deployment status
print("Monitoring deployment status...")
status_response = agentcore_runtime.status()
print(f"Initial status: {status_response}")

status = status_response.endpoint['status']
end_status = ['READY', 'CREATE_FAILED', 'DELETE_FAILED', 'UPDATE_FAILED']

while status not in end_status:
    print(f"Current status: {status}")
    time.sleep(10)  # Wait 10 seconds between checks
    try:
        status_response = agentcore_runtime.status()
        status = status_response.endpoint['status']
    except Exception as e:
        print(f"Error checking status: {e}")
        break

print(f"Final status: {status}")

if status == 'READY':
    print("🎉 Agent deployment successful!")
    
    # Quick test
    print("Running quick test...")
    try:
        invoke_response = agentcore_runtime.invoke({
            "prompt": "Hello! Can you help me analyze IoT sensor data?"
        })
        print(f"Test response: {invoke_response}")
    except Exception as e:
        print(f"⚠️  Test invocation failed: {e}")
        
elif status in ['CREATE_FAILED', 'DELETE_FAILED', 'UPDATE_FAILED']:
    print(f"❌ Agent deployment failed with status: {status}")
    print("Check the AWS console for detailed error logs")
else:
    print(f"⚠️  Agent deployment ended with unexpected status: {status}")

print("Deployment script completed.")

