#!/bin/bash
# Deploy Flask backend to AWS API Gateway + Lambda using Zappa or Serverless Framework
# For now, we'll use AWS App Runner or Elastic Beanstalk

echo "Checking deployment options..."
echo "Option 1: AWS App Runner (easiest for Flask)"
echo "Option 2: Elastic Beanstalk"
echo "Option 3: API Gateway + Lambda (requires refactoring)"

# For now, let's create a simple deployment package
cd backend
zip -r ../backend-deploy.zip . -x "*.pyc" "__pycache__/*" "*.git*"
cd ..

echo "✅ Backend package created: backend-deploy.zip"
echo ""
echo "To deploy:"
echo "1. AWS App Runner: Create service from container or source"
echo "2. Elastic Beanstalk: eb init && eb create"
echo "3. Or run locally and use ngrok for testing"
