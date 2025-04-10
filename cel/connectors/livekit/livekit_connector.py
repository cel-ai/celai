from fastapi.responses import StreamingResponse
from loguru import logger as log
from fastapi import APIRouter, BackgroundTasks, Request
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.connectors.livekit.model.livekit_message import LiveKitMessage
from cel.gateway.message_gateway import StreamMode
from cel.gateway.model.stream_content_chunk import StreamContentChunk
from cel.gateway.model.outgoing import OutgoingMessage

class LiveKitConnector(BaseConnector):
    """
    LiveKit connector that provides a FastAPI router for handling chat completions.
    """
    
    endpoint = '/chat/completions'
    
    def __init__(self):
        log.debug("Creating LiveKit connector")
        self.prefix = '/livekit'
        self.router = APIRouter(prefix=self.prefix)
        self.paused = False
        self.gateway = None
        self.__create_routes(self.router)
    
    def __create_routes(self, router: APIRouter):
        @router.post(f"{LiveKitConnector.endpoint}")
        async def chat_completion(request: Request, background_tasks: BackgroundTasks):
            data = await request.json()
            log.debug(f"[LiveKit] Incoming JSON: {data}")
            return StreamingResponse(self.__process_stream(data), media_type='text/event-stream')

    async def __process_stream(self, payload: dict):
        try:
            log.debug(f"[LiveKit] Processing stream with payload: {payload}")

            msg = await LiveKitMessage.load_from_message(payload, connector=self)
            
            if self.gateway:
                # Use a buffer to accumulate chunks and handle spacing properly
                current_partial = ""
                
                async for chunk in self.gateway.process_message(msg, mode=StreamMode.DIRECT, capture_repsonse=True):
                    assert isinstance(chunk, StreamContentChunk), "stream chunk must be a StreamContentChunk object"
                    
                    # Send the content with proper formatting
                    if chunk.content:
                        yield f"data: {chunk.content}\n\n"
                    
                    # If this is the end of a partial chunk, add the flush sentinel
                    if not chunk.is_partial:
                        yield f"data: <FLUSH>\n\n"
            
            # End of stream
            yield f"data: \n\n"

        except Exception as e:
            log.error(f"Error processing LiveKit stream: {e}")
            yield f"data: Error: {str(e)}\n\n"

    async def send_typing_action(self, lead):
        # LiveKit doesn't support typing indicators
        log.debug("Typing indicators not supported in LiveKit")
        pass
    
    async def send_message(self, message: OutgoingMessage):
        # This method is not needed for the streaming interface
        log.debug("Direct message sending not used in LiveKit connector")
        pass
    
    def name(self) -> str:
        return "livekit"
    
    def get_router(self) -> APIRouter:
        return self.router
    
    def set_gateway(self, gateway):
        from cel.gateway.message_gateway import MessageGateway
        assert isinstance(gateway, MessageGateway), \
            "gateway must be an instance of MessageGateway"
        self.gateway = gateway

    def startup(self, context: MessageGatewayContext):
        # Verify if the webhook_url is set and is HTTPS
        if not context.webhook_url:
            log.warning("webhook_url is not set in the context - make sure your endpoint is accessible")
            return
            
        if not context.webhook_url.startswith("https"):
            log.warning(f"webhook_url should be HTTPS for production, got: {context.webhook_url}")
        
        webhook_url = f"{context.webhook_url}{self.prefix}{LiveKitConnector.endpoint}"
        log.info(f"Starting LiveKit connector with endpoint: {webhook_url}")
        log.info("Use this URL in the LiveKit Assistant settings under Model → Custom LLM URL")

    def shutdown(self, context: MessageGatewayContext):
        log.debug("Shutting down LiveKit connector")
    
    def pause(self):
        log.debug("Pausing LiveKit connector")
        self.paused = True

    def resume(self):
        log.debug("Resuming LiveKit connector")
        self.paused = False