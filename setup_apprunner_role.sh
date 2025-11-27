#!/bin/bash
# Create IAM role for App Runner to access ECR

ROLE_NAME="AppRunnerECRAccessRole"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Creating IAM role for App Runner ECR access..."

# Trust policy for App Runner
cat > /tmp/apprunner-trust-policy.json << TRUST
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
TRUST

# Create role if it doesn't exist
if aws iam get-role --role-name $ROLE_NAME &>/dev/null; then
  echo "Role $ROLE_NAME already exists"
else
  aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file:///tmp/apprunner-trust-policy.json
  
  # Attach ECR read policy
  aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess
  
  echo "✅ Role created and policies attached"
fi

ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "Role ARN: $ROLE_ARN"
echo ""
echo "✅ App Runner IAM role ready!"
