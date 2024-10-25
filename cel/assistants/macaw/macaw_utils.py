from typing import List
from langchain_core.messages import BaseMessage, trim_messages
from cel.assistants.common import FunctionDefinition, Param


def get_last_n_elements(msgs: List[BaseMessage], n: int) -> List[BaseMessage]:
    return trim_messages(
        msgs,
        # Keep the last <= n_count tokens of the messages.
        strategy="last",
        token_counter=len,
        # When token_counter=len, each message
        # will be counted as a single token.
        # Remember to adjust for your use case
        max_tokens=n,
        # Most chat models expect that chat history starts with either:
        # (1) a HumanMessage or
        # (2) a SystemMessage followed by a HumanMessage
        start_on="human",
        # Most chat models expect that chat history ends with either:
        # (1) a HumanMessage or
        # (2) a ToolMessage
        end_on=("human", "tool"),
        # Usually, we want to keep the SystemMessage
        # if it's present in the original history.
        # The SystemMessage has special instructions for the model.
        include_system=True,
    )
            


def map_function_parameters_to_tool_message(parameters: list[Param]):
    assert isinstance(parameters, list),\
        "parameters must be a list"

    properties = {}
    for p in parameters:
        properties[p.name] = {
            "type": p.type,
            "description": p.description
        }
        if p.enum:
            properties[p.name]["enum"] = p.enum
            
    return properties


def map_function_to_tool_message(function: FunctionDefinition):
    assert isinstance(function, FunctionDefinition),\
        "function must be an instance of FunctionDefinition"
        
    return {
        "type": "function",
        "function": {
            "name": function.name,
            "description": function.description,
            "parameters": {
                "type": "object",
                "properties": map_function_parameters_to_tool_message(function.parameters),
                "required": [p.name for p in function.parameters if p.required]
            }
        }
    }

def map_functions_to_tool_messages(functions: list[FunctionDefinition]):
    assert isinstance(functions, list),\
        "functions must be a list"
        
    return [map_function_to_tool_message(f) for f in functions]
