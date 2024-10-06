import inspect
import json
from loguru import logger as log

from langchain.load.load import load
from langchain.load.dump import dumps

from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider
from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
from cel.stores.state.state_inmemory_provider import InMemoryStateProvider
from cel.assistants.macaw.macaw_history_adapter import MacawHistoryAdapter


class LogicRouter(BaseAssistant):

        
    def __init__(self, 
                 assistants: list[BaseAssistant], 
                 assistant_selector_func: callable,
                 history_store: BaseHistoryProvider = None,
                 state_store: BaseChatStateProvider = None
                ):
        
        
        super().__init__(name="Logic Router Assistant", description="This assistant routes the user to the most suitable assistant based on a logic function")
        log.debug(f"Logic Router Assistant created with {len(assistants)} assistants")
        assert len(assistants) > 0, "At least one assistant is required"
        assert callable(assistant_selector_func), "Assistant selector function must be a callable"
        
        # List of assistants
        self._assistants = assistants
        self._assistant_selector_func = assistant_selector_func
        
        # Init state and history store
        self._state_store = state_store or InMemoryStateProvider()
        self._history_store = history_store or InMemoryHistoryProvider()      
        
        # Make sure than all assistants share the same state and history store
        for ast in self._assistants:
            log.debug(f"Assistant Name: {ast.name} -> {ast.description}")
            
            if ast._state_store != self._state_store:
                # TODO: evaluate if this is the correct behavior
                # If the assistant has a different state store, overwrite it???
                log.critical(f"Assistant {ast.name} has different state store")
                ast.set_state_store(self._state_store)
                
            if ast._history_store != self._history_store:
                # If the assistant has a different history store, overwrite it
                # is important to keep the history store consistent
                # History consistency is important for the router to work properly
                log.warning(f"Assistant {ast.name} has different history store")
                ast.set_history_store(self._history_store)
                log.warning(f"Assistant {ast.name} history store overwritten!!")
            
            
    async def __call_function(self, 
                              lead: ConversationLead = None,
                              message: str = None) -> BaseAssistant:
        
        # Get the current state for this lead
        current_state = await self._state_store.get_store(lead.get_session_id()) or {}
        
        args_dict = {
            'lead': lead,
            'session_id': lead.get_session_id(),
            'message': message,
            'state': current_state,
            'assistants': self._assistants
        }

        func = self._assistant_selector_func

        args = inspect.getfullargspec(func).args
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

        assert isinstance(response, BaseAssistant), "Assistant selector function must return a BaseAssistant instance"
        return response

            
            
    async def get_assistant(self, lead: ConversationLead, message: str):
        return await self.__call_function(lead, message)
        

    async def new_message(self, message: Message, local_state: dict = {}):
        log.debug(f"Router Assistant: new message: {message}")
        lead = message.lead
        # Get the assistant
        ast = await self.get_assistant(lead, message)
        assert isinstance(ast, BaseAssistant), "Agent must be a BaseAssistant instance"
        log.debug(f"Router Assistant selected: {ast.name}")
        
        # Call 'message' event in the selected assistant
        await ast.call_event("message", lead, message)
    
        # Call the assistant new_message method
        async for chunk in ast.new_message(message, local_state):
            yield chunk
        
       
    async def blend(self, lead: ConversationLead, text: str, history_length: int = None):
        log.debug(f"Router Assistant: blend: {text}")
        ast = await self.get_assistant(lead, text)
        
        return await ast.blend(lead, text, history_length)

    
    async def do_insights(self, lead: ConversationLead, targets: dict = {}, history_length: int = 10):
        log.warning("Router Assistant: do insights not implemented")
        return {}
    

    async def append_message_to_history(self, lead: ConversationLead, message: str, role: str = "assistant"):
        assert role in ["assistant", "user", "system"], "role must be one of: assistant, user, system"

        history = MacawHistoryAdapter(self._history_store)
        
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        entry = None
        if role == "assistant":
            entry = AIMessage(message)
        elif role == "user":
            entry = HumanMessage(message)
        elif role == "system":
            entry = SystemMessage(message)
            
        await history.append_to_history(lead, entry)
        
        
    async def process_client_command(self, lead: ConversationLead, command: str, args: list[str]):
    
        if command == "reset":
            
            if args and args[0] == "all":
                await self._history_store.clear_history(lead.get_session_id())
                yield "History cleared"
                await self._state_store.set_store(lead.get_session_id(), {})
                yield "State cleared"
                return

            await self._history_store.clear_history(lead.get_session_id())
            yield "History cleared"
            return
        
        if command == "state":
            state = self._state_store.get_store(lead.get_session_id())
            if state is None:
                yield "No state found"
                return
            for k, v in state.items():
                yield f"{k}: {v}"
            return
        
        if command == "history":
            history = await self._history_store.get_history(lead.get_session_id()) or []    

            if history is None or len(history) == 0:
                yield "History is empty"
                return

            for h in history:
                aux = load(h)
                log.debug(f"History: {aux}")
                yield dumps(aux)
            
            return
        
        if command == "set":
            if len(args) < 2:
                yield "Not enough arguments"
                return
            key = args[0]
            value = args[1]
            state = self._state_store.get_store(lead.get_session_id())
            state[key] = value
            self._state_store.set_store(lead.get_session_id(), state)
            yield f"State updated: {key}: {value}"
            return
        
        if command == "prompt":
            yield "Macaw Assistant v0.1"

            if args and args[0] == "all":            
                prompt = self.prompt
                # split into 250 chars aprox chunks
                for i in range(0, len(prompt), 250):
                    yield prompt[i:i+250]
                return
            
            # first 250 chars
            yield self.prompt[:250]
            return

            
            