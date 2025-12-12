"""
S2S Session Manager for Amazon Nova Sonic bidirectional streaming.
"""

import asyncio
import json
import warnings
import time
import logging

from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient, InvokeModelWithBidirectionalStreamOperationInput
from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart
from aws_sdk_bedrock_runtime.config import Config, HTTPAuthSchemeResolver, SigV4AuthScheme
from smithy_aws_core.identity.environment import EnvironmentCredentialsResolver
from smithy_core.shapes import ShapeID

from .s2s_events import S2sEvent

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("S2sSessionManager")


class S2sSessionManager:
    """S2S Session Manager for Nova Sonic bidirectional streaming."""
    
    def __init__(self, model_id='amazon.nova-sonic-v1:0', region='us-east-1'):
        """Initialize the stream manager."""
        self.model_id = model_id
        self.region = region
        
        # Audio and output queues
        self.audio_input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()
        
        self.response_task = None
        self.stream = None
        self.is_active = False
        self.bedrock_client = None
        
        # Session information
        self.prompt_name = None
        self.content_name = None
        self.audio_content_name = None

    def _initialize_client(self):
        """Initialize the Bedrock client."""
        config = Config(
            endpoint_uri=f"https://bedrock-runtime.{self.region}.amazonaws.com",
            region=self.region,
            aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
            auth_scheme_resolver=HTTPAuthSchemeResolver(),
            auth_schemes={ShapeID("aws.auth#sigv4"): SigV4AuthScheme(service="bedrock")}
        )
        self.bedrock_client = BedrockRuntimeClient(config=config)

    async def initialize_stream(self):
        """Initialize the bidirectional stream with Bedrock."""
        try:
            if not self.bedrock_client:
                self._initialize_client()
        except Exception as ex:
            self.is_active = False
            logger.error(f"Failed to initialize Bedrock client: {str(ex)}")
            raise

        try:
            logger.info(f"Connecting to Nova Sonic model: {self.model_id}")
            self.stream = await self.bedrock_client.invoke_model_with_bidirectional_stream(
                InvokeModelWithBidirectionalStreamOperationInput(model_id=self.model_id)
            )
            logger.info("Stream established successfully!")
            self.is_active = True
            
            # Start listening for responses
            self.response_task = asyncio.create_task(self._process_responses())

            # Start processing audio input
            asyncio.create_task(self._process_audio_input())
            
            # Wait a bit to ensure everything is set up
            await asyncio.sleep(0.1)
            
            logger.info("Stream initialized successfully")
            return self
        except Exception as e:
            self.is_active = False
            logger.error(f"Failed to initialize stream: {str(e)}")
            raise
    
    async def send_raw_event(self, event_data):
        """Send a raw event to the Bedrock stream."""
        try:
            if not self.stream or not self.is_active:
                logger.warning("Stream not initialized or closed")
                return
            
            event_json = json.dumps(event_data)
            event = InvokeModelWithBidirectionalStreamInputChunk(
                value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
            )
            await self.stream.input_stream.send(event)

            # Close session
            if "sessionEnd" in event_data.get("event", {}):
                self.close()
            
        except Exception as e:
            logger.error(f"Error sending event: {str(e)}")
    
    async def _process_audio_input(self):
        """Process audio input from the queue and send to Bedrock."""
        while self.is_active:
            try:
                # Get audio data from the queue
                data = await self.audio_input_queue.get()
                
                # Extract data from the queue item
                prompt_name = data.get('prompt_name')
                content_name = data.get('content_name')
                audio_bytes = data.get('audio_bytes')
                
                if not audio_bytes or not prompt_name or not content_name:
                    logger.warning("Missing required audio data properties")
                    continue

                # Create the audio input event
                audio_event = S2sEvent.audio_input(
                    prompt_name, 
                    content_name, 
                    audio_bytes.decode('utf-8') if isinstance(audio_bytes, bytes) else audio_bytes
                )
                
                # Send the event
                await self.send_raw_event(audio_event)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
    
    def add_audio_chunk(self, prompt_name, content_name, audio_data):
        """Add an audio chunk to the queue."""
        self.audio_input_queue.put_nowait({
            'prompt_name': prompt_name,
            'content_name': content_name,
            'audio_bytes': audio_data
        })
    
    async def _process_responses(self):
        """Process incoming responses from Bedrock."""
        logger.info("Starting response processor...")
        while self.is_active:
            try:
                output = await self.stream.await_output()
                result = await output[1].receive()
                
                if result.value and result.value.bytes_:
                    response_data = result.value.bytes_.decode('utf-8')
                    
                    json_data = json.loads(response_data)
                    json_data["timestamp"] = int(time.time() * 1000)
                    
                    # Put the response in the output queue for forwarding
                    await self.output_queue.put(json_data)

            except json.JSONDecodeError as ex:
                logger.error(f"JSON decode error: {ex}")
            except StopAsyncIteration:
                logger.info("Stream ended")
                break
            except Exception as e:
                if "ValidationException" in str(e):
                    logger.error(f"Validation error: {e}")
                else:
                    logger.error(f"Error receiving response: {e}")
                break

        self.is_active = False
        self.close()
    
    def close(self):
        """Close the stream properly."""
        if not self.is_active:
            return
            
        self.is_active = False
        
        if self.stream:
            asyncio.create_task(self.stream.input_stream.close())
        
        if self.response_task and not self.response_task.done():
            self.response_task.cancel()
        
        logger.info("Session manager closed")

