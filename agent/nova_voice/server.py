"""
WebSocket server for Nova Sonic voice streaming.
"""

import asyncio
import websockets
import json
import logging
import warnings

from .s2s_session_manager import S2sSessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NovaVoiceServer")

# Suppress warnings
warnings.filterwarnings("ignore")


async def websocket_handler(websocket, model_id, region):
    """Handle WebSocket connections."""
    stream_manager = None
    forward_task = None
    
    logger.info(f"New WebSocket connection")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if 'body' in data:
                    data = json.loads(data["body"])
                
                if 'event' in data:
                    event_type = list(data['event'].keys())[0]
                    
                    # Initialize stream manager only once per WebSocket connection
                    if stream_manager is None:
                        logger.info("Initializing Nova Sonic stream manager")
                        stream_manager = S2sSessionManager(
                            model_id=model_id,
                            region=region
                        )
                        
                        # Initialize the Bedrock stream
                        await stream_manager.initialize_stream()
                        
                        # Start a task to forward responses from Bedrock to the WebSocket
                        forward_task = asyncio.create_task(
                            forward_responses(websocket, stream_manager)
                        )
                    
                    # Store prompt name and content names if provided
                    if event_type == 'promptStart':
                        stream_manager.prompt_name = data['event']['promptStart']['promptName']
                    elif event_type == 'contentStart' and data['event']['contentStart'].get('type') == 'AUDIO':
                        stream_manager.audio_content_name = data['event']['contentStart']['contentName']
                    
                    # Handle audio input separately
                    if event_type == 'audioInput':
                        prompt_name = data['event']['audioInput']['promptName']
                        content_name = data['event']['audioInput']['contentName']
                        audio_base64 = data['event']['audioInput']['content']
                        stream_manager.add_audio_chunk(prompt_name, content_name, audio_base64)
                    else:
                        # Send other events directly to Bedrock
                        await stream_manager.send_raw_event(data)
                        
            except json.JSONDecodeError:
                logger.error("Invalid JSON received from WebSocket")
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                    
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket handler error: {e}")
    finally:
        logger.info("Cleaning up WebSocket connection")
        if stream_manager:
            stream_manager.close()
        if forward_task and not forward_task.done():
            forward_task.cancel()
        logger.info("WebSocket connection cleanup complete")


async def forward_responses(websocket, stream_manager):
    """Forward responses from Bedrock to the WebSocket."""
    try:
        while stream_manager.is_active:
            response = await stream_manager.output_queue.get()
            
            try:
                event = json.dumps(response)
                await websocket.send(event)
            except websockets.exceptions.ConnectionClosed:
                logger.info("WebSocket connection closed during response forwarding")
                break
            except Exception as send_error:
                logger.error(f"Error sending response to WebSocket: {send_error}")
                break
                
    except asyncio.CancelledError:
        logger.info("Response forwarding task cancelled")
    except Exception as e:
        logger.error(f"Error forwarding responses: {e}")
    finally:
        logger.info("Response forwarding stopped")


async def run_server(host="localhost", port=8080, model_id="amazon.nova-sonic-v1:0", region="us-east-1"):
    """Run the WebSocket server."""
    logger.info("=" * 60)
    logger.info("Nova Voice Agent - WebSocket Server")
    logger.info("=" * 60)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Model: {model_id}")
    logger.info(f"Region: {region}")
    logger.info("=" * 60)
    
    try:
        async with websockets.serve(
            lambda ws: websocket_handler(ws, model_id, region),
            host,
            port
        ):
            logger.info(f"WebSocket server started at ws://{host}:{port}")
            logger.info("Waiting for connections...")
            
            # Keep the server running forever
            await asyncio.Future()
    except Exception as e:
        logger.error(f"Failed to start WebSocket server: {e}")
        raise


if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Nova Voice WebSocket Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--model", default="amazon.nova-sonic-v1:0", help="Nova Sonic model ID")
    parser.add_argument("--region", default=os.getenv("AWS_DEFAULT_REGION", "us-east-1"), help="AWS region")
    
    args = parser.parse_args()
    
    asyncio.run(run_server(
        host=args.host,
        port=args.port,
        model_id=args.model,
        region=args.region
    ))

