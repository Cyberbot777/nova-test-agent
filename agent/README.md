# Nova Voice Agent

Python agent using Strands SDK + Amazon Nova 2.0 Sonic for voice conversations.

## Installation

```bash
pip install -r requirements.txt
```

## Current Usage (Console Test Mode)

```bash
python nova_agent.py
```

This runs in text mode for testing the agent logic before audio integration.

## AWS Credentials

Ensure you have AWS credentials configured:

```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

## Current State

**Placeholder Mode**
- Using Claude Sonnet as placeholder model
- Text input/output only
- Streaming works
- System prompt optimized for voice

## What Needs to Be Done

1. **Find Nova Sonic Model ID**
   - Current guess: `amazon.nova-sonic-v2:0`
   - Need to verify in AWS Bedrock console or docs

2. **Configure for Audio**
   - Understand Nova Sonic's audio input format
   - Implement audio chunk handling
   - Configure for speech-to-speech mode

3. **Bidirectional Streaming**
   - Implement audio stream ingestion
   - Handle Nova's audio + text responses
   - Synchronize audio and text output

4. **Integration with Backend**
   - Connect to backend WebSocket server
   - Handle audio chunk streaming
   - Coordinate with frontend

## Testing

Once Nova integration is complete:

```bash
# Console test (text mode)
python nova_agent.py

# Backend integration test
# Run backend server, then test with frontend
```

See main README.md for complete research checklist.

