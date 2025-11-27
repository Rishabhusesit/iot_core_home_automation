#!/bin/bash
# Deploy Flask backend to AWS App Runner

SERVICE_NAME="iot-dashboard-api"
ECR_URI="381492092651.dkr.ecr.us-east-1.amazonaws.com/iot-dashboard-backend:latest"
REGION="us-east-1"

echo "🚀 Deploying backend to AWS App Runner..."

# Create App Runner service configuration
cat > /tmp/apprunner-config.json << CONFIG
{
  "ServiceName": "$SERVICE_NAME",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "$ECR_URI",
      "ImageConfiguration": {
        "Port": "5000",
        "RuntimeEnvironmentVariables": {
          "AWS_REGION": "$REGION",
          "THING_NAME": "ESP32_SmartDevice"
        }
      },
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": true
  },
  "InstanceConfiguration": {
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB"
  }
}
CONFIG

# Check if service exists
if aws apprunner describe-service --service-arn $(aws apprunner list-services --region $REGION --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text 2>/dev/null) --region $REGION &>/dev/null 2>&1; then
  echo "Service exists, updating..."
  SERVICE_ARN=$(aws apprunner list-services --region $REGION --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text)
  aws apprunner update-service --service-arn $SERVICE_ARN --source-configuration file:///tmp/apprunner-config.json --region $REGION
else
  echo "Creating new service..."
  aws apprunner create-service --cli-input-json file:///tmp/apprunner-config.json --region $REGION --query "Service.{ServiceArn:ServiceArn,ServiceUrl:ServiceUrl,Status:Status}" --output json
fi

echo ""
echo "✅ Deployment initiated!"
echo "Monitor status: aws apprunner describe-service --service-arn <arn> --region $REGION"
