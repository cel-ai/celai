from cel.connectors.telegram.model.telegram_message import TelegramMessage
from deepgram import DeepgramClient, PrerecordedOptions, ClientOptionsFromEnv, FileSource
from loguru import logger as log
from cel.voice.deepgram_adapter import DeepgramAdapter



def process_stt(message: TelegramMessage, 
                model: str = None,
                smart_format: bool = None, 
                detect_language:bool = None, 
                on_fail_message: str = None,
                **kwargs):
    """Deepgram Speech to Text processing for Telegram voice messages. 
    It wll set the message.text with the STT result. This function is a wrapper 
    for the DeepgramAdapter.STT method. And is planned to be fail safe.
    
    Args:
        message (TelegramMessage): Telegram message object
        model (str, optional): Deepgram model. Defaults to None.
        smart_format (bool, optional): Smart format. Defaults to None.
        detect_language (bool, optional): Detect language. Defaults to None.
        on_fail_message (str, optional): Message to set in Message.text on fail STT. Defaults to None.
    """

    if not message.is_voice_message():
        return
    
    try:
        dp = DeepgramAdapter(
            model=model,
            smart_format=smart_format,
            detect_language=detect_language,
            **kwargs
        )
        
        voice = message.attachments[0]
        
        if voice.type != "voice":
            log.error(f"Attachment is not a voice message")
            return
        
        text = dp.STT(voice.file_url)
        log.debug(f"Message {message.lead.get_session_id()} -> STT: {text}")
        
        message.text = text
        message.isSTT = True
        
    except Exception as e:
        log.error(f"Error processing STT: {e}")
        if on_fail_message:
            message.text = on_fail_message
        return