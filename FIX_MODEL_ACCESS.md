# Fix Model Access Issue

## Current Error
```
AccessDeniedException: Model access is denied due to IAM user or service role 
is not authorized to perform the required AWS Marketplace actions 
(aws-marketplace:ViewSubscriptions, aws-marketplace:Subscribe)
```

## Solution

### Option 1: Add Marketplace Permissions to IAM Role

The agent's execution role needs Marketplace permissions:

```bash
# Get the role name
ROLE_NAME="AmazonBedrockAgentCoreSDKRuntime-us-east-1-07898fecc7"

# Create policy for Marketplace access
cat > /tmp/marketplace-policy.json << 'POLICY'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "aws-marketplace:ViewSubscriptions",
        "aws-marketplace:Subscribe"
      ],
      "Resource": "*"
    }
  ]
}
POLICY

# Attach policy to role
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name BedrockMarketplaceAccess \
  --policy-document file:///tmp/marketplace-policy.json \
  --region us-east-1
```

### Option 2: Use a Model That Doesn't Require Marketplace

Switch to Claude 3 Haiku which typically has broader access:

Update `.env`:
```
BEDROCK_MODEL_ID=us.anthropic.claude-3-haiku-20240307-v1:0
```

Then redeploy.

