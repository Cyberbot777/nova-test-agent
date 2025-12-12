# Nova Voice Agent

Production-ready bidirectional streaming voice agent using **Amazon Nova 2.0 Sonic**.

## What This Is

A voice agent with real-time speech-to-speech conversation:
- Speak to the agent (microphone → Nova Sonic)
- Agent responds with voice (Nova Sonic → speakers)
- Text transcription displayed in real-time
- No Polly needed - Nova Sonic handles both transcription and speech generation

**Model:** `amazon.nova-sonic-v1:0`  
**Region:** `us-east-1`

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS account with Bedrock access

### 1. Setup (One-Time)

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
cd agent
pip install -r requirements.txt
```

**Credentials:**
```bash
cd agent
cp env.example .env
# Edit .env with your AWS credentials
```

### 2. Run

**Terminal 1 - Backend:**
```bash
cd agent
source .venv/Scripts/activate  # Windows: .venv/Scripts/activate
python run_voice_server.py --port 8080
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Browser:** http://localhost:3000

### 3. Use
1. Click "Start Conversation"
2. Speak into your microphone
3. Agent responds with voice

---

## Project Structure

```
nova-test-agent/
├── agent/
│   ├── nova_voice/           # Nova Sonic core implementation
│   │   ├── s2s_events.py     # Event definitions
│   │   ├── s2s_session_manager.py  # Stream manager
│   │   └── server.py         # WebSocket server
│   ├── run_voice_server.py   # Main entry point
│   ├── requirements.txt      # Python dependencies
│   ├── .env                  # AWS credentials (create from env.example)
│   └── env.example           # Template for credentials
│
├── frontend/
│   ├── src/
│   │   ├── VoiceAgent.js     # Voice UI component
│   │   ├── helper/           # Audio processing utilities
│   │   └── components/       # React components
│   └── package.json          # Node.js dependencies
│
└── backend/                  # Deprecated (use agent/ instead)
```

---

## Architecture

```
Browser (localhost:3000)
    │
    │ WebSocket (audio streaming)
    ▼
Python Backend (localhost:8080)
    │
    │ invoke_model_with_bidirectional_stream
    ▼
Amazon Nova Sonic (Bedrock)
    │
    └── Speech-to-Speech
```

**Audio Flow:**
- Input: 16kHz PCM (microphone)
- Output: 24kHz PCM (speakers)
- Encoding: Base64 over WebSocket

---

## Configuration

### AWS Credentials

Create `agent/.env`:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
```

The `.env` file is in `.gitignore` and will not be committed.

### Model Configuration

Edit `agent/run_voice_server.py` to change:
- `--model` - Nova Sonic model ID (default: `amazon.nova-sonic-v1:0`)
- `--port` - WebSocket port (default: 8080)
- `--region` - AWS region (default: us-east-1)

---

## Troubleshooting

**Backend won't start:**
- Check `agent/.env` exists with valid AWS credentials
- Verify: `aws sts get-caller-identity`
- Ensure Bedrock access in us-east-1

**No audio:**
- Allow microphone access in browser
- Verify backend is running on port 8080
- Check browser console for errors

**WebSocket connection fails:**
- Start backend before frontend
- Check firewall isn't blocking port 8080
- Verify WebSocket URL in frontend settings

**Frontend won't start:**
- Ensure `npm install` completed successfully
- Check port 3000 is available
- Delete `node_modules/` and reinstall if needed

---

## Dependencies

**Python:**
- `aws-sdk-bedrock-runtime` - Bedrock bidirectional streaming
- `smithy-aws-core` - AWS authentication
- `websockets` - WebSocket server
- `python-dotenv` - Environment variable loading

**JavaScript:**
- `react` - UI framework
- `@cloudscape-design/components` - AWS UI components

---

## License

Internal use - Kind Lending

---

**Status:** Production ready  
**Last Updated:** December 12, 2025
