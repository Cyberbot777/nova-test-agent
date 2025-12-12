"""
Nova 2 Sonic Test - Based on Official AWS Sample

This is based on the aws-samples/sample-aws-strands-nova-voice-assistant repo.
"""
import asyncio
import json
import uuid

# Use the EXACT imports from the AWS sample
from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient, InvokeModelWithBidirectionalStreamOperationInput
from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart
from aws_sdk_bedrock_runtime.config import Config, HTTPAuthSchemeResolver, SigV4AuthScheme

# Use our version's import path
from smithy_aws_core.identity.environment import EnvironmentCredentialsResolver

import os
import boto3

REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"


def get_env_creds():
    """Get AWS credentials and set as environment variables for EnvironmentCredentialsResolver."""
    session = boto3.Session()
    creds = session.get_credentials().get_frozen_credentials()
    os.environ['AWS_ACCESS_KEY_ID'] = creds.access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = creds.secret_key
    if creds.token:
        os.environ['AWS_SESSION_TOKEN'] = creds.token
    print(f"[OK] Set credentials in environment: {creds.access_key[:8]}...")


def create_event(event_data):
    """Create a properly formatted input chunk."""
    event_json = json.dumps({"event": event_data})
    return InvokeModelWithBidirectionalStreamInputChunk(
        value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
    )


async def run_test():
    print("\n" + "=" * 60)
    print("Nova 2 Sonic Test (Based on Official AWS Sample)")
    print("=" * 60 + "\n")

    # Set up environment credentials
    print("[1] Setting up credentials...")
    get_env_creds()

    # Create client with EXACT config from AWS sample
    print("\n[2] Creating Bedrock client...")
    # Import ShapeID for the auth scheme key
    from smithy_core.shapes import ShapeID
    
    config = Config(
        endpoint_uri=f"https://bedrock-runtime.{REGION}.amazonaws.com",
        region=REGION,
        aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
        auth_scheme_resolver=HTTPAuthSchemeResolver(),
        auth_schemes={ShapeID("aws.auth#sigv4"): SigV4AuthScheme(service="bedrock")}
    )
    client = BedrockRuntimeClient(config=config)
    print("[OK] Client created")

    # Start bidirectional stream
    print("\n[3] Starting bidirectional stream...")
    stream = await client.invoke_model_with_bidirectional_stream(
        InvokeModelWithBidirectionalStreamOperationInput(model_id=MODEL_ID)
    )
    print("[OK] Stream established!")

    # Generate IDs
    prompt_name = str(uuid.uuid4())
    system_content = str(uuid.uuid4())
    audio_content = str(uuid.uuid4())

    # Send events in correct order (based on AWS sample)
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

    # 2. Prompt Start (with audio output config)
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

    # 3. System prompt - Content Start (TEXT, SYSTEM role)
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
    print("  [>] contentStart (SYSTEM)")

    # 4. Text Input - System prompt
    await stream.input_stream.send(create_event({
        "textInput": {
            "promptName": prompt_name,
            "contentName": system_content,
            "content": "You are a helpful voice assistant. Keep responses very brief."
        }
    }))
    print("  [>] textInput (system prompt)")

    # 5. Content End - System prompt
    await stream.input_stream.send(create_event({
        "contentEnd": {
            "promptName": prompt_name,
            "contentName": system_content
        }
    }))
    print("  [>] contentEnd (SYSTEM)")

    # 6. User message - Content Start (TEXT, USER role)
    user_content = str(uuid.uuid4())
    await stream.input_stream.send(create_event({
        "contentStart": {
            "promptName": prompt_name,
            "contentName": user_content,
            "type": "TEXT",
            "interactive": True,
            "role": "USER",
            "textInputConfiguration": {"mediaType": "text/plain"}
        }
    }))
    print("  [>] contentStart (USER)")

    # 7. Text Input - User message
    await stream.input_stream.send(create_event({
        "textInput": {
            "promptName": prompt_name,
            "contentName": user_content,
            "content": "Hello! Say hello back please."
        }
    }))
    print("  [>] textInput (user message)")

    # 8. Content End - User message
    await stream.input_stream.send(create_event({
        "contentEnd": {
            "promptName": prompt_name,
            "contentName": user_content
        }
    }))
    print("  [>] contentEnd (USER)")

    # 9. Prompt End - Signal we're done with input
    await stream.input_stream.send(create_event({
        "promptEnd": {
            "promptName": prompt_name
        }
    }))
    print("  [>] promptEnd")
    print("[OK] All events sent\n")

    # Process responses using the EXACT pattern from AWS sample
    print("[5] Waiting for responses...")
    responses = []
    text_content = []
    audio_chunks = []
    
    try:
        while True:
            # This is the key pattern from the AWS sample!
            output = await asyncio.wait_for(stream.await_output(), timeout=15.0)
            result = await output[1].receive()
            
            if result.value and result.value.bytes_:
                data = json.loads(result.value.bytes_.decode('utf-8'))
                responses.append(data)
                
                if 'event' in data:
                    event_name = list(data['event'].keys())[0]
                    
                    if event_name == 'textOutput':
                        role = data['event']['textOutput'].get('role', '')
                        content = data['event']['textOutput'].get('content', '')
                        if content and role == 'ASSISTANT':
                            text_content.append(content)
                            print(f"  [TEXT] {content}")
                    
                    elif event_name == 'audioOutput':
                        chunk = data['event']['audioOutput'].get('content', '')
                        if chunk:
                            audio_chunks.append(chunk)
                            print(f"  [AUDIO] chunk ({len(chunk)} chars)")
                    
                    elif event_name == 'contentEnd':
                        print(f"  [EVENT] contentEnd")
                    
                    elif event_name == 'promptEnd':
                        print(f"  [EVENT] promptEnd - Response complete!")
                        break
                    
                    else:
                        print(f"  [EVENT] {event_name}")
                        
    except asyncio.TimeoutError:
        print("  [TIMEOUT] No more responses")
    except StopAsyncIteration:
        print("  [END] Stream ended")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # Close stream
    print("\n[6] Closing stream...")
    await stream.input_stream.send(create_event({"sessionEnd": {}}))
    await stream.input_stream.close()
    print("[OK] Stream closed")

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total response events: {len(responses)}")
    print(f"Text responses: {len(text_content)}")
    print(f"Audio chunks: {len(audio_chunks)}")
    
    if text_content:
        print(f"\nAssistant said: \"{' '.join(text_content)}\"")
    
    if audio_chunks:
        total_audio = sum(len(c) for c in audio_chunks)
        print(f"\nAudio data: {total_audio} base64 characters total")
        print("(This is Nova Sonic speaking the response!)")

    success = len(text_content) > 0 or len(audio_chunks) > 0
    print("\n" + "=" * 60)
    print(f"{'SUCCESS! Nova Sonic responded!' if success else 'No response received'}")
    print("=" * 60 + "\n")
    
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(run_test())
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()

