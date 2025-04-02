"""
Unofficial Python wrapper for the WhatsApp Cloud API.
"""
from __future__ import annotations
import json
from typing import Any, BinaryIO, Callable, Dict
import aiohttp
from fastapi import APIRouter, BackgroundTasks, Request
from loguru import logger as log
import aiohttp
import shortuuid
from cel.connectors.telegram.telegram_connector import hash_token
from cel.connectors.whatsapp.components.list_item import ListItem
from cel.gateway.model.base_connector import BaseConnector
from cel.connectors.whatsapp.components.reply_button import ReplyButton
from cel.connectors.whatsapp.constants import BASE_URL
from cel.connectors.whatsapp import WhatsappLead
from cel.connectors.whatsapp.model.whatsapp_message import WhatsappMessage
from cel.connectors.whatsapp.utils import build_headers
from cel.gateway.message_gateway import StreamMode
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.gateway.model.outgoing import OutgoingMessage,\
                                            OutgoingMessageType,\
                                            OutgoingLinkMessage,\
                                            OutgoingSelectMessage,\
                                            OutgoingTextMessage
from cel.gateway.model.outgoing.outgoing_message_buttons import OutgoingButtonsMessage
from .functions.utils import changed_field, is_message, is_reaction




async def nothing(*args):
    pass


class WhatsappConnector(BaseConnector):
    def __init__(self, 
                 token: str = None,
                 phone_number_id: str = None,
                 allowed_numbers: list[str] = None,
                 endpoint_prefix: str = None,
                 stream_mode: StreamMode = StreamMode.SENTENCE,
                 verify_token: str = None,
                 ssl: bool = False):
        """
        Initialize the Async WhatsApp Cloud API Connector with the Meta Access Token and the Phone Number Id

        Args:
            - token[str]: The Meta Access Token
            - phone_number_id[str]: The Meta Phone Number Id
            - verify_token[str]: The verification token, defaults to a random string
            - webhook_prefix[str]: The prefix for the webhook, defaults to "/whatsapp"
            - stream_mode[StreamMode]: The stream mode for the gateway, defaults to StreamMode.SENTENCE
        """

        # Verify the token and phone number id
        assert token is not None, "Token not provided"
        assert phone_number_id is not None, "Phone number id not provided"
        # assert verify_token is not None, "Verify token not provided"
        
        self.token = token
        self.phone_number_id = phone_number_id
        self.allowed_numbers = allowed_numbers
        self.base_url = BASE_URL
        self.url = f"{self.base_url}/{phone_number_id}/messages"
        self.verify_token = verify_token or shortuuid.uuid()
        self.endpoint_prefix = endpoint_prefix or "/whatsapp"
        self.stream_mode = stream_mode
        self.verification_handler = nothing
        self.ssl = ssl
        log.debug("Whatsapp Connector initialized")
        
        
        
    def __build_routes(self, endpoint_prefix: str):
        assert endpoint_prefix is not None, "Endpoint prefix not provided"
        
        def shutdown():
            log.warning("Shutting down whatsapp connector")
        
        def startup():
            log.debug(f"Starting up whatsapp connector")

        router = APIRouter(prefix=endpoint_prefix,
                            on_startup=[startup],
                            on_shutdown=[shutdown])

        # Define the routes
        # ---------------------------------------------------------------
        @router.get("/")
        async def verify_endpoint(r: Request):
            if r.query_params.get("hub.verify_token") == self.verify_token:
                log.info("Verified webhook")
                challenge = r.query_params.get("hub.challenge")
                await self.verification_handler(challenge)
                return int(challenge)
            log.error("Webhook Verification failed")
            await self.verification_handler(False)
            return {"success": False}

        def get_display_phone_number(data: dict) -> str:
            """Safely retrieve the display phone number from the incoming data."""
            try:
                return data["entry"][0]["changes"][0]["value"]["metadata"]["display_phone_number"]
            except (IndexError, KeyError, TypeError) as e:
                log.error(f"Error retrieving display phone number: {e}")
                return None

        @router.post("/")
        async def hook(r: Request, background_tasks: BackgroundTasks):
            try:
                # Handle Webhook Subscriptions
                log.info("Received message from Whatsapp")
                data = await r.json()
                log.debug(json.dumps(data, indent=2))
                display_phone_number = get_display_phone_number(data)
                if self.allowed_numbers and display_phone_number not in self.allowed_numbers:
                    log.warning(f"Display phone number {display_phone_number} is not allowed.")
                    return {"success": True}
                else:
                    background_tasks.add_task(self.__process_message, data)
                    return {"success": True}
            except Exception as e:
                # Avoid replaying the message
                log.error(f"Error processing message: {e}")
                return {"success": True}
        # ---------------------------------------------------------------
        return router
    
    async def __process_message(self, data: dict):      
        changed_field = self.changed_field(data)
        log.debug(f"Changed field: {changed_field}")
        if changed_field == "messages":
            if self.is_reaction(data):
                log.debug("Reaction received")
                return
            new_message = self.is_message(data)
            log.debug(f"New message: {new_message}")
            if new_message:
                msg = await WhatsappMessage.load_from_message(data=data, 
                                                        token=self.token, 
                                                        phone_number_id=self.phone_number_id, 
                                                        connector=self)
                await self.__mark_as_read(msg.id)
                if self.gateway:
                    async for m in self.gateway.process_message(msg, mode=self.stream_mode):
                        pass

    def on_verification(self, handler: callable):
        """
        Set the handler for verification
        Args:
            handler[function]: The handler function
        """
        assert callable(handler), "Handler must be a function"
        self.verification_handler = handler

    def name(self) -> str:
        """ This method returns the name of the connector. This is used to identify the connector
        In order to allow multiple connectors of the same type to be used in the same application 
        this method must return a unique name for the connector. 
        A good practice is to return the name and a hash of the token.
        """
        h = hash_token(self.phone_number_id)
        return f"whatsapp:{h}"
    
    def set_gateway(self, gateway):
        from cel.gateway.message_gateway import MessageGateway
        assert isinstance(gateway, MessageGateway), \
            "gateway must be an instance of MessageGateway"
        self.gateway = gateway

    def get_router(self) -> APIRouter:
        return self.__build_routes(self.endpoint_prefix)

    def startup(self, context: MessageGatewayContext):
        log.warning(f"Be sure to setup in Meta Whatsapp Cloud API -> Webhoook this URL: {context.webhook_url}{self.endpoint_prefix}")

    def shutdown(self, context: MessageGatewayContext):
        pass

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
        

    async def __mark_as_read(self, message_id: str) -> dict:
        """Mark a message as read"""
        assert message_id is not None, "Message ID not provided"
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(f"{self.url}", 
                                    headers=build_headers(self.token), 
                                    json=payload) as response:
                if response.status == 200:
                    log.info(await response.json())
                    return await response.json()
                else:
                    log.error(await response.json())
                    return await response.json()              
        

    async def send_text_message(self, 
                                lead: WhatsappLead, 
                                text: str, 
                                metadata: dict = {}, 
                                is_partial: bool = True):
        """ Send a text message to the lead. The simplest way to send a message to the lead.
        
        Args:
            - lead[WhatsappLead]: The lead to send the message
            - text[str]: The text to send
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
        """
        
        assert isinstance(lead, WhatsappLead), "lead must be instance of WhatsappLead"
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": lead.phone,
            "type": "text",
            "text": {
                "preview_url": False, 
                "body": text
            },
        }
        
        headers = build_headers(self.token)
        log.info(f"Sending message to {lead.phone}")
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(f"{self.url}", headers=headers, json=data) as r:
                if r.status == 200:
                    log.info(f"Message sent to {lead.phone}")
                else:
                    log.error(await r.json())

    async def send_select_message(self, 
                                  lead: WhatsappLead, 
                                  text: str,
                                  options: list[str],
                                  header: str = None,
                                  footer: str = None,
                                  button_text: str = None,
                                  list_title: str = None,
                                  metadata: dict = {}, 
                                  is_partial: bool = True):
        """ Send a select message to the lead. This will send a message with a list of options
        to the lead. The lead will be able to select one of the options.
        
        Args:
            - lead[WhatsappLead]: The lead to send the message
            - text[str]: The text to send with the options
            - options[list[str]]: A list of options to send to the lead
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
        """        
        assert isinstance(lead, WhatsappLead), "lead must be instance of WhatsappLead"
        assert options is not None, "Options not provided"
        assert len(options) > 0, "Options must be a list of strings"
        
        # trim options to 20 characters
        options = [opt[:20] for opt in options]
        
        if len(options) > 10:
            log.critical(f"The maximum number of options is 10. Got: {options}")
            # trim options to 10
            options = options[:10]
        
        items = [ListItem(title=opt) for opt in options]
        
        # "rows": [
        #     {
        #       "id": "<ROW_ID>",
        #       "title": "<ROW_TITLE_TEXT>",
        #       "description": "<ROW_DESCRIPTION_TEXT>"
        #     }
        #     /* Additional rows would go here*/
        #   ]
        
        response = await self._send_select(
            recipient_id=lead.phone,
            list={
                "type": "list",
                "header": {"type": "text", "text": header} if header else None,
                "body": {"text": text} if text else None,
                "footer": {"text": footer} if footer else None,
                "action": {
                    "sections": [
                        {
                            "title": list_title,
                            "rows": [json.loads(str(item)) for item in items]
                        }
                    ],
                    "button": button_text                    
                },

            }
        )
        log.debug(f"Select message response: {response}")
    
    
    async def send_buttons_message(self, 
                                  lead: WhatsappLead, 
                                  text: str,
                                  options: list[str],
                                  header: str = None,
                                  footer: str = None,
                                  metadata: dict = {}, 
                                  is_partial: bool = True):
        """ Send a message with buttons. This will send a message with a limited number of options
        to the lead. The lead will be able to select one of the options.
        For WhatsApp, the maximum number of buttons is 3. And the message is a interactive message with
        reply buttons.
        
        Args:
            - lead[WhatsappLead]: The lead to send the message
            - text[str]: The text to send with the options
            - options[list[str]]: A list of options to send to the lead
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
        """        
        assert isinstance(lead, WhatsappLead), "lead must be instance of WhatsappLead"
        assert options is not None, "Options not provided"
        assert len(options) > 0, "Options must be a list of strings"
        
        # trim options to 20 characters
        options = [opt[:20] for opt in options]
        
        if len(options) > 3:
            log.critical(f"The maximum number of options is 3. Got: {options}")
            # trim options to 3
            options = options[:3]
        
        buttons = [ReplyButton(title=opt) for opt in options]
        
        response = await self._send_reply_button(
            recipient_id=lead.phone,
            button={
                "type": "button",
                "header": {"type": "text", "text": header} if header else None,
                "body": {"text": text} if text else None,
                "footer": {"text": footer} if footer else None,
                "action": {
                    "buttons": [json.loads(str(button)) for button in buttons]
                }
            }
        )
        log.debug(f"Select message response: {response}")    
    
    async def send_link_message(self, lead: WhatsappLead, text: str, links: list, metadata: dict = {}, is_partial: bool = True):
        """ Send a link message to the lead. When you need to send a link to some platforms
        like WhatsApp, the platform will automatically generate a preview of the link and embed a link
        to the text in a normal message.
        This method will help you to send a link message most effectively, hidden the preview and 
        embeding the link into a button. This will bring a better user experience.
        
        Args:
        
            - lead[WhatsappLead]: The lead to send the message
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
        assert isinstance(lead, WhatsappLead), "lead must be instance of WhatsappLead"
        assert links is not None, "Links not provided"
        assert len(links) > 0, "Links must be a list of dictionaries"
        assert text is not None, "Text not provided"
        
        log.debug(f"Sending Link Message to phone: {lead.phone}, text: {text}, url: {links}")
        response = await self._send_link(
            link_label=links[0].get("text"),
            link=links[0].get("url"),
            body=text,
            recipient_id=lead.phone,
        )
         
    async def send_typing_action(self, lead):
        """Send typing action to the lead. This will show the typing action in the chat.
        
        Args:
            - lead[TelegramLead]: The lead to send the typing action
        """    
        assert isinstance(lead, WhatsappLead), "lead must be instance of WhatsappLead"
        # do nothing, there is no typing action in whatsapp cloud api
        log.warning(f"Whatsapp typing action not currently supported by Cloud API")
        pass
    
    
    async def send_message(self, message: OutgoingMessage):
        assert isinstance(message, OutgoingMessage),\
            "message must be an instance of OutgoingMessage"
        assert isinstance(message.lead, WhatsappLead),\
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
                                           button_text=message.button,
                                           list_title=message.list_title,
                                           is_partial=message.is_partial)
            
        if message.type == OutgoingMessageType.BUTTONS:
            assert isinstance(message, OutgoingButtonsMessage),\
            "message must be an instance of OutgoingSelectMessage"
            
            await self.send_buttons_message(lead, 
                                           message.content, 
                                           options=message.options, 
                                           metadata=message.metadata, 
                                           is_partial=message.is_partial)            
        
        if message.type == OutgoingMessageType.LINK:
            assert isinstance(message, OutgoingLinkMessage),\
            "message must be an instance of OutgoingLinkMessage"
            
            await self.send_link_message(lead, 
                                         message.content, 
                                         links=message.links, 
                                         metadata=message.metadata, 
                                         is_partial=message.is_partial)


    async def _send_link(self, 
                         link_label: str, 
                         body: str | None,
                         link: str,
                         recipient_id: str,
                         footer: str | None = None,
                         image_url: str = None) -> None:
        await self._send_cta_url(
            recipient_id=recipient_id,
            cta_url={
                "type": "cta_url",
                "header": {
                    "type": "image",
                    "image": {"link": image_url}
                } if image_url else None,
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "name": "cta_url",
                    "parameters": {
                        "display_text": link_label,
                        "url": link
                    }
                }                
            }
        )

    def _create_button(self, button: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Method to create a button object to be used in the send_message method.

        Args:
                button[dict]: A dictionary containing the button data
        """
        data = {"type": "list", "action": button.get("action")}
        if button.get("header"):
            data["header"] = {"type": "text", "text": button.get("header")}
        if button.get("body"):
            data["body"] = {"text": button.get("body")}
        if button.get("footer"):
            data["footer"] = {"text": button.get("footer")}
        return data

    async def _send_button(self, button: Dict[Any, Any], recipient_id: str) -> Dict[Any, Any]:
        """
        Sends an interactive buttons message to a WhatsApp user

        Args:
            button[dict]: A dictionary containing the button data(rows-title may not exceed 20 characters)
            recipient_id[str]: Phone number of the user with country code wihout +

        check https://github.com/Neurotech-HQ/whatsapp#sending-interactive-reply-buttons for an example.
        """
        assert isinstance(recipient_id, str) and recipient_id != "", "Recipient ID must be a string"
        assert isinstance(button, dict), "Button must be a dictionary"
        
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "interactive",
            "interactive": self._create_button(button),
        }
        
        log.debug(f"Sending buttons to {recipient_id}")
        headers = build_headers(self.token)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(f"{self.url}", headers=headers, json=data) as r:
                if r.status == 200:
                    log.debug(f"Message sent to {recipient_id}")
                else:
                    log.error(await r.json())     
                    
    async def _send_select(
        self, 
        list: Dict[Any, Any], 
        recipient_id: str
    ) -> Dict[Any, Any]:
        """
        Sends an interactive list message to a WhatsApp user

        Args:
            button[dict]: A dictionary containing the button data
            recipient_id[str]: Phone number of the user with country code wihout +

        Note:
            The maximum number of buttons is 3, more than 3 buttons will rise an error.
        """

        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "interactive",
            "interactive": list,
        }
        headers = build_headers(self.token)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(f"{self.url}", headers=headers, json=data) as r:
                if r.status == 200:
                    log.debug(f"Message sent to {recipient_id}")
                else:
                    log.error(await r.json())                       
                       

    async def _send_reply_button(
        self, 
        button: Dict[Any, Any], 
        recipient_id: str
    ) -> Dict[Any, Any]:
        """
        Sends an interactive reply buttons[menu] message to a WhatsApp user

        Args:
            button[dict]: A dictionary containing the button data
            recipient_id[str]: Phone number of the user with country code wihout +

        Note:
            The maximum number of buttons is 3, more than 3 buttons will rise an error.
        """
        if len(button["action"]["buttons"]) > 3:
            raise ValueError("The maximum number of buttons is 3.")
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "interactive",
            "interactive": button,
        }
        headers = build_headers(self.token)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(f"{self.url}", headers=headers, json=data) as r:
                if r.status == 200:
                    log.debug(f"Message sent to {recipient_id}")
                else:
                    log.error(await r.json())     
                    
    async def _send_cta_url(
        self, cta_url: Dict[Any, Any], 
        recipient_id: str
    ) -> Dict[Any, Any]:
        """
        Sends a call to action url message to a WhatsApp user

        Args:
            cta_url[dict]: A dictionary containing the cta url data
            recipient_id[str]: Phone number of the user with country code wihout +

        check
        
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "interactive",
            "interactive": cta_url,
        }
        headers = build_headers(self.token)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(f"{self.url}", headers=headers, json=data) as r:
                if r.status == 200:
                    log.debug(f"Message sent to {recipient_id}")
                else:
                    log.error(await r.json())     



    async def send_document_message(self, lead, content: str | bytes | BinaryIO, 
                                    filename:str, caption:str = None, metadata: dict = {}, is_partial: bool = True):
        log.debug(f"Sending document {filename} (caption:{caption}) message to {lead.phone}")
        
        assert isinstance(lead, WhatsappLead), "lead must be instance of WhatsappLead"
        assert isinstance(filename, str), "filename must be a string"
        
        from pywa import WhatsApp
        
        # get mimet type from filename
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        log.debug(f"Mime type: {mime_type}")

        wa = WhatsApp(
            phone_id=self.phone_number_id,
            token=self.token
        )

        # Send the document
        wa.send_document(
            to=lead.phone,
            document=content,
            filename=filename,
            caption=caption,
            mime_type=mime_type,
            footer=caption
        )



    # all the files starting with _ are imported here, and should not be imported directly.
    changed_field = staticmethod(changed_field)
    is_message = staticmethod(is_message)
    is_reaction = staticmethod(is_reaction)
