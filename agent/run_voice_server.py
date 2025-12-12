#!/usr/bin/env python3
"""
Nova Voice Agent - Main Entry Point

This runs the Nova Sonic bidirectional streaming voice server.

Usage:
    python run_voice_server.py --port 8080

Requirements:
    - AWS credentials set as environment variables:
        export AWS_ACCESS_KEY_ID=your_key
        export AWS_SECRET_ACCESS_KEY=your_secret
        export AWS_DEFAULT_REGION=us-east-1
"""

import asyncio
import argparse
import os
import sys
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nova_voice.server import run_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("NovaVoiceAgent")


def check_credentials():
    """Check if AWS credentials are set."""
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('AWS_DEFAULT_REGION', os.environ.get('AWS_REGION', 'us-east-1'))
    
    if not access_key or not secret_key:
        logger.error("AWS credentials not found!")
        logger.error("Please set environment variables:")
        logger.error("  export AWS_ACCESS_KEY_ID=your_key")
        logger.error("  export AWS_SECRET_ACCESS_KEY=your_secret")
        logger.error("  export AWS_DEFAULT_REGION=us-east-1")
        return False
    
    logger.info(f"AWS credentials found: {access_key[:8]}...")
    logger.info(f"AWS region: {region}")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Nova Voice Agent - WebSocket Server")
    parser.add_argument(
        "--host",
        default="localhost",
        help="WebSocket server host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="WebSocket server port (default: 8080)"
    )
    parser.add_argument(
        "--model",
        default="amazon.nova-sonic-v1:0",
        help="Nova Sonic model ID (default: amazon.nova-sonic-v1:0)"
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        help="AWS region (default: us-east-1)"
    )

    args = parser.parse_args()

    # Check credentials
    if not check_credentials():
        sys.exit(1)

    logger.info("")
    logger.info("=" * 60)
    logger.info("Nova Voice Agent")
    logger.info("=" * 60)
    logger.info(f"Model: {args.model}")
    logger.info(f"Region: {args.region}")
    logger.info(f"Server: ws://{args.host}:{args.port}")
    logger.info("")
    logger.info("Connect your frontend to this WebSocket endpoint")
    logger.info("=" * 60)
    logger.info("")

    try:
        asyncio.run(
            run_server(
                host=args.host,
                port=args.port,
                model_id=args.model,
                region=args.region
            )
        )
    except KeyboardInterrupt:
        logger.info("Voice agent stopped by user")
    except Exception as e:
        logger.error(f"Voice agent failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

