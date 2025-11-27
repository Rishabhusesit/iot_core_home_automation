#!/usr/bin/env python3
import json
import sys
import boto3

iot = boto3.client('iot', region_name='us-east-1')

# Create new certificate
response = iot.create_keys_and_certificate(setAsActive=True)
cert_arn = response['certificateArn']
cert_id = response['certificateId']

# Save certificate and key
with open('certificates/certificate.pem.crt', 'w') as f:
    f.write(response['certificatePem'])

with open('certificates/private.pem.key', 'w') as f:
    f.write(response['keyPair']['PrivateKey'])

# Attach to policy and thing
iot.attach_policy(policyName='ESP32_SmartDevice_Policy', target=cert_arn)
iot.attach_thing_principal(thingName='ESP32_SmartDevice', principal=cert_arn)

print("✅ Certificates created and attached")
print(f"Certificate ID: {cert_id}")







