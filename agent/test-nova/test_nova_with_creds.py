"""
Nova Sonic test using boto3 credentials with smithy SDK.
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
from aws_sdk_bedrock_runtime.config import Config, SigV4AuthScheme
from aws_sdk_bedrock_runtime.auth import HTTPAuthSchemeResolver
# Not needed - credentials passed directly to Config
# from smithy_aws_core.identity import StaticCredentialsResolver, AWSCredentialsIdentity
from smithy_core.shapes import ShapeID

REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"


def get_boto3_credentials():
    """Get credentials from boto3 session."""
    session = boto3.Session()
    credentials = session.get_credentials()
    if credentials is None:
        raise ValueError("No AWS credentials found")
    
    frozen = credentials.get_frozen_credentials()
    return {
        'access_key': frozen.access_key,
        'secret_key': frozen.secret_key,
        'token': frozen.token  # May be None for non-temporary credentials
    }


async def test_with_creds():
    print("\n=== Nova Sonic Test with boto3 Credentials ===\n")
    
    # Get credentials from boto3
    print("[1] Getting credentials from boto3...")
    try:
        creds = get_boto3_credentials()
        print(f"[OK] Access key: {creds['access_key'][:8]}...")
        print(f"[OK] Has session token: {creds['token'] is not None}")
    except Exception as e:
        print(f"[ERROR] Failed to get credentials: {e}")
        return False

    # Create config with credentials directly
    print("\n[2] Creating config with credentials...")
    config = Config(
        endpoint_uri=f"https://bedrock-runtime.{REGION}.amazonaws.com",
        region=REGION,
        aws_access_key_id=creds['access_key'],
        aws_secret_access_key=creds['secret_key'],
        aws_session_token=creds['token'],
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

    # Start stream with timeout
    print("\n[4] Starting bidirectional stream (10s timeout)...")
    try:
        stream = await asyncio.wait_for(
            client.invoke_model_with_bidirectional_stream(
                InvokeModelWithBidirectionalStreamOperationInput(model_id=MODEL_ID)
            ),
            timeout=10.0
        )
        print("[OK] Stream established!")
        print(f"[INFO] Stream type: {type(stream)}")
        
        # Check stream attributes
        if hasattr(stream, 'input_stream'):
            print("[OK] Has input_stream")
        if hasattr(stream, 'output_stream'):
            print("[OK] Has output_stream")
            
        # Try sending a simple event
        print("\n[6] Sending session start event...")
        session_event = {
            "event": {
                "sessionStart": {
                    "inferenceConfiguration": {
                        "maxTokens": 512
                    }
                }
            }
        }
        
        event_bytes = json.dumps(session_event).encode('utf-8')
        await stream.input_stream.send(event_bytes)
        print("[OK] Session start sent")
        
        # Try receiving
        print("\n[7] Waiting for response (5s timeout)...")
        try:
            response = await asyncio.wait_for(
                stream.output_stream.__anext__(),
                timeout=5.0
            )
            print(f"[OK] Got response: {type(response)}")
            print(f"[DATA] {response}")
        except asyncio.TimeoutError:
            print("[TIMEOUT] No response in 5 seconds")
        except StopAsyncIteration:
            print("[END] Stream ended")
            
        # Close
        print("\n[8] Closing stream...")
        await stream.input_stream.close()
        print("[OK] Stream closed")
        
        return True
        
    except asyncio.TimeoutError:
        print("[TIMEOUT] Stream creation timed out after 10 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_with_creds())
        print(f"\n{'='*50}")
        print(f"[RESULT] {'SUCCESS!' if result else 'Failed'}")
        print(f"{'='*50}\n")
    except Exception as e:
        print(f"[FATAL] {e}")
        import traceback
        traceback.print_exc()

