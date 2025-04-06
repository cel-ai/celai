# import random
import asyncio
import time
import pytest
# import fakeredis.aioredis
from cel.assistants.common import FunctionDefinition, Param
from cel.assistants.function_context import FunctionContext
from cel.gateway.model.conversation_lead import ConversationLead





@pytest.fixture
def lead():
    lead = ConversationLead()
    return lead.get_session_id()

    
# @pytest.fixture
# def history() -> InMemoryHistoryProvider:
#     h = InMemoryHistoryProvider(key_prefix='test')
#     return h

@pytest.mark.asyncio
async def test_validate_required_params(lead):

    func = FunctionDefinition(
        name="test_function",
        description="Test function",
        parameters=[
            Param(name="param1", type="string", description="Test param 1", required=True),
            Param(name="param2", type="int", description="Test param 2", required=True),
            Param(name="param3", type="float", description="Test param 3", required=True),
        ]
    )
    
    prams = {   
        "param1": "test",
        "param2": 123
    }


    fc = FunctionContext(
        lead=lead,
        params=prams,
        function_definition=func
    )
    
    res = fc.validate_params()
    
    assert len(res) == 1
    assert "param3" in res[0] and "Missing" in res[0]

    
    

@pytest.mark.asyncio
async def test_validate_types_happy(lead):
    
    # string: To represent simple text.
    # integer: For whole numeric values.
    # float: For numeric values with decimals.
    # boolean: To represent true or false values.
    # object (or JSON): To pass more complex structures organized in key-value pairs.
    # array: Lists of values, which can be of any of the aforementioned types.  

    func = FunctionDefinition(
        name="test_function",
        description="Test function",
        parameters=[
            Param(name="param_str", type="string", description="Test param String", required=True),
            Param(name="param_number", type="number", description="Test param Number", required=True),
            Param(name="param_integer", type="integer", description="Test param Integer", required=True),
            Param(name="param_bool", type="boolean", description="Test param Boolean", required=True),
        ]
    )
    
    prams = {   
        "param_str": "test",
        "param_number": 123.45,
        "param_integer": 123,
        "param_bool": True
    }


    fc = FunctionContext(
        lead=lead,
        params=prams,
        function_definition=func
    )
    
    res = fc.validate_params(validate_types=True)
    
    assert len(res) == 0
    
    
@pytest.mark.asyncio
async def test_validate_types_fail_number(lead):
    
    # string: To represent simple text.
    # integer: For whole numeric values.
    # float: For numeric values with decimals.
    # boolean: To represent true or false values.
    # object (or JSON): To pass more complex structures organized in key-value pairs.
    # array: Lists of values, which can be of any of the aforementioned types.  

    func = FunctionDefinition(
        name="test_function",
        description="Test function",
        parameters=[
            Param(name="param_number", type="number", description="Test param Number", required=True),
        ]
    )
    
    prams = {   
        "param_number": "123",
    }


    fc = FunctionContext(
        lead=lead,
        params=prams,
        function_definition=func
    )
    
    res = fc.validate_params(validate_types=True)
    
    assert len(res) == 1
    assert "param_number" in res[0] and "must be a number" in res[0]
    
    
@pytest.mark.asyncio
async def test_validate_types_fail_all(lead):
    
    # string: To represent simple text.
    # integer: For whole numeric values.
    # float: For numeric values with decimals.
    # boolean: To represent true or false values.
    # object (or JSON): To pass more complex structures organized in key-value pairs.
    # array: Lists of values, which can be of any of the aforementioned types.  

    func = FunctionDefinition(
        name="test_function",
        description="Test function",
        parameters=[
            Param(name="param_str", type="string", description="Test param String", required=True),
            Param(name="param_number", type="number", description="Test param Number", required=True),
            Param(name="param_integer", type="integer", description="Test param Integer", required=True),
            Param(name="param_bool", type="boolean", description="Test param Boolean", required=True),
        ]
    )
    
    prams = {   
        "param_str": 123,
        "param_number": "123",
        "param_integer": "123",
        "param_bool": 123
    }


    fc = FunctionContext(
        lead=lead,
        params=prams,
        function_definition=func
    )
    
    res = fc.validate_params(validate_types=True)
    
    assert len(res) == 4
    assert "param_str" in res[0] and "must be a string" in res[0]
    assert "param_number" in res[1] and "must be a number" in res[1]
    assert "param_integer" in res[2] and "must be an integer" in res[2]
    assert "param_bool" in res[3] and "must be a boolean" in res[3]
    
    
    
@pytest.mark.asyncio
async def test_validate_types_enum(lead):
    
    # string: To represent simple text.
    # integer: For whole numeric values.
    # float: For numeric values with decimals.
    # boolean: To represent true or false values.
    # object (or JSON): To pass more complex structures organized in key-value pairs.
    # array: Lists of values, which can be of any of the aforementioned types.  

    func = FunctionDefinition(
        name="test_function",
        description="Test function",
        parameters=[
            Param(name="param1", type="string", enum=["value1", "value2"], 
                  description="Test param String", required=True),
            Param(name="param2", type="string", enum=["value3", "value4"], 
                  description="Test param String", required=True),            
        ]
    )
    
    prams = {   
        "param1": "value1",
        "param2": "value5"
    }


    fc = FunctionContext(
        lead=lead,
        params=prams,
        function_definition=func
    )
    
    res = fc.validate_params(validate_types=True)
    
    assert len(res) == 1
    assert "param2" in res[0] and "Expected one of ['value3', 'value4']" in res[0]
    
    