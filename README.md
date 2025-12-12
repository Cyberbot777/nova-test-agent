# Nova Voice Agent POC

A simple proof of concept for a streaming voice agent using **Amazon Nova 2.0 Sonic** - a speech-to-speech model with bidirectional streaming capabilities.

## 🎉 **UPDATE: December 12, 2025 - NOVA 2 SONIC CONFIRMED!**

✅ **Model Available:** `amazon.nova-2-sonic-v1:0` in US East-1  
✅ **Strands SDK Support:** Experimental bidirectional streaming ready  
✅ **Test Script Created:** Ready to validate connection  
📚 **Documentation:** See `NOVA_SONIC_RESEARCH.md` and `PROGRESS_SESSION_1.md`

**Status:** 🟢 **Ready to build** - Framework validated, dependencies updated

---

## 🎯 Goal

Create a voice agent where you can:
- **Speak** to the agent (Nova transcribes)
- Agent processes and responds
- **Agent speaks back** (Nova generates speech)
- **Text streams** to the screen in real-time

## 📁 Project Structure

```
NOVA/
├── agent/              # Python agent using Strands SDK + Nova
│   ├── nova_agent.py   # Main agent code (NEEDS NOVA INTEGRATION)
│   └── requirements.txt
├── backend/            # WebSocket/SSE server for audio streaming
│   ├── server.js       # Express server (PLACEHOLDER - NEEDS NOVA AUDIO)
│   └── package.json
├── frontend/           # React UI with audio recording/playback
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   └── components/
│   │       └── VoiceChat.jsx   # Chat interface (adapted from test-frontend)
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md           # This file
```

## ✅ What Was Done

### 1. Frontend (Copied from `test-frontend/client`)
- ✅ React app with Vite
- ✅ Streaming SSE handling
- ✅ Dark theme UI
- ✅ Real-time text display
- ✅ Typing animations
- ✅ Error handling
- ⚠️ **NEEDS**: Audio recording (microphone access)
- ⚠️ **NEEDS**: Audio playback for agent responses

### 2. Backend (Skeleton from `test-frontend/proxy`)
- ✅ Express server structure
- ✅ CORS setup
- ⚠️ **NEEDS**: WebSocket for audio streaming (not just SSE)
- ⚠️ **NEEDS**: Nova Sonic API integration
- ⚠️ **NEEDS**: Bidirectional audio stream handling

### 3. Agent (Adapted from `ScoutAgent/test_agent.py`)
- ✅ Strands SDK setup
- ✅ BedrockModel configuration
- ✅ Async/await patterns
- ✅ Streaming response handling
- ⚠️ **NEEDS**: Nova Sonic model integration
- ⚠️ **NEEDS**: Audio input/output handling

## 🔬 Research Needed

Before this POC can work, we need to determine:

### 1. **Nova Sonic Model ID**
- [ ] What is the exact Bedrock model ID? (e.g., `amazon.nova-sonic-v2:0`?)
- [ ] Is it available in `us-east-1`?
- [ ] What regions support Nova Sonic?

### 2. **API Integration**
- [ ] Does Strands SDK support Nova Sonic natively?
- [ ] Or do we need direct Bedrock client (`boto3`) calls?
- [ ] What's the API endpoint for bidirectional streaming?
  - Is it `converse_stream`?
  - A new Nova-specific API?
  - WebRTC-based?

### 3. **Audio Format Requirements**
- [ ] Input audio format: PCM? Opus? MP3?
- [ ] Sample rate: 16kHz? 48kHz?
- [ ] Encoding: Linear16? Opus?
- [ ] Chunk size for streaming?

### 4. **Bidirectional Streaming**
- [ ] How to send audio chunks while receiving responses?
- [ ] Is it true bidirectional (full duplex)?
- [ ] Or request/response with streaming?
- [ ] Can the agent interrupt/barge-in?

### 5. **Text + Audio Response**
- [ ] Does Nova return both transcribed text AND audio?
- [ ] Or just audio (and we need to transcribe it)?
- [ ] How do we stream text to the frontend while audio plays?

### 6. **Frontend Audio Handling**
- [ ] Browser API: MediaRecorder? WebRTC? Web Audio API?
- [ ] Format conversion in browser or backend?
- [ ] How to play audio responses? (Audio element? Web Audio API?)

## 🚀 Quick Start (Once Research is Complete)

### Prerequisites
- Node.js 18+
- Python 3.11+
- AWS credentials configured
- Access to Bedrock Nova models

### Setup

**1. Install Frontend**
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000
```

**2. Install Backend**
```bash
cd backend
npm install
npm start  # Runs on http://localhost:3001
```

**3. Install Agent**
```bash
cd agent
pip install -r requirements.txt
python nova_agent.py  # Test in console first
```

## 📚 Resources to Check

- [Amazon Nova 2 Documentation](https://docs.aws.amazon.com/nova/)
- [Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Strands SDK Docs](https://strandsagents.com/latest/documentation/docs/)
- AWS Bedrock pricing for Nova Sonic
- Code examples for bidirectional audio streaming

## 🎬 Development Plan

1. **Research Phase** (See checklist above)
2. **Backend Integration** - Connect to Nova Sonic API
3. **Audio Pipeline** - Browser → WebSocket → Nova → Browser
4. **Frontend Audio** - Add microphone capture and playback
5. **Testing** - Local voice interaction testing
6. **Polish** - Error handling, UX improvements

## 📝 Notes

- **No AWS AgentCore deployment** - This is local testing only
- **No tools/functions** - Simple conversation agent
- **Streaming text is key** - Even though it's voice, we display text
- **Start simple** - Get basic voice working before adding features

## 🤝 Contributing

This is a personal POC. Once we get Nova Sonic working, we can:
- Add conversation memory
- Add custom system prompts
- Add agent tools/functions
- Deploy to production

---

**Status:** 🟡 Setup complete, awaiting Nova Sonic API research

**Next Step:** Research Nova Sonic API specifications and update integration code

