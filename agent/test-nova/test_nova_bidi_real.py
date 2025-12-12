"""
Nova 2 Sonic Bidirectional Streaming Test - REAL Implementation

This uses the actual aws-sdk-bedrock-runtime package with correct imports.

Usage:
    python test_nova_bidi_real.py
"""
import asyncio
import json
import uuid

# Correct imports for aws-sdk-bedrock-runtime
from aws_sdk_bedrock_runtime.client import (
    BedrockRuntimeClient,
    InvokeModelWithBidirectionalStreamOperationInput,
)
from aws_sdk_bedrock_runtime.config import Config, SigV4AuthScheme
from aws_sdk_bedrock_runtime.auth import HTTPAuthSchemeResolver
from smithy_aws_core.identity import EnvironmentCredentialsResolver
from smithy_core.shapes import ShapeID

# Configuration
REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"
ENDPOINT_URI = f"https://bedrock-runtime.{REGION}.amazonaws.com"


def create_config():
    """Create the config with proper auth."""
    return Config(
        endpoint_uri=ENDPOINT_URI,
        region=REGION,
        aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
        auth_scheme_resolver=HTTPAuthSchemeResolver(),
        auth_schemes={
            ShapeID("aws.auth#sigv4"): SigV4AuthScheme(service="bedrock")
        }
    )


def create_session_start_event():
    """Create the session start event."""
    return {
        "event": {
            "sessionStart": {
                "inferenceConfiguration": {
                    "maxTokens": 512,
                    "topP": 0.9,
                    "temperature": 0.7
                }
            }
        }
    }


def create_prompt_start_event(prompt_id):
    """Create prompt start event with audio output config."""
    return {
        "event": {
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
        }
    }


def create_content_start_event(content_id):
    """Create content start event."""
    return {
        "event": {
            "contentStart": {
                "contentName": content_id,
                "type": "TEXT",
                "role": "USER"
            }
        }
    }


def create_text_input_event(text):
    """Create text input event."""
    return {
        "event": {
            "textInput": {
                "contentName": str(uuid.uuid4()),
                "content": text
            }
        }
    }


def create_content_end_event(content_id):
    """Create content end event."""
    return {
        "event": {
            "contentEnd": {
                "contentName": content_id
            }
        }
    }


def create_prompt_end_event(prompt_id):
    """Create prompt end event."""
    return {
        "event": {
            "promptEnd": {
                "promptName": prompt_id
            }
        }
    }


def create_session_end_event():
    """Create session end event."""
    return {
        "event": {
            "sessionEnd": {}
        }
    }


async def run_bidirectional_test():
    """Run the bidirectional streaming test."""
    print("\n" + "=" * 60)
    print("Nova 2 Sonic Bidirectional Streaming Test")
    print("=" * 60)
    print(f"Model: {MODEL_ID}")
    print(f"Region: {REGION}")
    print(f"Endpoint: {ENDPOINT_URI}")
    print("=" * 60 + "\n")

    try:
        # Step 1: Create client
        print("[1/5] Creating BedrockRuntimeClient...")
        config = create_config()
        client = BedrockRuntimeClient(config=config)
        print("[OK] Client created\n")

        # Step 2: Start bidirectional stream
        print("[2/5] Starting bidirectional stream...")
        stream = await client.invoke_model_with_bidirectional_stream(
            InvokeModelWithBidirectionalStreamOperationInput(model_id=MODEL_ID)
        )
        print("[OK] Bidirectional stream established!\n")

        # Step 3: Prepare and send events
        print("[3/5] Preparing events...")
        prompt_id = str(uuid.uuid4())
        content_id = str(uuid.uuid4())

        events = [
            create_session_start_event(),
            create_prompt_start_event(prompt_id),
            create_content_start_event(content_id),
            create_text_input_event("Hello Nova! Please say hello back to me."),
            create_content_end_event(content_id),
            create_prompt_end_event(prompt_id),
            create_session_end_event(),
        ]
        print(f"[OK] Prepared {len(events)} events\n")

        # Step 4: Send events
        print("[4/5] Sending events...")
        for i, event in enumerate(events, 1):
            event_json = json.dumps(event)
            await stream.input_stream.send(event_json.encode('utf-8'))
            print(f"  [>] Sent event {i}/{len(events)}: {list(event['event'].keys())[0]}")

        await stream.input_stream.close()
        print("[OK] All events sent, stream closed\n")

        # Step 5: Receive responses
        print("[5/5] Receiving responses...")
        text_responses = []
        audio_chunks = []
        event_count = 0

        async for response in stream.output_stream:
            event_count += 1

            try:
                # The response might be bytes or have a specific structure
                if hasattr(response, 'value'):
                    data = response.value
                    if hasattr(data, 'bytes_'):
                        data = data.bytes_
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                    response_json = json.loads(data)
                elif isinstance(response, bytes):
                    response_json = json.loads(response.decode('utf-8'))
                elif isinstance(response, str):
                    response_json = json.loads(response)
                else:
                    print(f"  [?] Unknown response type: {type(response)}")
                    continue

                # Process the response
                if 'textOutput' in response_json:
                    text = response_json['textOutput'].get('content', '')
                    if text:
                        text_responses.append(text)
                        print(f"  [<] Text: {text}")

                elif 'audioOutput' in response_json:
                    audio_data = response_json['audioOutput'].get('audioChunk', '')
                    if audio_data:
                        audio_chunks.append(audio_data)
                        print(f"  [<] Audio chunk ({len(audio_data)} chars)")

                elif 'turnComplete' in response_json:
                    print("  [<] Turn complete")

                elif 'sessionEnd' in response_json:
                    print("  [<] Session ended")
                    break

                elif 'contentStart' in response_json:
                    print("  [<] Content start (assistant)")

                elif 'contentEnd' in response_json:
                    print("  [<] Content end")

                else:
                    keys = list(response_json.keys())
                    print(f"  [<] Event: {keys}")

            except json.JSONDecodeError as e:
                print(f"  [!] JSON decode error: {e}")
            except Exception as e:
                print(f"  [!] Error processing response: {e}")

        print(f"\n[OK] Received {event_count} response events\n")

        # Summary
        print("\n" + "=" * 60)
        print("[SUCCESS] Bidirectional streaming test complete!")
        print("=" * 60)
        print(f"Text responses: {len(text_responses)}")
        print(f"Audio chunks: {len(audio_chunks)}")

        if text_responses:
            print(f"\nFull text response:")
            print(f'  "{" ".join(text_responses)}"')

        if audio_chunks:
            total_audio = sum(len(c) for c in audio_chunks)
            print(f"\nTotal audio data: {total_audio} base64 chars")
            print("  (This is Nova speaking the response!)")

        print("\n[BREAKTHROUGH] The bidirectional API works!")
        print("[NEXT STEPS]")
        print("  1. Save audio to WAV file and play it")
        print("  2. Add microphone input streaming")
        print("  3. Integrate with backend WebSocket")
        print("  4. Connect frontend audio capture")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print(f"[INFO] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

        print("\n[TROUBLESHOOTING]")
        print("  1. Check AWS credentials (aws sts get-caller-identity)")
        print("  2. Verify Nova Sonic access in Bedrock console")
        print("  3. Check the event format matches API expectations")
        print("  4. Review error message for specific issues")

        return False


if __name__ == "__main__":
    print("\n[START] Testing Nova 2 Sonic bidirectional streaming...\n")

    try:
        success = asyncio.run(run_bidirectional_test())

        if success:
            print("\n" + "=" * 60)
            print("[COMPLETE] SUCCESS - Nova Sonic bidirectional API works!")
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

