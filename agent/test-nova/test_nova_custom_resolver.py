"""
Nova Sonic test with custom credential resolver.
"""
import asyncio
import json
import uuid
import boto3

# Smithy SDK imports
from aws_sdk_bedrock_runtime.client import (
    BedrockRuntimeClient,
    InvokeModelWithBidirectionalStreamOperationInput,
)
from aws_sdk_bedrock_runtime.models import (
    InvokeModelWithBidirectionalStreamInputChunk,
    BidirectionalInputPayloadPart,
)
from aws_sdk_bedrock_runtime.config import Config, SigV4AuthScheme
from aws_sdk_bedrock_runtime.auth import HTTPAuthSchemeResolver
from smithy_aws_core.identity import AWSCredentialsIdentity, AWSIdentityProperties
from smithy_core.aio.interfaces.identity import IdentityResolver
from smithy_core.shapes import ShapeID

REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"


class Boto3CredentialsResolver(IdentityResolver[AWSCredentialsIdentity, AWSIdentityProperties]):
    """Credential resolver that uses boto3 session credentials."""
    
    def __init__(self):
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            raise ValueError("No AWS credentials found in boto3 session")
        frozen = credentials.get_frozen_credentials()
        self._access_key = frozen.access_key
        self._secret_key = frozen.secret_key
        self._token = frozen.token
    
    async def get_identity(self, *, properties: AWSIdentityProperties) -> AWSCredentialsIdentity:
        return AWSCredentialsIdentity(
            access_key_id=self._access_key,
            secret_access_key=self._secret_key,
            session_token=self._token
        )


async def test_with_custom_resolver():
    print("\n=== Nova Sonic Test with Custom Credential Resolver ===\n")
    
    # Create custom resolver
    print("[1] Creating boto3 credential resolver...")
    try:
        resolver = Boto3CredentialsResolver()
        print(f"[OK] Access key: {resolver._access_key[:8]}...")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # Create config
    print("\n[2] Creating config...")
    config = Config(
        endpoint_uri=f"https://bedrock-runtime.{REGION}.amazonaws.com",
        region=REGION,
        aws_credentials_identity_resolver=resolver,
        auth_scheme_resolver=HTTPAuthSchemeResolver(),
        auth_schemes={
            ShapeID("aws.auth#sigv4"): SigV4AuthScheme(service="bedrock")
        }
    )
    print("[OK] Config created")

    # Create client
    print("\n[3] Creating client...")
    client = BedrockRuntimeClient(config=config)
    print("[OK] Client created")

    # Start stream
    print("\n[4] Starting bidirectional stream (15s timeout)...")
    try:
        stream = await asyncio.wait_for(
            client.invoke_model_with_bidirectional_stream(
                InvokeModelWithBidirectionalStreamOperationInput(model_id=MODEL_ID)
            ),
            timeout=15.0
        )
        print("[OK] Stream established!")
        print(f"[INFO] Stream type: {type(stream)}")
        
        # Check what we got
        attrs = [a for a in dir(stream) if not a.startswith('_')]
        print(f"[INFO] Stream attributes: {attrs}")
        
        # Send session start
        print("\n[5] Sending session start...")
        event = {
            "event": {
                "sessionStart": {
                    "inferenceConfiguration": {"maxTokens": 512}
                }
            }
        }
        event_bytes = json.dumps(event).encode('utf-8')
        payload = BidirectionalInputPayloadPart(bytes_=event_bytes)
        chunk = InvokeModelWithBidirectionalStreamInputChunk(value=payload)
        await stream.input_stream.send(chunk)
        print("[OK] Sent")
        
        # Check stream output options
        print("\n[6] Checking output methods...")
        print(f"  output_stream: {stream.output_stream}")
        print(f"  output: {stream.output}")
        print(f"  await_output: {stream.await_output}")
        
        # Try await_output
        print("\n[7] Calling await_output (10s)...")
        try:
            output = await asyncio.wait_for(stream.await_output(), timeout=10.0)
            print(f"[OK] Got output: {type(output)}")
            print(f"[DATA] {output}")
            
            # Check if output has an async iterator
            if hasattr(output, '__aiter__'):
                print("\n[8] Iterating output...")
                count = 0
                async for item in output:
                    count += 1
                    print(f"[<] Item {count}: {item}")
                    if count >= 5:
                        break
        except asyncio.TimeoutError:
            print("[TIMEOUT]")
        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
        
        # Close
        await stream.input_stream.close()
        return True
        
    except asyncio.TimeoutError:
        print("[TIMEOUT] Stream creation timed out")
        return False
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_with_custom_resolver())
        print(f"\n{'='*50}")
        print(f"[RESULT] {'SUCCESS!' if result else 'Failed'}")
        print(f"{'='*50}\n")
    except Exception as e:
        print(f"[FATAL] {e}")
        import traceback
        traceback.print_exc()

