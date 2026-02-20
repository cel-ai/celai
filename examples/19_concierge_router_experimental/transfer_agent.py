
# Import Cel.ai modules
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.rag.providers.markdown_rag import MarkdownRAG
from cel.assistants.function_context import FunctionContext
from cel.assistants.function_response import RequestMode
from cel.assistants.common import Param
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider


def build_transfer_agent(base_prompt: str = ''):
    # For matching and observability purposes, its required to provide a name to the assistant
    name = "Transfer Agent"

    # This is the description of the assistant, it will be used only in semantic routers
    # Use name for AgenticRouter
    description="""You are a virtual assistant specializing in bank transfers.
Your goal is to help customers transfer money between their accounts or to third-party accounts.""",

    # Setup prompt
    prompt = base_prompt + """You are a virtual assistant called Antonio specializing in bank transfers.
Your goal is to help customers transfer money between their accounts or to third-party accounts.
Answer questions like 'How can I transfer money?' or 'I want to send $100 to John Doe's account.'.
If the user asks for a balance, you should transfer the conversation to the Balance Agent.
Today is {date}
""" 

    ast = MacawAssistant(
        name=name,
        description=description,
        prompt=PromptTemplate(prompt)
    )

    # ----------------------------------------------------------------------
    # TODO: Add RAG here
    # TODO: Add Tooling here
    # ----------------------------------------------------------------------
    
    
    return ast