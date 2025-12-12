"""
Event definitions for Amazon Nova Sonic integration.
Based on the s2s_events.py from Amazon Nova samples.
"""

import json


class S2sEvent:
    """
    Utility class for creating events for Amazon Nova Sonic.
    """

    # Default configuration values
    DEFAULT_INFER_CONFIG = {
        "maxTokens": 1024,
        "topP": 1.0,
        "temperature": 1.0,
        "topK": 1,
    }

    DEFAULT_SYSTEM_PROMPT = """You are a helpful voice assistant named Nova.

Keep your responses:
- Natural and conversational (like you're speaking)
- Concise (people don't want to listen to long monologues)
- Friendly and engaging
- Clear and easy to understand when spoken aloud

Since this is a voice conversation, avoid:
- Long lists or bullet points
- Complex formatting
- Overly technical jargon
- Very long explanations

If you need to share detailed information, break it into digestible chunks."""

    DEFAULT_AUDIO_INPUT_CONFIG = {
        "mediaType": "audio/lpcm",
        "sampleRateHertz": 16000,
        "sampleSizeBits": 16,
        "channelCount": 1,
        "audioType": "SPEECH",
        "encoding": "base64",
    }

    DEFAULT_AUDIO_OUTPUT_CONFIG = {
        "mediaType": "audio/lpcm",
        "sampleRateHertz": 24000,
        "sampleSizeBits": 16,
        "channelCount": 1,
        "voiceId": "matthew",
        "encoding": "base64",
        "audioType": "SPEECH",
    }

    @staticmethod
    def session_start(inference_config=None):
        """Create a session start event."""
        if inference_config is None:
            inference_config = S2sEvent.DEFAULT_INFER_CONFIG
        return {
            "event": {
                "sessionStart": {
                    "inferenceConfiguration": inference_config,
                    "turnDetectionConfiguration": {
                        "type": "SEMANTIC",
                        "prefillPoisedSilenceThresholdInMsec": 500,
                        "endSilenceThresholdInMsec": 1000
                    }
                }
            }
        }

    @staticmethod
    def prompt_start(prompt_name, audio_output_config=None, tool_config=None):
        """Create a prompt start event."""
        if audio_output_config is None:
            audio_output_config = S2sEvent.DEFAULT_AUDIO_OUTPUT_CONFIG
        
        event = {
            "event": {
                "promptStart": {
                    "promptName": prompt_name,
                    "textOutputConfiguration": {"mediaType": "text/plain"},
                    "audioOutputConfiguration": audio_output_config,
                }
            }
        }
        
        # Add tool configuration if provided
        if tool_config:
            event["event"]["promptStart"]["toolUseOutputConfiguration"] = {"mediaType": "application/json"}
            event["event"]["promptStart"]["toolConfiguration"] = tool_config
        
        return event

    @staticmethod
    def content_start_text(prompt_name, content_name):
        """Create a content start event for text."""
        return {
            "event": {
                "contentStart": {
                    "promptName": prompt_name,
                    "contentName": content_name,
                    "type": "TEXT",
                    "interactive": True,
                    "role": "SYSTEM",
                    "textInputConfiguration": {"mediaType": "text/plain"},
                }
            }
        }

    @staticmethod
    def text_input(prompt_name, content_name, system_prompt=None):
        """Create a text input event."""
        if system_prompt is None:
            system_prompt = S2sEvent.DEFAULT_SYSTEM_PROMPT
        return {
            "event": {
                "textInput": {
                    "promptName": prompt_name,
                    "contentName": content_name,
                    "content": system_prompt,
                }
            }
        }

    @staticmethod
    def content_end(prompt_name, content_name):
        """Create a content end event."""
        return {
            "event": {
                "contentEnd": {"promptName": prompt_name, "contentName": content_name}
            }
        }

    @staticmethod
    def content_start_audio(prompt_name, content_name, audio_input_config=None):
        """Create a content start event for audio."""
        if audio_input_config is None:
            audio_input_config = S2sEvent.DEFAULT_AUDIO_INPUT_CONFIG
        return {
            "event": {
                "contentStart": {
                    "promptName": prompt_name,
                    "contentName": content_name,
                    "type": "AUDIO",
                    "interactive": True,
                    "audioInputConfiguration": audio_input_config,
                }
            }
        }

    @staticmethod
    def audio_input(prompt_name, content_name, content):
        """Create an audio input event."""
        return {
            "event": {
                "audioInput": {
                    "promptName": prompt_name,
                    "contentName": content_name,
                    "content": content,
                }
            }
        }

    @staticmethod
    def content_start_tool(prompt_name, content_name, tool_use_id):
        """Create a content start event for a tool."""
        return {
            "event": {
                "contentStart": {
                    "promptName": prompt_name,
                    "contentName": content_name,
                    "interactive": True,
                    "type": "TOOL",
                    "role": "TOOL",
                    "toolResultInputConfiguration": {
                        "toolUseId": tool_use_id,
                        "type": "TEXT",
                        "textInputConfiguration": {"mediaType": "text/plain"},
                    },
                }
            }
        }

    @staticmethod
    def text_input_tool(prompt_name, content_name, content):
        """Create a text input event for a tool result."""
        return {
            "event": {
                "toolResult": {
                    "promptName": prompt_name,
                    "contentName": content_name,
                    "content": content,
                }
            }
        }

    @staticmethod
    def prompt_end(prompt_name):
        """Create a prompt end event."""
        return {"event": {"promptEnd": {"promptName": prompt_name}}}

    @staticmethod
    def session_end():
        """Create a session end event."""
        return {"event": {"sessionEnd": {}}}

