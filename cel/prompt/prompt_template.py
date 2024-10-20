
import asyncio
import inspect
import json
import re
from loguru import logger as log    
from typing import Callable, Dict, Optional
from cel.gateway.model.conversation_lead import ConversationLead



class PromptTemplate:
    """
    This class is used to compile a prompt template by replacing placeholders with values from the state.
    Placeholders are defined as {key} where key is a key in the state dictionary.
    The values in the state dictionary can be strings, integers, floats, lists, dictionaries, or functions that return
    any of the previous types.
    
    :param prompt: The prompt template with placeholders.
    :param initial_state: The initial state dictionary with values to replace placeholders. This state is static and
    will not be modified during the conversation. It will be used as a default value if the key is not found in the
    current stored state.
    """
    
    
    def __init__(self, prompt: str, initial_state: Optional[Dict] = {}):
        self.prompt = prompt
        self.initial_state = initial_state


    async def compile(self, state: Dict, lead: ConversationLead, message: str) -> str:
        """
        Compiles the prompt template by replacing placeholders with values from the state.
        
        :param state: The state dictionary with values to replace placeholders.
        :param lead: The ConversationLead instance.
        :param message: The message that triggered the prompt.
        :return: The compiled prompt as a string.
        """
        
        assert isinstance(state, dict), "PromptTemplate: state must be a dictionary"
        assert isinstance(lead, ConversationLead), "PromptTemplate: lead must be a ConversationLead instance"
        
        current_state = self.initial_state.copy()
        # merge initial state with state param
        current_state.update(state)
        
        async def compile_value(key):
            if key in current_state:
                value = current_state[key]
                try:
                    if callable(value):
                        return {key: await self.call_function(value, 
                                                              lead=lead, 
                                                              message=message,
                                                              current_state=state)}
                    return {key: str(value)}
                except Exception as e:
                    return {key: f"Error: {str(e)}"}
            return {key: ''}

        # Compile regex pattern outside the function if reused
        pattern = re.compile(r'\{(\w+)\}')
        tasks = [asyncio.create_task(compile_value(match)) for match in pattern.findall(self.prompt)]
        
        results = await asyncio.gather(*tasks)
        
        replacements = {key: value for result in results for key, value in result.items()}
        
        # Use a single pass to replace placeholders
        return pattern.sub(lambda m: replacements.get(m.group(1), ''), self.prompt)
            

    async def call_function(self, 
                            func: Callable, 
                            message: Optional[str] = None,
                            current_state: Optional[dict] = None,
                            lead: Optional[ConversationLead] = None) -> str:
        """
        Calls a provided function with dynamic arguments.

        :param func: The function to be called.
        :param message: Optional message to pass to the function.
        :param current_state: Optional current state to pass to the function.
        :param lead: Optional lead to pass to the function.
        :return: Function response as a JSON string if it's a dictionary or as a normal string.
        """
        
        if not lead:
            raise ValueError("PromptTemplate call_function: lead is required")
        
        if not isinstance(lead, ConversationLead):
            raise ValueError("PromptTemplate call_function: lead must be a ConversationLead instance")
        
        args_dict = {
            'lead': lead,
            'session_id': lead.get_session_id(),
            'message': message,
            'state': current_state
        }
        
        func_signature = inspect.signature(func)
        kwargs = {arg: args_dict[arg] for arg in func_signature.parameters if arg in args_dict}

        try:
            if inspect.iscoroutinefunction(func):
                response = await func(**kwargs)
            else:
                response = func(**kwargs)
        except Exception as e:
            # Log exception or handle it as needed
            response = f"Error occurred: {str(e)}"
            func_name = func.__name__ if hasattr(func, '__name__') else str(func)
            log.error(f"Error occurred while calling function {func_name}:  {str(e)}")
        
        return json.dumps(response) if isinstance(response, dict) else str(response)
