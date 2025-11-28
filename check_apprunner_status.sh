#!/bin/bash
# Diagnostic script to check App Runner service status and logs

set -e

AWS_REGION="${AWS_REGION:-us-east-1}"
SERVICE_ARN="${APP_RUNNER_SERVICE_ARN}"

if [ -z "$SERVICE_ARN" ]; then
    echo "❌ Error: APP_RUNNER_SERVICE_ARN environment variable is required"
    echo "   Example: export APP_RUNNER_SERVICE_ARN=arn:aws:apprunner:us-east-1:123456789:service/your-service"
    exit 1
fi

echo "=" | head -c 80
echo ""
echo "🔍 App Runner Service Diagnostics"
echo "=" | head -c 80
echo ""
echo "Service ARN: $SERVICE_ARN"
echo "Region: $AWS_REGION"
echo ""

# 1. Check service status
echo "📊 Step 1: Service Status"
echo "----------------------------------------"
aws apprunner describe-service \
    --service-arn "$SERVICE_ARN" \
    --region "$AWS_REGION" \
    --query 'Service.{Name:ServiceName,Status:Status,Url:ServiceUrl,UpdatedAt:UpdatedAt}' \
    --output table

echo ""
echo "📋 Full Service Configuration:"
aws apprunner describe-service \
    --service-arn "$SERVICE_ARN" \
    --region "$AWS_REGION" \
    --query 'Service.SourceConfiguration.ImageRepository.ImageConfiguration.RuntimeEnvironmentVariables' \
    --output json | jq '.'

# 2. Check recent operations
echo ""
echo "📊 Step 2: Recent Operations"
echo "----------------------------------------"
aws apprunner list-operations \
    --service-arn "$SERVICE_ARN" \
    --region "$AWS_REGION" \
    --max-results 5 \
    --output table

# 3. Check CloudWatch Log Groups
echo ""
echo "📊 Step 3: CloudWatch Log Groups"
echo "----------------------------------------"
SERVICE_NAME=$(aws apprunner describe-service \
    --service-arn "$SERVICE_ARN" \
    --region "$AWS_REGION" \
    --query 'Service.ServiceName' \
    --output text)

LOG_GROUP="/aws/apprunner/$SERVICE_NAME/$SERVICE_ARN/application"

echo "Looking for log group: $LOG_GROUP"
aws logs describe-log-groups \
    --log-group-name-prefix "/aws/apprunner" \
    --region "$AWS_REGION" \
    --query "logGroups[?contains(logGroupName, '$SERVICE_NAME')].{Name:logGroupName,CreationTime:creationTime}" \
    --output table || echo "No log groups found"

# 4. Get recent log events
echo ""
echo "📊 Step 4: Recent Log Events (last 50 lines)"
echo "----------------------------------------"
LOG_GROUPS=$(aws logs describe-log-groups \
    --log-group-name-prefix "/aws/apprunner" \
    --region "$AWS_REGION" \
    --query "logGroups[?contains(logGroupName, '$SERVICE_NAME')].logGroupName" \
    --output text)

if [ -n "$LOG_GROUPS" ]; then
    for LOG_GROUP in $LOG_GROUPS; do
        echo ""
        echo "Log Group: $LOG_GROUP"
        echo "---"
        aws logs tail "$LOG_GROUP" \
            --region "$AWS_REGION" \
            --since 10m \
            --format short \
            --max-items 50 || echo "No recent logs"
    done
else
    echo "⚠️  No log groups found. Service may not have started yet."
fi

# 5. Check ECR repository
echo ""
echo "📊 Step 5: ECR Repository Status"
echo "----------------------------------------"
ECR_REPO="iot-backend"
aws ecr describe-repositories \
    --repository-names "$ECR_REPO" \
    --region "$AWS_REGION" \
    --query 'repositories[0].{Name:repositoryName,Uri:repositoryUri,CreatedAt:createdAt}' \
    --output table || echo "⚠️  ECR repository not found"

# 6. Check latest ECR images
echo ""
echo "📊 Step 6: Latest ECR Images"
echo "----------------------------------------"
aws ecr list-images \
    --repository-name "$ECR_REPO" \
    --region "$AWS_REGION" \
    --max-items 5 \
    --query 'imageIds[*].{Tag:imageTag,PushedAt:imagePushedAt}' \
    --output table || echo "⚠️  No images found"

# 7. Test service endpoint
echo ""
echo "📊 Step 7: Service Health Check"
echo "----------------------------------------"
SERVICE_URL=$(aws apprunner describe-service \
    --service-arn "$SERVICE_ARN" \
    --region "$AWS_REGION" \
    --query 'Service.ServiceUrl' \
    --output text)

if [ -n "$SERVICE_URL" ]; then
    echo "Service URL: $SERVICE_URL"
    echo ""
    echo "Testing /healthz endpoint:"
    curl -s -w "\nHTTP Status: %{http_code}\n" "$SERVICE_URL/healthz" || echo "❌ Health check failed"
    echo ""
    echo "Testing /api/device/status endpoint:"
    curl -s "$SERVICE_URL/api/device/status" | jq '.' || echo "❌ API endpoint failed"
else
    echo "⚠️  Service URL not available"
fi

echo ""
echo "=" | head -c 80
echo ""
echo "✅ Diagnostics complete!"
echo ""
echo "Next steps:"
echo "1. If service is OPERATION_IN_PROGRESS, wait for it to complete"
echo "2. Check CloudWatch logs for errors"
echo "3. Verify environment variables are set correctly"
echo "4. Test the API endpoint manually"

