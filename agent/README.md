# Nova Voice Agent

Python agent using Amazon Nova Sonic for bidirectional streaming voice conversations.

## Nova Sonic Voice Server

Nova Sonic implementation with bidirectional audio streaming.

### Quick Start

**1. Set AWS credentials (choose one):**

**Option A: Create `.env` file (recommended):**
```bash
# Copy the example and edit with your credentials
cp env.example .env
# Edit .env with your actual AWS credentials
```

**Option B: Environment variables:**
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run the voice server:**
```bash
python run_voice_server.py --port 8080
```

**4. Connect your frontend to `ws://localhost:8080`**

### Command Line Options

```bash
python run_voice_server.py --help

Options:
  --host    WebSocket server host (default: localhost)
  --port    WebSocket server port (default: 8080)
  --model   Nova Sonic model ID (default: amazon.nova-sonic-v1:0)
  --region  AWS region (default: us-east-1)
```

### Full Command (with credentials inline)

```bash
export AWS_ACCESS_KEY_ID=YOUR_KEY && \
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET" && \
export AWS_DEFAULT_REGION=us-east-1 && \
python run_voice_server.py --port 8080
```

## Files

```
agent/
  run_voice_server.py      # Main entry point - run this!
  nova_voice/
    __init__.py            # Package init
    s2s_events.py          # Nova Sonic event definitions & system prompt
    s2s_session_manager.py # Bidirectional stream manager
    server.py              # WebSocket server
  requirements.txt         # Python dependencies
  env.example              # AWS credentials template
```

## Architecture

```
Frontend (Browser)
    |
    | WebSocket (ws://localhost:8080)
    v
run_voice_server.py
    |
    | Nova Sonic Bidirectional Stream
    v
Amazon Nova Sonic (amazon.nova-sonic-v1:0)
    |
    | Speech-to-Speech (no Polly needed!)
    v
Audio Response streamed back to Frontend
```

## Features

- [x] Bidirectional audio streaming
- [x] Real-time speech-to-speech
- [x] WebSocket server for frontend connection
- [x] No Polly needed - Nova Sonic does voice output
- [x] Semantic turn detection
- [x] Interrupt/barge-in support
- [x] Tool integration ready (add your own tools)

## Customization

**System Prompt:** Edit `nova_voice/s2s_events.py` → `DEFAULT_SYSTEM_PROMPT`

**Voice Selection:** Edit `nova_voice/s2s_events.py` → `DEFAULT_AUDIO_OUTPUT_CONFIG` → `voiceId`

**Add Tools:** Pass `tool_config` to `S2sEvent.prompt_start()` with your tool definitions
