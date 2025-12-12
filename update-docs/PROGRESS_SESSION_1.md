# Session 1 Progress: Nova 2 Sonic Setup (Coffee Cup #2-3 ☕)

**Date:** December 12, 2025  
**Session Goal:** Research and validate Nova 2 Sonic feasibility  
**Pace:** Slow and methodical (one thing at a time)

---

## What We Accomplished

### 1. **Confirmed Nova 2 Sonic Availability**
- ✅ Model available in your AWS account
- ✅ Region: US East-1 (company standard)
- ✅ Model ID: `amazon.nova-2-sonic-v1:0`
- ✅ Console access confirmed via screenshot

### 2. **Discovered Strands SDK Support**
- ✅ Strands SDK has experimental Nova Sonic support!
- ✅ Package: `strands-amazon-nova`
- ✅ Uses bidirectional streaming patterns
- ✅ Compatible with company standards (Strands SDK + AgentCore)

### 3. **Updated Project Dependencies**
- ✅ Updated `agent/requirements.txt` with:
  - `strands-amazon-nova>=0.1.0` (Nova Sonic support)
  - `bedrock-agentcore>=1.0.0` (production deployment)
  - `aws-opentelemetry-distro==0.12.2` (observability)

### 4. **Created Research Documentation**
- ✅ `NOVA_SONIC_RESEARCH.md` - Comprehensive research notes
- ✅ Documented API details, architecture, and plan
- ✅ Captured advantages over 11labs

### 5. **Created Test Script**
- ✅ `agent/test_nova_sonic.py` - Minimal connection test
- ✅ Uses Strands SDK experimental bidirectional API
- ✅ Tests model initialization and I/O setup
- ✅ Ready to validate connection

---

## Progress Status

**Phase 1: Research & Setup** ✅ **COMPLETE**
- [x] Research Nova Sonic API
- [x] Confirm model availability
- [x] Find Strands SDK support
- [x] Create minimal test script
- [ ] Validate audio flow ← **NEXT STEP**

**Phase 2-5:** Not yet started (as planned)

---

## Next Immediate Step

### **Test the Connection**

Run the test script to validate Nova 2 Sonic is accessible:

```bash
cd agent
pip install -r requirements.txt
python test_nova_sonic.py
```

**Expected outcomes:**
1. ✅ **Success** - Model initializes, we proceed to audio testing
2. ⚠️ **Error** - We debug and document the issue

---

## Key Decisions Made

### Go Forward with Nova 2 Sonic
- Model is ready and accessible
- Strands SDK support exists
- Meets R&D cutting-edge requirements
- Good 11labs replacement candidate

### Use Strands Experimental Bidirectional API
- `BidiNovaSonicModel` instead of regular `BedrockModel`
- `BidiAgent` for streaming audio
- `BidiAudioIO` and `BidiTextIO` for I/O handling

### Follow Company Standards
- Strands SDK usage: ✅
- AgentCore deployment path: ✅
- Region us-east-1: ✅
- Async/await patterns: ✅

---

## 🔍 What We Learned

### About Nova 2 Sonic
- Brand new (released Dec 2, 2025 - just 10 days ago)
- True speech-to-speech (no separate STT/TTS)
- Returns both audio AND text (perfect for your POC)
- Supports tool calling / RAG (future enhancement)
- 1M token context window

### About Strands SDK Integration
- Has experimental support already (great timing!)
- Different API pattern: `BidiAgent` vs `Agent`
- Audio I/O utilities handle encoding/decoding
- Requires async context managers

### Technical Considerations
- Bidirectional streaming is more complex than request/response
- Audio format handling required (PCM encoding likely)
- Event-driven architecture (different from text flow)
- Very new - expect some trial & error

---

## 📂 Files Created/Modified

### Created:
1. `NOVA_SONIC_RESEARCH.md` - Research documentation
2. `PROGRESS_SESSION_1.md` - This file
3. `agent/test_nova_sonic.py` - Connection test script

### Modified:
1. `agent/requirements.txt` - Added Nova Sonic packages

### Reviewed:
1. `.cursor/rules/strands_sdk.mdc` - Company Strands SDK standards
2. `.cursor/rules/agentcore_deployment.mdc` - AgentCore deployment requirements

---

## Next Session Plan (When Ready)

### If Test Succeeds
1. Document the API behavior we observe
2. Test with actual audio input/output
3. Start updating `nova_agent.py` with real integration

### If Test Fails
1. Debug the error (likely auth or package issue)
2. Search for additional Strands SDK examples
3. Potentially contact Strands support or check their GitHub

---

## 💬 Boss Update Template

*"We've validated that Nova 2 Sonic is available and ready to use. Strands SDK has experimental support for it, which aligns perfectly with our standards. Created test scripts and documentation. Next step is to validate the connection and start building the actual voice agent. Timeline: 2-3 weeks for full POC to replace 11labs."*

---

## Resources Collected

- AWS Nova Sonic Docs: https://docs.aws.amazon.com/nova/latest/userguide/speech.html
- Strands SDK Nova Sonic: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/experimental/bidirectional-streaming/models/nova_sonic/
- Strands Main Docs: https://strandsagents.com/latest/documentation/docs/
- Model ID: `amazon.nova-2-sonic-v1:0`
- Region: `us-east-1`

---

## Stopping Point

Good stopping point for today! We have:
- ✅ Clear understanding of the technology
- ✅ Test framework in place
- ✅ Documentation started
- ✅ Next steps defined

**We went slow, one thing at a time, as requested.** 🐢

Ready to pick up next time with the connection test!

---

**Session Duration:** ~30-45 minutes (research + setup)  
**Lines of Code:** ~250 (mostly documentation and test script)  
**Confidence Level:** 🟢 High - Path is clear, tools are available

☕ Time for coffee cup #4!

