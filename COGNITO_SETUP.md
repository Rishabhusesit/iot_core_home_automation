# Cognito User Setup Guide

## Problem
The username `learningaccount1` doesn't exist in Cognito.

## Solution Options

### Option 1: Create a New User (Recommended)

```bash
python3 create_cognito_user.py
```

Enter:
- Username: `learningaccount1` (or any username you want)
- Email: your email
- Password: your password (must meet requirements)

Then get token:
```bash
python3 get_cognito_token.py
```

### Option 2: Use Existing User

There are existing users in the pool:
- `testuser@iot-dashboard.com` (UUID username)
- `amitjha8080@gmail.com` (UUID username)

If you know the password for one of these, use:
```bash
python3 get_cognito_token.py
# Enter the UUID username (from list-users output)
# Enter the password
```

### Option 3: Quick Setup Script

```bash
./setup_cognito_user.sh
```

This will guide you through creating a user or using an existing one.

## Password Requirements

Cognito passwords typically require:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

## After Creating User

1. User is created and ready to use
2. Run `python3 get_cognito_token.py` to get token
3. Token is saved to `.env` as `BEARER_TOKEN`
4. Restart backend to use token

## Troubleshooting

**"User already exists":**
- User was already created
- Just run `get_cognito_token.py` with that username

**"Invalid password":**
- Check password meets requirements
- Try a stronger password

**"User not confirmed":**
- User needs email confirmation
- Check email for confirmation link
- Or use admin_confirm_sign_up

## Quick Commands

```bash
# Create user
python3 create_cognito_user.py

# Get token
python3 get_cognito_token.py

# Or use quick setup
./setup_cognito_user.sh
```




