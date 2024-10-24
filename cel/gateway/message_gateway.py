import asyncio
from typing import Callable
from langsmith import tracing_context
from loguru import logger as log
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response
from loguru import logger as log

from cel.assistants.common import EventResponse
from cel.assistants.stream_content_chunk import StreamContentChunk
from cel.comms.sentense_detection import streaming_sentence_detector_async
from cel.gateway.model.base_connector import BaseConnector
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.message import ConversationLead, Message 
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.gateway.model.outgoing import OutgoingMessage, OutgoingTextMessage
from cel.message_enhancers.default_message_enhancer import DefaultMessageEnhancer


DEFAULT_CHARS_SLEEP_TIME_RATIO = 25

class StreamMode:
    """
    StreamMode is a class that defines different modes for streaming messages.

    Attributes:
        DIRECT (str): The response is sent as soon as it is ready.
        WORD (str): TODO: not implemented yet.
        SENTENCE (str): pySBD based streaming sentence detector available.
        FULL (str): The whole response is sent at once.
    """
    # the response is sent as soon as it is ready
    DIRECT = "direct"
    # TODO: not implemented yet
    WORD = "word"
    
    # pySBD based streaming sentence detector available
    SENTENCE = "sentence"
    
    # the whole response is sent at once
    FULL = "full"


class MessageGateway:
    """ A message gateway for handling messages from different sources. This class is a singleton.
    MessageGateway is a FastAPI application that can be run as a standalone server. It can be used to
    handle messages from different sources and send them to an assistant for processing.
    
    Since the gateway is a FastAPI application, it can be extended with additional routes and middlewares.
    We strongly recommend using async functions for the middlewares and the routes in connectors.
    Avoid using blocking code in all components of the gateway and the connectors.
    

    Args:
        - webhook_url (str): The webhook url for the gateway. This is the url that the 
        connectors will use to send messages to the gateway. It should be a public url with ssl.
        If you are running the gateway locally, you can use ngrok to create a public url for your local server.
        This is required for connectors that need to receive messages from external sources in a webhook.
        No need to set this if you are using the gateway in a local environment.
        
        - host (str, optional): The host for the gateway. Defaults to '127.0.0.1'.
        
        - port (int, optional): The port for the gateway. Defaults to 8000.
        
        - assistant (BaseAssistant, optional): The assistant to use for processing messages. 
        Defaults to None.
        
        - delivery_rate_control (bool, optional): If True, the gateway will control the delivery rate
        of messages based on the length of the message. Defaults to True. Only available in StreamMode.SENTENCE
        this is useful to prevent the assistant from sending messages too fast to the user. A delay is added
        between messages based on the length of the message.
        
        - delivery_rate_control_ratio (int, optional): The ratio of characters to sleep time. Defaults to 25.
        
        - middlewares (list[Callable[[Message, BaseConnector], bool]], optional): A list of middlewares to
        process messages before they are sent to the assistant. Defaults to None.
        
        - message_enhancer (Callable[[ConversationLead, str, bool], OutgoingMessage], optional): A function
        that enhances the outgoing message before it is sent to the connector. Defaults to None.
        
        - gateway_api_key (str, optional): An API key for securing the gateway. If set, the gateway will
        require the API key to be sent in the header of the request. Defaults to None.
        
        - gateway_api_key_header (str, optional): The header key for the API key. Defaults to "x-api-key".
        
        - auto_voice_response (bool, optional): If True, the gateway will automatically send voice messages in 
        response to text messages from users. Defaults to False.
        
    """
    
    #singleton
    _instance = None
    
    @staticmethod
    def instance():
        if MessageGateway._instance is None:
            raise Exception("MessageGateway not initialized")
        return MessageGateway._instance
    
    def __init__(self, 
                 assistant: BaseAssistant = None,
                 host: str = '127.0.0.1', 
                 port: int = 8000,
                 webhook_url: str = None,
                 delivery_rate_control: bool = False,
                 delivery_rate_control_ratio: int = DEFAULT_CHARS_SLEEP_TIME_RATIO,
                 middlewares: list[Callable[[Message, BaseConnector], bool]] = None,
                 message_enhancer: Callable[[ConversationLead, str, bool], OutgoingMessage] = None,
                 gateway_api_key: str = None,
                 gateway_api_key_header: str = "x-api-key",
                 auto_voice_response: bool = False
                ):
        self.webhook_url = webhook_url or f"http://{host}:{port}"
        self.host = host
        self.port = port
        self.connectors : list[BaseConnector] = []
        self.secured_paths = ["/gateway", "/middlewares"]
        
        self.app = FastAPI(
            title="Message Gateway",
            description="A message gateway for handling messages from different sources",
            on_startup=[self.__startup],
            on_shutdown=[self.__shutdown]
        )
        
        if gateway_api_key is not None:
            def path_is_secure(path: str):
                for p in self.secured_paths:
                    if path.startswith(p):
                        return True
                return False
            
            
            @self.app.middleware("http")
            async def secure_middleware(request: Request, call_next):
                
                if path_is_secure(request.url.path):             
                    if gateway_api_key_header not in request.headers:
                        response = await call_next(request)
                        response.status_code = 401
                        log.error(f"API key not found in headers: {request.url}")
                        log.error(f"Headers: {request.headers}")
                        log.warning(f"Add your API Key into header: {gateway_api_key_header}")
                        return response
                    
                    key = request.headers[gateway_api_key_header]
                    if key != gateway_api_key:
                        response = await call_next(request)
                        response.status_code = 401
                        log.error(f"Invalid API key: {request.url} invalid key: {key}")
                        return response
                
                response = await call_next(request)
                return response
            
        health_router = APIRouter(prefix="/health", tags=["health"])
        
        @health_router.get("/")
        async def health():
            return {"status": "ok"}
        
        
        
        self.app.include_router(health_router)
        self.app.include_router(self.base_routes())
        self.assistant: BaseAssistant = assistant
        self.delivery_rate_control = delivery_rate_control
        self.delivery_rate_control_ratio = delivery_rate_control_ratio
        self.middlewares = middlewares or []
        self.message_enhancer = message_enhancer or DefaultMessageEnhancer()
        self.auto_voice_response = auto_voice_response
        
    def register_middleware(self, 
                            middleware: Callable[[Message, BaseConnector, BaseAssistant], bool]):
        self.middlewares.append(middleware)
        log.debug(f"Middleware {middleware.__class__.__name__} registered")
        # if middleware has a setup method, call it, passing self.app as the argument
        # only if the setup method has one argument
        if hasattr(middleware, "setup"):
            try:
                # get middleware class name
                name = middleware.__class__.__name__
                # create a router with prefix: middlewares
                router = APIRouter(prefix=f"/middlewares/{name}", tags=["middlewares"])
                middleware.setup(router)
                # register the router with the app
                self.app.include_router(router)
            except Exception as e:
                log.error(f"Error setting up middleware: {e}")
        
        
        
    def base_routes(self):
       
        router = APIRouter(prefix="/gateway", 
                           tags=["gateway"])
                
        @router.get("/pause")
        async def get_pause():
            for connector in self.connectors:
                connector.pause()
            return {"message": "paused"}
        
        @router.get("/resume")
        async def get_resume():
            for connector in self.connectors:
                connector.resume()
            return {"message": "resumed"}
        
        return router
        
    def __startup(self):
        log.debug("Starting message gateway")
        for connector in self.connectors:
            connector.startup(self.get_context())
    
    def __shutdown(self):
        log.debug("Shutting down message gateway")
        for connector in self.connectors:
            connector.shutdown(self.get_context())

    def get_context(self):
        return MessageGatewayContext(router=APIRouter(), webhook_url=self.webhook_url)
    
    
    async def __process_middlewares(self, message: Message):
        try:
            for middleware in self.middlewares:
                res = await middleware(message, message.lead.connector, self.assistant)
                # Break the chain if any middleware returns False
                if not res:
                    log.error(f"Middleware {type(middleware)} rejected message: {message.text}")
                    return False
            return True
        except Exception as e:
            log.error(f"Error processing middlewares: {e}")
            return False
        
    async def __process_events(self, message: Message):
        try:
            connector = message.lead.connector
            res = await self.assistant.call_event("message", message.lead, message)
            assert res is None or isinstance(res, EventResponse)
            
            if res is None:
                log.debug(f"Event: 'message' response is None for message: {message.text}")

            if res is not None and res.disable_ai_response:
                log.warning(f"Event 'message' response has disabled AI response for message: {message.text}")
                return False
            
            return True
        except Exception as e:
            log.error(f"Error processing events: {e}")
            return True
        
    async def __process_client_command(self, message: Message):
        # client commands are commands that are sent by the user to the assistant
        # message.text should be in the format: /command arg1 arg2 arg3
        text = message.text or ''
        if not text.startswith("/"):
            return True
        
        log.warning(f"Got a client command: {message.text}")
        parts = message.text.split(" ")
        command = parts[0][1:]
        args = parts[1:]
        
        # will return false if the command is handled by the assistant implementation
        cmd_executed = not await self.assistant.eval_client_command(
                                                            command=command,
                                                            args=args, 
                                                            message=message)
        
        # if the command was executed by the assistant, return False
        if cmd_executed:
            return False
        
        
        stream = self.assistant.process_client_command(message.lead, command, args)
        async for sentence in stream:
            await message.lead.connector.send_text_message(message.lead, sentence)
            
        return False


    async def process_message(self, message: Message, mode: StreamMode = StreamMode.SENTENCE, capture_repsonse: bool = False):
        """Process a message using the assistant. 
        The message is sent to the assistant for processing.
        
        Args:
            - message (Message): The message to process.
            - mode (StreamMode, optional): The mode for streaming the response. Defaults to StreamMode.SENTENCE.
            - capture_repsonse (bool, optional): If True, the response is captured and returned as a generator.
            if False, the response from genAI is sent to the client immediately by the gateway. Defaults to False.
            Look at capture_repsonse as a fire and forget mode when set to False.
            Set to True if you want to capture the response and process it in the connector code. For example,
            if you are building a voice assistant, you can capture the response and use it to synthesize speech.
            
            Fire and Forget use example:
            ```python
            async for chunk in gateway.process_message(message, mode=StreamMode.SENTENCE):
                pass
            ```
            That's it. The gateway will send the response to the user.
            
            Capture response use example:
            ```python
            async for chunk in gateway.process_message(message, mode=StreamMode.SENTENCE, capture_repsonse=True):
                # HERE: process the chunk
                # THEN send the chunk to the user
            ```
        """
        

        assert message is not None, "Message is None"
        assert isinstance(message, Message), "Message is not of type Message"
        # assert mode in [StreamMode.SENTENCE, 
        #                 StreamMode.FULL, 
        #                 StreamMode.DIRECT], "Invalid StreamMode"
        
        
        log.warning(f"Handling message: {message}")
        connector = message.lead.connector
        lead = message.lead
        
        if not await self.__process_middlewares(message):
            log.warning(f"Message {message.lead.get_session_id()} rejected by middlewares")
            return
        
        if not await self.__process_client_command(message):
            return
        
        if not await self.__process_events(message):
            log.warning("Event response has disabled AI response")
            return
        
        await connector.send_typing_action(lead)
        if self.assistant:

            # Langsmith Tracing 
            from langsmith.run_trees import RunTree
            rt = RunTree(name="Chat Message")
            try:
                rt.add_metadata({
                    "session_id": lead.get_session_id(),
                    "lead_metadata": lead.metadata
                })
                rt.add_tags(["message", lead.connector_name])
                
                with tracing_context(parent=rt):
                    stream = self.assistant.new_message(message, {})
                    content = ''
                    
                    if mode == StreamMode.SENTENCE:
                        rt.add_tags("sentence")
                        async for sentence in streaming_sentence_detector_async(stream): 
                            assert isinstance(sentence, StreamContentChunk), "stream must be a StreamChunk"
                            content += sentence.content
                            
                            if capture_repsonse:
                                yield sentence
                                # pass
                            else:
                                # Send the sentence to the connector
                                await self.dispatch_outgoing_genai_message(message, 
                                                                    text=sentence.content, 
                                                                    is_partial=sentence.is_partial)
                                await connector.send_typing_action(message.lead)
                                # Time delation based on the length of the sentence
                                if self.delivery_rate_control:
                                    length = len(sentence.content)
                                    wait_time = length / self.delivery_rate_control_ratio
                                    await asyncio.sleep(wait_time)


                    if mode == StreamMode.DIRECT:
                        rt.add_tags("direct")
                        async for chunk in stream:
                            assert isinstance(chunk, StreamContentChunk), "stream must be a StreamChunk"
                            content += chunk.content
                            
                            if capture_repsonse:
                                yield chunk
                                # pass
                            else:
                                await self.dispatch_outgoing_genai_message(message, text=chunk.content, is_partial=chunk.is_partial)
                                await connector.send_typing_action(message.lead)

                    
                    if mode == StreamMode.FULL:
                        rt.add_tags("full")
                        await connector.send_typing_action(message.lead)
                        async for chunk in stream:
                            assert isinstance(chunk, StreamContentChunk), "stream must be a StreamChunk"
                            content += chunk.content
                            
                            if capture_repsonse:
                                yield chunk.content
                                # pass
                            else:
                                await self.dispatch_outgoing_genai_message(message, text=content, is_partial=False)
                            
                    log.debug(f"Assistant response: {content}")
                    
                    rt.end()
                    rt.post()
            except Exception as e:
                rt.end(error=str(e))
                rt.post()
                raise e
        else: 
            log.critical("No assistant available")
            if capture_repsonse:
                yield "No assistant available"
                # pass
            else:
                await connector.send_text_message(message.lead, text="No assistant available")


    @staticmethod
    async def send_text_message(lead: ConversationLead, 
                                text: str, 
                                source_message: Message = None, 
                                is_partial=True):
        
        _self = MessageGateway.instance()
        assert isinstance(lead, ConversationLead), "lead must be an instance of ConversationLead"
        assert isinstance(text, str), "text must be a string"
        assert source_message is None or isinstance(source_message, Message), "source_message must be an instance of Message"
        connector = lead.connector
        
        # await connector.send_text_message(lead, text)
        # create outgoing message
        message = OutgoingTextMessage(content=text, lead=lead, is_partial=is_partial)
        await connector.send_message(message)


    async def dispatch_outgoing_genai_message(self, 
                                              src_message: Message, 
                                              text: str, 
                                              is_partial=False):
        assert isinstance(src_message, Message), "src_message must be an instance of Message"
        lead = src_message.lead
        assert isinstance(text, str),\
            "text must be a string"
        assert isinstance(lead.connector, BaseConnector),\
            "connector must be an instance of BaseConnector"
        connector = lead.connector
        
        msg = await self.message_enhancer(lead, text, is_partial)

        assert isinstance(msg, OutgoingMessage), "message enhancer must return an instance of OutgoingMessage"        

        await connector.send_message(msg)
        
        if not is_partial and src_message.isSTT and self.auto_voice_response:
            await connector.send_typing_action(lead)
            if isinstance(msg, OutgoingTextMessage):
                await connector.send_voice_message(lead, msg.content)



    def register_connector(self, connector: BaseConnector):
        assert isinstance(connector, BaseConnector), "Connector must be an instance of BaseConnector"
        conn = connector.get_router()
        assert conn is None or\
            isinstance(conn, APIRouter) or\
            isinstance(conn, FastAPI), "Router must be an instance of APIRouter or FastAPI"
        
        if conn is None:
            log.warning(f"Connector {connector.name()} has no router")
        else:
            if isinstance(conn, FastAPI):
                self.app.mount(f"/{connector.name()}", conn)
            else:
                self.app.include_router(conn)

        self.connectors.append(connector)
        connector.set_gateway(self)

    def run(self, enable_ngrok: bool = False):
        # check if uvicorn is installed
        try:
            import uvicorn
        except ImportError:
            log.error("Uvicorn is not installed. Please install uvicorn to run the gateway")
            return
    
        if enable_ngrok:
            
            try:
                import ngrok
            except ImportError:
                log.error("Ngrok is not installed."
                    "Please install ngrok to run the gateway with ngrok. "
                    "Execute the following command to install ngrok: "
                    "pip install ngrok")
                return
            

            log.info("Starting ngrok session")
            async def setup():
                session = await ngrok.SessionBuilder().authtoken_from_env().connect()
                listener = await session.http_endpoint().listen()
                log.info(f"Ngrok public endpoint: {listener.url()}")
                self.webhook_url = listener.url()
                
                # Bind this session to the gateway host and port
                forwardto = f"{self.host}:{self.port}"
                listener.forward(forwardto)
                log.info(f"Forwarding established from {listener.url()} to {forwardto}")

            asyncio.run(setup())
            # uvicorn.run(app=self.app)
            uvicorn.run(self.app, host=self.host, port=self.port)
            return 
                
        
        else:
            uvicorn.run(self.app, host=self.host, port=self.port)
            return
    
        
 