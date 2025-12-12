# Session 2 Progress: Dependency Setup & Critical Discovery

**Date:** December 12, 2025  
**Session Goal:** Install dependencies and test Nova Sonic connection  
**Result:** ✅ SUCCESS - but with important pivot needed

---

## What We Accomplished

### 1. **Environment Setup Complete**
- ✅ Python virtual environment created (`agent/.venv`)
- ✅ 127+ Python packages installed via uv
- ✅ Frontend dependencies installed (154 packages)
- ✅ Backend dependencies installed (168 packages)
- ✅ All installations successful, 0 vulnerabilities

### 2. **Nova 2 Sonic Access Confirmed**
- ✅ Successfully connected to AWS Bedrock
- ✅ Verified `amazon.nova-2-sonic-v1:0` is accessible
- ✅ Authenticated as `rhall@kindlending.com`
- ✅ 22 Nova models available in account

### 3. **Critical Discovery Made**

**IMPORTANT: `strands-amazon-nova` is NOT for Bedrock!**

The package connects to `api.nova.amazon.com` (Nova API Service), not AWS Bedrock.

---

## 🔄 Major Pivot Required

### What We Thought:
- Use Strands SDK's `BidiNovaSonicModel`
- Follow standard Strands patterns
- Experimental bidirectional streaming module

### Reality:
- ❌ `strands-amazon-nova` is for different service
- ❌ No Strands SDK bidirectional streaming for Bedrock yet
- ✅ Must use boto3 `invoke_model_with_bidirectional_stream()` directly
- ✅ Need custom integration layer

---

## Test Results

### Test 1: Strands Package (FAILED)
```
[ERROR] No module named 'strands.experimental.bidi.models.novasonic'
```
**Finding:** Module doesn't exist - wrong package!

### Test 2: Bedrock Access (SUCCESS)
```
[SUCCESS] amazon.nova-2-sonic-v1:0 is available!
[INFO] Found 22 Nova models available
```
**Finding:** Model is accessible, we just need different integration approach

---

## Dependencies Installed

### Python Packages (agent/.venv)
- `strands-agents==1.19.0`
- `bedrock-agentcore==1.1.1`
- `boto3==1.42.8`
- `aws-sdk-bedrock-runtime==0.2.0`
- `pyaudio==0.2.14`
- `prompt_toolkit==3.0.52`
- `sounddevice==0.5.3`
- `numpy==2.3.5`
- Plus 119 other packages (OpenTelemetry, etc.)

### Node Packages
- Frontend: 154 packages (React, Vite, Framer Motion)
- Backend: 168 packages (Express, WebSocket, AWS SDK)

---

## New Implementation Plan

### Approach: Hybrid Integration

**1. Use boto3 for Nova Sonic Bidirectional Streaming**
```python
import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Use invoke_model_with_bidirectional_stream()
response = client.invoke_model_with_bidirectional_stream(
    modelId='amazon.nova-2-sonic-v1:0',
    # Bidirectional streaming configuration
)
```

**2. Wrap with Custom Strands-Compatible Layer**
- Create custom `NovaSonicModel` class
- Implement Strands SDK interface
- Handle bidirectional streaming internally
- Maintain AgentCore compatibility

**3. Maintain Company Standards**
- Still use Strands SDK for agent logic
- Custom model wrapper for Nova Sonic only
- AgentCore deployment path unchanged
- Follow async/await patterns

---

## Updated Requirements

### Working Dependencies
```txt
strands-agents>=0.1.0
bedrock-agentcore>=1.0.0
boto3>=1.35.0
aws-sdk-bedrock-runtime>=0.2.0
pyaudio>=0.2.14
sounddevice>=0.5.3
numpy>=2.3.5
prompt_toolkit>=3.0.52
```

### Remove from requirements.txt
```txt
strands-amazon-nova  # Wrong service!
```

---

## What We Need to Research Next

### 1. boto3 Bidirectional Streaming API
- [ ] Find documentation for `invoke_model_with_bidirectional_stream()`
- [ ] Understand event structure for Nova Sonic
- [ ] Learn audio format requirements
- [ ] Test basic bidirectional flow

### 2. Custom Strands Integration
- [ ] Design custom model wrapper class
- [ ] Implement Strands SDK interface
- [ ] Handle async bidirectional streaming
- [ ] Maintain AgentCore compatibility

### 3. Audio Pipeline
- [ ] Audio input format (PCM? Sample rate?)
- [ ] Audio output format
- [ ] Streaming chunk size
- [ ] Encoding/decoding requirements

---

## Advantages of This Approach

**Why Custom Integration is OK:**
1. ✅ Still follows company standards (Strands + AgentCore)
2. ✅ boto3 is well-documented and stable
3. ✅ Full control over bidirectional streaming
4. ✅ Can contribute back to Strands SDK later
5. ✅ Bleeding edge = we're pioneers!

**Why This is Better Than Waiting:**
1. ✅ Strands SDK may not add bidirectional support soon
2. ✅ boto3 approach is the "official" AWS way
3. ✅ We learn the underlying API (valuable knowledge)
4. ✅ Can still wrap it in Strands-compatible interface

---

## Next Steps (Session 3)

### Immediate (Coffee Cup #4 ☕)
1. Search for boto3 bidirectional streaming examples
2. Find AWS documentation for `invoke_model_with_bidirectional_stream()`
3. Understand event protocol for Nova Sonic

### Short Term
1. Create test script using boto3 directly
2. Send simple audio, receive audio response
3. Document the API behavior

### Medium Term
1. Design custom model wrapper
2. Integrate with existing agent structure
3. Test with WebSocket backend

---

## 📂 Files Created This Session

### New Files
- `agent/test_nova_sonic.py` - Initial test (wrong approach, kept for reference)
- `agent/test_nova_bedrock.py` - Bedrock access test ✅ WORKING
- `SETUP_COMPLETE.md` - Dependency installation summary
- `PROGRESS_SESSION_2.md` - This file

### Modified Files
- `agent/requirements.txt` - Added missing dependencies
- `NOVA_SONIC_RESEARCH.md` - Updated with critical findings

---

## 🎓 Key Learnings

### Technical
1. **Package Names Don't Always Reveal Purpose**
   - `strands-amazon-nova` ≠ Bedrock Nova
   - Always test actual imports!

2. **Bleeding Edge Means Blazing Trail**
   - Very new models may not have SDK support
   - Direct API access is sometimes necessary
   - This is normal for R&D work!

3. **boto3 is Your Friend**
   - When SDK doesn't support something, boto3 usually does
   - AWS services always have boto3 support first
   - Worth learning the low-level API

### Process
1. **Test Early, Pivot Fast**
   - Caught wrong approach before writing too much code
   - Saved potentially days of work
   - Now have correct path forward

2. **Document Everything**
   - These findings will help others
   - Clear audit trail of decisions
   - Can explain to boss why we pivoted

---

## 💬 Boss Update

*"We confirmed Nova 2 Sonic is accessible in Bedrock. Discovered that the initial Strands SDK approach won't work - the SDK doesn't support bidirectional streaming for Bedrock yet. Pivoting to use boto3 directly with a custom Strands-compatible wrapper. This is actually better because we'll have full control and can contribute back to Strands SDK later. Still on track, just taking the 'official AWS' route instead of the SDK shortcut."*

---

## Session End Status

**Time Invested:** ~45-60 minutes  
**Lines of Code:** ~350 (tests + documentation)  
**Confidence Level:** 🟢 High - Clear path forward  
**Blocker Status:** ✅ Resolved - Know exactly what to do next

---

**Ready for Session 3:** Research boto3 bidirectional streaming API ☕


