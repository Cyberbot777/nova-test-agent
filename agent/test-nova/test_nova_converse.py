"""
Nova 2 Sonic Test using Converse Stream API

Tests if we can use boto3's converse_stream API with Nova Sonic
as an alternative to the bidirectional API that's not yet available.

Usage:
    python test_nova_converse.py

This is our workaround until bidirectional streaming is in boto3.
"""
import boto3
import json

# Configuration  
REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"


def test_converse_stream_with_nova():
    """Test if converse_stream works with Nova Sonic."""
    print("\n" + "=" * 60)
    print("Nova 2 Sonic Converse Stream Test")
    print("=" * 60)
    print(f"Model: {MODEL_ID}")
    print(f"Region: {REGION}")
    print(f"API: converse_stream (boto3)")
    print("=" * 60 + "\n")
    
    try:
        # Step 1: Create client
        print("[1/3] Creating Bedrock Runtime client...")
        client = boto3.client('bedrock-runtime', region_name=REGION)
        print("[OK] Client created\n")
        
        # Step 2: Prepare message
        print("[2/3] Preparing message...")
        message = {
            "role": "user",
            "content": [
                {"text": "Hello Nova! Please say hello back to me in a friendly voice."}
            ]
        }
        
        messages = [message]
        print(f"[OK] Message: \"{message['content'][0]['text']}\"\n")
        
        # Step 3: Call converse_stream
        print("[3/3] Calling converse_stream...")
        response = client.converse_stream(
            modelId=MODEL_ID,
            messages=messages,
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.7,
                "topP": 0.9
            }
        )
        
        print("[OK] Stream started\n")
        print("[RECEIVING] Streaming response...\n")
        
        # Process stream
        full_text = ""
        event_count = 0
        
        for event in response['stream']:
            event_count += 1
            
            # Text content
            if 'contentBlockDelta' in event:
                delta = event['contentBlockDelta'].get('delta', {})
                if 'text' in delta:
                    text = delta['text']
                    full_text += text
                    print(f"  [TEXT] {text}", end='', flush=True)
            
            # Metadata
            elif 'messageStart' in event:
                print(f"  [START] Message started")
                role = event['messageStart'].get('role', 'unknown')
                print(f"  [ROLE] {role}")
            
            elif 'messageStop' in event:
                print(f"\n  [STOP] Message complete")
                stop_reason = event['messageStop'].get('stopReason', 'unknown')
                print(f"  [REASON] {stop_reason}")
            
            elif 'metadata' in event:
                metadata = event['metadata']
                usage = metadata.get('usage', {})
                if usage:
                    print(f"\n  [USAGE] Input: {usage.get('inputTokens', 0)}, Output: {usage.get('outputTokens', 0)}")
        
        print(f"\n[OK] Received {event_count} events\n")
        
        # Summary
        print("\n" + "=" * 60)
        if full_text:
            print("[SUCCESS] Nova Sonic responded via converse_stream!")
            print("=" * 60)
            print(f"\nFull response:")
            print(f'  "{full_text}"')
            print("\n[ANALYSIS]")
            print("  ✅ converse_stream WORKS with Nova Sonic")
            print("  ✅ We got text response")
            print("  ⚠️  No audio in response (text-only mode)")
            print("\n[NEXT STEPS]")
            print("  1. Research if converse_stream supports audio output")
            print("  2. Check for audio configuration parameters")
            print("  3. Or wait for bidirectional API in boto3")
            print("  4. Build POC with text-to-speech fallback (Polly)")
            return True
        else:
            print("[WARNING] No text received")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print(f"[INFO] Error type: {type(e).__name__}")
        
        # Check if it's a model not supported error
        error_str = str(e)
        if "model" in error_str.lower() and "not support" in error_str.lower():
            print("\n[FINDING] Nova Sonic may not support converse_stream")
            print("[INFO] This means we need the bidirectional API")
            print("[ACTION] Must wait for boto3 update OR use preview SDK")
        else:
            import traceback
            traceback.print_exc()
        
        return False


if __name__ == "__main__":
    print("\n[START] Testing converse_stream with Nova Sonic...\n")
    
    try:
        success = test_converse_stream_with_nova()
        
        if success:
            print("\n" + "=" * 60)
            print("[COMPLETE] Test revealed path forward!")
            print("=" * 60 + "\n")
        else:
            print("\n" + "=" * 60)
            print("[COMPLETE] Test showed limitations - need different approach")
            print("=" * 60 + "\n")
            
    except KeyboardInterrupt:
        print("\n\n[STOP] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()

