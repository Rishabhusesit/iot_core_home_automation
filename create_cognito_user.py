#!/usr/bin/env python3
"""
Create a Cognito user for IoT Dashboard
"""
import boto3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

if not USER_POOL_ID:
    print("❌ COGNITO_USER_POOL_ID not set in .env")
    sys.exit(1)

print("=" * 60)
print("Create Cognito User")
print("=" * 60)
print(f"User Pool: {USER_POOL_ID}")
print()

# Get user details
username = input("Enter username: ").strip()
email = input("Enter email: ").strip()
password = input("Enter password (min 8 chars, must have uppercase, lowercase, number, special char): ").strip()
temp_password = input("Is this a temporary password? (y/n, default: n): ").strip().lower() == 'y'

if not username or not email or not password:
    print("❌ Username, email, and password are required")
    sys.exit(1)

try:
    cognito = boto3.client('cognito-idp', region_name=AWS_REGION)
    
    print("\n👤 Creating user...")
    
    # Create user
    try:
        response = cognito.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=username,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'}
            ],
            TemporaryPassword=password if temp_password else None,
            MessageAction='SUPPRESS'  # Don't send welcome email
        )
        
        print("✅ User created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Status: {response['User']['UserStatus']}")
        
        # If temporary password, set permanent password
        if temp_password or response['User']['UserStatus'] == 'FORCE_CHANGE_PASSWORD':
            print("\n🔐 Setting permanent password...")
            try:
                # First, we need to authenticate with temp password to get session
                # Then use change_password
                print("⚠️  User has temporary password.")
                print("   You'll need to:")
                print("   1. Use initiate_auth with USER_PASSWORD_AUTH")
                print("   2. If it returns NEW_PASSWORD_REQUIRED, use respond_to_auth_challenge")
                print("   3. Or use admin_set_user_password to set permanent password directly")
                
                # Try to set permanent password directly (admin)
                cognito.admin_set_user_password(
                    UserPoolId=USER_POOL_ID,
                    Username=username,
                    Password=password,
                    Permanent=True
                )
                print("✅ Permanent password set!")
                
            except Exception as e:
                print(f"⚠️  Could not set permanent password: {e}")
                print("   You may need to change password on first login")
        else:
            # Set password directly
            try:
                cognito.admin_set_user_password(
                    UserPoolId=USER_POOL_ID,
                    Username=username,
                    Password=password,
                    Permanent=True
                )
                print("✅ Password set!")
            except Exception as e:
                print(f"⚠️  Could not set password: {e}")
        
        print("\n✅ User is ready to use!")
        print(f"\nNow run: python3 get_cognito_token.py")
        print(f"Username: {username}")
        print(f"Password: {password}")
        
    except cognito.exceptions.UsernameExistsException:
        print(f"❌ User '{username}' already exists")
        print("   Use get_cognito_token.py to get token")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()




