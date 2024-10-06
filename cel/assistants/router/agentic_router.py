import json
from loguru import logger as log

from langchain.load.load import load
from langchain.load.dump import dumps
from langchain_core.prompts import PromptTemplate as LangchainPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable

from cel.assistants.base_assistant import BaseAssistant
from cel.assistants.router.utils import build_router_query
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider
from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
from cel.stores.state.state_inmemory_provider import InMemoryStateProvider
from cel.assistants.macaw.macaw_history_adapter import MacawHistoryAdapter


class AgenticRouter(BaseAssistant):
    """
    The AgenticRouter class provides multi-assistant support for Cel.ai by routing incoming 
    messages to the most suitable assistant based on user intent. 
    It leverages a GPT-4o-based agentic router to determine the best assistant for handling 
    the user's request. To accurately detect user intent, the router considers a window 
    of messages from the history to provide context.

    If the router cannot correctly determine the user's intent, such as in the case 
    of the first message, it defaults to routing the message to the default assistant.

    It is important to note that this multi-assistant architecture uses shared history 
    and state storages to avoid inconsistencies and potential issues.

    Attributes:
        assistants (list[BaseAssistant]): A list of assistant instances to route messages to.
        history_store (BaseHistoryProvider): The provider for storing message history. Defaults to InMemoryHistoryProvider if not provided.
        state_store (BaseChatStateProvider): The provider for storing chat state. Defaults to InMemoryStateProvider if not provided.
        history_length (int): The number of historical messages to consider for context. Defaults to 5.
        llm: The language model used for intent detection. Defaults to None.
        default_assistant (int): The index of the default assistant to use when intent cannot be determined. Defaults to 0.
        
    Example:
    ```python
        # Create a list of assistants
        assistants = [build_balance_agent(), build_transfer_agent()]
        # Instantiate the Agentic Router
        ast = AgenticRouter(assistants=assistants) 
    ```

    Methods:
        infer_best_assistant(input_text: str) -> BaseAssistant:
            Determines the best assistant to handle the user's request based on the input text.

        build_dialog(lead: ConversationLead, text: str) -> list[dict]:
            Builds a dialog to be used by the agent to get the most suitable assistant to process the message.

        format_dialog_to_plain_text(dialog: list[dict]) -> str:
            Formats the dialog into plain text.

        get_assistant(lead: ConversationLead, text: str) -> BaseAssistant:
            Gets the assistant that best fits the input text.

        new_message(lead: ConversationLead, message: str, local_state: dict = {}) -> AsyncGenerator:
            Handles a new message by routing it to the appropriate assistant and yielding the response.
    """
        
    def __init__(self, 
                 assistants: list[BaseAssistant], 
                 history_store: BaseHistoryProvider = None,
                 state_store: BaseChatStateProvider = None,
                 history_length: int = 5,
                 llm=None,
                 default_assistant: int = 0):
        """
        Initializes the AgenticRouter instance.

        Args:
            assistants (list[BaseAssistant]): A list of assistant instances to route messages to.
            history_store (BaseHistoryProvider, optional): The provider for storing message history. Defaults to InMemoryHistoryProvider if not provided.
            state_store (BaseChatStateProvider, optional): The provider for storing chat state. Defaults to InMemoryStateProvider if not provided.
            history_length (int, optional): The number of historical messages to consider for context. Defaults to 5.
            llm (optional): The LLM model used for intent detection. Defaults to None.
            default_assistant (int, optional): The index of the default assistant to use when intent cannot be determined. Defaults to 0.

        Raises:
            AssertionError: If no assistants are provided or if the default assistant index is out of range.
        """
        
        
        super().__init__(name="Router Assistant", description="This assistant routes messages to other assistants")
        log.debug(f"Router Assistant created with {len(assistants)} assistants")
        assert len(assistants) > 0, "At least one assistant is required"
        assert default_assistant < len(assistants), "Default assistant index out of range"
        
        
        # List of assistants
        self._assistants = assistants
        self._current_assistant = self._assistants[default_assistant]
        self._hisory_length = history_length
        self._llm = llm
        
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
            
            
        log.debug(f"Default Assistant: {self._current_assistant.name}")
    

    @traceable
    async def infer_best_assistant(self, input_text: str) -> BaseAssistant:
        """ Get the agent that best fits the input text """
        
        llm = self._llm or ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=100)
        prompt_str = """From the following dialog, detect the user's intention, then return the most suitable assistant to handle the user's request: 
{input_text}

Available assistants:
Default Agent
{asts}

If you are not sure, please select the default agent.
Returns only the name of the assistant."""

        asts = "\n".join([f"{agent.name}" for i, agent in enumerate(self._assistants)])
        
        prompt = LangchainPromptTemplate.from_template(prompt_str)
        
        # invoke
        res = llm.invoke(prompt.format(input_text=input_text, asts=asts))
        ast_name = res.content
        
        if ast_name == "Default Agent":
            log.warning(f"AgenticRouter could not determine the assistant, using default assistant: {self._current_assistant.name}")
            return self._current_assistant
        
        # find the agent
        for i, agent in enumerate(self._assistants):
            if agent.name == ast_name:
                return agent
        
        raise ValueError(f"Agent {ast_name} not found")

    
    
    async def build_dialog(self, lead: ConversationLead, text: str):
        """ Build a dialog to be used by the agent to get the most suitable assistant to process the message """
        query = await build_router_query(self._history_store, lead, text, length=self._hisory_length)
        query.append({
            "role": "user",
            "text": text
        })
        return query
    
    async def format_dialog_to_plain_text(self, dialog: list[dict]):
        """ Format the dialog to plain text """
        return "\n".join([f"{d['role']}: {d['text']}" for d in dialog])
        
        
    async def get_assistant(self, lead: ConversationLead, text: str):
        """ Get the assistant that best fits the input text """
        dialog = await self.build_dialog(lead, text)
        plain_dialog = await self.format_dialog_to_plain_text(dialog)
        return await self.infer_best_assistant(plain_dialog)

    async def new_message(self, message: Message, local_state: dict = {}):
        log.debug(f"Router Assistant: new message: {message}")
        lead = message.lead
        ast = await self.get_assistant(lead, message.text)
        
        # Call 'message' event in the selected assistant
        await ast.call_event("message", lead, message)
        
        assert isinstance(ast, BaseAssistant), "Agent must be a BaseAssistant instance"
        log.debug(f"Router Assistant selected: {ast.name}")
        # return 
    
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

            
            