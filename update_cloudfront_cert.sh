#!/bin/bash
# Script to update CloudFront distribution with custom domain and certificate

DIST_ID="E2BRDUE7DYPTI6"
CERT_ARN="arn:aws:acm:us-east-1:381492092651:certificate/a080c9a5-0b7f-4bdb-9ccb-ff32241b42cd"
DOMAIN="noone-knowsaboutit.com"

echo "Checking certificate status..."
CERT_STATUS=$(aws acm describe-certificate --certificate-arn "$CERT_ARN" --region us-east-1 --query "Certificate.Status" --output text)

if [ "$CERT_STATUS" != "ISSUED" ]; then
    echo "❌ Certificate not validated yet. Status: $CERT_STATUS"
    echo "Please add the DNS validation record and wait for validation."
    exit 1
fi

echo "✅ Certificate is validated! Updating CloudFront distribution..."

# Get current config
aws cloudfront get-distribution-config --id "$DIST_ID" > /tmp/dist-config.json
ETAG=$(jq -r '.ETag' /tmp/dist-config.json)
CONFIG=$(jq '.DistributionConfig' /tmp/dist-config.json)

# Update config with custom domain and certificate
UPDATED_CONFIG=$(echo "$CONFIG" | jq --arg domain "$DOMAIN" --arg cert "$CERT_ARN" '
    .Aliases.Quantity = 1 |
    .Aliases.Items = [$domain] |
    .ViewerCertificate.ACMCertificateArn = $cert |
    .ViewerCertificate.SSLSupportMethod = "sni-only" |
    .ViewerCertificate.MinimumProtocolVersion = "TLSv1.2_2021" |
    .ViewerCertificate.CertificateSource = "acm" |
    del(.ViewerCertificate.CloudFrontDefaultCertificate)
')

echo "$UPDATED_CONFIG" > /tmp/updated-config.json

# Update distribution
aws cloudfront update-distribution \
    --id "$DIST_ID" \
    --distribution-config file:///tmp/updated-config.json \
    --if-match "$ETAG" \
    --query "Distribution.{Id:Id,DomainName:DomainName,Status:Status}" \
    --output json

echo ""
echo "✅ Distribution update initiated!"
echo "Deployment will take 10-15 minutes."
echo "After deployment, update DNS: $DOMAIN → d1diy0f6h0ksvv.cloudfront.net"
