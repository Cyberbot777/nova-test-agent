"""
Nova 2 Sonic Test via Bedrock Runtime API

This uses the standard AWS Bedrock Runtime API directly to test
Nova 2 Sonic connectivity, bypassing Strands SDK for now.

Usage:
    python test_nova_bedrock.py

Requirements:
    - AWS credentials configured
    - Nova 2 Sonic access in us-east-1
    - boto3 installed
"""
import json
import boto3
from botocore.exceptions import ClientError

# Configuration
REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"

def test_model_access():
    """Test if we can access Nova 2 Sonic model."""
    print("\n" + "=" * 60)
    print("Nova 2 Sonic Bedrock Access Test")
    print("=" * 60)
    print(f"Model: {MODEL_ID}")
    print(f"Region: {REGION}")
    print("=" * 60 + "\n")
    
    try:
        # Create Bedrock Runtime client
        print("[1/3] Creating Bedrock Runtime client...")
        client = boto3.client(
            service_name='bedrock-runtime',
            region_name=REGION
        )
        print("[OK] Client created\n")
        
        # Check AWS credentials
        print("[2/3] Verifying AWS credentials...")
        sts = boto3.client('sts', region_name=REGION)
        identity = sts.get_caller_identity()
        print(f"[OK] Authenticated as: {identity['Arn']}\n")
        
        # Try to get model info (this will fail if model not accessible)
        print("[3/3] Checking Nova 2 Sonic model access...")
        bedrock = boto3.client('bedrock', region_name=REGION)
        
        try:
            # List foundation models to see if Nova Sonic is available
            response = bedrock.list_foundation_models()
            nova_models = [m for m in response['modelSummaries'] if 'nova' in m['modelId'].lower()]
            
            print(f"[INFO] Found {len(nova_models)} Nova models available:")
            for model in nova_models:
                marker = "[*]" if model['modelId'] == MODEL_ID else "   "
                print(f"  {marker} {model['modelId']}")
            
            # Check if our specific model is in the list
            if any(m['modelId'] == MODEL_ID for m in nova_models):
                print(f"\n[SUCCESS] {MODEL_ID} is available!")
                print("\n[NEXT STEPS]")
                print("  1. Nova Sonic uses bidirectional streaming API")
                print("  2. We need to use invoke_model_with_bidirectional_stream()")
                print("  3. This is different from regular Strands SDK patterns")
                print("  4. May need custom integration with boto3")
                return True
            else:
                print(f"\n[WARNING] {MODEL_ID} not found in available models")
                print("[INFO] You may need to request access in Bedrock console")
                return False
                
        except Exception as e:
            print(f"[ERROR] Could not list models: {e}")
            print("[INFO] This might be a permissions issue")
            return False
            
    except ClientError as e:
        print(f"[ERROR] AWS Client Error: {e}")
        print("\n[TROUBLESHOOTING]")
        print("  1. Check AWS credentials: aws sts get-caller-identity")
        print("  2. Verify Bedrock access in IAM permissions")
        print("  3. Check if you're in the right region (us-east-1)")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n[START] Testing Nova 2 Sonic access via Bedrock...\n")
    
    try:
        success = test_model_access()
        
        if success:
            print("\n" + "=" * 60)
            print("[COMPLETE] Test passed - Nova 2 Sonic is accessible!")
            print("=" * 60 + "\n")
        else:
            print("\n" + "=" * 60)
            print("[INCOMPLETE] Test completed with warnings")
            print("=" * 60 + "\n")
            
    except KeyboardInterrupt:
        print("\n\n[STOP] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

