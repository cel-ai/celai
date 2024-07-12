import pytest

from cel.assistants.common import FunctionDefinition, Param
from cel.assistants.macaw.macaw_inference_context import MacawNlpInferenceContext
from cel.assistants.macaw.macaw_nlp import process_new_message
from cel.assistants.macaw.macaw_settings import MacawSettings
from cel.gateway.model.conversation_lead import ConversationLead
from cel.prompt.prompt_template import PromptTemplate
from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
from cel.stores.state.state_inmemory_provider import InMemoryStateProvider


func1 = FunctionDefinition(
    name='get_crypto_price', 
    description='Get the current price of a cryptocurrency.',
    parameters=[
        Param(name='crypto',
            type='string',
            description='The name of the cryptocurrency ex: BTC, ETH, ADA, etc.',
            required=True
            ),
        Param(name='currency',
            type='string',
            description='Currency name eg. USD, ARS',
            required=False,
            enum=['USD', 'ARS']
            )
        ]
    )

# @pytest.mark.asyncio
# async def test_new_message():
    
#     prompt = PromptTemplate(
#         "Your are a helpful assistant that can get the current price of a cryptocurrency. Get the price of a cryptocurrency."
#     )
    
    
#     ctx = MacawNlpInferenceContext(
#         lead = ConversationLead(),
#         prompt=prompt,
#         # functions=[func1],
#         history_store=InMemoryHistoryProvider(),
#         state_store=InMemoryStateProvider(),
#         settings=MacawSettings()
#     )
    
#     async for chunk in process_new_message(ctx, message="What is the price of BTC?"):
#         assert chunk
#         print(chunk)
        
        
#     assert True
    
    
@pytest.mark.asyncio
async def test_new_message_fail_func():
    
    prompt = PromptTemplate(
        "Your are a helpful assistant that can get the current price of a cryptocurrency. Get the price of a cryptocurrency."
    )
    
    
    ctx = MacawNlpInferenceContext(
        lead = ConversationLead(),
        prompt=prompt,
        functions=[func1],
        history_store=InMemoryHistoryProvider(),
        state_store=InMemoryStateProvider(),
        settings=MacawSettings()
    )
    
    async for chunk in process_new_message(ctx, message="What is the price of BTC?"):
        assert chunk
        print(chunk)
        
        
    assert True