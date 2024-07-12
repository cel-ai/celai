from dataclasses import dataclass, field
from cel.assistants.common import EventResponse
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from cel.assistants.base_assistant import BaseAssistant


@dataclass
class RequestContext:
    lead: ConversationLead
    connector: BaseConnector | None = None
    state: dict | None = field(default_factory=dict)
    history: list[dict] | None = field(default_factory=list)
    prompt: str | None = None
    message: Message | None = None
    assistant: BaseAssistant | None = None
    
    
    async def send_text_message(self, text: str):
        if self.connector:
            await self.connector.send_text_message(self.lead, text)
    
    async def send_typing_action(self):
        if self.connector:
            await self.connector.send_typing_action(self.lead)
    

    @staticmethod
    def cancel_response():
        return EventResponse(disable_ai_response=True, is_private=False, blend=False)
    
    @staticmethod
    def response_text(text: str, disable_ai_response: bool = False, is_private: bool = False, blend: bool = False):
        return EventResponse(text=text, disable_ai_response=disable_ai_response, is_private=is_private, blend=blend)

    @staticmethod
    def response_image(image_url: str, disable_ai_response: bool = False, is_private: bool = False, blend: bool = False):
        return EventResponse(image=image_url, disable_ai_response=disable_ai_response, is_private=is_private, blend=blend)

    @staticmethod
    def response_audio(audio: str, disable_ai_response: bool = False, is_private: bool = False, blend: bool = False):
        return EventResponse(audio=audio, disable_ai_response=disable_ai_response, is_private=is_private, blend=blend)

    @staticmethod
    def response_video(video_url: str, disable_ai_response: bool = False, is_private: bool = False, blend: bool = False):
        return EventResponse(video=video_url, disable_ai_response=disable_ai_response, is_private=is_private, blend=blend)