# Fix for Agent Sandbox 400 Error

## Problem
Agent Sandbox returns 400 error when sending simple text like "hi"

## Root Cause
The `BedrockAgentCoreApp` framework validates JSON **before** calling our entrypoint function. When the sandbox sends plain text like `"hi"`, the framework rejects it.

## Solution

### In Agent Sandbox, use JSON format:

**❌ Wrong (causes 400 error):**
```
hi
```

**✅ Correct (works):**
```json
{"prompt": "hi"}
```

Or:
```json
{"message": "hi"}
```

Or:
```json
{"input": "hi"}
```

## Current Status
- ✅ Agent code handles all payload formats
- ✅ Agent deployed and READY
- ⚠️  Framework validates JSON before our code runs
- ✅ When proper JSON is sent, agent works perfectly (confirmed in logs)

## Test Format
In Agent Sandbox, always send JSON:
```json
{
  "prompt": "your message here"
}
```

The agent will work correctly when the sandbox sends proper JSON format.

