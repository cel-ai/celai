import pytest
from cel.assistants.albert.albert_assistant import AlbertAssistant
from cel.gateway.model.conversation_lead import ConversationLead

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
<function name="get_cryptocurrency_price" description="Get the current cryptocurrency price">
    <parameters type="object">
        <param name="cryptocurrency" type="string" description="The cryptocurrency abbreviation eg. BTC, ETH"/>
        <param name="currency" type="string" enum="USD,ARG" />
    </parameters>
</function>    
    """
    
    assistant = AlbertAssistant(prompt=prompt)
    
    stream = assistant.new_message(lead, "price of bitcoin?", {})
    
    content = ''
    async for chunk in stream:
        print(chunk, end='')
        content += chunk
        
    print(content)
    
    
    
    
