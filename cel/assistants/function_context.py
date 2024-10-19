from dataclasses import dataclass
from cel.assistants.function_response import FunctionResponse, RequestMode
from cel.assistants.context import Context


@dataclass
class FunctionContext(Context):
    
    @staticmethod
    def response_text(text: str, request_mode: RequestMode = RequestMode.SINGLE):
        return FunctionResponse(text=text, request_mode=request_mode)
