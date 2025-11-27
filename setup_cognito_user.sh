#!/bin/bash
# Quick script to create a Cognito user and get token

echo "============================================================"
echo "Cognito User Setup"
echo "============================================================"
echo ""

# Check if user wants to create new user or use existing
echo "Options:"
echo "1. Create new user"
echo "2. Use existing user (testuser@iot-dashboard.com)"
echo ""
read -p "Choose option (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo ""
    echo "Creating new user..."
    python3 create_cognito_user.py
    echo ""
    echo "Now getting token..."
    python3 get_cognito_token.py
elif [ "$choice" == "2" ]; then
    echo ""
    echo "Using existing user: testuser@iot-dashboard.com"
    echo "Note: You'll need the password for this user"
    echo ""
    python3 get_cognito_token.py
else
    echo "Invalid choice"
    exit 1
fi




