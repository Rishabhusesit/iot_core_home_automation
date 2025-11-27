#!/bin/bash

# AWS IoT Core Setup Script
# This script helps you set up AWS IoT Core resources

set -e

echo "=========================================="
echo "AWS IoT Core Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}AWS credentials are not configured.${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}AWS CLI is installed and configured.${NC}"
echo ""

# Get AWS region
read -p "Enter AWS region (e.g., us-east-1): " AWS_REGION
export AWS_DEFAULT_REGION=$AWS_REGION

# Get Thing name
read -p "Enter Thing name (e.g., MyIoTDevice): " THING_NAME

# Create Thing
echo ""
echo "Creating IoT Thing: $THING_NAME"
aws iot create-thing --thing-name "$THING_NAME" --region "$AWS_REGION" || {
    echo -e "${YELLOW}Thing might already exist. Continuing...${NC}"
}

# Create certificates directory
mkdir -p certificates

# Create keys and certificate
echo ""
echo "Creating keys and certificate..."
CERT_OUTPUT=$(aws iot create-keys-and-certificate \
    --set-as-active \
    --region "$AWS_REGION" \
    --output json)

CERTIFICATE_ARN=$(echo $CERT_OUTPUT | jq -r '.certificateArn')
CERTIFICATE_ID=$(echo $CERT_OUTPUT | jq -r '.certificateId')

echo $CERT_OUTPUT | jq -r '.certificatePem' > certificates/certificate.pem.crt
echo $CERT_OUTPUT | jq -r '.keyPair.PrivateKey' > certificates/private.pem.key
echo $CERT_OUTPUT | jq -r '.keyPair.PublicKey' > certificates/public.pem.key

echo -e "${GREEN}Certificates created successfully!${NC}"

# Download Root CA
echo ""
echo "Downloading Amazon Root CA..."
curl -o certificates/AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Create IoT Policy
POLICY_NAME="${THING_NAME}_Policy"
echo ""
echo "Creating IoT Policy: $POLICY_NAME"

POLICY_DOCUMENT=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect"
      ],
      "Resource": "arn:aws:iot:${AWS_REGION}:*:client/\${iot:ClientId}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish"
      ],
      "Resource": "arn:aws:iot:${AWS_REGION}:*:topic/devices/${THING_NAME}/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Subscribe"
      ],
      "Resource": "arn:aws:iot:${AWS_REGION}:*:topicfilter/devices/${THING_NAME}/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Receive"
      ],
      "Resource": "arn:aws:iot:${AWS_REGION}:*:topic/devices/${THING_NAME}/*"
    }
  ]
}
EOF
)

aws iot create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document "$POLICY_DOCUMENT" \
    --region "$AWS_REGION" || {
    echo -e "${YELLOW}Policy might already exist. Continuing...${NC}"
}

# Attach policy to certificate
echo ""
echo "Attaching policy to certificate..."
aws iot attach-policy \
    --policy-name "$POLICY_NAME" \
    --target "$CERTIFICATE_ARN" \
    --region "$AWS_REGION"

# Attach thing principal (certificate) to thing
echo ""
echo "Attaching certificate to thing..."
aws iot attach-thing-principal \
    --thing-name "$THING_NAME" \
    --principal "$CERTIFICATE_ARN" \
    --region "$AWS_REGION"

# Get IoT Endpoint
echo ""
echo "Getting IoT Endpoint..."
IOT_ENDPOINT=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --region "$AWS_REGION" --output text)

echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Thing Name: $THING_NAME"
echo "IoT Endpoint: $IOT_ENDPOINT"
echo "Certificate ID: $CERTIFICATE_ID"
echo ""
echo "Certificates saved in: certificates/"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env"
echo "2. Update .env with your IoT Endpoint: $IOT_ENDPOINT"
echo "3. Update .env with your Thing Name: $THING_NAME"
echo "4. Install dependencies: pip install -r requirements.txt"
echo "5. Run the device: python device_publisher.py"
echo ""







