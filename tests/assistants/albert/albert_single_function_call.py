import pytest
from cel.assistants.albert.albert_assistant import AlbertAssistant
from cel.assistants.base_assistant import Param
from cel.gateway.model.conversation_lead import ConversationLead
from loguru import logger as log    

# load envs
from dotenv import load_dotenv
load_dotenv()



@pytest.fixture
def lead():
    lead = ConversationLead()
    return lead

@pytest.mark.asyncio
async def test_process_user_message_async(lead):
    assistant = AlbertAssistant()
    
    stream = assistant.new_message(lead, "2+2?", {})
    
    content = ''
    async for chunk in stream:
        print(chunk, end='')
        content += chunk
        
    assert '4' in content
    
    

@pytest.mark.asyncio
async def test_process_user_message_with_func_async(lead):
    
    prompt = """
    Your an Crypto Assistant. You can ask me about the price of cryptocurrencies. Questions about prices should be answered shortly for example: "What is the price of Bitcoin?" Answer: "The price is 3123 USD." 
    """
    assistant = AlbertAssistant(prompt=prompt)
    lead = ConversationLead()
    
    @assistant.function('get_cryptocurrency_price', desc='Get the current cryptocurrency price', params=[
        Param(name='cryptocurrency', type='string', description='The cryptocurrency abbreviation eg. BTC, ETH', required=True),
        Param(name='currency', type='string', description='Currency name eg. USD, ARS', required=False, enum=['USD', 'ARS'])
    ])
    async def handle_get_cryptocurrency_price(session, params):
        log.debug(f"Got get_cryptocurrency_price call with params: {params}")
        return "1000"

    stream = assistant.new_message(lead, "price of bitcoin?", {})

    content = ''
    async for chunk in stream:
        print(chunk, end='')
        content += chunk
    
    print("--------------------DONE--------------------------")
    
    assert '1000' in content
    
    
    
    
    
# DEPRECATED
@pytest.mark.asyncio
async def test_process_user_message_with_DEPRECTED_func_async(lead):
    
    prompt = """
    Your an Crypto Assistant. You can ask me about the price of cryptocurrencies. Questions about prices should be answered shortly for example: "What is the price of Bitcoin?" Answer: "The price is 3123 USD."
    <function name="get_cryptocurrency_price" description="Get the current cryptocurrency price">
    <parameters type="object">
        <param name="cryptocurrency" type="string" description="The cryptocurrency abbreviation eg. BTC, ETH"/>
        <param name="currency" type="string" enum="USD,ARG" />
    </parameters>
    </function>    
    """
    assistant = AlbertAssistant(prompt=prompt)
    lead = ConversationLead()
    
    @assistant.function('get_cryptocurrency_price', desc='Get the current cryptocurrency price', params=[
        Param(name='cryptocurrency', type='string', description='The cryptocurrency abbreviation eg. BTC, ETH', required=True),
        Param(name='currency', type='string', description='Currency name eg. USD, ARS', required=False, enum=['USD', 'ARS'])
    ])
    async def handle_get_cryptocurrency_price(session, params):
        log.debug(f"Got get_cryptocurrency_price call with params: {params}")
        return "1000"

    stream = assistant.new_message(lead, "price of bitcoin?", {})

    content = ''
    async for chunk in stream:
        print(chunk, end='')
        content += chunk
    
    print("--------------------DONE--------------------------")
    
    assert '1000' in content
    
    
    