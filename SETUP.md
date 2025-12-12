# Setup Guide - Nova Voice Agent POC

Quick setup instructions for getting the POC running locally.

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **AWS Account** with Bedrock access
- **AWS CLI** configured with credentials

## Step-by-Step Setup

### 1. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

### 2. Backend Setup

```bash
cd backend
npm install

# Create .env file
cat > .env << EOF
AWS_REGION=us-east-1
NOVA_MODEL_ID=amazon.nova-sonic-v2:0
PORT=3001
EOF

npm start
```

Backend will run on `http://localhost:3001`

### 3. Agent Setup

```bash
cd agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test in console mode
python nova_agent.py
```

### 4. Verify AWS Credentials

```bash
aws sts get-caller-identity
```

Should return your AWS account information.

### 5. Test the Stack

1. **Backend health check:**
   ```bash
   curl http://localhost:3001/api/health
   ```

2. **Open frontend:**
   Open browser to `http://localhost:3000`

3. **Try text interaction:**
   Type a message and send (audio not yet implemented)

## Current Limitations

**This is a placeholder setup**. The following are NOT yet implemented:

- [ ] Nova Sonic API integration
- [ ] Audio recording from microphone
- [ ] Audio playback of responses
- [ ] Bidirectional audio streaming
- [ ] Speech-to-speech functionality

**What DOES work:**
- [x] Frontend UI (text mode)
- [x] Backend server (placeholder responses)
- [x] Agent logic (using Claude instead of Nova)
- [x] Text streaming display

## Troubleshooting

### Frontend won't start
- Ensure port 3000 is available
- Check `npm install` completed without errors
- Clear node_modules and reinstall

### Backend won't start
- Ensure port 3001 is available
- Verify AWS credentials are configured
- Check .env file exists and is correct

### Agent errors
- Verify Python 3.11+ is installed
- Check AWS credentials with `aws sts get-caller-identity`
- Ensure Bedrock access is enabled in your AWS account
- Try: `pip install --upgrade boto3 strands-agents`

### AWS Permission Issues
You need these AWS permissions:
- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`

## Next Steps

See README.md for the full research checklist on implementing Nova Sonic integration.

## Development Tips

- **Frontend hot reload:** Vite will auto-reload on file changes
- **Backend auto-reload:** Use `npm run dev` instead of `npm start`
- **Agent testing:** Run in console mode first before integrating
- **Debugging:** Check browser console and terminal logs

## Project Structure Quick Reference

```
NOVA/
├── frontend/     → React app (Vite + React)
├── backend/      → Express server (SSE/WebSocket)
├── agent/        → Python agent (Strands SDK)
├── README.md     → Project overview + research checklist
└── SETUP.md      → This file
```

