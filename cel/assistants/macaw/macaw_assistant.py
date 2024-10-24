import asyncio
import json
import warnings
from loguru import logger as log
from cel.assistants.base_assistant import BaseAssistant
from cel.assistants.macaw.macaw_history_adapter import MacawHistoryAdapter
from cel.assistants.macaw.macaw_inference_context import MacawNlpInferenceContext
from cel.assistants.macaw.macaw_nlp import MacawFunctionCall, blend_message, process_insights, process_new_message
from cel.assistants.macaw.macaw_settings import MacawSettings
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from cel.prompt.prompt_template import PromptTemplate
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider
from langchain.load.load import loads, load
from langchain.load.dump import dumps


class MacawAssistant(BaseAssistant):
    """Macaw Assistant is a conversational assistant that uses Langchain as core NLP.
    This assistant perform different NLP tasks like blending, insights, and more.
    To perform these tasks, Macaw Assistant uses differents models and tools. You can
    configure the assistant with different settings and tools for each task.
    
    If you use this assistant make sure to setup your LLM API key in the environment variable:
        - OPENAI_API_KEY: The OpenAI API key for the assistant.
    
    Tasks:
        - Blending: Blend a message with the current context.
        - Insights: Get insights from the current context.
        - Process new message: Process a new message with the current context and return the response.

    Args:
        state (dict, optional): Initial state for the assistant. Defaults to None.
        history_store (BaseHistoryProvider, optional): History store provider. Defaults to None.
        state_store (BaseChatStateProvider, optional): State store provider. Defaults to None.
        prompt (PromptTemplate, optional): Prompt template for the assistant. Defaults to None.
        insight_targets (dict, optional): Insight targets for the assistant. Defaults to {}.
        settings (MacawSettings, optional): Settings for the assistant. Defaults to None.

    """
    
    def __init__(self, 
                 state: dict = None,
                 history_store: BaseHistoryProvider = None, 
                 state_store: BaseChatStateProvider = None,
                 prompt: PromptTemplate = None,
                 insight_targets: dict = {},
                 settings: MacawSettings = None,
                 llm=None,
                 name: str = "Macaw",
                 description: str = "Default Assistant"
                ):
        
        super().__init__(prompt=prompt, 
                         history_store=history_store, 
                         state_store=state_store,
                         name=name,
                         description=description)
        
        if state is not None:
            log.warning("MacawAssistant: The 'state' parameter is deprecated and will be removed in a future version.")
        
        self.state = state or {}
        self.insight_targets = insight_targets
        if settings is None:
            log.warning("No settings provided for Macaw Assistant, using default settings")
        self.settings = settings or MacawSettings()
        self.llm = llm
        log.debug(f"Macaw Assistant initialized with settings: {self.settings}")
        

    async def new_message(self, message: Message, local_state: dict = {}):
        # create context
        ctx = MacawNlpInferenceContext(
            lead=message.lead,
            prompt=self.prompt,
            init_state=self.state,
            local_state=local_state,
            functions=self.get_functions(),
            history_store=self._history_store,
            state_store=self._state_store,
            settings=self.settings,
            rag_retriever=self.rag_retriever,
            llm=self.llm
        )
        
        async def on_function_call(ctx: MacawNlpInferenceContext, call: MacawFunctionCall):
            return await self.call_function(
                    func_name=call.name,
                    params=call.args,
                    lead=ctx.lead
                )
        try:
            # stream this message content from string
            async for chunk in process_new_message(ctx, message.text, on_function_call):
                yield chunk
    
        except Exception as e:
            # log.error(f"Macaw Assistant: error processing new message: {e}")
            log.exception(e)
            
        # execute coroutine to get insights in background dont wait for it
        if self.insight_targets:
            asyncio.create_task(self.do_insights(message.lead, history_length=self.settings.insights_history_window_length))
        
        

    async def blend(self, lead: ConversationLead, text: str, history_length: int = None):
        # create context
        ctx = MacawNlpInferenceContext(
            lead=lead,
            prompt=self.prompt,
            init_state=self.state,
            local_state={},
            history_store=self._history_store,
            state_store=self._state_store,
            settings=self.settings
        )
        
        
        return await blend_message(ctx, message=text)
    
    async def do_insights(self, lead: ConversationLead, targets: dict = {}, history_length: int = 10):
        try:
            assert isinstance(targets, dict), "targets must be a dictionary"
            
            if self.settings.insights_enabled is False:
                log.warning("Insights are disabled, returning None")
                return None
            
            log.debug(f"Getting insights for lead: {lead} with targets: {targets}")
            
            mix_targets = {**self.insight_targets, **targets}
            
            # create context
            ctx = MacawNlpInferenceContext(
                lead=lead,
                prompt=self.prompt,
                init_state=self.state,
                local_state={},
                history_store=self._history_store,
                state_store=self._state_store,
                settings=self.settings
            )
            
            insights = await process_insights(ctx, targets=mix_targets)
            
            # raise insight event
            await self.call_event("insights", lead, data=insights)
            return insights
        except Exception as e:
            log.error(f"Error getting insights: {e}")
            log.exception(e)
            return None
        
    
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
            state = await self._state_store.get_store(lead.get_session_id())
            if state is None:
                yield "Stored state: empty"
            else:
                yield "Stored state:"
                for k, v in state.items():
                    yield f"{k}: {v}"
                
            initial_state = self.prompt.initial_state
            if initial_state:
                yield "Initial state:"
                for k, v in initial_state.items():
                    yield f"{k}: {v}"
            else:
                yield "Initial state: empty"
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
        
            
            
    def to_json(self):
        return {
            "state": self.state,
            "insight_targets": self.insight_targets,
            "settings": self.settings,
            "prompt": self.prompt
        }