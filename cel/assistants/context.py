from dataclasses import dataclass, field
from loguru import logger as log
import warnings
from cel.assistants.common import EventResponse
from cel.assistants.state_manager import AsyncStateManager
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.outgoing.outgoing_message_text import OutgoingTextMessage
from cel.stores.history.base_history_provider import BaseHistoryProvider
from cel.stores.state.base_state_provider import BaseChatStateProvider


@dataclass
class Context:
    lead: ConversationLead
    connector: BaseConnector | None = None
    prompt: str | None = None
    message: Message | None = None
    assistant: BaseAssistant | None = None
    state: BaseChatStateProvider | None = None
    history: BaseHistoryProvider | None = None
    
    def state_manager(self, commit_on_error: bool = False):
        return AsyncStateManager(self.lead, self.state, commit_on_error)
    
    async def send_text_message(self, text: str, append_to_history: bool = True, is_private: bool = False):
        """ Send a direct message text to the user conversation. 
        This message will be sent without any AI processing.
        If append_to_history is True, the message will be added to the conversation history. 
        """
                
        # TODO:
        #  1- Create an OutgoingTextMessage object
        #  2- Send the message using MessageGateway in order to include middlewares in the loop
        #  3- Send the message using the connector
        #  4- Add the message to the history if append_to_history is True
        
        
        # 1- Create an OutgoingTextMessage object
        outgoing_message = OutgoingTextMessage(
            content=text,
            lead=self.lead,
            is_partial=False,
            is_private=is_private
        )
        
        
        try:
            from cel.gateway.message_gateway import MessageGateway
            from cel.gateway.message_gateway import StreamMode
            
            # 2- Send the message using MessageGateway in order to include middlewares in the loop
            mg = MessageGateway.instance()
            res = await mg.process_outgoing_msg_middlewares(
                    message=outgoing_message, 
                    is_partial=False, 
                    is_summary=False, 
                    mode=StreamMode.FULL)
            
            # 3- Send the message using the connector
            await self.lead.connector.send_message(outgoing_message)
            
            # 4- Add the message to the history if append_to_history is True
            if append_to_history:
                await self.assistant.append_message_to_history(self.lead, text)            

        except Exception as e:
            log.error(f"Error sending message: {e}")
            

            

            
            
    async def send_link_message(self, body: str, button_text: str, url: str, append_to_history: bool = False):
        # TODO: Add same logic as send_text_message!!!!!
        
        link = {"text": button_text, "url": url}
        await self.connector.send_link_message(self.lead, body, [link], is_partial=False)
        
        if append_to_history:
            await self.assistant.append_message_to_history(self.lead, f"{body} {url}")
    
    async def send_voice_message(self, text: str, append_to_history: bool = True):
        # TODO: Add same logic as send_text_message!!!!!
        """ Send a direct voice message to the user conversation. 
        This message will be sent without any AI processing. 
        And won't be stored in the conversation history. 
        Use this method only for messages that are not part of the conversation flow. """
        if self.connector:
            await self.connector.send_voice_message(self.lead, text, options={})
            
        if append_to_history:
            await self.assistant.append_message_to_history(self.lead, text)
            
    async def blend_message(self, text: str, history_length: int = None):
        # TODO: Add same logic as send_text_message!!!!!
        """ Blend a message into the conversation context. 
        and return the blended text. """    
        return await self.assistant.blend(self.lead, text, history_length)
        
    
    async def send_typing_action(self):
        """ Send a typing action to the user conversation. 
        Not all connectors support this feature. 
        It's fail safe, so if the connector does not support it, it will just ignore the action. """
        if self.connector:
            await self.connector.send_typing_action(self.lead)
    
    async def get_state(self):
        """ Get the current state of the conversation. """
        if self.state:
            return await self.state.get_store(self.lead.get_session_id())
        return None
    
    async def set_state(self, state: dict):
        """ Set the current state of the conversation. """
        if self.state:
            await self.state.set_store(self.lead.get_session_id(), state)
            
    async def get_history(self):
        """ Get the conversation history. """
        if self.history:
            return await self.history.get_history(self.lead.get_session_id())
        return None
    
    async def clear_history(self, message: Message):
        """ Clear the conversation history. """
        if self.history:
            await self.history.clear_history(self.lead.get_session_id())
            

    """ This method are meant to be used by used as shortcuts to create EventResponse objects. 
    EventResponse es a mechanism to delegate the response processing to the AI or to the Gateway.
    If the response require certain processing againts history (append meessage to history) or
    keep it hide from the user (is_private) and being added to the history.
    Also if the response should be blended into conversation context (blend) or not.   
    """
    async def cancel_ai_response(self):
        """ If you want to cancel further processing of the message by the AI """
        return EventResponse(disable_ai_response=True)
    
    @staticmethod
    def cancel_ai_response():
        """ If you want to cancel further processing of the message by the AI """
        return EventResponse(disable_ai_response=True)
    
    @staticmethod
    def response_text(text: str, disable_ai_response: bool = False, is_private: bool = False, blend: bool = False):
        warnings.warn(
            "The 'response_text' method is deprecated and will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2
        )        
        return EventResponse(text=text, disable_ai_response=disable_ai_response, is_private=is_private, blend=blend)
    