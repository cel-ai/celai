from cel.middlewares.chatwoot.chatwoot_client import ChatwootClient
from cel.middlewares.chatwoot.model import ChatwootConversationRef, ContactLead, InboxRef
from cel.middlewares.chatwoot.phone_util import format_to_e164
from loguru import logger as log
import time
from typing import Any, Dict, Optional




class ConversationManager:

    def __init__(self,
                 base_url: str,
                 access_key: str,
                 webhook_url: str,
                 account_id: str,
                 inbox_name: str):
        self.base_url = base_url
        self.access_key = access_key
        self.inbox_name = inbox_name
        self.account_id = account_id
        self.webhook_url = webhook_url
        self.client = ChatwootClient(base_url, account_id, access_key)
        self.inbox = None
        self.conversations = {}

    def __set_inbox(self, inbox):
        self.inbox = InboxRef(
            id=inbox.get("id"),
            name=inbox.get("name")
        )
        log.debug(f"Chawoot Inbox: {self.inbox}")


    async def init(self, auto_create_inbox: bool = True):
        """ Initialize the ConversationManager 
            auto_create_inbox: If True, create the inbox if not found.
        """
        log.debug(f"Initializing Chatwoot ConversationManager: {self.base_url}, account_id: {self.account_id}, inbox_name: {self.inbox_name}")
        # 1. Get inbox by name
        # 2. If not found, create inbox
        inbox = await self.client.get_inbox_by_name(self.account_id, self.inbox_name)
        
        # check if webhook url needs to be updated
        if inbox and inbox.get("webhook_url") != self.webhook_url:
            log.warning(f"Updating webhook url for inbox: {self.inbox_name} in Chatwoot: {self.base_url}")
            inbox = await self.client.update_api_inbox(self.account_id, inbox.get("id"), self.webhook_url)
            log.warning(f"Webhook url updated for inbox: {self.inbox_name} in Chatwoot: {self.base_url}")

        if not inbox and not auto_create_inbox:
            raise Exception(f"Inbox {self.inbox_name} not found in Chatwoot: {self.base_url}")

        if not inbox:
            log.warning(f"Inbox {self.inbox_name} not found in Chatwoot: {self.base_url}")
            inbox = await self.client.create_api_inbox(self.account_id, self.inbox_name, self.webhook_url)
            if not inbox:
                raise Exception(f"Failed to create inbox {self.inbox_name} in Chatwoot: {self.base_url}")

        self.__set_inbox(inbox)



    async def get_conversation(self, identifier: str) -> Optional[ChatwootConversationRef]:
        """ Get a conversation by Contact identifier 
            Conversations are stored in memory for faster access.
            Index by identifier
        """
        return self.conversations.get(identifier)

    async def create_new_conversation(self, contact_id: int, source_id: int, first_message: str = None) -> Optional[ChatwootConversationRef]:
        inbox_id = self.inbox.id
        conversation = await self.client.create_new_conversation(
            source_id=source_id,
            inbox_id=inbox_id,
            contact_id=contact_id,
            message={
                "content": first_message
            } if first_message else None
        )
        return conversation

    async def touch_contact(self, contact_ref: ContactLead) -> Optional[Dict[str, Any]]:
        """ Touch a contact by identifier 
            If not found, create a new contact.
        """
        phone = format_to_e164(contact_ref.phone_number)
        res = await self.client.search_contact(phone)
        contacts = res.get("payload", [])

        if len(contacts) > 1:
            log.critical(f"Multiple contacts found for phone: {phone} count: {len(contacts)}")
            # raise Exception(f"Multiple contacts found for identifier: {contact_ref.identifier}")
            

        contact = contacts[0] if contacts else None


        if not contact:
            log.debug(f"Contact with {phone} not found. Creating...")
            res = await self.client.create_contact(
                inbox_id=self.inbox.id,
                name=contact_ref.name,
                email=contact_ref.email,
                phone_number=phone,
                identifier=contact_ref.identifier
            )
            contact = res.get('payload', {}).get('contact')

            if not contact:
                raise Exception(f"Failed to create contact: {contact_ref} in Chatwoot: {self.base_url}. Message: {res.get('message')}")

        return contact

    async def touch_conversation(self, contact_ref: ContactLead) -> Optional[ChatwootConversationRef]:
        """ Touch a conversation by Contact identifier 
            If not found, create a new conversation.
        """

        conversation = await self.get_conversation(contact_ref.identifier)
        if not conversation:
            # Get or create contact
            contact = await self.touch_contact(contact_ref)

            cto_inboxes = contact.get("contact_inboxes", [])
            # Get source_id from contact_inboxe where inbox_id == self.inbox.id
            source_id = None
            for cto_inbox in cto_inboxes:
                if cto_inbox.get("inbox", {}).get("id") == self.inbox.id:
                    source_id = cto_inbox.get("source_id")
                    break

            if not source_id:
                raise Exception(f"Source ID not found for inbox: {self.inbox.id}")

            conversation = await self.create_new_conversation(contact_id=contact.get("id"), source_id=source_id)

            if not conversation:
                raise Exception(f"Failed to create conversation for contact: {contact} in Chatwoot: {self.base_url}")

            log.debug(f"Conversation created: {conversation}")
            self.conversations[contact_ref.identifier] = ChatwootConversationRef(
                id=conversation.get("id"),
                identifier=contact_ref.identifier,
                # current time posix
                updated_at=int(time.time())
            )
            log.debug(f"Conversation touched: {self.conversations[contact_ref.identifier]}")
            return self.conversations[contact_ref.identifier]

        return conversation

    async def send_outgoing_text_message(self, contact_ref: ContactLead, message: str, private: bool = False) -> Optional[Dict[str, Any]]:
        """ Send an outgoing message to a contact 
            If contact not found, create a new contact.
        """
        try:
            conversation = await self.touch_conversation(contact_ref)
            conversation_id = conversation.id
            return await self.client.create_message(
                account_id=self.account_id,
                conversation_id=conversation_id,
                content=message,
                private=private,
                content_type="text",
                message_type="outgoing"
            )
        except Exception as e:
            log.error(f"Middleware Chatwoot: Error sending outgoing message: {e}")
            return None

    async def send_incoming_text_message(self, contact_ref: ContactLead, message: str, private: bool = False) -> Optional[Dict[str, Any]]:
        """ Send an incoming message to a contact 
            If contact not found, create a new contact.
        """
        
        try:
            conversation = await self.touch_conversation(contact_ref)
            conversation_id = conversation.id
            return await self.client.create_message(
                account_id=self.account_id,
                conversation_id=conversation_id,
                content=message,
                private=private,
                content_type="text",
                message_type="incoming"
            )
        except Exception as e:
            log.error(f"Middleware Chatwoot: Error sending incoming message: {e}")
            return None
