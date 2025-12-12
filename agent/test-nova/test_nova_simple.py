"""
Simple Nova Sonic test with timeout for debugging.
"""
import asyncio

# Correct imports
from aws_sdk_bedrock_runtime.client import (
    BedrockRuntimeClient,
    InvokeModelWithBidirectionalStreamOperationInput,
)
from aws_sdk_bedrock_runtime.config import Config, SigV4AuthScheme
from aws_sdk_bedrock_runtime.auth import HTTPAuthSchemeResolver
from smithy_aws_core.identity import EnvironmentCredentialsResolver
from smithy_core.shapes import ShapeID

REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"


async def simple_test():
    print("[1] Creating config...")
    config = Config(
        endpoint_uri=f"https://bedrock-runtime.{REGION}.amazonaws.com",
        region=REGION,
        aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
        auth_scheme_resolver=HTTPAuthSchemeResolver(),
        auth_schemes={
            ShapeID("aws.auth#sigv4"): SigV4AuthScheme(service="bedrock")
        }
    )
    print("[OK] Config created")

    print("[2] Creating client...")
    client = BedrockRuntimeClient(config=config)
    print("[OK] Client created")

    print("[3] Starting bidirectional stream (5s timeout)...")
    try:
        stream = await asyncio.wait_for(
            client.invoke_model_with_bidirectional_stream(
                InvokeModelWithBidirectionalStreamOperationInput(model_id=MODEL_ID)
            ),
            timeout=5.0
        )
        print("[OK] Stream established!")
        print(f"[INFO] Stream type: {type(stream)}")
        print(f"[INFO] Stream attrs: {dir(stream)}")
        return True
    except asyncio.TimeoutError:
        print("[TIMEOUT] Stream creation timed out after 5 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n=== Simple Nova Sonic Test ===\n")
    try:
        result = asyncio.run(simple_test())
        print(f"\n[RESULT] {'Success' if result else 'Failed'}")
    except Exception as e:
        print(f"[FATAL] {e}")
        import traceback
        traceback.print_exc()

