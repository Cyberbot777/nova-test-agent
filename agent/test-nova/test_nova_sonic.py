"""
Minimal Nova 2 Sonic Test Script using Strands SDK

This script tests basic connectivity to Nova 2 Sonic using the
experimental bidirectional streaming support in Strands SDK.

Usage:
    python test_nova_sonic.py

Requirements:
    - AWS credentials configured
    - Nova 2 Sonic access in us-east-1
    - strands-amazon-nova package installed
"""
import asyncio
import sys

# Strands SDK experimental bidirectional streaming
try:
    from strands.experimental.bidi.models.novasonic import BidiNovaSonicModel
    from strands.experimental.bidi.io.audio import BidiAudioIO
    from strands.experimental.bidi.io.text import BidiTextIO
    from strands.experimental.bidi.agent import BidiAgent
except ImportError as e:
    print("[ERROR] Error importing Strands Nova Sonic modules")
    print(f"   {e}")
    print("\n[INFO] Install required packages:")
    print("   pip install strands-agents strands-amazon-nova")
    sys.exit(1)

# Configuration
REGION = "us-east-1"
MODEL_ID = "amazon.nova-2-sonic-v1:0"

# Simple system prompt for voice
SYSTEM_PROMPT = """You are a helpful voice assistant. 
Keep responses brief and conversational, as if speaking to someone."""


async def test_basic_connection():
    """Test basic connection to Nova 2 Sonic."""
    print("\n" + "=" * 60)
    print("Nova 2 Sonic Connection Test")
    print("=" * 60)
    print(f"Model: {MODEL_ID}")
    print(f"Region: {REGION}")
    print("=" * 60 + "\n")
    
    try:
        # Step 1: Initialize the model
        print("[1/3] Initializing BidiNovaSonicModel...")
        model = BidiNovaSonicModel(
            region=REGION,
            model_id=MODEL_ID,
            system_prompt=SYSTEM_PROMPT
        )
        print("[OK] Model initialized successfully\n")
        
        # Step 2: Set up audio and text I/O
        print("[2/3] Setting up Audio I/O...")
        audio_io = BidiAudioIO(audio_config={})
        print("[OK] Audio I/O configured\n")
        
        print("[2/3] Setting up Text I/O...")
        text_io = BidiTextIO()
        print("[OK] Text I/O configured\n")
        
        # Step 3: Create the bidirectional agent
        print("[3/3] Creating BidiAgent...")
        async with BidiAgent(model=model) as agent:
            print("[OK] Agent created successfully\n")
            
            print("[SUCCESS] Nova 2 Sonic is accessible and ready!")
            print("\n[NEXT STEPS]")
            print("   1. Test with actual audio input")
            print("   2. Integrate with backend WebSocket")
            print("   3. Connect frontend audio capture")
            print("   4. Test full voice conversation\n")
            
            # Note: Actual audio streaming would happen here
            # For now, we're just validating the connection
            
    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("\n[INFO] Make sure you have installed:")
        print("   pip install strands-amazon-nova")
    except Exception as e:
        print(f"[ERROR] {e}")
        print(f"\n[INFO] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("\n[TROUBLESHOOTING]")
        print("   1. Check AWS credentials: aws sts get-caller-identity")
        print("   2. Verify Nova 2 Sonic access in Bedrock console")
        print("   3. Confirm region is us-east-1")
        print("   4. Check if model ID is correct")


async def test_with_mock_audio():
    """Test with a mock audio scenario (future implementation)."""
    print("\n[TODO] Mock audio test not yet implemented")
    print("   Will be added once basic connection is validated")


if __name__ == "__main__":
    print("\n[START] Starting Nova 2 Sonic Test...\n")
    
    try:
        asyncio.run(test_basic_connection())
    except KeyboardInterrupt:
        print("\n\n[STOP] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60 + "\n")

