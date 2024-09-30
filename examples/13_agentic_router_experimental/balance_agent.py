
# Import Cel.ai modules
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.rag.providers.markdown_rag import MarkdownRAG
from cel.assistants.function_context import FunctionContext
from cel.assistants.function_response import RequestMode
from cel.assistants.common import Param
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider


def build_balance_agent(base_prompt: str = ''):
    
    # Setup prompt
    prompt = base_prompt + """You are a virtual assistant specializing in banking balance enquiries.
Your goal is to provide clients with accurate information about the balance of their bank accounts such as savings and checking accounts.
You answer questions like 'What is my current balance?' or 'How much money do I have in my savings account?'.
Today is {date}
"""
            
    prompt_template = PromptTemplate(prompt)

    ast = MacawAssistant(
        # For observability purposes, it is recommended to provide a name to the assistant
        name="Balance Agent",
        
        # This is the description of the assistant, it will be used by AssistantRouter 
        # to match the assistant with the user intent
        description="""You are a virtual assistant specializing in balance inquiries. 
Your goal is to provide clients with accurate information about the balance of 
their bank accounts such as savings and checking accounts.""",
            
        prompt=prompt_template,
    )
    
    # TODO: Add RAG here
    
    # TODO: Add Tooling here
    
    return ast