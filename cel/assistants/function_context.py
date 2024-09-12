from dataclasses import dataclass, field
from cel.assistants.function_response import FunctionResponse, RequestMode
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import ConversationLead, Message
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider


@dataclass
class FunctionContext:
    lead: ConversationLead
    message: Message | None = None
    connector: BaseConnector | None = None
    state: BaseChatStateProvider | None = None
    history: BaseHistoryProvider | None = None


    @staticmethod
    def response_text(text: str, request_mode: RequestMode = RequestMode.SINGLE):
        return FunctionResponse(text=text, request_mode=request_mode)

    
    # @staticmethod
    # def response_image(image_url: str, request_mode: RequestMode = RequestMode.SINGLE):
    #     return FunctionResponse(image_url=image_url, request_mode=request_mode)