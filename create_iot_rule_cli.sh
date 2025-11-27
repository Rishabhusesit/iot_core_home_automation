#!/bin/bash
# Create IoT Rule using AWS CLI
# Run this after setup_iot_rule.py (which creates DynamoDB table and IAM role)

set -e

# Get AWS account ID (or use default if command fails)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "381492092651")
REGION=${AWS_REGION:-us-east-1}
THING_NAME=${THING_NAME:-ESP32_SmartDevice}
TABLE_NAME="ESP32_${THING_NAME}_Data"
RULE_NAME="${THING_NAME}_DataForwarder"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/IoT_DynamoDB_Role"

echo "============================================================"
echo "Creating IoT Rule via AWS CLI"
echo "============================================================"
echo ""
echo "Account ID: ${ACCOUNT_ID}"
echo "Region: ${REGION}"
echo "Rule Name: ${RULE_NAME}"
echo "Table: ${TABLE_NAME}"
echo "Role: ${ROLE_ARN}"
echo ""

# Create rule JSON file
RULE_FILE=$(mktemp)
cat > "${RULE_FILE}" <<EOF
{
  "sql": "SELECT device_id, timestamp, sensor_data, relays, uptime_seconds, wifi_rssi FROM 'devices/${THING_NAME}/data'",
  "actions": [
    {
      "dynamoDBv2": {
        "roleArn": "${ROLE_ARN}",
        "putItem": {
          "tableName": "${TABLE_NAME}"
        }
      }
    }
  ],
  "ruleDisabled": false,
  "awsIotSqlVersion": "2016-03-23"
}
EOF

# Check if rule exists
if aws iot get-topic-rule --rule-name "${RULE_NAME}" >/dev/null 2>&1; then
    echo "✅ IoT Rule '${RULE_NAME}' already exists"
    echo "   Updating rule..."
    aws iot replace-topic-rule \
        --rule-name "${RULE_NAME}" \
        --topic-rule-payload file://"${RULE_FILE}"
    echo "✅ Rule updated successfully"
else
    echo "Creating IoT Rule '${RULE_NAME}'..."
    aws iot create-topic-rule \
        --rule-name "${RULE_NAME}" \
        --topic-rule-payload file://"${RULE_FILE}"
    echo "✅ Rule created successfully"
fi

# Clean up temp file
rm -f "${RULE_FILE}"

echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Verify rule in AWS Console: https://console.aws.amazon.com/iot/"
echo "2. Check DynamoDB table for incoming messages"
echo "3. Restart backend: cd backend && python3 app.py"
echo "4. Open dashboard: http://localhost:5000"

