#!/bin/bash

################################################################################
# AgentCore Runtime Setup Script for IoT Sensor Analysis
#
# This script sets up AgentCore Runtime for IoT sensor data analysis
# Following the device-management-agent pattern
#
# Steps:
# 1. Deploy Lambda function with IoT tools
# 2. Create Gateway
# 3. Configure Gateway targets
# 4. Deploy Agent Runtime
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display section headers
section() {
  echo ""
  echo "=========================================="
  echo "  $1"
  echo "=========================================="
  echo ""
}

# Check prerequisites
section "Checking prerequisites"

if ! command -v aws &> /dev/null; then
  echo -e "${RED}Error: AWS CLI is not installed${NC}"
  exit 1
fi

if ! command -v python3 &> /dev/null; then
  echo -e "${RED}Error: Python 3 is not installed${NC}"
  exit 1
fi

# Load environment variables
if [ ! -f .env ]; then
  echo -e "${RED}Error: .env file not found${NC}"
  exit 1
fi

source .env

AWS_REGION=${AWS_REGION:-us-east-1}
THING_NAME=${THING_NAME:-ESP32_SmartDevice}

echo -e "${GREEN}✓ Prerequisites check passed${NC}"

# Step 1: Deploy Lambda Function
section "Step 1: Deploy Lambda Function"

LAMBDA_FUNCTION_NAME="iot-sensor-tools"
LAMBDA_ROLE_NAME="iot-sensor-tools-role"

echo "Creating IAM role for Lambda..."
# Create IAM role (simplified - you may need to adjust)
cat > /tmp/lambda-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Check if role exists
if aws iam get-role --role-name $LAMBDA_ROLE_NAME &> /dev/null; then
  echo "Role $LAMBDA_ROLE_NAME already exists"
else
  aws iam create-role \
    --role-name $LAMBDA_ROLE_NAME \
    --assume-role-policy-document file:///tmp/lambda-trust-policy.json
  
  # Attach basic Lambda execution policy
  aws iam attach-role-policy \
    --role-name $LAMBDA_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
  
  # Attach IoT permissions
  cat > /tmp/lambda-iot-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish",
        "iot:GetThingShadow",
        "iot:UpdateThingShadow",
        "iot:DescribeThing",
        "iot:ListThings"
      ],
      "Resource": "*"
    }
  ]
}
EOF
  
  aws iam put-role-policy \
    --role-name $LAMBDA_ROLE_NAME \
    --policy-name IoTPermissions \
    --policy-document file:///tmp/lambda-iot-policy.json
  
  echo "Waiting for IAM role to propagate..."
  sleep 10
fi

LAMBDA_ROLE_ARN=$(aws iam get-role --role-name $LAMBDA_ROLE_NAME --query 'Role.Arn' --output text)
echo "Lambda Role ARN: $LAMBDA_ROLE_ARN"

# Package Lambda function
echo "Packaging Lambda function..."
cd lambda
zip -r /tmp/iot-tools-lambda.zip iot_tools_lambda.py
cd ..

# Deploy or update Lambda
if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION &> /dev/null; then
  echo "Updating existing Lambda function..."
  aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb:///tmp/iot-tools-lambda.zip \
    --region $AWS_REGION
else
  echo "Creating new Lambda function..."
  aws lambda create-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --runtime python3.11 \
    --role $LAMBDA_ROLE_ARN \
    --handler iot_tools_lambda.lambda_handler \
    --zip-file fileb:///tmp/iot-tools-lambda.zip \
    --timeout 30 \
    --environment Variables="{THING_NAME=$THING_NAME}" \
    --region $AWS_REGION
fi

LAMBDA_ARN=$(aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION --query 'Configuration.FunctionArn' --output text)
echo -e "${GREEN}✓ Lambda function deployed: $LAMBDA_ARN${NC}"

# Save Lambda ARN to .env
echo "LAMBDA_ARN=$LAMBDA_ARN" >> .env

# Step 2: Create Gateway (simplified - you'll need to implement full Gateway creation)
section "Step 2: Create Gateway"

echo -e "${YELLOW}Note: Gateway creation requires additional setup${NC}"
echo "Please follow the Gateway setup guide or use the Python script:"
echo "  cd agentcore"
echo "  python create_gateway.py"

echo ""
echo -e "${GREEN}Setup script completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Complete Gateway setup"
echo "2. Deploy Agent Runtime"
echo "3. Test the integration"

