import asyncio
import time
import pytest
from cel.assistants.albert.albert_assistant import AlbertAssistant
from cel.assistants.base_assistant import Events, Param
from cel.assistants.albert.nlp_job import NlpInferenceJob
from cel.assistants.engines.openai.openai_vanilla_engine import OpenAIVanilla
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
<function name="get_cryptocurrency_price" description="Get the current cryptocurrency price">
    <parameters type="object">
        <param name="cryptocurrency" type="string" description="The cryptocurrency abbreviation eg. BTC, ETH"/>
        <param name="currency" type="string" enum="USD,ARG" />
    </parameters>
</function>    
<function name="buy_crypto" description="Buy cryptocurrency">
    <parameters type="object">
        <param name="asset" type="string" description="The cryptocurrency abbreviation eg. BTC, ETH"/>
        <param name="asset_price" type="number" description="The price of the asset"/>
        <param name="fiat_amoount" type="string" description="The amount of fiat to spend"/>
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

    @assistant.function('buy_crypto', desc='Buy cryptocurrency', params=[
        Param(name='asset', type='string', description='The cryptocurrency abbreviation eg. BTC, ETH', required=True),
        Param(name='asset_amount', type='number', description='The amount of asset to buy', required=True)
    ])
    async def handle_buy_crypto(session, params):
        log.debug(f"Got buy_crypto call with params: {params}")
        return "Operation completed"

    stream = assistant.new_message(lead, "Buy 100 USD in BTC", {})

    content = ''
    async for chunk in stream:
        print(chunk, end='')
        content += chunk
        
    print("--------------------DONE--------------------------")
    
    assert '100' in content
    
    
    
    
    
