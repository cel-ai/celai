from abc import ABC
from typing import Any
from deepgram import DeepgramClient, PrerecordedOptions, ClientOptionsFromEnv
from cel.voice.base_voice_provider import BaseVoiceProvider



class DeepgramAdapter(BaseVoiceProvider):
    def __init__(self, 
                 smart_format:bool = True, 
                 detect_language: bool = True, 
                 model: str = None, 
                 **kwargs):

        self.deepgram = DeepgramClient("", ClientOptionsFromEnv())

        self.options = PrerecordedOptions(
            model=model or "nova-2-general",
            smart_format=smart_format or True,
            detect_language=detect_language or True,
            **kwargs
        )

    async def STT(self, audio: bytes | str ) -> str:
        if isinstance(audio, bytes):
            payload = {"buffer": audio}
            response = await self.deepgram.listen.asyncprerecorded.v("1").transcribe_file(audio, self.options)
        if isinstance(audio, str):
            payload = {"url": audio}
            response = await self.deepgram.listen.asyncprerecorded.v("1").transcribe_url(payload, self.options)

        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        return transcript
    
    async def TTS(self, text: str, voice: str = None, settings: Any = None):
        raise NotImplementedError

