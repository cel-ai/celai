import os
import json
import asyncio
import shortuuid
from loguru import logger as log
from typing import Any, Callable, Dict
from aiogram import Bot, Dispatcher
from fastapi import APIRouter, BackgroundTasks
from loguru import logger as log

from aiogram.types.input_file import BufferedInputFile
from aiogram.types import Message as AiogramMessage
from cel.comms.utils import async_run
from cel.connectors.telegram.run_mode import RunMode
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.message_gateway import StreamMode
from cel.gateway.model.message import Message
from cel.connectors.telegram.model.telegram_message import TelegramMessage
from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.voice.base_voice_provider import BaseVoiceProvider
from cel.gateway.model.outgoing import OutgoingMessage,\
                                            OutgoingMessageType,\
                                            OutgoingLinkMessage,\
                                            OutgoingSelectMessage,\
                                            OutgoingTextMessage




class TelegramConnector(BaseConnector):
       
    def __init__(self, 
                 token: str = None, 
                 stream_mode: StreamMode = StreamMode.SENTENCE,
                 voice_provider: BaseVoiceProvider = None,
                 report_errors_to_telegram: bool = False,
                 run_mode: str = RunMode.get_default()):
        
        log.debug("Creating telegram connector")
        self.token = token or os.getenv("TELEGRAM_TOKEN")     
        self.router = APIRouter(prefix="/telegram")
        self.bot = Bot(token)
        self.paused = False
        # generate shortuuid for security token
        self.security_token = shortuuid.uuid()
        self.__create_routes(self.router)
        self.stream_mode = stream_mode
        self.user_queues = {}
        self.voice_provider = voice_provider
        self.run_mode = RunMode.get_mode(run_mode)  
        
        
        self.report_errors_to_telegram = report_errors_to_telegram or os.getenv("REPORT_ERRORS_TO_TELEGRAM", False)
        
        assert self.token, "TELEGRAM_TOKEN env var must be set"
        
        
    def __create_routes(self, router: APIRouter):        
        @router.post("/webhook/{security_token}")
        async def telegram_webhook(security_token, payload: Dict[Any, Any], background_tasks: BackgroundTasks):
            
            if security_token != self.security_token:
                raise Exception("Invalid security token")
            # process message in background in order to quickly return 200 OK to telegram 
            # long running tasks should be processed in background
            # telegram timeout policy will retry sending the message if it does 
            # not receive 200 OK in ~30 seconds
            # return anything different than 200 OK will make telegram retry 
            # sending the message up to 3 times.
            # background_tasks.add_task(self.__process_message, payload)
            await self.__enqueue_message(payload)
            return {"status": "ok"}

    async def __process_user_queue(self, chat_id: str):
        queue = self.user_queues[chat_id]
        
        while True:
            message = await queue.get()
            try:
                # Procesa el mensaje (reemplaza esta función por tu lógica)
                await self.__process_message(message)
            except Exception as e:
                log.debug(f"Error processing message for user {chat_id}: {e}")
            finally:
                queue.task_done()

            # Si deseas limpiar las colas y tareas cuando estén vacías:
            if queue.empty():
                # Opcionalmente, puedes agregar un retraso aquí si esperas más mensajes pronto
                del self.user_queues[chat_id]
                log.debug(f"User {chat_id} queue has been cleared")
                break  # Sal del bucle y termina la tarea


    async def __enqueue_message(self, payload: dict | AiogramMessage):
        chat_id =  str(payload["message"]["from"]["id"])
        log.debug(f"Enqueuing message for chat_id: {chat_id}")
        if chat_id not in self.user_queues:
            # Crea una nueva cola y tarea para el nuevo usuario
            self.user_queues[chat_id] = asyncio.Queue()
            asyncio.create_task(self.__process_user_queue(chat_id))
        await self.user_queues[chat_id].put(payload)


    async def __process_message(self, msg: dict | AiogramMessage):
        try:
            log.debug("Received Telegram webhook")
            log.debug(msg)
            msg = await TelegramMessage.load_from_message(msg, self.token, connector=self)
            
            
            if self.paused:
                log.warning("Connector is paused, ignoring message")
                return 
            if self.gateway:
                async for m in self.gateway.process_message(msg, mode=self.stream_mode):
                    pass
            else:
                log.critical("Gateway not set in Telegram Connector")
                raise Exception("Gateway not set in Telegram Connector")
                
        except Exception as e:
            # TODO: TEST!
            log.error(f"Error processing telegram webhook: {e}")
            try:
                if self.report_errors_to_telegram:
                    if isinstance(msg, dict):
                        msg =  msg.get("message")
                        lead = TelegramLead.from_telegram_message(msg, connector=self)
                        await self.send_text_message(lead, f"Error processing message: {e}")
                    else:
                        await msg.answer(f"Error processing message: {e}")
            except Exception as e:
                log.error(f"Error reporting error to telegram: {e}")
                   
    
    async def send_text_message(self, lead: TelegramLead, text: str, metadata: dict = {}, is_partial: bool = True):
        """ Send a text message to the lead. The simplest way to send a message to the lead.
        
        Args:
            - lead[TelegramLead]: The lead to send the message
            - text[str]: The text to send
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
        """        
        log.debug(f"Sending message to chat_id: {lead.chat_id}, text: {text}, is_partial: {is_partial}")
        await self.bot.send_message(chat_id=lead.chat_id, text=text)      


    async def send_image_message(self, lead: TelegramLead, image: Any, filename: str,  caption:str = None, metadata: dict = {}, is_partial: bool = True):
        """ Send an image message from memory to the lead. The image must be an image file in memory.
        The image will be sent to the lead.
        
        Args:
            - lead[TelegramLead]: The lead to send the message
            - image[Any]: The image file to send
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
        """
        log.debug(f"Sending Image Message to chat_id: {lead.chat_id}, is_partial: {is_partial}")
        photo = BufferedInputFile(image, filename=filename)
        await self.bot.send_photo(chat_id=lead.chat_id, photo=photo, caption=caption)


    async def send_select_message(self, 
                                  lead: TelegramLead, 
                                  text: str, 
                                  options: list[str], 
                                  metadata: dict = {}, 
                                  is_partial: bool = True):
        """ Send a select message to the lead. This will send a message with a list of options
        to the lead. The lead will be able to select one of the options.
        
        Args:
            - lead[TelegramLead]: The lead to send the message
            - text[str]: The text to send with the options
            - options[list[str]]: A list of options to send to the lead
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
        """
        
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        log.debug(f"Sending select message to chat_id: {lead.chat_id}, text: {text}, options: {options}, is_partial: {is_partial}")
        
        # Crear el teclado con los botones
        if len(options) > 2: 
            keys = [[KeyboardButton(text=opt) for opt in options[i:i+2]] for i in range(0, len(options), 2)]
        else:
            keys = [[KeyboardButton(text=opt) for opt in options]]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, 
                                     is_persistent=False,
                                     one_time_keyboard=True,
                                     keyboard=keys)

        await self.bot.send_message(chat_id=lead.chat_id, text=text, reply_markup=markup)


    async def send_link_message(self, 
                                lead: TelegramLead, 
                                text: str, 
                                links: list, 
                                metadata: dict = {}, 
                                is_partial: bool = True):
        """ Send a link message to the lead. When you need to send a link to some platforms
        like WhatsApp, the platform will automatically generate a preview of the link and embed a link
        to the text in a normal message.
        This method will help you to send a link message most effectively, hidden the preview and 
        embeding the link into a button. This will bring a better user experience.
        
        Args:
        
            - lead[TelegramLead]: The lead to send the message
            - text[str]: The text to send with the link
            - links[list]: A list of dictionaries containing the link data. 
            Each dictionary must have a `text` and `url` key.
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
            
        Example:
            
            ```python
            links = [
                {"text": "Go to Google", "url": "https://www.google.com"},
                {"text": "Go to Facebook", "url": "https://www.facebook.com"}
            ]
            await conn.send_link_message(ctx.lead, text="Please follow this link", links=links)
            ```
    
        """
        
        # from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        log.debug(f"Sending Link Message to chat_id: {lead.chat_id}, text: {text}, url: {links}, is_partial: {is_partial}")
        # Crear el teclado con los botones
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=link.get("text"), url=link.get("url"))] for link in links
        ])

        await self.bot.send_message(chat_id=lead.chat_id, text=text, reply_markup=reply_markup)

    async def send_voice_message(self, lead: TelegramLead, text: str, options: dict = {}, is_partial: bool = False):
        assert isinstance(lead, TelegramLead), "lead must be an instance of TelegramLead"
        assert isinstance(text, str), "text must be a string"
        assert isinstance(self.voice_provider, BaseVoiceProvider), "voice_provider must be an instance of BaseVoiceProvider"
        
        if not self.voice_provider:
            log.critical("Error: Voice provider not set in Telegram Connector")
        # Convert text to voice
        voice = self.voice_provider.TTS(text, **options)
        data = BufferedInputFile(b"".join(voice), filename="voice.ogg")
        await self.bot.send_voice(chat_id=lead.chat_id, voice=data)
        
        
    async def send_typing_action(self, lead: TelegramLead):
        """Send typing action to the lead. This will show the typing action in the chat.
        
        Args:
            - lead[TelegramLead]: The lead to send the typing action
        """
        
        
        log.debug(f"Sending typing action to chat_id: {lead.chat_id}")
        await self.bot.send_chat_action(chat_id=lead.chat_id, action="typing")
        
        
        
    async def send_message(self, message: OutgoingMessage):
        assert isinstance(message, OutgoingMessage),\
            "message must be an instance of OutgoingMessage"
        assert isinstance(message.lead, TelegramLead),\
            "lead must be an instance of TelegramLead"
        lead = message.lead
        
        if message.type == OutgoingMessageType.TEXT:
            assert isinstance(message, OutgoingTextMessage),\
            "message must be an instance of OutgoingMessage"
            await self.send_text_message(lead, 
                                         message.content, 
                                         metadata=message.metadata, 
                                         is_partial=message.is_partial)
            
        if message.type == OutgoingMessageType.SELECT:
            assert isinstance(message, OutgoingSelectMessage),\
            "message must be an instance of OutgoingSelectMessage"
            
            await self.send_select_message(lead, 
                                           message.content, 
                                           options=message.options, 
                                           metadata=message.metadata, 
                                           is_partial=message.is_partial)

        if message.type == OutgoingMessageType.LINK:
            assert isinstance(message, OutgoingLinkMessage),\
            "message must be an instance of OutgoingLinkMessage"
            
            await self.send_link_message(lead, 
                                           message.content, 
                                           url=message.links, 
                                           metadata=message.metadata, 
                                           is_partial=message.is_partial)
        
        
        
    def name(self) -> str:
        return "telegram"
        
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
        
        webhook_url = f"{context.webhook_url}/telegram/webhook/{self.security_token}"
        log.debug(f"Starting telegram connector with webhook url: {webhook_url}")
        if self.run_mode == RunMode.WEBHOOK:
            log.debug("Starting telegram connector in webhook mode")
            async_run(self.bot.set_webhook(webhook_url), then=lambda r: log.debug(f'Webhook set: {r}'))
        else:
            log.debug("Starting telegram connector in polling mode")
            
            asyncio.create_task(self.bot.delete_webhook())
            dp = Dispatcher()
            
            @dp.message()
            async def message_handler(message: AiogramMessage) -> None:
                try:
                    message_dict=json.loads(message.model_dump_json(exclude_none=True, by_alias=True))
                    await self.__enqueue_message({"message": message_dict})
                except Exception as e:
                    log.error(f"Error processing message: {e}")
                    if self.report_errors_to_telegram:
                        await message.answer("Error processing message:" + str(e))
                    
            async def run_pulling() -> None:
                await self.bot.delete_webhook()
                # And the run events dispatching
                await dp.start_polling(self.bot)
                    
            task = asyncio.create_task(run_pulling())
            log.debug("Telegram Polling started")
                              
    
    def shutdown(self, context: MessageGatewayContext):
        log.debug("Shutting down telegram connector")
        async_run(self.bot.delete_webhook(), then=lambda r: log.debug(f'Webhook deleted: {r}'))
        
    def pause(self):
        log.debug("Pausing telegram connector")
        self.paused = True
    
    def resume(self):
        log.debug("Resuming telegram connector")
        self.paused = False
