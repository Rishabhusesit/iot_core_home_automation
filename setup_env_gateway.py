#!/usr/bin/env python3
"""
Quick script to add Gateway URL to .env file
"""
import os
from dotenv import load_dotenv, set_key

# Load existing .env
env_path = '.env'
load_dotenv(env_path)

# Gateway endpoint (found from create_gateway.py)
GATEWAY_URL = "https://iot-sensor-analysis-gateway-vcyqiyewsa.gateway.bedrock-agentcore.us-east-1.amazonaws.com"

# Update .env file
set_key(env_path, 'GATEWAY_URL', GATEWAY_URL)

print("=" * 60)
print("✅ Gateway URL added to .env file")
print("=" * 60)
print(f"GATEWAY_URL={GATEWAY_URL}")
print()
print("⚠️  Note: You still need to set BEARER_TOKEN")
print("   Get it from Cognito login:")
print("   aws cognito-idp initiate-auth ...")
print("   Then add to .env: BEARER_TOKEN=your-id-token")
print()
print("Or test without Bearer token (may fail if gateway requires auth)")




