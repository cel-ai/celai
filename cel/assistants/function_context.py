from cel.assistants.function_response import FunctionResponse, RequestMode
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import ConversationLead, Message


from dataclasses import dataclass, field


@dataclass
class FunctionContext:
    lead: ConversationLead
    message: Message | None = None
    connector: BaseConnector | None = None
    state: dict | None = field(default_factory=dict)
    history: list[dict] | None = field(default_factory=list)

    @staticmethod
    def response_text(text: str, request_mode: RequestMode = RequestMode.SINGLE):
        return FunctionResponse(text=text, request_mode=request_mode)

    
    # @staticmethod
    # def response_image(image_url: str, request_mode: RequestMode = RequestMode.SINGLE):
    #     return FunctionResponse(image_url=image_url, request_mode=request_mode)