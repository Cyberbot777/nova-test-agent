# Nova 2 Sonic Integration Research

**Date:** December 12, 2025  
**Goal:** Replace 11labs with Amazon Nova 2 Sonic  
**Team:** R&D AI Automation  
**Standards:** Strands SDK + AWS Bedrock AgentCore

---

## ✅ Confirmed Details

### Model Information
- **Model ID:** `amazon.nova-2-sonic-v1:0`
- **Region:** US East-1 (N. Virginia)
- **Release Date:** December 2, 2025 (10 days old)
- **Type:** Speech-to-speech with bidirectional streaming
- **Status:** ✅ Available in company AWS account

### Capabilities
- Real-time bidirectional audio streaming
- Speech input → Speech output + Text output
- Multilingual support (10+ languages)
- Tool calling / RAG support
- 1M token context window
- Handles interruptions gracefully
- Background noise robust

---

## 🎯 Strands SDK Support

### ⚠️ IMPORTANT DISCOVERY (Dec 12, 2025)

**`strands-amazon-nova` is NOT for Bedrock!**

The `strands-amazon-nova` package connects to `api.nova.amazon.com` (Nova API Service), not AWS Bedrock. 

### What We Learned

**Testing Results:**
- ✅ Nova 2 Sonic IS accessible via Bedrock in us-east-1
- ✅ Model ID `amazon.nova-2-sonic-v1:0` confirmed working
- ✅ 22 different Nova models available in account
- ⚠️ Requires `invoke_model_with_bidirectional_stream()` API
- ⚠️ NOT compatible with standard Strands `BedrockModel`

### Required Approach

**Option A: boto3 Direct Integration (Recommended for Now)**
```python
import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')
response = client.invoke_model_with_bidirectional_stream(
    modelId='amazon.nova-2-sonic-v1:0',
    # ... bidirectional streaming config
)
```

**Option B: Wait for Strands SDK Bedrock Bidirectional Support**
- Strands SDK currently doesn't support bidirectional streaming for Bedrock
- May need to implement custom wrapper

### Required Packages (Updated)
```bash
pip install strands-agents>=0.1.0
pip install bedrock-agentcore>=1.0.0
pip install boto3>=1.35.0
pip install aws-sdk-bedrock-runtime>=0.2.0
```

**DO NOT INSTALL** `strands-amazon-nova` (wrong service!)

---

## 🏗️ Architecture Pattern

### Strands SDK Approach (Recommended)
```python
# Initialize model
model = BidiNovaSonicModel(region="us-east-1")

# Set up I/O
audio_io = BidiAudioIO(audio_config={})
text_io = BidiTextIO()

# Create agent
async with BidiAgent(model=model) as agent:
    await agent.run(
        inputs=[audio_io.input()], 
        outputs=[audio_io.output(), text_io.output()]
    )
```

### Key Differences from Standard Strands Pattern
- Uses `BidiAgent` instead of regular `Agent`
- Experimental bidirectional streaming module
- Requires async context manager
- Audio I/O utilities handle encoding/decoding

---

## 📋 Implementation Plan

### Phase 1: Local Testing (Current)
1. ✅ Research Nova Sonic API
2. ✅ Confirm model availability
3. ✅ Find Strands SDK support
4. 🔄 Create minimal test script
5. ⏳ Validate audio flow

### Phase 2: Agent Integration
1. ⏳ Update `nova_agent.py` with BidiNovaSonicModel
2. ⏳ Test console mode with audio
3. ⏳ Document API behavior

### Phase 3: Backend Integration
1. ⏳ WebSocket bidirectional streaming
2. ⏳ Audio format handling
3. ⏳ Integration with Strands agent

### Phase 4: Frontend Integration
1. ⏳ Microphone capture (MediaRecorder)
2. ⏳ Audio playback
3. ⏳ Synchronize text streaming

### Phase 5: AgentCore Deployment
1. ⏳ Dockerfile with all dependencies
2. ⏳ `.bedrock_agentcore.yaml` configuration
3. ⏳ Production deployment

---

## 🔬 Technical Details (To Be Discovered)

### Audio Format
- Input format: ❓ (likely PCM 16kHz)
- Output format: ❓
- Chunk size: ❓
- Encoding: ❓

### Event Structure
- Session initialization events: ❓
- Audio streaming events: ❓
- Text response events: ❓
- Tool use events: ❓

### Strands SDK Configuration
- BidiAudioIO config options: ❓
- BidiNovaSonicModel parameters: ❓
- Error handling patterns: ❓

---

## 📝 Notes

### Advantages of Nova 2 Sonic vs 11labs
- Native AWS integration (no external API)
- Unified speech-to-speech (no separate STT/TTS)
- Tool calling support built-in
- Lower latency (within AWS network)
- Cost benefits (to be measured)
- 1M context window

### Challenges
- Very new (10 days old - limited community examples)
- Experimental in Strands SDK
- Bidirectional streaming more complex than request/response
- Audio format handling required
- Need to figure out AgentCore deployment for streaming

### Company Standards Compliance
- ✅ Strands SDK usage
- ✅ AgentCore deployment requirement
- ✅ Region: us-east-1
- ✅ Async/await patterns
- ✅ Reference implementation: kwikie_agent.py (to review)

---

## 🚀 Next Immediate Steps

1. **Review Strands Nova Sonic docs** (in progress)
2. **Update requirements.txt** with new packages
3. **Create minimal test script** to validate connection
4. **Document API behavior** as we learn

---

## 📚 Resources

- AWS Nova Docs: https://docs.aws.amazon.com/nova/latest/userguide/speech.html
- Strands SDK: https://strandsagents.com/latest/documentation/docs/
- AWS Bedrock Console: https://console.aws.amazon.com/bedrock/
- Model ID: `amazon.nova-2-sonic-v1:0`

---

**Status:** 🟢 Ready to build - framework exists, model available, SDK supports it!


