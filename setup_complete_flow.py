#!/usr/bin/env python3
"""
Complete setup script for the full IoT flow:
1. Add CloudWatch metrics to IoT Rule
2. Deploy Lambda functions for AgentCore tools
3. Create AgentCore agent with tools
4. Set up IAM roles and permissions
"""
import boto3
import json
import os
import zipfile
import tempfile
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
THING_NAME = os.getenv('THING_NAME', 'ESP32_SmartDevice')
TABLE_NAME = f'ESP32_{THING_NAME}_Data'
RULE_NAME = f'{THING_NAME}_DataForwarder'

def get_account_id():
    """Get AWS account ID"""
    sts = boto3.client('sts', region_name=AWS_REGION)
    return sts.get_caller_identity()['Account']

def create_lambda_function():
    """Create Lambda function for AgentCore tools"""
    lambda_client = boto3.client('lambda', region_name=AWS_REGION)
    account_id = get_account_id()
    function_name = 'iot-agentcore-tools'
    
    # Check if function exists
    try:
        lambda_client.get_function(FunctionName=function_name)
        print(f"✅ Lambda function '{function_name}' already exists")
        return f'arn:aws:lambda:{AWS_REGION}:{account_id}:function:{function_name}'
    except lambda_client.exceptions.ResourceNotFoundException:
        pass
    
    # Create deployment package
    print(f"Creating Lambda deployment package...")
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
        zip_path = tmp_file.name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add the Lambda function code
            lambda_code_path = 'lambda/agentcore_tools_lambda.py'
            if os.path.exists(lambda_code_path):
                zip_file.write(lambda_code_path, 'lambda_function.py')
            else:
                print(f"❌ Lambda code not found at {lambda_code_path}")
                return None
    
    # Create IAM role for Lambda
    iam = boto3.client('iam', region_name=AWS_REGION)
    role_name = 'IoT_AgentCore_Lambda_Role'
    role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
    
    try:
        iam.get_role(RoleName=role_name)
        print(f"✅ IAM role '{role_name}' already exists")
    except iam.exceptions.NoSuchEntityException:
        print(f"Creating IAM role '{role_name}'...")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "arn:aws:logs:*:*:*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:GetItem"
                    ],
                    "Resource": f"arn:aws:dynamodb:{AWS_REGION}:{account_id}:table/{TABLE_NAME}"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "iot:Publish",
                        "iot:DescribeThing"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Allows Lambda to access DynamoDB and IoT Core'
        )
        
        policy_name = f'{role_name}_Policy'
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        
        print(f"✅ IAM role '{role_name}' created")
    
    # Read zip file
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    # Create Lambda function
    print(f"Creating Lambda function '{function_name}'...")
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='AgentCore tools for IoT device queries and control',
            Timeout=30,
            Environment={
                'Variables': {
                    'THING_NAME': THING_NAME,
                    'DYNAMODB_TABLE': TABLE_NAME
                }
            }
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Lambda function '{function_name}' created: {function_arn}")
        
        # Clean up zip file
        os.unlink(zip_path)
        
        return function_arn
        
    except Exception as e:
        print(f"❌ Error creating Lambda function: {e}")
        if os.path.exists(zip_path):
            os.unlink(zip_path)
        return None

def update_iot_rule_with_cloudwatch():
    """Update IoT Rule to add CloudWatch metrics"""
    iot = boto3.client('iot', region_name=AWS_REGION)
    account_id = get_account_id()
    
    # Get existing rule
    try:
        rule = iot.get_topic_rule(ruleName=RULE_NAME)
        current_rule = rule['rule']
        current_actions = current_rule.get('actions', [])
    except iot.exceptions.ResourceNotFoundException:
        print(f"❌ IoT Rule '{RULE_NAME}' not found. Create it first.")
        return False
    
    # Check if CloudWatch action already exists
    has_cloudwatch = any('cloudwatchMetric' in action for action in current_actions)
    
    if has_cloudwatch:
        print(f"✅ CloudWatch metrics already added to rule '{RULE_NAME}'")
        return True
    
    # Add CloudWatch metric action
    cloudwatch_action = {
        'cloudwatchMetric': {
            'roleArn': f'arn:aws:iam::{account_id}:role/IoT_DynamoDB_Role',
            'metricNamespace': 'IoT/SensorData',
            'metricName': 'MessageCount',
            'metricValue': '1',
            'metricUnit': 'Count'
        }
    }
    
    # Update rule with new action
    current_actions.append(cloudwatch_action)
    
    rule_document = {
        'sql': current_rule['sql'],
        'actions': current_actions,
        'ruleDisabled': current_rule.get('ruleDisabled', False),
        'awsIotSqlVersion': current_rule.get('awsIotSqlVersion', '2016-03-23')
    }
    
    try:
        iot.replace_topic_rule(
            ruleName=RULE_NAME,
            topicRulePayload=rule_document
        )
        print(f"✅ Added CloudWatch metrics to rule '{RULE_NAME}'")
        return True
    except Exception as e:
        print(f"❌ Error updating rule: {e}")
        return False

def main():
    print("=" * 60)
    print("Complete IoT Flow Setup")
    print("=" * 60)
    print()
    
    print("Step 1: Creating Lambda function for AgentCore tools...")
    lambda_arn = create_lambda_function()
    if not lambda_arn:
        print("❌ Failed to create Lambda function")
        return
    
    print()
    print("Step 2: Updating IoT Rule with CloudWatch metrics...")
    if not update_iot_rule_with_cloudwatch():
        print("⚠️  Could not update IoT Rule (may need manual update)")
    
    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Deploy AgentCore agent with Lambda tool:")
    print(f"   Lambda ARN: {lambda_arn}")
    print("2. Add natural language interface to dashboard")
    print("3. Test queries: 'Show me all devices', 'What is the temperature?'")

if __name__ == '__main__':
    main()

