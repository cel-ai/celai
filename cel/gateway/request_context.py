from dataclasses import dataclass, field
from cel.assistants.common import EventResponse
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from cel.assistants.base_assistant import BaseAssistant
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider


@dataclass
class RequestContext:
    lead: ConversationLead
    connector: BaseConnector | None = None
    prompt: str | None = None
    message: Message | None = None
    assistant: BaseAssistant | None = None
    state: BaseChatStateProvider | None = None
    history: BaseHistoryProvider | None = None
    
    
    async def send_text_message(self, text: str):
        if self.connector:
            await self.connector.send_text_message(self.lead, text)
    
    async def send_typing_action(self):
        if self.connector:
            await self.connector.send_typing_action(self.lead)
    
    async def get_state(self):
        if self.state:
            return await self.state.get_store(self.lead.get_session_id())
        return None
    
    async def set_state(self, state: dict):
        if self.state:
            await self.state.set_store(self.lead.get_session_id(), state)
            
    async def get_history(self):
        if self.history:
            return await self.history.get_history(self.lead.get_session_id())
        return None
    
    async def clear_history(self, message: Message):
        if self.history:
            await self.history.clear_history(self.lead.get_session_id())
            

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