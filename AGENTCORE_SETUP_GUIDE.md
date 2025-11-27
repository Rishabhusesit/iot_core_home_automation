# AgentCore Runtime Setup Guide

## Overview

This project uses **AWS Bedrock AgentCore Runtime** (not traditional Bedrock Agents) for IoT sensor data analysis.

## Architecture

Following the pattern from: https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/02-use-cases/device-management-agent

### Components:
1. **AgentCore Runtime** - Hosts the Strands agent
2. **Gateway** - Routes requests and handles authentication
3. **Lambda Function** - Tools for IoT Core operations
4. **IoT Core** - Device data source (instead of DynamoDB)

## Key Differences from Reference

- **Data Source**: IoT Core instead of DynamoDB
- **Use Case**: Sensor data analysis instead of device management
- **Simpler Setup**: No frontend initially

## Setup Steps

1. Install dependencies
2. Create Lambda function with IoT Core tools
3. Create Gateway
4. Deploy Agent Runtime
5. Test

