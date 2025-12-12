# Quick Start Commands

Copy and paste these commands to get started quickly.

## Initial Setup (One-Time)

```bash
# 1. Frontend
cd frontend && npm install && cd ..

# 2. Backend  
cd backend && npm install && cd ..

# 3. Agent (with virtual environment)
cd agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

## Running the POC

**Open 3 terminal windows:**

### Terminal 1 - Frontend
```bash
cd frontend
npm run dev
```
Opens on http://localhost:3000

### Terminal 2 - Backend
```bash
cd backend
npm start
```
Opens on http://localhost:3001

### Terminal 3 - Agent Test (Optional)
```bash
cd agent
source venv/bin/activate  # Windows: venv\Scripts\activate
python nova_agent.py
```

## Quick Test

Once all running:
1. Open browser to http://localhost:3000
2. Type a message in the text box
3. Click Send
4. See placeholder response (Nova integration pending)

## Current Status

**Works:** Text streaming, UI, basic architecture  
**Pending:** Nova Sonic API, audio recording, audio playback

## Next Steps

See `README.md` Section: **Research Needed** for Nova integration checklist.

---

**Need help?** See `SETUP.md` for detailed setup and troubleshooting.

