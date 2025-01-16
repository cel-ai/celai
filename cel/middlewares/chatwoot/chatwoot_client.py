import aiohttp
from loguru import logger as log
from typing import Optional, Dict
from loguru import logger as log    
from typing import Any, Dict, Optional


class ChatwootClient:

    def __init__(self,
                 base_url: str,
                 account_id: str,
                 access_key: str,
                 headers: Optional[Dict[str, str]] = None,
                 ssl: bool = False):
        self.base_url = base_url
        self.account_id = account_id
        self.access_key = access_key
        self.headers = headers or {}
        self.headers.update({
            'api_access_token': access_key
        })
        self.ssl = ssl

    async def list_agent_bots(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/agent_bots"
        log.debug(f"Listing agent bots from Chatwoot url: {url}")

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.get(url, headers=self.headers) as response:
                response_data = await response.json()
                return response_data


    async def create_contact(self,
                                inbox_id: int,
                                name: Optional[str] = None,
                                email: Optional[str] = None,
                                phone_number: Optional[str] = None,
                                avatar: Optional[str] = None,
                                avatar_url: Optional[str] = None,
                                identifier: Optional[str] = None,
                                custom_attributes: Optional[Dict[str, str]] = None
                            ) -> Dict[str, Any]:

        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts"
        log.debug(f"Creating contact at Chatwoot url: {url}")

        payload = {
            'inbox_id': inbox_id,
            'name': name,
            'email': email,
            'phone_number': phone_number,
            'avatar': avatar,
            'avatar_url': avatar_url,
            'identifier': identifier,
            'custom_attributes': custom_attributes
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                response_data = await response.json()
                return response_data

    # GET https://app.chatwoot.com/api/v1/accounts/{account_id}/contacts/search?q=identifier:1234567890            
    async def search_contact(self, query: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts/search"
        log.debug(f"Searching contact at Chatwoot url: {url}")
        url = f"{url}?q={query}"

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.get(url, headers=self.headers) as response:
                response_data = await response.json()
                return response_data



    async def create_new_conversation(self,
                                        source_id: str,
                                        inbox_id: int,
                                        contact_id: int,
                                        additional_attributes: Optional[Dict[str, str]] = None,
                                        custom_attributes: Optional[Dict[str, str]] = None,
                                        status: Optional[str] = "open",
                                        assignee_id: Optional[str] = None,
                                        team_id: Optional[str] = None,
                                        message: Optional[Dict[str, str]] = None
                                    ) -> Dict[str, Any]:

        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations"
        log.debug(f"Creating conversation at Chatwoot url: {url}")

        payload = {
            'source_id': source_id,
            'inbox_id': inbox_id,
            'contact_id': contact_id,
            'additional_attributes': additional_attributes,
            'custom_attributes': custom_attributes,
            'status': status,
            'assignee_id': assignee_id,
            'team_id': team_id,
            'message': message
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                response_data = await response.json()
                return response_data

    async def create_message(self,
                                account_id: int,
                                conversation_id: int,
                                content: str,
                                message_type: Optional[str] = "outgoing",
                                private: Optional[bool] = False,
                                content_type: Optional[str] = "text",
                                content_attributes: Optional[Dict[str, str]] = None,
                                template_params: Optional[Dict[str, str]] = None
                            ) -> Dict[str, Any]:
        """ Create a new message in Chatwoot 

            content_type: "text", "input_email", "cards", "input_select", "form", "article"
        """
        # https://app.chatwoot.com/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages
        url = f"{self.base_url}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages"
        log.debug(f"Creating message at Chatwoot url: {url}")

        payload = {
            'content': content,
            'message_type': message_type,
            'private': private,
            'content_type': content_type,
            'content_attributes': content_attributes,
            'template_params': template_params
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                response_data = await response.json()
                return response_data

    async def get_inbox(self, account_id: int, inbox_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{account_id}/inboxes/{inbox_id}"
        log.debug(f"Getting inbox from Chatwoot url: {url}")

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.get(url, headers=self.headers) as response:
                response_data = await response.json()
                return response_data

    async def get_inboxes(self, account_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{account_id}/inboxes"
        log.debug(f"Getting inboxes from Chatwoot url: {url}")

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.get(url, headers=self.headers) as response:
                response_data = await response.json()
                return response_data

    async def get_inbox_by_name(self, account_id: int, name: str) -> Dict[str, Any]:
        payload = await self.get_inboxes(account_id)
        inboxes = payload.get("payload", {})
        for inbox in inboxes:
            if inbox.get("name") == name:
                return inbox

        return None

    async def create_api_inbox(self, account_id: int, name: str, webhook_url: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{account_id}/inboxes"
        log.debug(f"Creating inbox at Chatwoot url: {url}")

        payload = {
            'name': name,
            'channel': {
                'type': 'api',
                'webhook_url': webhook_url
            }
        }

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                response_data = await response.json()
                return response_data


    async def update_api_inbox(self, account_id: int, inbox_id: int, webhook_url: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{account_id}/inboxes/{inbox_id}"
        log.debug(f"Updating inbox at Chatwoot url: {url}")

        payload = {
            'enable_auto_assignment': False,
            'channel': {
                'webhook_url': webhook_url
            }
        }

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl)) as session:
            async with session.put(url, json=payload, headers=self.headers) as response:
                response_data = await response.json()
                return response_data