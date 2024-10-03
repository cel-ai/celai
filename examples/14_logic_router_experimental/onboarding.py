
# Import Cel.ai modules
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.rag.providers.markdown_rag import MarkdownRAG
from cel.assistants.function_context import FunctionContext
from cel.assistants.function_response import RequestMode
from cel.assistants.common import Param
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider


def build_onboarding_agent(base_prompt: str = ''):
    
    # Setup prompt
    prompt = base_prompt + """You are a virtual assistant specializing in banking balance enquiries.
Your goal is help clients in the onboarding process to Foobar Bank. 
Your target is to get the client registered. Invite the client to register on welcoming.
The user is not registered yet.
Today is {date}
"""
            
    prompt_template = PromptTemplate(prompt)

    ast = MacawAssistant(
        # For observability purposes, it is recommended to provide a name to the assistant
        name="Onboarding Agent",
        
        # This is the description of the assistant, it will be used by AssistantRouter 
        # to match the assistant with the user intent
        description="""You are a virtual assistant specializing in onboarding clients to Foobar Bank.""",
            
        prompt=prompt_template,
    )
    
    
    @ast.function('register_user', 'If the user wants to continue with the registration process', params=[
        Param('user_full_name', 'string', 'Full name of the user', required=True)
    ])
    async def handle_registration(session, params, ctx: FunctionContext):       
        # Change the state of the user to registered
        state = await ctx.state.get_store(session) or {}
        state["is_registered"] = True
        await ctx.state.set_store(session, state)
        
        # Response to user with success message
        name = params.get('user_full_name')
        return FunctionContext.response_text(f"Welcome {name}! You are now registered with Foobar Bank.")

        
    # TODO: Add RAG here
    
    # TODO: Add Tooling here
        
    return ast