from abc import ABC, abstractmethod
import inspect

from loguru import logger as log
from cel.assistants.function_response import FunctionResponse
from cel.gateway.model.base_connector import BaseConnector
from cel.assistants.common import EventResponse, FunctionDefinition
from cel.gateway.model.message import Message, ConversationLead
from cel.prompt.prompt_template import PromptTemplate
from cel.rag.providers.rag_retriever import RAGRetriever
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider
from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
from cel.stores.state.state_inmemory_provider import InMemoryStateProvider


class Events:
    START: str = "start"
    MESSAGE: str = "message"
    IMAGE: str = "image"
    AUDIO: str = "audio"
    END: str = "end"

class BaseAssistant(ABC):
    
    def __init__(self, 
                 name: str = None,
                 description: str = None,
                 prompt: PromptTemplate = None,
                 history_store: BaseHistoryProvider = None,
                 state_store: BaseChatStateProvider = None,
                ):
        self.name = name
        self.description = description
        self.function_handlers = {}
        self.event_handlers = {}
        self.client_commands_handlers = {}
        self.timeout_handlers = {}
        self._state_store = state_store or InMemoryStateProvider()
        self._history_store = history_store or InMemoryHistoryProvider()
        
        self.rag_retriever: RAGRetriever = None
        if prompt:
            assert isinstance(prompt, PromptTemplate), "prompt must be an instance of PromptTemplate"
        self.prompt = prompt or PromptTemplate('')

    def set_history_store(self, history_store: BaseHistoryProvider):
        # check type
        assert isinstance(history_store, BaseHistoryProvider), "history_store must be an instance of BaseHistoryProvider"
        self._history_store = history_store
        
    def set_state_store(self, state_store: BaseChatStateProvider):
        # check type
        assert isinstance(state_store, BaseChatStateProvider), "state_store must be an instance of BaseChatStateProvider"
        self._state_store = state_store
            
    def set_rag_retrieval(self, rag_retrieval: RAGRetriever):
        # check type
        assert isinstance(rag_retrieval, RAGRetriever), "rag_retrieval must be an instance of RAGRetriever"
        self.rag_retriever = rag_retrieval
        

    def function(self, name, desc, params):
        def decorator(func):
            self.function_handlers[name] = {
                # 'desc': desc,
                # 'params': params,
                'definition': FunctionDefinition(name=name, description=desc, parameters=params),
                'func': func
            }
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)          
                
            return wrapper
        return decorator    
        
        
    def event(self, name: Events | str):
        def decorator(func):
            self.event_handlers[name] = {
                'func': func
            }
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)          
                
            return wrapper
        return decorator
    
    
    def client_command(self, name):
        def decorator(func):
            self.client_commands_handlers[name] = {
                'func': func
            }
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)          
                
            return wrapper
        return decorator
    
    def timeout(self, label):
        def decorator(func):
            self.timeout_handlers[label] = {
                'func': func
            }
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)          
                
            return wrapper
        return decorator
    
    async def eval_client_command(self, command: str, args: list[str], message: Message):
        """Evaluate the client command and call the respective handler"""
        lead = message.lead
        connector = lead.connector
        
        if command in self.client_commands_handlers:
            func = self.client_commands_handlers[command]['func']
            # Build args_dict
            from cel.assistants.request_context import RequestContext
            ctx = RequestContext(lead=lead, 
                                 connector=connector,
                                 assistant=self)
            args_dict = {
                'session': lead.get_session_id(),
                'ctx': ctx,
                'lead': lead,
                'message': None,
                'connector': connector,
                'command': command,
                'args': args
            }
            
            # Build kwargs using args and args_dict
            args = inspect.getfullargspec(func).args
            kwargs = {}
            for arg in args:
                if arg in args_dict:
                    kwargs[arg] = args_dict[arg]

            # Check if the function is a coroutine (async function)
            if inspect.iscoroutinefunction(func):
                await func(**kwargs)
            else:
                func(**kwargs)      
            return False
        else:
            log.warning(f"Client command {command} not found in assistant implementation")
            return True
    
    async def call_event(self, event_name: str, lead: ConversationLead, message: Message = None, connector: BaseConnector = None, data: dict= None) -> EventResponse:
        """Call the respective event handler, if exists"""
        if event_name in self.event_handlers:
            func = self.event_handlers[event_name]['func']
            connector = connector or lead.connector
            from cel.assistants.request_context import RequestContext
            ctx = RequestContext(lead=lead, 
                                 message=message,
                                 assistant=self,
                                 state=self._state_store,
                                 history=self._history_store,
                                 connector=connector)
            
            # Build args_dict
            args_dict = {
                'session': lead.get_session_id(),
                'ctx': ctx,
                'lead': lead,
                'message': message,
                'connector': connector,
                'data': data,
                'state': self._state_store,
                'history': self._history_store
            }
            
            # Build kwargs using args and args_dict
            args = inspect.getfullargspec(func).args
            kwargs = {}
            for arg in args:
                if arg in args_dict:
                    kwargs[arg] = args_dict[arg]

            # Check if the function is a coroutine (async function)
            response = None
            if inspect.iscoroutinefunction(func):
                response = await func(**kwargs)
            else:
                response = func(**kwargs)    
                
            assert isinstance(response, EventResponse) or response is None, "Event handler must return an instance of EventResponse or None"
            return response
        else:
            # raise ValueError(f"Event {event_name} not found")
            log.error(f"Event {event_name} not found")
        
    
    async def call_function(self, func_name: str, params: dict, lead: ConversationLead) -> FunctionResponse:
        """Call the respective function handler, if exists. Map function arguments to the function handler signature"""
        from cel.assistants.function_context import FunctionContext
        connector = lead.connector
        if func_name in self.function_handlers:
            func = self.function_handlers[func_name]['func']
            args = inspect.getfullargspec(func).args

            ctx = FunctionContext(lead=lead, 
                                  connector=connector, 
                                  state=self._state_store, 
                                  history=self._history_store)
            
            args_dict = {
                'session': lead.get_session_id(),
                'ctx': ctx,
                'params': params,
                'lead': lead,
                'message': None,
                'connector': connector,
                'state': self._state_store,
                'history': self._history_store                
            }

            # Build kwargs using args and args_dict
            kwargs = {}
            for arg in args:
                if arg in args_dict:
                    kwargs[arg] = args_dict[arg]

            # Check if the function is a coroutine (async function)
            response = None
            if inspect.iscoroutinefunction(func):
                response = await func(**kwargs)
            else:
                response = func(**kwargs)
                
            assert isinstance(response, FunctionResponse) or response is None, "Function handler must return an instance of CommandResponse or None"
            return response
        
        else:
            raise ValueError(f"Function {func_name} not found")
            
    @abstractmethod
    async def new_message(self, message: Message, local_state: dict = {}):
        raise NotImplementedError
    
    
    @abstractmethod
    async def blend(self, lead: ConversationLead, text: str, history_length: int = 3):
        raise NotImplementedError
    
    @abstractmethod
    async def process_client_command(self, lead: ConversationLead, command: str, args: list[str]):
        yield "Command not found"
        
    @abstractmethod
    async def append_message_to_history(self, lead: ConversationLead, message: str, role: str = "assistant"):
        raise NotImplementedError
    
    def get_functions(self) -> list[FunctionDefinition]:
       return [f['definition'] for f in self.function_handlers.values()] 

    def get_events(self):
        return self.event_handlers
    
    # str method
    def __str__(self):
        return f"{self.name}: {self.description}"
    
    # json dumps method
    def to_json(self):
        return {
            'name': self.name,
            'description': self.description
        }
