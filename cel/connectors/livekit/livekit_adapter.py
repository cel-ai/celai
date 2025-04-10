"""
LiveKitAdapter masquerades as a livekit.LLM and communicates with Celai
through HTTP API calls with proper handling of stream formatting.
"""

from typing import Dict, Optional, Any
from loguru import logger as log

# If livekit-agents not installed raise ImportError
try:
    from livekit.agents import llm
    from livekit.agents.tts import SynthesizeStream
    from livekit.agents.types import APIConnectOptions, DEFAULT_API_CONNECT_OPTIONS
    from livekit.agents.utils import shortuuid
except ImportError:
    raise ImportError(
        "LiveKit agents library not installed. Please install it using 'pip install livekit-agents'."
    )

import httpx


class FlushSentinel(str, SynthesizeStream._FlushSentinel):
    """
    A sentinel object that indicates when to flush the stream.
    """
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)


class LiveKitStream(llm.LLMStream):
    """
    Stream implementation for LiveKit that handles communication with Celai API.
    """
    
    def __init__(
        self,
        llm: llm.LLM,
        chat_ctx: llm.ChatContext,
        session_id: str,
        api_url: str,
        timeout: float = 30.0,
        fnc_ctx: Optional[Dict] = None,
        conn_options: APIConnectOptions = None,
        **kwargs
    ):
        """
        Initialize the LiveKit stream.
        
        Args:
            llm: The LLM instance
            chat_ctx: The chat context from LiveKit
            session_id: The session ID for this conversation
            api_url: URL for the Celai API endpoint
            timeout: Timeout for HTTP requests in seconds
            fnc_ctx: The function context from LiveKit
            conn_options: Connection options from LiveKit
            **kwargs: Additional parameters to pass to the API
        """
        super().__init__(
            llm, chat_ctx=chat_ctx, fnc_ctx=fnc_ctx, conn_options=conn_options
        )
        self._session_id = session_id
        self._api_url = api_url
        self._timeout = timeout
        self._kwargs = kwargs
    
    def _to_message(self, msg: llm.ChatMessage) -> str:
        """
        Convert a LiveKit ChatMessage to text.
        
        Args:
            msg: The LiveKit chat message
            
        Returns:
            The extracted text from the message
        """
        if isinstance(msg.content, str):
            return msg.content
        elif isinstance(msg.content, list):
            text_parts = []
            for c in msg.content:
                if isinstance(c, str):
                    text_parts.append(c)
                elif isinstance(c, dict) and c.get("type") == "text":
                    text_parts.append(c.get("text", ""))
                elif hasattr(c, "text"):
                    text_parts.append(c.text)
            return " ".join(text_parts)
        return ""
    
    @staticmethod
    def _create_livekit_chunk(content: str, *, id: str | None = None) -> llm.ChatChunk | None:
        """
        Create a LiveKit chat chunk from content.
        
        Args:
            content: The content to include in the chunk
            id: Optional ID for the chunk
            
        Returns:
            A LiveKit chat chunk
        """
        return llm.ChatChunk(
            request_id=id or shortuuid(),
            choices=[
                llm.Choice(delta=llm.ChoiceDelta(role="assistant", content=content))
            ],
        )
    
    async def _to_livekit_chunk(self, content: str | Any) -> llm.ChatChunk | None:
        """
        Convert text content to a LiveKit chat chunk.
        
        Args:
            content: The content to convert
            
        Returns:
            A LiveKit chat chunk or None if the content is invalid
        """
        if not content:
            return None
        
        request_id = None
        if hasattr(content, 'id'):
            request_id = content.id
        
        if isinstance(content, str):
            return self._create_livekit_chunk(content, id=request_id)
        elif isinstance(content, dict) and "content" in content:
            return self._create_livekit_chunk(content["content"], id=content.get("id", request_id))
        
        return None
    
    async def _run(self):
        """Process the incoming message and stream the response"""
        try:
            # Find the most recent user message
            input_text = None
            for m in reversed(self.chat_ctx.messages):
                if m.role == "user":
                    input_text = self._to_message(m)
                    break
            
            if not input_text:
                log.warning("No user message found in chat context")
                return
            
            log.debug(f"Processing via API for session {self._session_id}")
            
            # Prepare the request payload
            payload = {
                "session_id": self._session_id,
                "user_text": input_text,
                **self._kwargs
            }
            
            # Make the request and stream the response
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    self._api_url,
                    json=payload,
                    timeout=self._timeout,
                ) as response:
                    # Check for successful response
                    if response.status_code != 200:
                        err_txt = await response.text()
                        raise RuntimeError(f"API error => status {response.status_code}: {err_txt}")

                    buffer = ""
                    
                    # Process the response line by line
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            content = line.removeprefix("data: ").strip()
                            
                            # Handle flush sentinel
                            if content == "<FLUSH>":
                                # First send the buffered content if any
                                if buffer:
                                    log.debug(f"Sending buffered content: {buffer}")
                                    chunk = await self._to_livekit_chunk(buffer)
                                    if chunk:
                                        self._event_ch.send_nowait(chunk)
                                    buffer = ""
                                
                                # Then send the flush sentinel
                                self._event_ch.send_nowait(
                                    self._create_livekit_chunk(FlushSentinel())
                                )
                            elif content:  # Skip empty content
                                # Accumulate content in buffer with proper spacing
                                if buffer:
                                    buffer += " " + content
                                else:
                                    buffer = content
                    
                    # Send any remaining buffered content
                    if buffer:
                        chunk = await self._to_livekit_chunk(buffer)
                        if chunk:
                            self._event_ch.send_nowait(chunk)
                    
                    # End of stream
                    self._event_ch.send_nowait(
                        self._create_livekit_chunk(FlushSentinel())
                    )
                
        except Exception as e:
            log.error(f"Error in LiveKitStream._run: {e}")
            error_message = f"Error processing your request: {str(e)}"
            if chunk := await self._to_livekit_chunk(error_message):
                self._event_ch.send_nowait(chunk)
            
            # Always send a flush sentinel on error to ensure the stream completes
            self._event_ch.send_nowait(
                self._create_livekit_chunk(FlushSentinel())
            )


class LiveKitAdapter(llm.LLM):
    """
    Adapter class that implements LiveKit's LLM interface
    and delegates to Celai API for actual processing.
    """
    
    def __init__(
        self, 
        api_url: str,
        timeout: float = 30.0,
        **kwargs
    ):
        """
        Initialize the adapter with parameters for API communication.
        
        Args:
            api_url: URL for the Celai API endpoint
            timeout: Timeout for HTTP requests in seconds
            **kwargs: Additional parameters to pass to the API
        """
        super().__init__()
        
        # Store configuration
        self._api_url = api_url
        self._timeout = timeout
        self._kwargs = kwargs
        
        log.info(f"Initialized LiveKitAdapter using API URL: {api_url}")
    
    def chat(
        self,
        chat_ctx: llm.ChatContext,
        fnc_ctx: llm.FunctionContext,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> llm.LLMStream:
        """
        Create a stream for LiveKit chat.
        
        This method is called by LiveKit to process a message and get a response.
        
        Args:
            chat_ctx: The chat context from LiveKit
            fnc_ctx: The function context from LiveKit
            conn_options: Connection options from LiveKit
            
        Returns:
            A LiveKit stream for handling the chat
        """
        # Extract a stable session ID from the chat context
        # Using the first message ID as a base to ensure consistency
        base_id = chat_ctx.messages[0].id if chat_ctx.messages else shortuuid()
        session_id = f"livekit:{base_id}"
        
        # Return a stream that will process the message
        return LiveKitStream(
            llm=self,
            chat_ctx=chat_ctx,
            session_id=session_id,
            api_url=self._api_url,
            timeout=self._timeout,
            fnc_ctx=fnc_ctx,
            conn_options=conn_options,
            **self._kwargs
        )