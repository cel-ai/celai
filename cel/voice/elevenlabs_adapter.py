import os
from elevenlabs import Voice, VoiceSettings, play
from elevenlabs.client import ElevenLabs
from cel.voice.base_voice_provider import BaseVoiceProvider


# https://help.elevenlabs.io/hc/en-us/articles/17883183930129-What-models-do-you-offer-and-what-is-the-difference-between-them
DEFAULT_MODEL="eleven_turbo_v2_5"

class ElevenLabsAdapter(BaseVoiceProvider):
    
    def __init__(self, api_key: str = None, 
                 default_voice: str = "N2lVS1w4EtoT3dr4eOWO", 
                 settings: VoiceSettings = None,
                 preprocessing_callback: callable = None
                ):
        
        self.api_key = api_key
        self.default_voice = default_voice
        self.default_voice_settings = settings or VoiceSettings(
                                                        stability=0.50, 
                                                        similarity_boost=0.75, 
                                                        style=0.0, 
                                                        use_speaker_boost=True
                                                    )
        
        key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not key:
            raise Exception("ELEVENLABS_API_KEY not found in the environment")
        
        self.client = ElevenLabs(api_key=key)
        self.preprocessing_callback = preprocessing_callback
        
        
    def TTS(self, text: str, voice: str = None, settings: VoiceSettings = None) -> Voice:
        
        if self.preprocessing_callback:
            text = self.preprocessing_callback(text)

        audio = self.client.generate(
            text=text,
            model=DEFAULT_MODEL,
            voice=Voice(
                voice_id=voice or self.default_voice,
                settings=settings or self.default_voice_settings,
            )
        )
        return audio
    
    
    def STT(self, audio: bytes | str) -> str:
        raise NotImplementedError
    
    
    
if __name__ == "__main__":
    
    import os
    import dotenv
    dotenv.load_dotenv()
    ELEVENLABS_API_KEY= os.getenv("ELEVENLABS_API_KEY")
    tts = ElevenLabsAdapter(
        api_key=ELEVENLABS_API_KEY,
        preprocessing_callback=lambda x: x + " - from ElevenLabs"
    )
    audio = tts.TTS("This is a test")
    play(audio)
    
    