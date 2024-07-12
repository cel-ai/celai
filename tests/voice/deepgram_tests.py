import pytest

from cel.voice.deepgram_adapter import DeepgramAdapter


# TESTS 
# -------------------------------------------
@pytest.mark.asyncio
async def test_deepgram_stt():

    dg = DeepgramAdapter()
    text = dg.STT("https://api.telegram.org/file/bot5843053461:AAHjt8DMBEjFrjuep4i3HblRwKTmQZeRy_A/voice/file_1.oga")
    assert len(text) > 5
    assert 'hola' in text.lower()