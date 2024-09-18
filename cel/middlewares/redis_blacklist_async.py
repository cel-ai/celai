from redis import asyncio as aioredis
import json
from dataclasses import asdict
import time
from loguru import logger as log
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from cel.middlewares.in_mem_blacklist import BlackListEntry

Redis = aioredis.Redis

class RedisBlackListAsyncMiddleware:
    """Middleware to block users based on a blacklist. The blacklist is stored in a Redis database."""

    def __init__(self, redis: str | Redis = None, key_prefix: str = "blacklist"):
        self.client = redis if isinstance(redis, Redis) else aioredis.from_url(redis or 'redis://localhost:6379/0')
        self.black_list_key = key_prefix

    async def __call__(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        assert isinstance(message, Message), "Message must be a Message object"
        
        id =  message.lead.get_session_id()
        source = message.lead.connector_name
        entry = await self.client.hget(self.black_list_key, id)
        if entry:
            entry = json.loads(entry)
            log.critical(f"User {id} from {source} is blacklisted. Reason: {entry['reason']}")
            return False
        else:
            return True

    async def add_to_black_list(self, id: str, reason: str = None, ttl: int = None):
        entry = BlackListEntry(reason=reason, date=int(time.time()))
        await self.client.hset(self.black_list_key, id, json.dumps(asdict(entry)))
        # set expiration
        if ttl:
            await self.client.expire(self.black_list_key, ttl)

    async def remove_from_black_list(self, id: str):
        await self.client.hdel(self.black_list_key, id)

    async def get_entry(self, id: str):
        entry = await self.client.hget(self.black_list_key, id)
        if entry:
            return json.loads(entry)
        return None
