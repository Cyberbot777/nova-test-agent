"""
Nova 2 Sonic Test - WITH AUDIO INPUT

Nova Sonic REQUIRES audio input - it's a speech-to-speech model!
This test sends silent audio to trigger a response.
"""
import asyncio
import json
import uuid
import base64
import numpy as np
import os
import boto3

from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient, InvokeModelWithBidirectionalStreamOperationInput
from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart
from aws_sdk_bedrock_runtime.config import Config, HTTPAuthSchemeResolver, SigV4AuthScheme
from smithy_aws_core.identity.environment import EnvironmentCredentialsResolver
from smithy_core.shapes import ShapeID

REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"


def get_env_creds():
    """Set AWS credentials as environment variables."""
    session = boto3.Session()
    creds = session.get_credentials().get_frozen_credentials()
    os.environ['AWS_ACCESS_KEY_ID'] = creds.access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = creds.secret_key
    if creds.token:
        os.environ['AWS_SESSION_TOKEN'] = creds.token
    print(f"[OK] Credentials set: {creds.access_key[:8]}...")


def generate_audio_with_tone(duration_ms=2000, sample_rate=16000, frequency=440):
    """Generate audio with a simple tone (to simulate speech presence)."""
    num_samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, num_samples, dtype=np.float32)
    # Generate a simple tone
    audio = np.sin(2 * np.pi * frequency * t) * 0.3
    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)
    return base64.b64encode(audio_int16.tobytes()).decode('utf-8')


def create_event(event_data):
    """Create a properly formatted input chunk."""
    event_json = json.dumps({"event": event_data})
    return InvokeModelWithBidirectionalStreamInputChunk(
        value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
    )


async def run_test():
    print("\n" + "=" * 60)
    print("Nova 2 Sonic Test WITH AUDIO INPUT")
    print("=" * 60 + "\n")

    # Set up credentials
    print("[1] Setting up credentials...")
    get_env_creds()

    # Create client
    print("\n[2] Creating Bedrock client...")
    config = Config(
        endpoint_uri=f"https://bedrock-runtime.{REGION}.amazonaws.com",
        region=REGION,
        aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
        auth_scheme_resolver=HTTPAuthSchemeResolver(),
        auth_schemes={ShapeID("aws.auth#sigv4"): SigV4AuthScheme(service="bedrock")}
    )
    client = BedrockRuntimeClient(config=config)
    print("[OK] Client created")

    # Start stream
    print("\n[3] Starting bidirectional stream...")
    stream = await client.invoke_model_with_bidirectional_stream(
        InvokeModelWithBidirectionalStreamOperationInput(model_id=MODEL_ID)
    )
    print("[OK] Stream established!")

    # Generate IDs
    prompt_name = str(uuid.uuid4())
    system_content = str(uuid.uuid4())
    audio_content = str(uuid.uuid4())

    print("\n[4] Sending session events...")
    
    # 1. Session Start
    await stream.input_stream.send(create_event({
        "sessionStart": {
            "inferenceConfiguration": {
                "maxTokens": 1024,
                "topP": 0.9,
                "temperature": 0.7
            }
        }
    }))
    print("  [>] sessionStart")

    # 2. Prompt Start
    await stream.input_stream.send(create_event({
        "promptStart": {
            "promptName": prompt_name,
            "textOutputConfiguration": {"mediaType": "text/plain"},
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
    }))
    print("  [>] promptStart")

    # 3. System prompt
    await stream.input_stream.send(create_event({
        "contentStart": {
            "promptName": prompt_name,
            "contentName": system_content,
            "type": "TEXT",
            "interactive": True,
            "role": "SYSTEM",
            "textInputConfiguration": {"mediaType": "text/plain"}
        }
    }))
    await stream.input_stream.send(create_event({
        "textInput": {
            "promptName": prompt_name,
            "contentName": system_content,
            "content": "You are a helpful voice assistant. When you hear a tone, say hello."
        }
    }))
    await stream.input_stream.send(create_event({
        "contentEnd": {"promptName": prompt_name, "contentName": system_content}
    }))
    print("  [>] system prompt sent")

    # 4. AUDIO INPUT - This is what Nova Sonic requires!
    print("\n[5] Generating and sending audio...")
    audio_data = generate_audio_with_tone(duration_ms=500)  # 500ms tone
    print(f"  [>] Generated {len(audio_data)} base64 chars of audio")

    # Audio content start
    await stream.input_stream.send(create_event({
        "contentStart": {
            "promptName": prompt_name,
            "contentName": audio_content,
            "type": "AUDIO",
            "interactive": True,
            "role": "USER",
            "audioInputConfiguration": {
                "mediaType": "audio/lpcm",
                "sampleRateHertz": 16000,
                "sampleSizeBits": 16,
                "channelCount": 1,
                "audioType": "SPEECH",
                "encoding": "base64"
            }
        }
    }))
    print("  [>] contentStart (AUDIO)")

    # Send audio in chunks
    chunk_size = 8000  # ~500ms of audio per chunk at 16kHz
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i+chunk_size]
        await stream.input_stream.send(create_event({
            "audioInput": {
                "promptName": prompt_name,
                "contentName": audio_content,
                "content": chunk
            }
        }))
        print(f"  [>] audioInput chunk ({len(chunk)} chars)")
        await asyncio.sleep(0.05)

    # Audio content end
    await stream.input_stream.send(create_event({
        "contentEnd": {"promptName": prompt_name, "contentName": audio_content}
    }))
    print("  [>] contentEnd (AUDIO)")

    # 5. Prompt End
    await stream.input_stream.send(create_event({
        "promptEnd": {"promptName": prompt_name}
    }))
    print("  [>] promptEnd")
    print("[OK] All events sent\n")

    # Process responses
    print("[6] Waiting for responses...")
    responses = []
    text_content = []
    audio_chunks = []
    
    try:
        while True:
            output = await asyncio.wait_for(stream.await_output(), timeout=20.0)
            result = await output[1].receive()
            
            if result.value and result.value.bytes_:
                data = json.loads(result.value.bytes_.decode('utf-8'))
                responses.append(data)
                
                if 'event' in data:
                    event_name = list(data['event'].keys())[0]
                    
                    if event_name == 'textOutput':
                        role = data['event']['textOutput'].get('role', '')
                        content = data['event']['textOutput'].get('content', '')
                        if content:
                            text_content.append(content)
                            print(f"  [TEXT] {content}")
                    
                    elif event_name == 'audioOutput':
                        chunk = data['event']['audioOutput'].get('content', '')
                        if chunk:
                            audio_chunks.append(chunk)
                            print(f"  [AUDIO] chunk ({len(chunk)} chars)")
                    
                    elif event_name == 'promptEnd':
                        print(f"  [EVENT] promptEnd - Response complete!")
                        break
                    
                    else:
                        print(f"  [EVENT] {event_name}")
                        
    except asyncio.TimeoutError:
        print("  [TIMEOUT]")
    except StopAsyncIteration:
        print("  [END]")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # Close
    print("\n[7] Closing stream...")
    try:
        await stream.input_stream.send(create_event({"sessionEnd": {}}))
        await stream.input_stream.close()
    except:
        pass
    print("[OK] Stream closed")

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total events: {len(responses)}")
    print(f"Text responses: {len(text_content)}")
    print(f"Audio chunks: {len(audio_chunks)}")
    
    if text_content:
        print(f"\nTranscript: \"{' '.join(text_content)}\"")
    
    if audio_chunks:
        total = sum(len(c) for c in audio_chunks)
        print(f"\nAudio: {total} base64 chars (~{total * 3 // 4 // 48000:.1f}s at 24kHz)")

    success = len(audio_chunks) > 0 or len(text_content) > 0
    print("\n" + "=" * 60)
    print(f"{'SUCCESS! Nova Sonic responded!' if success else 'No response'}")
    print("=" * 60 + "\n")
    
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(run_test())
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()

