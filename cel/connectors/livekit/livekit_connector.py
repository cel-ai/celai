from fastapi.responses import StreamingResponse
from loguru import logger as log
from fastapi import APIRouter, BackgroundTasks, Request
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.connectors.livekit.model.livekit_message import LiveKitMessage
from cel.gateway.message_gateway import StreamMode
from cel.assistants.stream_content_chunk import StreamContentChunk
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
        self.__create_routes(self.router)
    
    def __create_routes(self, router: APIRouter):

        @router.post(f"{LiveKitConnector.endpoint}")
        async def chat_completion(request: Request, background_tasks: BackgroundTasks):
            data = await request.json()
            log.debug(f"[LiveKit] Incoming JSON: {data}")
            return StreamingResponse(self.__process_stream(data), media_type='text/event-stream')

    async def __process_stream(self, payload: dict):
        try:
            log.debug(f"Received LiveKit text for Stream Processing: {payload}")

            msg = await LiveKitMessage.load_from_message(payload, connector=self)

            if self.gateway:
                async for chunk in self.gateway.process_message(msg, mode=StreamMode.DIRECT, capture_repsonse=True):
                    assert isinstance(chunk, StreamContentChunk), "stream chunk must be a StreamContentChunk object"
                    yield f"data: {chunk.content}\n\n"
                
            # end of stream
            yield f"data: \n\n"

        except Exception as e:
            log.error(f"Error processing LiveKit stream: {e}")
            yield f"data: Error: {str(e)}\n\n"

    async def send_typing_action(self, lead):
        log.warning("send_typing_action must be implemented in LiveKit connector")
    
    async def send_message(self, message: OutgoingMessage):
        log.warning("send_message must be implemented in LiveKit connector")
    
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
        # verify if the webhook_url is set and is HTTPS
        assert context.webhook_url, "webhook_url must be set in the context"
        assert context.webhook_url.startswith("https"),\
            f"webhook_url must be HTTPS, got: {context.webhook_url}.\
            Be sure that your url is public and has a valid SSL certificate."
        
        webhook_url = f"{context.webhook_url}{self.prefix}{LiveKitConnector.endpoint}"
        log.debug(f"Starting LiveKit connector with url: {webhook_url}")
        log.debug("Be sure to setup this url in the LiveKit Assistant, \
            go to Assistant Settings -> Model and select Custom LLM.\
            Then set the url in the Custom LLM URL field")

    def shutdown(self, context: MessageGatewayContext):
        log.debug("Shutting down LiveKit connector")
    
    def pause(self):
        log.debug("Pausing LiveKit connector")
        self.paused = True

    def resume(self):
        log.debug("Resuming LiveKit connector")
        self.paused = False