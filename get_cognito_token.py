#!/usr/bin/env python3
"""
Get Cognito IdToken for AgentCore Gateway
"""
import boto3
import json
import os
import sys
from dotenv import load_dotenv, set_key

load_dotenv()

# Get Cognito details from .env
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

if not USER_POOL_ID or not CLIENT_ID:
    print("=" * 60)
    print("❌ Cognito Configuration Missing")
    print("=" * 60)
    print()
    print("Please set in .env file:")
    print("  COGNITO_USER_POOL_ID=us-east-1_XXXXX")
    print("  COGNITO_CLIENT_ID=XXXXX")
    print()
    
    # Try to find existing pools
    print("Searching for existing Cognito User Pools...")
    try:
        cognito = boto3.client('cognito-idp', region_name=AWS_REGION)
        pools = cognito.list_user_pools(MaxResults=10)
        
        if pools.get('UserPools'):
            print("\nFound User Pools:")
            for pool in pools['UserPools']:
                print(f"  - {pool['Name']}: {pool['Id']}")
                print(f"    Use: COGNITO_USER_POOL_ID={pool['Id']}")
        else:
            print("  No user pools found")
    except Exception as e:
        print(f"  Error: {e}")
    
    sys.exit(1)

print("=" * 60)
print("Cognito Token Retrieval")
print("=" * 60)
print(f"User Pool: {USER_POOL_ID}")
print(f"Client ID: {CLIENT_ID}")
print()

# Get username and password
username = input("Enter username: ").strip()
password = input("Enter password: ").strip()

if not username or not password:
    print("❌ Username and password required")
    sys.exit(1)

try:
    cognito = boto3.client('cognito-idp', region_name=AWS_REGION)
    
    print("\n🔐 Authenticating...")
    
    # Initiate auth
    response = cognito.initiate_auth(
        ClientId=CLIENT_ID,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )
    
    # Extract tokens
    auth_result = response.get('AuthenticationResult', {})
    id_token = auth_result.get('IdToken')
    access_token = auth_result.get('AccessToken')
    refresh_token = auth_result.get('RefreshToken')
    
    if id_token:
        print("✅ Authentication successful!")
        print()
        print("=" * 60)
        print("Token Retrieved")
        print("=" * 60)
        print(f"IdToken (first 50 chars): {id_token[:50]}...")
        print()
        
        # Update .env file
        env_path = '.env'
        set_key(env_path, 'BEARER_TOKEN', id_token)
        
        print("✅ BEARER_TOKEN added to .env file")
        print()
        print("You can now use AI analysis in the dashboard!")
        print()
        print("⚠️  Note: Tokens expire. Re-run this script when token expires.")
        
    else:
        print("❌ No IdToken in response")
        print(f"Response: {json.dumps(response, indent=2)}")
        
except cognito.exceptions.NotAuthorizedException as e:
    print("❌ Authentication failed: Invalid username or password")
    print("\n💡 Options:")
    print("   1. Create a new user: python3 create_cognito_user.py")
    print("   2. Check if username/password is correct")
    print("   3. User may need to change password on first login")
except cognito.exceptions.UserNotFoundException:
    print("❌ User not found")
    print("\n💡 Create a new user: python3 create_cognito_user.py")
except cognito.exceptions.UserNotConfirmedException:
    print("❌ User not confirmed. Please confirm your account first.")
    print("\n💡 Confirm user via AWS Console or admin_confirm_sign_up")
except cognito.exceptions.InvalidParameterException as e:
    error_msg = str(e)
    if 'NEW_PASSWORD_REQUIRED' in error_msg or 'challenge' in error_msg.lower():
        print("⚠️  User needs to set a new password (first login)")
        print("\n💡 Options:")
        print("   1. Use create_cognito_user.py to set permanent password")
        print("   2. Or use admin_set_user_password in AWS Console")
        print("   3. Or handle NEW_PASSWORD_REQUIRED challenge (see script)")
    else:
        print(f"❌ Invalid parameter: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

