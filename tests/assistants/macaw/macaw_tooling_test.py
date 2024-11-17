import pytest
import os
from cel.assistants.common import FunctionDefinition, Param
from cel.assistants.macaw.macaw_utils import map_function_to_tool_message


is_github_actions = 'OPENAI_API_KEY' in os.environ


@pytest.mark.asyncio
@pytest.mark.skipif(is_github_actions, reason="Disable in Github Actions")
async def test_map_function_to_tool_message():
    

    func = FunctionDefinition(
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
    
    spected = {
       "type": "function", 
        "function": {
            "name": "get_crypto_price",
            "description": "Get the current price of a cryptocurrency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "crypto": {
                        "type": "string",
                        "description": "The name of the cryptocurrency ex: BTC, ETH, ADA, etc."
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency name eg. USD, ARS",
                        "enum": ["USD", "ARS"]
                    }
                },
                "required": ["crypto"]
            }
        }
    } 

    d = map_function_to_tool_message(func)
    
    

    assert d == spected