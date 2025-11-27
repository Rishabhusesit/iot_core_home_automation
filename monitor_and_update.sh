#!/bin/bash
# Monitor certificate and update CloudFront when ready

CERT_ARN="arn:aws:acm:us-east-1:381492092651:certificate/a080c9a5-0b7f-4bdb-9ccb-ff32241b42cd"
DIST_ID="E2BRDUE7DYPTI6"

echo "Monitoring certificate validation..."
echo "Press Ctrl+C to stop"

while true; do
    STATUS=$(aws acm describe-certificate --certificate-arn "$CERT_ARN" --region us-east-1 --query "Certificate.Status" --output text 2>/dev/null)
    
    if [ "$STATUS" = "ISSUED" ]; then
        echo "✅ Certificate validated! Updating CloudFront..."
        ./update_cloudfront_cert.sh
        break
    elif [ "$STATUS" = "VALIDATION_TIMED_OUT" ] || [ "$STATUS" = "FAILED" ]; then
        echo "❌ Certificate validation failed. Please check DNS records."
        break
    else
        echo "⏳ Certificate status: $STATUS (checking again in 30 seconds...)"
        sleep 30
    fi
done
