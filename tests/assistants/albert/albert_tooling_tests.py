import asyncio
import time
import pytest
from cel.assistants.albert.albert_assistant import AlbertAssistant
from cel.assistants.base_assistant import Events, Param

# load envs
from dotenv import load_dotenv
load_dotenv()




@pytest.mark.asyncio
async def test_process_user_message_async():
    assistant = AlbertAssistant()
    res = assistant.get_functions()
    
    assert res == []
    
    @assistant.function('get_cryptocurrency_price', 'Get the current cryptocurrency price', [
        Param(name='asset', type='string', description='Cryptocurrency name eg. BTC, ETH', required=True),
        Param(name='currency', type='string', description='Currency name eg. USD, ARS', required=False, enum=['USD', 'ARS'])
    ])
    async def handle_get_cryptocurrency_price(session, params):
        print(f"Got get_cryptocurrency_price call with params: {params}")
        return "1000"
    
    
    @assistant.event(Events.START)
    def handle_start(session, ctx, message):
        print(f"Got start event with message: {message}")


    funcs = assistant.get_functions()

    assert len(funcs) == 1
    assert 'get_cryptocurrency_price' == funcs[0].name


    # call a coroutine async assistant.call_function
    res = await assistant.call_function('get_cryptocurrency_price', {'asset': 'BTC', 'currency': 'USD'}, None)
    assert res == "1000"


def test_process_user_message_sync():
    assistant = AlbertAssistant()
    res = assistant.get_functions()
    
    assert res == []
    
    @assistant.function('get_cryptocurrency_price', 'Get the current cryptocurrency price', [
        Param(name='asset', type='string', description='Cryptocurrency name eg. BTC, ETH', required=True),
        Param(name='currency', type='string', description='Currency name eg. USD, ARS', required=False, enum=['USD', 'ARS'])
    ])
    def handle_get_cryptocurrency_price(session, params):
        print(f"Got get_cryptocurrency_price call with params: {params}")
        time.sleep(1)
        return "1000"
    
    
    @assistant.event(Events.START)
    def handle_start(session, ctx, message):
        print(f"Got start event with message: {message}")


    funcs = assistant.get_functions()

    assert len(funcs) == 1
    assert 'get_cryptocurrency_price' == funcs[0].name


    # call a coroutine async assistant.call_function
    call_func = asyncio.wait_for(assistant.call_function('get_cryptocurrency_price', {'asset': 'BTC', 'currency': 'USD'}, None), timeout=1)
    
    # wait for the result
    res = asyncio.run(call_func)
    
    assert res == "1000"
    

    

