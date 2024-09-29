from loguru import logger as log
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from cel.voice.deepgram_adapter import DeepgramAdapter



class DeepgramSTTMiddleware:
    """Deepgram Speech to Text Middleware for voice messages. 
    It wll set the message.text with the STT result. This function is a wrapper 
    for the DeepgramAdapter.STT method. And is planned to be fail safe.
    
    Args:
        model (str, optional): Deepgram model. Defaults to None.
        smart_format (bool, optional): Smart format. Defaults to None.
        detect_language (bool, optional): Detect language. Defaults to None.
        on_fail_message (str, optional): Message to set in Message.text on fail STT. Defaults to None.
        this message will go to the LLM if the STT fails.
    """    
    
    def __init__(self,
                model: str = None,
                smart_format: bool = None, 
                detect_language:bool = None, 
                on_fail_message: str = None,
                **kwargs):
        self.dp = DeepgramAdapter(
            model=model,
            smart_format=smart_format,
            detect_language=detect_language,
            **kwargs
        )
        log.debug(f"DeepgramSTTMiddleware initialized")
        self.on_fail_message = on_fail_message or "ERROR: User sent an audio message, but it could not be understood."
        
    async def __call__(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        assert isinstance(message, Message), "Message must be a Message object"
        
        try:
            if not message.is_voice_message():
                return True
            voice = message.attachments[0]
            
            if voice.type != "voice":
                log.error(f"Attachment is not a voice message")
                return True
            
            text = await self.dp.STT(voice.file_url)
            log.debug(f"Message {message.lead.get_session_id()} -> STT: {text}")
            
            # if text is empty or None, set the on_fail_message
            message.text = text if text else self.on_fail_message
            message.isSTT = True            
            
            return True
        except Exception as e:
            log.error(f"Error processing STT: {e}")
            # return True, so fails on STT won't stop the message processing
            if self.on_fail_message:
                message.text = self.on_fail_message
            return True
        
    
