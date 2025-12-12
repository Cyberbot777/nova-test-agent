"""
FULL Nova 2 Sonic Bidirectional Streaming Test

Sends the complete event sequence required for a response.
"""
import asyncio
import json
import uuid
import boto3

from aws_sdk_bedrock_runtime.client import (
    BedrockRuntimeClient,
    InvokeModelWithBidirectionalStreamOperationInput,
)
from aws_sdk_bedrock_runtime.config import Config, SigV4AuthScheme
from aws_sdk_bedrock_runtime.auth import HTTPAuthSchemeResolver
from aws_sdk_bedrock_runtime.models import (
    InvokeModelWithBidirectionalStreamInputChunk,
    BidirectionalInputPayloadPart,
)
from smithy_aws_core.identity import AWSCredentialsIdentity, AWSIdentityProperties
from smithy_core.aio.interfaces.identity import IdentityResolver
from smithy_core.shapes import ShapeID

REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"


class Boto3CredResolver(IdentityResolver[AWSCredentialsIdentity, AWSIdentityProperties]):
    def __init__(self):
        creds = boto3.Session().get_credentials().get_frozen_credentials()
        self._ak, self._sk, self._tok = creds.access_key, creds.secret_key, creds.token
    
    async def get_identity(self, *, properties: AWSIdentityProperties) -> AWSCredentialsIdentity:
        return AWSCredentialsIdentity(access_key_id=self._ak, secret_access_key=self._sk, session_token=self._tok)


def make_event(event_data):
    """Create a properly formatted input chunk."""
    payload = BidirectionalInputPayloadPart(bytes_=json.dumps({"event": event_data}).encode())
    return InvokeModelWithBidirectionalStreamInputChunk(value=payload)


async def run_full_test():
    print("\n" + "=" * 60)
    print("FULL Nova 2 Sonic Bidirectional Test")
    print("=" * 60 + "\n")

    # Setup
    print("[1] Setting up client...")
    config = Config(
        endpoint_uri=f"https://bedrock-runtime.{REGION}.amazonaws.com",
        region=REGION,
        aws_credentials_identity_resolver=Boto3CredResolver(),
        auth_scheme_resolver=HTTPAuthSchemeResolver(),
        auth_schemes={ShapeID("aws.auth#sigv4"): SigV4AuthScheme(service="bedrock")}
    )
    client = BedrockRuntimeClient(config=config)
    print("[OK] Client ready")

    # Start stream
    print("\n[2] Starting bidirectional stream...")
    stream = await asyncio.wait_for(
        client.invoke_model_with_bidirectional_stream(
            InvokeModelWithBidirectionalStreamOperationInput(model_id=MODEL_ID)
        ),
        timeout=15.0
    )
    print("[OK] Stream established")

    # Prepare events
    prompt_id = str(uuid.uuid4())
    content_id = str(uuid.uuid4())

    events = [
        # Session Start
        {"sessionStart": {
            "inferenceConfiguration": {"maxTokens": 512, "temperature": 0.7, "topP": 0.9}
        }},
        # Prompt Start
        {"promptStart": {
            "promptName": prompt_id,
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
        }},
        # Content Start
        {"contentStart": {
            "promptName": prompt_id,
            "contentName": content_id,
            "type": "TEXT",
            "interactive": True,
            "role": "USER"
        }},
        # Text Input
        {"textInput": {
            "promptName": prompt_id,
            "contentName": content_id,
            "content": "Hello! Please say hello back."
        }},
        # Content End
        {"contentEnd": {
            "promptName": prompt_id,
            "contentName": content_id
        }},
        # Prompt End
        {"promptEnd": {
            "promptName": prompt_id
        }},
    ]

    # Send all events
    print("\n[3] Sending events...")
    for i, evt in enumerate(events, 1):
        key = list(evt.keys())[0]
        await stream.input_stream.send(make_event(evt))
        print(f"  [{i}/{len(events)}] Sent: {key}")
        await asyncio.sleep(0.05)  # Small delay between events
    print("[OK] All events sent")

    # Wait for and process responses
    print("\n[4] Waiting for responses...")
    
    # Start a task to read responses
    async def read_responses():
        responses = []
        try:
            output = await stream.await_output()
            if output and hasattr(output, '__aiter__'):
                async for item in output:
                    responses.append(item)
                    # Print progress
                    if hasattr(item, 'value') and hasattr(item.value, 'bytes_'):
                        data = json.loads(item.value.bytes_.decode())
                        if 'textOutput' in data:
                            print(f"  [TEXT] {data['textOutput'].get('content', '')[:50]}...")
                        elif 'audioOutput' in data:
                            print(f"  [AUDIO] chunk received")
                        else:
                            print(f"  [EVENT] {list(data.keys())}")
        except Exception as e:
            print(f"  [ERROR] {e}")
        return responses

    try:
        responses = await asyncio.wait_for(read_responses(), timeout=30.0)
        print(f"\n[OK] Received {len(responses)} response events")
    except asyncio.TimeoutError:
        print("\n[TIMEOUT] No response in 30 seconds")
        responses = []

    # Close
    print("\n[5] Closing stream...")
    try:
        await stream.input_stream.send(make_event({"sessionEnd": {}}))
        await stream.input_stream.close()
    except:
        pass
    print("[OK] Done")

    return len(responses) > 0


if __name__ == "__main__":
    try:
        success = asyncio.run(run_full_test())
        print(f"\n{'='*60}")
        print(f"RESULT: {'SUCCESS - Nova Sonic responded!' if success else 'No response received'}")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()

