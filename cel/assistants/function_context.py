from dataclasses import dataclass
from typing import Any
from cel.assistants.common import FunctionDefinition, Param
from cel.assistants.function_response import FunctionResponse, RequestMode
from cel.assistants.context import Context
from loguru import logger as log

@dataclass
class FunctionContext(Context):
    def __init__(self, *args, params: dict, function_definition: FunctionDefinition, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = params
        self.function_definition = function_definition

    @staticmethod
    def response_text(text: str, request_mode: RequestMode = RequestMode.SINGLE):
        return FunctionResponse(text=text, request_mode=request_mode)

    def validate_params(self, validate_types: bool = False):
        # TODO: Implement validation of params
        assert isinstance(self.params, dict), "Params must be a dictionary"
        assert isinstance(self.function_definition, FunctionDefinition), "Function definition must be an instance of FunctionDefinition"
        
        name = self.function_definition.name
        params_definition = self.function_definition.parameters
        
        if not params_definition or len(params_definition) == 0:
            return
        
        errors = []
        for param in params_definition:
            assert isinstance(param, Param), "Param must be an instance of Param"
            param_name = param.name
            param_type = param.type
            param_value = self.params.get(param_name)
            
            if param_value is None and param.required:
                errors.append(f"Missing required parameter '{param_name}' in function '{name}'")
            
            if param_value is not None:
                if validate_types:        
                    type_error = self.validate_type(param, param_value)
                    if type_error:
                        errors.append(type_error)
                
        return errors
    
    
    def validate_type(self, param: Param, param_value: Any):
        """
            Para types to validate:
                - string: for string values.
                - integer: For int values.
                - number: float for decimal values and int for whole numbers.
                - boolean:for bool values.
                - enum: for enum values.
            
            The value must be converted to the type defined in the function definition, in order to
            test and validate the type.
            
            This function returns an error message if the type is not valid, otherwise it returns None        
        """
        
        try:
            param_type = param.type
            param_name = param.name
            
            if param_type == "string":
                if not isinstance(param_value, str):
                    return f"Parameter '{param_name}' must be a string, but got {type(param_value).__name__}"
                if param.enum and param_value not in param.enum:
                    return f"Invalid value '{param_value}' for parameter '{param_name}'. Expected one of {param.enum}"
                
            elif param_type == "integer":
                if not isinstance(param_value, int):
                    return f"Parameter '{param_name}' must be an integer, but got {type(param_value).__name__}"
            elif param_type == "number":
                if not isinstance(param_value, (int, float)):
                    return f"Parameter '{param_name}' must be a number, but got {type(param_value).__name__}"
            elif param_type == "boolean":
                if not isinstance(param_value, bool):
                    return f"Parameter '{param_name}' must be a boolean, but got {type(param_value).__name__}"
            else:
                log.warning(f"FunctionContext: Type validation not implemented for parameter '{param_name}' with type '{param_type}'")
        except Exception as e:
            return f"Error validating parameter '{param_name}': {str(e)}"
        
        return None

        