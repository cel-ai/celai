"""
LiveKitAdapter masquerades as a livekit.LLM and communicates with Celai
through HTTP API calls with proper handling of stream formatting.
"""

from typing import Optional, Any, List
from loguru import logger as log

# If livekit-agents not installed raise ImportError
try:
    from livekit.agents import llm
    from livekit.agents import llm, FunctionTool  
    from livekit.agents.tts import SynthesizeStream
    from livekit.agents.types import APIConnectOptions, DEFAULT_API_CONNECT_OPTIONS
    from livekit.agents.utils import shortuuid
except ImportError:
    raise ImportError(
        "LiveKit agents library not installed. Please install it using 'pip install livekit-agents'."
    )

try:
    import httpx
except ImportError:
    raise ImportError(
        "httpx library not installed. Please install it using 'pip install httpx'."
    )


class FlushSentinel(str, SynthesizeStream._FlushSentinel):
    """
    A sentinel object that indicates when to flush the stream.
    """
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)


class LiveKitStream(llm.LLMStream):
    def __init__(
        self,
        llm: llm.LLM,
        *,
        chat_ctx: llm.ChatContext,
        session_id: str,
        api_url: str,
        timeout: float = 30.0,
        tools: Optional[List[FunctionTool]] = None,
        conn_options: APIConnectOptions | None = None,
        **kwargs,
    ):
        super().__init__(llm, chat_ctx=chat_ctx, tools=tools, conn_options=conn_options)
        self._session_id = session_id
        self._api_url = api_url
        self._timeout = timeout
        self._kwargs = kwargs

    @staticmethod
    def _create_livekit_chunk(
        content: str,
        *,
        id: str | None = None,
    ) -> llm.ChatChunk:
        """Generates a ChatChunk with the new schema (id + delta)."""
        return llm.ChatChunk(
            id=id or shortuuid(),
            delta=llm.ChoiceDelta(role="assistant", content=content),
        )
    
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
    
    async def _to_livekit_chunk(self, content: str | Any) -> llm.ChatChunk | None:
        if not content:
            return None
        chunk_id = getattr(content, "id", None)
        if isinstance(content, str):
            return self._create_livekit_chunk(content, id=chunk_id)
        if isinstance(content, dict) and "content" in content:
            return self._create_livekit_chunk(content["content"], id=content.get("id", chunk_id))
        return None
    
    async def _run(self):
        """Process the incoming message and stream the response"""
        try:
            # Find the most recent user message
            input_text = None
            for m in reversed(self.chat_ctx.items):
                if m.role == "user":
                    print(f"User message found: {m}")
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

                    
                    # Process the response line by line
                    async for raw in response.aiter_lines():
                        if not raw.startswith("data: "):
                            continue

                        content = raw.removeprefix("data: ").strip("\r\n")

                        if not content:
                            continue

                        # -- flush sentinel —
                        if content == "<FLUSH>":
                            self._event_ch.send_nowait(
                                self._create_livekit_chunk(FlushSentinel())
                            )
                            continue

                        # -- token normal: lo enviamos tal cual, sin tocar espacios —
                        self._event_ch.send_nowait(
                            self._create_livekit_chunk(content)
                        )
                    
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
        *,
        chat_ctx: llm.ChatContext,
        tools: list[FunctionTool] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        **kwargs: Any,
        
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
        base_id = chat_ctx.items[0].id if chat_ctx.items else shortuuid()
        session_id = f"livekit:{base_id}"
        return LiveKitStream(
            llm=self,
            chat_ctx=chat_ctx,
            session_id=session_id,
            api_url=self._api_url,
            timeout=self._timeout,
            tools=tools,
            conn_options=conn_options,
            **self._kwargs,
        )