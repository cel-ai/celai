from cel.assistants.common import FunctionDefinition, Param



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
