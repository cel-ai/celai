import json
from typing import Any
from loguru import logger as log
from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.state.base_state_provider import BaseChatStateProvider
      

class AsyncStateManager:

    def __init__(self, 
                 lead: ConversationLead,
                 store: BaseChatStateProvider,
                 commit_on_error: bool = False
                ):
        """ StateManager is a context manager to manage the state of a conversation.
        
        :param lead: ConversationLead
        :param store: BaseChatStateProvider
        :param commit_on_error: if True, the state will be saved on error, default is False
        """
        
        if not isinstance(store, BaseChatStateProvider):
            raise ValueError("StateManager: store must be an instance of BaseChatStateProvider")
        if not isinstance(lead, ConversationLead):
            raise ValueError("StateManager: lead must be an instance of ConversationLead")
        
        self.store = store
        self.lead = lead
        self.state = {}
        self.commit_on_error = commit_on_error
        

    async def __aenter__(self):
        await self.load_state()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            log.error(f"StateManager: error on context execution {exc_type} {exc_value}")
            if self.commit_on_error:
                await self.save_state()
            # Return False to raise the exception
            return False
        else:
            await self.save_state()
            return True


    async def load_state(self):
        self.state = await self.store.get_store(self.lead.get_session_id()) or {}
        return self.state

    async def save_state(self):
        await self.store.set_store(self.lead.get_session_id(), self.state)
        
    def get(self, key, default=None):
        return self.state.get(key, default)
    
    def set(self, key, value):
        self.state[key] = value

    def __getitem__(self, key):
        return self.state.get(key)

    def __setitem__(self, key, value):
        self.state[key] = value




