#!/bin/bash

################################################################################
# Create IAM Role for AgentCore Gateway
#
# This script creates an IAM role with the necessary permissions for
# Amazon Bedrock AgentCore Gateway operations.
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

AWS_REGION=${AWS_REGION:-us-east-1}
ROLE_NAME="AgentCore-Gateway-Role"

echo "Creating IAM role for AgentCore Gateway..."

# Create trust policy for AgentCore
cat > /tmp/gateway-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock-agentcore.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Check if role exists
if aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
  echo -e "${YELLOW}Role $ROLE_NAME already exists${NC}"
else
  echo "Creating IAM role: $ROLE_NAME"
  aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file:///tmp/gateway-trust-policy.json
  
  echo "Waiting for role to propagate..."
  sleep 5
fi

# Create policy for AgentCore Gateway permissions
cat > /tmp/gateway-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:*",
        "lambda:InvokeFunction",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Attach policy to role
echo "Attaching policy to role..."
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name AgentCoreGatewayPolicy \
  --policy-document file:///tmp/gateway-policy.json

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

echo ""
echo -e "${GREEN}✅ IAM Role created successfully!${NC}"
echo "Role Name: $ROLE_NAME"
echo "Role ARN: $ROLE_ARN"
echo ""

# Update .env file
ENV_FILE="../.env"
if [ -f "$ENV_FILE" ]; then
  # Check if ROLE_ARN already exists in .env
  if grep -q "^ROLE_ARN=" "$ENV_FILE"; then
    # Update existing ROLE_ARN
    if [[ "$OSTYPE" == "darwin"* ]]; then
      # macOS
      sed -i '' "s|^ROLE_ARN=.*|ROLE_ARN=$ROLE_ARN|" "$ENV_FILE"
    else
      # Linux
      sed -i "s|^ROLE_ARN=.*|ROLE_ARN=$ROLE_ARN|" "$ENV_FILE"
    fi
    echo -e "${GREEN}✅ Updated ROLE_ARN in .env file${NC}"
  else
    # Append ROLE_ARN to .env
    echo "" >> "$ENV_FILE"
    echo "# AgentCore Gateway IAM Role" >> "$ENV_FILE"
    echo "ROLE_ARN=$ROLE_ARN" >> "$ENV_FILE"
    echo -e "${GREEN}✅ Added ROLE_ARN to .env file${NC}"
  fi
else
  echo -e "${YELLOW}⚠️  .env file not found. Please manually add:${NC}"
  echo "ROLE_ARN=$ROLE_ARN"
fi

echo ""
echo "You can now create the Gateway:"
echo "  cd agentcore"
echo "  python create_gateway.py"






