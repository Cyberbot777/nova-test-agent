# Quick Start - Nova Voice Agent

Run everything from THIS repo. No external dependencies.

## One-Time Setup

```bash
# 1. Install Frontend
cd frontend
npm install
cd ..

# 2. Install Backend (Python)
cd agent
pip install -r requirements.txt
cd ..
```

## Running the Voice Agent

Open 2 terminal windows:

### Terminal 1 - Backend (Python)

```bash
cd agent
export AWS_ACCESS_KEY_ID=YOUR_KEY
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
export AWS_DEFAULT_REGION=us-east-1
python run_voice_server.py --port 8080
```

### Terminal 2 - Frontend (React)

```bash
cd frontend
npm start
```

Opens at http://localhost:3000

## Full Backend Command (Single Line)

```bash
cd agent && export AWS_ACCESS_KEY_ID=YOUR_KEY && export AWS_SECRET_ACCESS_KEY="YOUR_SECRET" && export AWS_DEFAULT_REGION=us-east-1 && python run_voice_server.py --port 8080
```

## Usage

1. Open http://localhost:3000
2. Click "Start Conversation"
3. Speak into your microphone
4. Nova responds with voice

## Kill All Processes

```bash
# Windows
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Mac/Linux
pkill -f python
pkill -f node
```

## Troubleshooting

**Backend won't start:**
- Check AWS credentials are set correctly
- Run `aws sts get-caller-identity` to verify

**No audio:**
- Allow microphone access in browser
- Check that backend is running on port 8080

**WebSocket errors:**
- Make sure backend is running before frontend
- Check firewall isn't blocking port 8080
