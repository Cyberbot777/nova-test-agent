"""
Nova 2 Sonic Bidirectional Streaming Test

Tests the actual bidirectional streaming API with Nova Sonic using
the aws-sdk-bedrock-runtime package.

Usage:
    python test_nova_streaming.py

This test sends a simple text message and receives both text and audio responses.
"""
import asyncio
import json
import uuid
import base64
from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient
from aws_sdk_bedrock_runtime.config import Config
from aws_sdk_bedrock_runtime.auth import (
    EnvironmentCredentialsResolver,
    HTTPAuthSchemeResolver,
    SigV4AuthScheme
)
from aws_sdk_bedrock_runtime.model import (
    InvokeModelWithBidirectionalStreamOperationInput,
    InvokeModelWithBidirectionalStreamInputChunk,
    BidirectionalInputPayloadPart
)

# Configuration
REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"


def create_client():
    """Create Bedrock Runtime client for bidirectional streaming."""
    config = Config(
        endpoint_uri=f"https://bedrock-runtime.{REGION}.amazonaws.com",
        region=REGION,
        aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
        auth_scheme_resolver=HTTPAuthSchemeResolver(),
        auth_schemes={"aws.auth#sigv4": SigV4AuthScheme(service="bedrock")}
    )
    return BedrockRuntimeClient(config=config)


def create_event(event_data):
    """Create an input chunk from event data."""
    event_json = json.dumps({"event": event_data})
    return InvokeModelWithBidirectionalStreamInputChunk(
        value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
    )


async def test_text_conversation():
    """Test a simple text conversation with Nova Sonic."""
    print("\n" + "=" * 60)
    print("Nova 2 Sonic Bidirectional Streaming Test")
    print("=" * 60)
    print(f"Model: {MODEL_ID}")
    print(f"Region: {REGION}")
    print(f"Test: Simple text-to-speech conversation")
    print("=" * 60 + "\n")
    
    try:
        # Step 1: Create client
        print("[1/5] Creating Bedrock Runtime client...")
        client = create_client()
        print("[OK] Client created\n")
        
        # Step 2: Start bidirectional stream
        print("[2/5] Starting bidirectional stream...")
        stream = await client.invoke_model_with_bidirectional_stream(
            InvokeModelWithBidirectionalStreamOperationInput(model_id=MODEL_ID)
        )
        print("[OK] Stream established\n")
        
        # Step 3: Prepare events
        print("[3/5] Preparing events...")
        
        prompt_id = str(uuid.uuid4())
        content_id = str(uuid.uuid4())
        
        events = [
            # Session start
            create_event({
                "sessionStart": {
                    "inferenceConfiguration": {
                        "maxTokens": 512,
                        "topP": 0.9,
                        "temperature": 0.7
                    },
                    "turnDetectionConfiguration": {
                        "endpointingSensitivity": "HIGH"
                    }
                }
            }),
            
            # Prompt start
            create_event({
                "promptStart": {
                    "promptName": prompt_id,
                    "textOutputConfiguration": {
                        "mediaType": "text/plain"
                    },
                    "audioOutputConfiguration": {
                        "mediaType": "audio/lpcm",
                        "sampleRateHertz": 24000,
                        "sampleSizeBits": 16,
                        "channelCount": 1,
                        "voiceId": "matthew",
                        "encoding": "base64",
                        "audioType": "SPEECH"
                    }
                }
            }),
            
            # Content start
            create_event({
                "contentStart": {
                    "contentName": content_id,
                    "contentType": "text",
                    "role": "USER"
                }
            }),
            
            # Text input
            create_event({
                "textInput": {
                    "content": "Hello Nova! Please say hello back to me."
                }
            }),
            
            # Content end
            create_event({
                "contentEnd": {
                    "contentName": content_id
                }
            }),
            
            # Prompt end
            create_event({
                "promptEnd": {
                    "promptName": prompt_id
                }
            }),
            
            # Session end
            create_event({
                "sessionEnd": {}
            })
        ]
        
        print(f"[OK] Prepared {len(events)} events\n")
        
        # Step 4: Send events
        print("[4/5] Sending events to Nova Sonic...")
        for i, event in enumerate(events, 1):
            await stream.input_stream.send(event)
            print(f"  [>] Sent event {i}/{len(events)}")
        
        await stream.input_stream.close()
        print("[OK] All events sent\n")
        
        # Step 5: Receive responses
        print("[5/5] Receiving responses...")
        text_responses = []
        audio_chunks = []
        event_count = 0
        
        async for response in stream.output_stream:
            event_count += 1
            
            if hasattr(response, 'value') and hasattr(response.value, 'bytes_'):
                try:
                    response_json = json.loads(response.value.bytes_.decode('utf-8'))
                    
                    if 'textOutput' in response_json:
                        text = response_json['textOutput'].get('content', '')
                        if text:
                            text_responses.append(text)
                            print(f"  [<] Text: {text}")
                    
                    elif 'audioOutput' in response_json:
                        audio_data = response_json['audioOutput'].get('audioChunk', '')
                        if audio_data:
                            audio_chunks.append(audio_data)
                            print(f"  [<] Audio chunk received ({len(audio_data)} chars base64)")
                    
                    elif 'turnComplete' in response_json:
                        print(f"  [<] Turn complete")
                    
                    elif 'sessionEnd' in response_json:
                        print(f"  [<] Session ended")
                        break
                    
                    else:
                        print(f"  [<] Other event: {list(response_json.keys())}")
                        
                except json.JSONDecodeError as e:
                    print(f"  [!] Could not decode response: {e}")
        
        print(f"[OK] Received {event_count} response events\n")
        
        # Summary
        print("\n" + "=" * 60)
        print("[SUCCESS] Bidirectional streaming test complete!")
        print("=" * 60)
        print(f"Text responses: {len(text_responses)}")
        print(f"Audio chunks: {len(audio_chunks)}")
        
        if text_responses:
            print(f"\nFull text response:")
            print(f"  \"{' '.join(text_responses)}\"")
        
        if audio_chunks:
            print(f"\nAudio received: {sum(len(c) for c in audio_chunks)} total base64 chars")
            print(f"  (This is Nova speaking the response!)")
            
        print("\n[NEXT STEPS]")
        print("  1. Save audio to file and play it")
        print("  2. Add microphone input")
        print("  3. Implement real-time streaming")
        print("  4. Integrate with backend/frontend")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print(f"[INFO] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        print("\n[TROUBLESHOOTING]")
        print("  1. Check AWS credentials")
        print("  2. Verify Nova Sonic access in Bedrock")
        print("  3. Check network connectivity")
        print("  4. Review error message above")
        return False


if __name__ == "__main__":
    print("\n[START] Testing Nova 2 Sonic bidirectional streaming...\n")
    
    try:
        success = asyncio.run(test_text_conversation())
        
        if success:
            print("\n" + "=" * 60)
            print("[COMPLETE] Test passed!")
            print("=" * 60 + "\n")
        else:
            print("\n" + "=" * 60)
            print("[INCOMPLETE] Test failed - see errors above")
            print("=" * 60 + "\n")
            
    except KeyboardInterrupt:
        print("\n\n[STOP] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()

