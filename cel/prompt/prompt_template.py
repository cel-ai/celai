
import asyncio
import inspect
import json
import re
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message


class PromptTemplate:
    def __init__(self, prompt: str):
        self.prompt = prompt

    async def compile(self, state: dict, lead: ConversationLead):
        assert isinstance(state, dict), "PromptTemplate: state must be a dictionary"
        
        async def compile_value(key):
            var_name = key
            if var_name in state:
                value = state[var_name]
                if callable(value):
                    return { key: await self.call_function(value, lead=lead) }
                else:
                    return { key: str(value) }
            else:
                return { key: '' }

        pattern = re.compile(r'\{(\w+)\}')
        matches = re.findall(pattern, self.prompt)
        # Asumiendo que 'matches' es la lista de coincidencias
        tasks = [asyncio.ensure_future(compile_value(match)) for match in matches]
        await asyncio.gather(*tasks)

        prompt = self.prompt
        for task in tasks:
            # replace the key with the value in the prompt
            key, value = task.result().popitem()
            prompt = prompt.replace(f"{{{key}}}", value)
        return prompt
            

    async def call_function(self, 
                            func: callable, 
                            message: Message = None,
                            lead: ConversationLead = None) -> str:
        
        args_dict = {
            'lead': lead,
            'session_id': lead.get_session_id(),
            'message': message
        }

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

        return json.dumps(response)