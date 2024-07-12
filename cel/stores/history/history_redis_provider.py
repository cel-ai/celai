# DEPERECATED SYNC VERSION

# import json
# from redis import Redis
# from loguru import logger as log
# from prompter.stores.history.base_history_provider import BaseHistoryProvider


# class RedisHistoryProvider(BaseHistoryProvider):

#     def __init__(self, redis: str | Redis, key_prefix: str = "h"):
#         self.client = redis if isinstance(redis, Redis) else Redis.from_url(redis)
#         self.key_prefix = key_prefix
#         log.debug(f"Create: RedisHistoryProvider")

#     def get_key(self, sessionId: str):
#         return f"{self.key_prefix}:{sessionId}"

#     def append_to_history(self, sessionId: str, entry, metadata=None, ttl=None):
#         key = self.get_key(sessionId)
#         value = json.dumps(entry)
#         self.client.rpush(key, value)

#         # set expiration to 24 hours
#         self.client.expire(key, ttl if ttl else 86400)

#     def get_history(self, sessionId: str):
#         key = self.get_key(sessionId)
#         values = self.client.lrange(key, 0, -1)
#         res = [json.loads(v) for v in values]
#         # remove None elements
#         res = [r for r in res if r]

#         return res
        

#     def clear_history(self, sessionId: str, keep_last_messages=None):
#         key = self.get_key(sessionId)
#         if keep_last_messages:
#             self.client.ltrim(key, 0, keep_last_messages)
#         else:
#             self.client.delete(key)

#     def get_history_slice(self, sessionId: str, start, end):
#         key = self.get_key(sessionId)
#         history = self.client.lrange(key, start, end)
#         return [json.loads(h) for h in history]

#     def get_last_messages(self, sessionId: str, count):
#         key = self.get_key(sessionId)
#         history = self.client.lrange(key, -count, -1)
#         return [json.loads(h) for h in history]

#     def close_conversation(self, sessionId: str):
#         raise NotImplementedError("Method not implemented.")
    

