#!/bin/bash
# Deploy Flask backend to Elastic Beanstalk using AWS CLI

APP_NAME="iot-dashboard-api"
ENV_NAME="iot-dashboard-api-env"
REGION="us-east-1"

echo "Deploying Flask backend to Elastic Beanstalk..."

# Check if application exists
if aws elasticbeanstalk describe-applications --application-names $APP_NAME --region $REGION &>/dev/null; then
    echo "Application $APP_NAME exists"
else
    echo "Creating Elastic Beanstalk application..."
    aws elasticbeanstalk create-application \
        --application-name $APP_NAME \
        --description "IoT Dashboard Backend API" \
        --region $REGION
fi

# Create application version
VERSION_LABEL="v$(date +%s)"
cd backend
zip -r ../app-version.zip . -x "*.pyc" "__pycache__/*" "*.git*" ".venv/*"
cd ..

echo "Uploading application version..."
aws s3 cp app-version.zip s3://elasticbeanstalk-$REGION-$(aws sts get-caller-identity --query Account --output text)/$APP_NAME/app-version.zip --region $REGION

aws elasticbeanstalk create-application-version \
    --application-name $APP_NAME \
    --version-label $VERSION_LABEL \
    --source-bundle S3Bucket="elasticbeanstalk-$REGION-$(aws sts get-caller-identity --query Account --output text)",S3Key="$APP_NAME/app-version.zip" \
    --region $REGION

# Check if environment exists
if aws elasticbeanstalk describe-environments --application-name $APP_NAME --environment-names $ENV_NAME --region $REGION --query 'Environments[0].Status' --output text 2>/dev/null | grep -q "Ready\|Updating"; then
    echo "Updating environment..."
    aws elasticbeanstalk update-environment \
        --application-name $APP_NAME \
        --environment-name $ENV_NAME \
        --version-label $VERSION_LABEL \
        --region $REGION
else
    echo "Creating environment (this takes 5-10 minutes)..."
    aws elasticbeanstalk create-environment \
        --application-name $APP_NAME \
        --environment-name $ENV_NAME \
        --solution-stack-name "64bit Amazon Linux 2023 v4.0.0 running Python 3.11" \
        --version-label $VERSION_LABEL \
        --option-settings \
            Namespace=aws:elasticbeanstalk:application:environment,OptionName=AWS_REGION,Value=us-east-1 \
            Namespace=aws:elasticbeanstalk:application:environment,OptionName=THING_NAME,Value=ESP32_SmartDevice \
        --region $REGION
fi

echo ""
echo "✅ Deployment initiated!"
echo "Check status: aws elasticbeanstalk describe-environments --application-name $APP_NAME --environment-names $ENV_NAME --region $REGION"
