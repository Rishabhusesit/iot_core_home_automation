#!/usr/bin/env python3
"""
Create IoT Rule to forward ESP32 messages to DynamoDB
This allows the backend to query the latest sensor data
"""
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

THING_NAME = os.getenv('THING_NAME', 'ESP32_SmartDevice')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
TABLE_NAME = f'ESP32_{THING_NAME}_Data'

def create_dynamodb_table():
    """Create DynamoDB table to store IoT messages"""
    dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
    
    try:
        # Check if table exists
        dynamodb.describe_table(TableName=TABLE_NAME)
        print(f"✅ DynamoDB table '{TABLE_NAME}' already exists")
        return True
    except dynamodb.exceptions.ResourceNotFoundException:
        pass
    
    try:
        print(f"Creating DynamoDB table '{TABLE_NAME}'...")
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'device_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'device_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # On-demand pricing
        )
        
        # Wait for table to be created
        print("Waiting for table to be active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=TABLE_NAME)
        
        print(f"✅ DynamoDB table '{TABLE_NAME}' created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

def create_iot_rule():
    """Create IoT Rule to forward messages to DynamoDB"""
    iot = boto3.client('iot', region_name=AWS_REGION)
    
    rule_name = f'{THING_NAME}_DataForwarder'
    topic_pattern = f'devices/{THING_NAME}/data'
    
    # SQL statement to select all fields
    sql = f"SELECT * FROM '{topic_pattern}'"
    
    # DynamoDB action
    action = {
        'dynamoDBv2': {
            'roleArn': get_or_create_iot_role_arn(),
            'putItem': {
                'tableName': TABLE_NAME
            }
        }
    }
    
    rule_document = {
        'sql': sql,
        'actions': [action],
        'ruleDisabled': False,
        'awsIotSqlVersion': '2016-03-23'
    }
    
    try:
        # Check if rule exists
        try:
            iot.get_topic_rule(ruleName=rule_name)
            print(f"✅ IoT Rule '{rule_name}' already exists")
            return True
        except iot.exceptions.ResourceNotFoundException:
            pass
        
        print(f"Creating IoT Rule '{rule_name}'...")
        iot.create_topic_rule(
            ruleName=rule_name,
            topicPattern=topic_pattern,
            sql=sql,
            actions=[action],
            ruleDisabled=False,
            awsIotSqlVersion='2016-03-23'
        )
        
        print(f"✅ IoT Rule '{rule_name}' created successfully")
        print(f"   Topic: {topic_pattern}")
        print(f"   Action: DynamoDB table '{TABLE_NAME}'")
        return True
    except Exception as e:
        print(f"❌ Error creating rule: {e}")
        return False

def get_or_create_iot_role_arn():
    """Get or create IAM role for IoT Rule to write to DynamoDB"""
    iam = boto3.client('iam', region_name=AWS_REGION)
    sts = boto3.client('sts', region_name=AWS_REGION)
    
    account_id = sts.get_caller_identity()['Account']
    role_name = 'IoT_DynamoDB_Role'
    role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
    
    try:
        # Check if role exists
        iam.get_role(RoleName=role_name)
        print(f"✅ IAM role '{role_name}' already exists")
        return role_arn
    except iam.exceptions.NoSuchEntityException:
        pass
    
    try:
        print(f"Creating IAM role '{role_name}'...")
        
        # Trust policy for IoT
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "iot.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Create role
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Allows IoT Rules to write to DynamoDB'
        )
        
        # Attach DynamoDB write policy
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem"
                    ],
                    "Resource": f"arn:aws:dynamodb:{AWS_REGION}:{account_id}:table/{TABLE_NAME}"
                }
            ]
        }
        
        policy_name = f'{role_name}_DynamoDB_Policy'
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        
        print(f"✅ IAM role '{role_name}' created with DynamoDB permissions")
        return role_arn
    except Exception as e:
        print(f"❌ Error creating role: {e}")
        # Return a placeholder - user will need to create manually
        return role_arn

def main():
    print("=" * 60)
    print("Setting up IoT Rule → DynamoDB Integration")
    print("=" * 60)
    print()
    
    print("Step 1: Creating DynamoDB table...")
    if not create_dynamodb_table():
        print("❌ Failed to create DynamoDB table")
        return
    
    print()
    print("Step 2: Creating IoT Rule...")
    if not create_iot_rule():
        print("❌ Failed to create IoT Rule")
        print()
        print("⚠️  Manual setup required:")
        print("   1. Go to AWS IoT Console → Rules")
        print(f"   2. Create rule with SQL: SELECT * FROM 'devices/{THING_NAME}/data'")
        print(f"   3. Add action: DynamoDB → Table: {TABLE_NAME}")
        return
    
    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print(f"1. ESP32 messages will be stored in DynamoDB table: {TABLE_NAME}")
    print("2. Update backend/app.py to query DynamoDB for latest data")
    print("3. Restart backend to use DynamoDB data source")

if __name__ == '__main__':
    main()


