import os
import pytest
from langchain_openai import ChatOpenAI
from cel.assistants.macaw.macaw_utils import get_last_n_elements
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    ToolCall,
    FunctionMessage,
    trim_messages,
)

@pytest.fixture
def messages():
    
    # Crea una instancia de FunctionCall
    tool_call = ToolCall({
                "name": "foo",
                "args": {"a": 1},
                "id": "call_5Gdgx3R2z97qIycWKixgD2OU"
            })


    return [
        SystemMessage("Assistant started."),
        HumanMessage("Hello"),
        AIMessage("How are you?"),
        HumanMessage("I'm fine."),
        AIMessage("What's your name?"),
        # Tool Call get_name
        AIMessage("", tool_calls=[tool_call]),
        ToolMessage("John", tool_call_id='call_5Gdgx3R2z97qIycWKixgD2OU'),
        HumanMessage("I'm John."),
        AIMessage("Nice to meet you."),
        HumanMessage("Nice to meet you too."),
    ]    



@pytest.mark.asyncio
async def test_get_last_n_messages_len(messages):
    
    n_count = len(messages)
    msgs = get_last_n_elements(messages, n_count)
    
    assert len(msgs) == n_count


@pytest.mark.asyncio
async def test_get_last_n_messages_empty(messages):
    
    # Create a list with no messages, only system message
    messages = [messages[0]]
    
    # Get the last 5 messages
    msgs = get_last_n_elements(messages, 5)
    
    # The result should be the same as the input
    assert len(msgs) == 1
    
@pytest.mark.asyncio
async def test_get_last_n_messages_3(messages):
        
        count = 3
        # Get the last 3 messages
        msgs = get_last_n_elements(messages, count)
        
        # The result should be the last human message and the system message
        # couse the system message is the first message
        # and in order to start_on=("human") and complain with len of 3
        # the result should be 2 messages
        assert len(msgs) == 3
        assert isinstance(msgs[0], SystemMessage)
        assert isinstance(msgs[1], AIMessage)
        assert isinstance(msgs[2], HumanMessage)


@pytest.mark.asyncio
async def test_get_last_n_messages_5(messages):
        
        # Get the last 5 messages
        msgs = get_last_n_elements(messages, 5)
        
        # The result should be the last 4 messages
        # couse tool_call and tool_message are not counted
        assert len(msgs) == 4
        assert isinstance(msgs[0], SystemMessage)
        assert isinstance(msgs[1], HumanMessage)
        assert isinstance(msgs[2], AIMessage)
        assert isinstance(msgs[3], HumanMessage)
        
        # invoke chat LLM openai using langchain_openai
        # with this msgs
        if os.environ.get("OPENAI_API_KEY"):
            chat = ChatOpenAI()
            response = chat.invoke(msgs)
            assert response is not None
            

@pytest.mark.asyncio
async def test_get_last_n_messages_6(messages):
            
        # Get the last 6 messages
        msgs = get_last_n_elements(messages, 6)
        
        # The result should be the last 6 messages
        assert len(msgs) == 6
                       
        assert isinstance(msgs[0], SystemMessage)
        assert isinstance(msgs[1], AIMessage)
        assert isinstance(msgs[2], ToolMessage)
        assert isinstance(msgs[3], HumanMessage)
        assert isinstance(msgs[4], AIMessage)
        assert isinstance(msgs[5], HumanMessage)
        
        
        
        # invoke chat LLM openai using langchain_openai
        # with this msgs
        if os.environ.get("OPENAI_API_KEY"):
            chat = ChatOpenAI()
            response = chat.invoke(msgs)
            assert response is not None
            
@pytest.mark.asyncio
async def test_get_last_n_messages_7(messages):
                
        # Get the last 7 messages
        msgs = get_last_n_elements(messages, 7)
        
        # The result should be the last 7 messages
        assert len(msgs) == 7
        assert isinstance(msgs[0], SystemMessage)
        assert isinstance(msgs[1], AIMessage)
        assert isinstance(msgs[2], AIMessage)
        assert isinstance(msgs[3], ToolMessage)
        assert isinstance(msgs[4], HumanMessage)
        assert isinstance(msgs[5], AIMessage)
        assert isinstance(msgs[6], HumanMessage)
        
        
        # invoke chat LLM openai using langchain_openai
        # with this msgs
        if os.environ.get("OPENAI_API_KEY"):
            chat = ChatOpenAI()
            response = chat.invoke(msgs)
            assert response is not None