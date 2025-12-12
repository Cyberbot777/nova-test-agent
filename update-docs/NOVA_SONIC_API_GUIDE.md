# Nova Sonic Bidirectional Streaming API Guide

**Date:** December 12, 2025  
**Model:** `amazon.nova-2-sonic-v1:0`  
**API:** `InvokeModelWithBidirectionalStream`

---

## 📚 Official Documentation

- **Main Guide:** https://docs.aws.amazon.com/nova/latest/userguide/speech-bidirection.html
- **Input Events:** https://docs.aws.amazon.com/nova/latest/nova2-userguide/sonic-input-events.html
- **Output Events:** https://docs.aws.amazon.com/nova/latest/nova2-userguide/sonic-output-events.html
- **Code Examples:** https://docs.aws.amazon.com/nova/latest/nova2-userguide/sonic-code-examples.html

---

## 🏗️ Architecture Overview

### Event-Driven Bidirectional Streaming

Nova Sonic uses a **persistent bidirectional connection** where:
- Client sends **input events** (JSON) to the model
- Model sends **output events** (JSON) back to client
- Both streams operate **simultaneously** (full duplex)
- Events control **session lifecycle**, **audio streaming**, and **responses**

###Flow:
```
Client                          Nova Sonic Model
  |                                     |
  |---> sessionStart                    |
  |---> promptStart                     |
  |---> contentStart                    |
  |---> textInput/audioInput            |
  |                              <------|  textOutput
  |                              <------|  audioOutput
  |---> contentEnd                      |
  |---> promptEnd                       |
  |---> sessionEnd                      |
  |                              <------|  sessionEnd
```

---

## 📥 Input Events (Client → Model)

### 1. sessionStart
**Purpose:** Initialize the conversation session

```json
{
  "event": {
    "sessionStart": {
      "inferenceConfiguration": {
        "maxTokens": 1024,
        "topP": 0.9,
        "temperature": 0.7
      },
      "turnDetectionConfiguration": {
        "endpointingSensitivity": "HIGH"  // LOW, MEDIUM, HIGH
      }
    }
  }
}
```

### 2. promptStart
**Purpose:** Begin a new prompt/turn

```json
{
  "event": {
    "promptStart": {
      "promptName": "unique-prompt-id",
      "textOutputConfiguration": {
        "mediaType": "text/plain"
      },
      "audioOutputConfiguration": {
        "mediaType": "audio/lpcm",
        "sampleRateHertz": 24000,
        "sampleSizeBits": 16,
        "channelCount": 1,
        "voiceId": "matthew",  // or "joanna", "amy", etc.
        "encoding": "base64",
        "audioType": "SPEECH"
      }
    }
  }
}
```

### 3. contentStart
**Purpose:** Start content block (user input)

```json
{
  "event": {
    "contentStart": {
      "contentName": "unique-content-id",
      "contentType": "text",  // or "audio"
      "role": "USER"
    }
  }
}
```

### 4. textInput
**Purpose:** Send text to the model

```json
{
  "event": {
    "textInput": {
      "content": "Hello, how are you?"
    }
  }
}
```

### 5. audioInput
**Purpose:** Send audio chunks to the model

```json
{
  "event": {
    "audioInput": {
      "audioChunk": "base64-encoded-audio-data",
      "mediaType": "audio/lpcm",
      "sampleRateHertz": 16000,
      "sampleSizeBits": 16,
      "channelCount": 1
    }
  }
}
```

### 6. contentEnd
**Purpose:** Signal end of content block

```json
{
  "event": {
    "contentEnd": {
      "contentName": "unique-content-id"
    }
  }
}
```

### 7. promptEnd
**Purpose:** Signal end of prompt

```json
{
  "event": {
    "promptEnd": {
      "promptName": "unique-prompt-id"
    }
  }
}
```

### 8. sessionEnd
**Purpose:** Close the session

```json
{
  "event": {
    "sessionEnd": {}
  }
}
```

---

## 📤 Output Events (Model → Client)

### 1. sessionStart (Acknowledgment)
Model confirms session started

### 2. textOutput
Model's text response (transcription or generated text)

```json
{
  "textOutput": {
    "content": "Hello! I'm doing well, thank you for asking."
  }
}
```

### 3. audioOutput
Model's audio response (base64-encoded audio chunks)

```json
{
  "audioOutput": {
    "audioChunk": "base64-encoded-audio-data"
  }
}
```

### 4. turnComplete
Model finished its turn

### 5. sessionEnd (Acknowledgment)
Model confirms session ended

---

## 🎵 Audio Format Specifications

### Input Audio (Client → Model)
- **Format:** PCM (Linear PCM)
- **Sample Rate:** 16000 Hz (16 kHz)
- **Bit Depth:** 16-bit
- **Channels:** 1 (mono)
- **Encoding:** base64
- **Media Type:** `audio/lpcm`

### Output Audio (Model → Client)
- **Format:** PCM (Linear PCM)
- **Sample Rate:** 24000 Hz (24 kHz)
- **Bit Depth:** 16-bit
- **Channels:** 1 (mono)
- **Encoding:** base64
- **Media Type:** `audio/lpcm`

---

## 🗣️ Available Voices

### US English
- `matthew` (masculine)
- `joanna` (feminine)
- `ivy` (feminine, child)
- `justin` (masculine, child)
- `kendra` (feminine)
- `kimberly` (feminine)
- `salli` (feminine)
- `joey` (masculine)
- `stephen` (masculine)

### UK English
- `brian` (masculine)
- `emma` (feminine)
- `amy` (feminine)

### Other Languages
- See AWS documentation for Spanish, French, German, Italian, Portuguese, Hindi voices

---

## 🔧 Python SDK Usage

### Package Required
```bash
pip install aws-sdk-bedrock-runtime
```

### Basic Structure
```python
from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient
from aws_sdk_bedrock_runtime.config import Config
from aws_sdk_bedrock_runtime.auth import (
    EnvironmentCredentialsResolver,
    HTTPAuthSchemeResolver,
    SigV4AuthScheme
)

# Initialize client
config = Config(
    endpoint_uri="https://bedrock-runtime.us-east-1.amazonaws.com",
    region="us-east-1",
    aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
    auth_scheme_resolver=HTTPAuthSchemeResolver(),
    auth_schemes={"aws.auth#sigv4": SigV4AuthScheme(service="bedrock")}
)

client = BedrockRuntimeClient(config=config)

# Start bidirectional stream
stream = await client.invoke_model_with_bidirectional_stream(
    InvokeModelWithBidirectionalStreamOperationInput(
        model_id="amazon.nova-2-sonic-v1:0"
    )
)

# Send events
await stream.input_stream.send(event_chunk)

# Receive responses
response = await stream.output_stream.receive()
```

---

## 🎯 Event Ordering Rules

**Critical:** Events must be sent in correct order!

### Minimal Text Conversation
```
1. sessionStart
2. promptStart
3. contentStart
4. textInput
5. contentEnd
6. promptEnd
7. sessionEnd
```

### Audio Conversation
```
1. sessionStart
2. promptStart
3. contentStart
4. audioInput (multiple chunks)
5. contentEnd
6. promptEnd
(receive audio/text output)
7. promptStart (next turn)
...
N. sessionEnd
```

### Barge-In (Interrupt Model)
```
1. sessionStart
2. promptStart
3. audioInput (streaming)
4. < model starts responding >
5. audioInput (user interrupts)
6. < model stops >
7. contentEnd
8. promptEnd
```

---

## ⚙️ Configuration Options

### Inference Configuration
- `maxTokens`: Maximum response length (default: 1024)
- `topP`: Nucleus sampling (0.0-1.0, default: 0.9)
- `temperature`: Randomness (0.0-1.0, default: 0.7)

### Turn Detection Configuration
- `endpointingSensitivity`: When model detects end of user speech
  - `LOW`: Wait longer (less likely to interrupt)
  - `MEDIUM`: Balanced (default)
  - `HIGH`: Respond quickly (may cut off user)

---

## 🐛 Common Issues

### Issue: "Invalid event ordering"
**Solution:** Ensure events are sent in correct sequence

### Issue: "Audio format not supported"
**Solution:** Use PCM 16kHz 16-bit mono, base64-encoded

### Issue: "Session timeout"
**Solution:** Keep session alive with periodic events or increase timeout

### Issue: "No audio output"
**Solution:** Ensure `audioOutputConfiguration` is set in `promptStart`

---

## 📝 Notes for Implementation

1. **UUIDs for IDs:** Use unique IDs for `promptName` and `contentName`
2. **Base64 Encoding:** All audio must be base64-encoded
3. **Async Streams:** Both input and output are async generators
4. **Error Handling:** Model may send error events
5. **Barge-In:** Model handles interruptions automatically if configured
6. **Multi-Turn:** Reuse same session, send new `promptStart` for each turn

---

## 🚀 Next Steps

1. Create basic text-to-speech test
2. Add audio input handling
3. Implement bidirectional audio streaming
4. Integrate with WebSocket backend
5. Connect to frontend

---

**Status:** Ready to implement with aws-sdk-bedrock-runtime package!

