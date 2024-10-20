from abc import ABC
import re
import time
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel
from redis import asyncio as aioredis
import json
from dataclasses import asdict, dataclass
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from loguru import logger as log

Redis = aioredis.Redis

# WARNING: DO NOT USE THIS KEY IN PRODUCTION
DEFUALT_MASTER_KEY = "123456"


@dataclass
class AuthEntry(ABC):
    session_id: str = None
    invite_code: str = None
    client_cmd_enabled: bool = False
    last_request: int = 0
    metadata: dict = None
    
@dataclass
class InvitationEntry(ABC):
    invite_code: str = None
    created_at: int = 0
    # 0 means never expires
    expires_at: int = 0
    used: bool = False
    name: str = None
    metadata: dict = None

class InvitationGuardMiddlewareEvents:
    new_conversation = "new_conversation"
    invitation_accepted = "invitation_accepted"
    rejected_code = "rejected_code"
    admin_login = "admin_login"
    admin_logout = "admin_logout"



class InvitationGuardMiddleware(ABC):
    """Middleware to secure client commands, session handling and user lyfe cycle related events
    Invite code is a 6 alphanumeric characters, including uppercase and lowercase.
    This middleware will search for the invite code in the message and handle it accordingly.
    It specs code formatted as #XXXXXX where X is an alphanumeric character.
    
    
    Invitations:
        - Create, revoke and get invitations
        - Claim an invitation
        - Handle invitation codes in messages
        - Backdoor code to bypass invitation system
        
    
    Triggered events:
        - new_conversation: Event called when a new conversation is started.
        - rejected_code: Event called when a user enters an invalid code.
        - admin_login: Event called when a user logs in as admin.
        - admin_logout: Event called when a user logs out as admin.
        
    Args:
        telegram_bot_name: The name of the Telegram bot for URL generation
        whatsapp_phone_number: The phone number of the WhatsApp bot for URL generation
        redis: The Redis database URL
        key_prefix: The prefix for the keys in the Redis database
        master_key: The master key to login as admin
        reject_message: The message to send when a user is rejected
        backdoor_invite_code: The backdoor invite code
        allow_only_invited: Allow only invited users to access the service
        
    """
    
    events: InvitationGuardMiddlewareEvents = InvitationGuardMiddlewareEvents()
    
    
    def __init__(self, 
                 telegram_bot_name: str = None,
                 whatsapp_phone_number: str = None,
                 redis: str | Redis = None, 
                 key_prefix: str = "igm", 
                 master_key: str = None,
                 # default reject message with wrong way emoji
                 reject_message: str = "🚫 You are not allowed to access this service.",
                 backdoor_invite_code: str = None,
                 allow_only_invited: bool = True):
        
        self.client = redis if isinstance(redis, Redis) else aioredis.from_url(redis or 'redis://localhost:6379/0')
        self.key_prefix = key_prefix
        log.critical("No master key provided. Using default key") if not master_key else None
        self.master_key = master_key or DEFUALT_MASTER_KEY
        self.allow_only_invited = allow_only_invited
        self.reject_message = reject_message
        self.backdoor_invite_code = backdoor_invite_code
        self.telegram_bot_name = telegram_bot_name
        self.whatsapp_phone_number = whatsapp_phone_number
        
        
    
    # Setup the middleware with the FastAPI application    
    def setup(self, app):
        """ Setup the middleware with the FastAPI application. Here you can define
        the routes for the invitation system.
        
        Use the prefix /middleware/guard to register the routes.
        """
        log.debug("InvitationGuardMiddleware initialized")
        prefix = "/middleware/guard"
        
        class InvitationRequest(BaseModel):
            # code: str
            expires_at: Optional[int] = 0
            name: Optional[str] = None

        class InvitationResponse(BaseModel):
            invite_code: str
            message: str
        
        # Add echo route
        @app.get(prefix + "/echo")
        async def echo():
            return {"status": "ok"}
        
        @app.get(prefix + "/invitations/{code}", 
                 response_model=InvitationEntry, 
                 summary="Get invitation", 
                 description="This endpoint allows you to get an invitation by code.")
        async def get_invitation(code: str):
            """
            Get invitation by code
            """
            entry = await self.get_invitation(code)
            
            if entry is None:
                raise HTTPException(status_code=404, detail="Invitation not found")
            
            return entry 
        
        @app.post(prefix + "/invitations", 
                  response_model=InvitationResponse, 
                  summary="Create a new invitation", 
                  description="This endpoint allows you to create a new invitation.")
        async def create_invitation(request: InvitationRequest):
            """
            Create a new invitation

            - **code**: The invitation code
            - **expires_at**: The expiration time of the invitation (optional)
            - **name**: The name associated with the invitation (optional)
            """
            code = self.__gen_invite_code()
            await self.create_invitation(code, name=request.name, expires_at=request.expires_at)
            return {
                "message": "Invitation created successfully",
                "invite_code": code
            }
        
        @app.delete(prefix + "/invitations/{code}", 
                    response_model=InvitationResponse, 
                    summary="Revoke an invitation", 
                    description="This endpoint allows you to revoke an invitation.")
        async def revoke_invitation(code: str):
            """
            Revoke an invitation by code
            """
            await self.revoke_invitation(code)
            return {"message": "Invitation revoked successfully"}

    # MAIN METHOD - Handle the message
    async def __call__(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        try:
            assert isinstance(message, Message), "Message must be a Message object"
            assert isinstance(connector, BaseConnector), "Connector must be a BaseConnector object"
            
            if not await self.__handle_invitation_code(message, connector, assistant):
                return False        
            
            entry = await self.get_auth_entry(message.lead.get_session_id())
            
            # add last request time in message
            if entry:
                assert isinstance(entry, AuthEntry), "Entry must be an AuthEntry object"
                
                if self.allow_only_invited and entry.invite_code is None:
                    log.critical(f"User {message.lead.get_session_id()} is not invited")
                    await connector.send_text_message(message.lead, self.reject_message)
                    return False
                
                time_since_last_request = time.time() - (entry.last_request or 0)
                message.metadata = message.metadata or {}
                message.metadata['time_since_last_request'] = time_since_last_request
                message.metadata['invitation'] = entry.metadata
                message.lead.metadata = message.lead.metadata or {}
                message.lead.metadata['time_since_last_request'] = time_since_last_request
                message.lead.metadata['invitation'] = entry.metadata
                
                await self.set_entry(message.lead.get_session_id(), 
                                    client_cmd_enabled=entry.client_cmd_enabled, 
                                    metadata=entry.metadata,
                                    invite_code=entry.invite_code)
            else:
                await self.set_entry(message.lead.get_session_id(), 
                                    client_cmd_enabled=False, 
                                    metadata={})
                await connector.send_text_message(message.lead, self.reject_message)
                await assistant.call_event(self.events.new_conversation, message.lead, message, connector)
                return False
                
            if not await self.__handle_login_command(message, connector, entry, assistant):
                return False
            
            if not await self.__secure_client_commands(message, connector, entry):
                return False
            
            return True
        except Exception as e:
            log.error(f"Error in InvitationGuardMiddleware: {e}")
            return False
    
    
    # Handle invitation claim
    def __search_invitation_code(self, text: str):
        # regex to match code in string
        regex = r"#\w{6}"
        
        # search for the pattern in the message content
        match = re.search(regex, text)
        
        # return the matched code or None if no match is found
        if match:
            return match.group(0)
        
        return None
    
    async def __handle_invitation_code(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        code = self.__search_invitation_code(message.text)
        if code:
            inv = await self.get_invitation(code)
            
            if code == self.backdoor_invite_code and self.backdoor_invite_code:
                await self.set_entry(message.lead.get_session_id(), invite_code=code)
                await connector.send_text_message(message.lead, "Backdoor code accepted")
                message.text = message.text.replace(code, "")
                await assistant.call_event(self.events.invitation_accepted, message.lead, message, connector, data=inv)
                return True
            
            # Reject cases
            # --------------------------------
            if inv is None:
                log.critical(f"Invalid code {code} provided")
                await connector.send_text_message(message.lead, "Invalid code provided")
                await assistant.call_event(self.events.rejected_code, message.lead, message, connector)
                return False
            
            if inv.expires_at > 0 and time.time() > inv.expires_at:
                log.critical(f"Expired code {code} provided")
                await connector.send_text_message(message.lead, "Expired code provided")
                await assistant.call_event(self.events.rejected_code, message.lead, message, connector)
                return False
            
            if inv.used:
                log.critical(f"Code {code} already used")
                await connector.send_text_message(message.lead, "Code already used")
                await assistant.call_event(self.events.rejected_code, message.lead, message, connector)
                return False

            # Accept the code
            # --------------------------------
            await self.set_entry(message.lead.get_session_id(), invite_code=code, metadata=inv.metadata)
            await self.claim_invitation(code)
            await connector.send_text_message(message.lead, "Code accepted")      
            message.text = message.text.replace(code, "")      
            await assistant.call_event(self.events.invitation_accepted, message.lead, message, connector, data=inv)
            
            return True
        return True
                
    # Handle invitations 
    def __gen_invite_code(self):
        # genereate a random code 6 alphanumeric characters, including uppercase and lowercase
        import random
        import string
        code = '#' + ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6))
        return code
    
    def __gen_barcode(self, url: str):
        import qrcode
        import io
        log.debug(f"Generating QR code for {url}")
        qr = qrcode.make(url)
        stream = io.BytesIO()
        qr.save(stream)
        qr_bytes = stream.getvalue()
        return qr_bytes
    
    def __gen_telegram_invitation_url(self, code: str):
        assert self.telegram_bot_name, "Telegram bot name must be provided"
        import base64
        #  the code must be up to 64 base64url characters
        input_bytes = code.encode('utf-8')
        base64url_bytes = base64.urlsafe_b64encode(input_bytes)
        code_encoded = base64url_bytes.decode('utf-8')        
        
        assert len(code_encoded) <= 64, "Code must be up to 64 base64url characters"
    
        url = f"https://t.me/{self.telegram_bot_name}?start={code_encoded}"
        return url        
        
    def __gen_whatsapp_invitation_url(self, code: str):
        assert self.whatsapp_phone_number, "WhatsApp phone number must be provided"
        url = f"https://wa.me/{self.whatsapp_phone_number}?text={code}"
        return url
    
    async def create_invitation(self, name: str = None, metadata: dict = None, expires_at: int = 0):
        code = self.__gen_invite_code()
        entry = InvitationEntry(invite_code=code, 
                                created_at=int(time.time()), 
                                expires_at=expires_at, 
                                metadata=metadata,
                                name=name)
        await self.client.hset(self.key_prefix, code, json.dumps(asdict(entry)))
        return entry
    
    async def get_invitation(self, code: str):
        entry = await self.client.hget(self.key_prefix, code)
        if entry:
            entry = json.loads(entry)
            return InvitationEntry(invite_code=entry.get('invite_code'), 
                                   created_at=entry.get('created_at'), 
                                   expires_at=entry.get('expires_at'),
                                   used=entry.get('used'), 
                                   metadata=entry.get('metadata'),
                                   name=entry.get('name'))
        return None
    
    async def claim_invitation(self, code: str):
        inv = await self.get_invitation(code)
        if inv:
            inv.used = True
            await self.client.hset(self.key_prefix, code, json.dumps(asdict(inv)))
            return inv
        return None
    
    async def revoke_invitation(self, code: str):
        await self.client.hdel(self.key_prefix, code)

    async def clear_invitations(self):
        log.warning(f"Clearing invitations from Redis, all keys with prefix {self.key_prefix} will be deleted")
        await self.client.delete(self.key_prefix)
        log.debug("Invitations cleared successfully")
    
    # Handle login/logout commands and secure client commands
    async def __handle_login_command(self, 
                                     message: Message, 
                                     connector: BaseConnector, 
                                     entry: AuthEntry,
                                     assistant: BaseAssistant):
        text = message.text or ''
        if text.startswith("/logout"):
            await self.clear_auth(message.lead.get_session_id())
            await connector.send_text_message(message.lead, "You have been logged out!")
            await assistant.call_event(self.events.admin_logout,  message.lead, message, connector)
            return False
        
        if text.startswith("/login"):
            parts = text.split(" ")
            if len(parts) == 2:
                if parts[1] == self.master_key:
                    await self.enable_client_commands(message.lead.get_session_id())
                    await assistant.call_event(self.events.admin_login,  message.lead, message, connector)
                    await connector.send_text_message(message.lead, "You have been logged in.")
                    await connector.send_text_message(message.lead, "Welcome AI bender!")
                    return False
                else:
                    log.critical(f"Invalid master key provided for login")
                    return False
            else:
                log.critical(f"Invalid login command format")
                return False
        return True
        
    async def __secure_client_commands(self, message: Message, connector: BaseConnector, entry: AuthEntry):
        text = message.text or ''
        if text.startswith("/") and not text.startswith("/login") and not text.startswith("/logout"):
            if not entry or not entry.client_cmd_enabled:
                log.critical(f"Client command {text} from {message.lead.get_session_id()} is not allowed")
                return False

        if text.startswith("/help"):
            await connector.send_text_message(message.lead, "Available commands:")
            await connector.send_text_message(message.lead, "/login <master_key> - Login as admin")
            await connector.send_text_message(message.lead, "/logout - Logout as admin")
            await connector.send_text_message(message.lead, "/help - Show help")
            await connector.send_text_message(message.lead, "/reset_auth - Reset session data")
            await connector.send_text_message(message.lead, "/reset_to_fabric - Reset session data and revoke all invitations")
            await connector.send_text_message(message.lead, "/invite <name> - Create an invitation")
            await connector.send_text_message(message.lead, "/authinfo - Show session data")
        
        if text.startswith("/reset_to_fabric"):
            # clear entry for this session
            await connector.send_text_message(message.lead, "Resetting session data")
            await self.clear_auth(message.lead.get_session_id())
            await connector.send_text_message(message.lead, "Revoking all invitations!")
            await self.clear_invitations()
            await connector.send_text_message(message.lead, "Now you are uninvited, logged out and all invitations are revoked")
            
        if text.startswith("/reset_auth"):
            # clear entry for this session
            await connector.send_text_message(message.lead, "Resetting session data")
            await self.clear_auth(message.lead.get_session_id())
            
        if text.startswith("/authinfo"):
            await connector.send_text_message(message.lead, f"Auth info: {entry}")
            await connector.send_text_message(message.lead, f"Session ID: {message.lead.get_session_id()}")
        
        if text.startswith("/invite"):
            parts = text.split(" ")
            if len(parts) == 2:
                invitation = await self.create_invitation(name=parts[1])
                source = message.lead.connector_name
                qr, url = await self.get_invitation_assets(message.lead, invitation)
                    
                if qr and url:
                    await connector.send_image_message(message.lead, qr, filename="qrcode.png")
                    await connector.send_text_message(message.lead, f"Invitation link: {url}")
                    await connector.send_text_message(message.lead, f"Code: {invitation.invite_code}")
                else: 
                    log.error(f"Invalid source {source} for invitation")
            else:
                await connector.send_text_message(message.lead, "Invalid invite command format")
            
            
        return True
    
    async def get_invitation_assets(self, lead: ConversationLead, invitation: InvitationEntry):
        qr = None
        url = None
        source = lead.connector_name
        
        if source == "telegram":
            url = self.__gen_telegram_invitation_url(invitation.invite_code)
            qr = self.__gen_barcode(url)
        
        if source == "whatsapp":
            url = self.__gen_whatsapp_invitation_url(invitation.invite_code)
            qr = self.__gen_barcode(url)
        
        return qr, url
    
    async def send_invitation_assets(self, lead: ConversationLead, invitation: InvitationEntry):
        qr, url = await self.get_invitation_assets(lead, invitation)
        connector = lead.connector
        await connector.send_image_message(lead, qr, filename="qrcode.png")
        await connector.send_text_message(lead, f"Invitation link: {url}")
        await connector.send_text_message(lead, f"Code: {invitation.invite_code}")


    # Auth Methods
    async def set_entry(self, 
                        session_id: str, 
                        client_cmd_enabled: bool = False, 
                        metadata: dict = None,
                        invite_code: str = None):
        
        entry = AuthEntry(session_id=session_id, 
                          client_cmd_enabled=client_cmd_enabled, 
                          metadata=metadata,
                          invite_code=invite_code,
                          last_request=time.time()
                        )
        await self.client.hset(self.key_prefix, session_id, json.dumps(asdict(entry)))
        return entry
        
    async def clear_auth(self, id: str):
        await self.client.hdel(self.key_prefix, id)
        
    async def get_auth_entry(self, id: str):
        entry = await self.client.hget(self.key_prefix, id)
        if entry:
            entry = json.loads(entry)
            return AuthEntry(session_id=entry.get('session_id'),
                            invite_code=entry.get('invite_code'),
                            client_cmd_enabled=entry.get('client_cmd_enabled'), 
                            last_request=entry.get('last_request'),
                            metadata=entry.get('metadata'))

        return None
    
    async def enable_client_commands(self, id: str):
        entry = await self.get_auth_entry(id)
        if entry:
            entry.client_cmd_enabled = True
            await self.client.hset(self.key_prefix, id, json.dumps(asdict(entry)))
            return entry
        return None