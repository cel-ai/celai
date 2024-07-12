import asyncio
from typing import Callable
import pysbd

from cel.assistants.stream_content_chunk import StreamContentChunk


def streaming_sentence_detector(stream, language="en"):
    """pySBD based streaming sentence detector"""
    
    buffer = ''
    seg = pysbd.Segmenter(language=language, clean=False)
    for char in stream:
        buffer += char
        sentences = seg.segment(buffer)
        if len(sentences) > 1:
            yield from sentences[:-1]
            buffer = sentences[-1]
    if buffer:
        yield buffer
        
async def streaming_word_detector_async(stream):
    def pop_word(s):
        if s:
            word = s.split(' ')[0]
            s = s[len(word):]
            return word, s
        return None, s

    buffer = ""
    async for token in stream:
        buffer += token
        word, buffer = pop_word(buffer)
        if word:
            yield word
            
    if buffer:
        yield buffer


async def streaming_sentence_detector_async(stream, language="en", on_chunk = None):
    """pySBD based streaming sentence detector"""
    
    buffer = ''
    seg = pysbd.Segmenter(language=language, clean=False)
    async for chunk in stream:
        # cast char to class StreamChunk
        assert isinstance(chunk, StreamContentChunk), "stream must be a StreamChunk"
      
        if not chunk.is_partial:
            yield StreamContentChunk(content=chunk.content, is_partial=False)     
            break
      
        buffer += chunk.content   
        
        if on_chunk:
            await on_chunk(chunk, buffer)
            
        sentences = seg.segment(buffer)
        if len(sentences) > 1:
            for sentence in sentences[:-1]:
                yield StreamContentChunk(content=sentence, is_partial=chunk.is_partial)
            buffer = sentences[-1]
    if buffer:
        yield StreamContentChunk(content=buffer, is_partial=chunk.is_partial)





if __name__ == "__main__":

    text = """Holi is a popular ancient Hindu festival https://github.com/nipunsadvilkar/pySBD, also known as the "Festival of Colors" or the "Festival of Love." The festival celebrates the arrival of spring, the end of winter, the blossoming of love, and for many it's a festive day to meet others, play and laugh, forget and forgive, and repair broken relationships. It is also celebrated as a thanksgiving for a good harvest. Holi is typically celebrated in India, Nepal, and other parts of the world with significant populations of Hindus or people of Indian origin. The festival has spread to parts of Europe and North America as a spring celebration of love, frolic, and colors. Holi celebrations start on the night before Holi with a Holika Dahan where people gather, perform religious rituals in front of the bonfire, and pray that their internal evil be destroyed the way Holika, the sister of the demon king Hiranyakashipu, was killed in the fire. The next morning is celebrated as Rangwali Holi – a free-for-all festival of colors, where participants play, chase and color each other with dry powder and colored water, with some carrying water guns and colored water-filled balloons for their water fight. The festival also provides an opportunity to enjoy seasonal foods and delicacies, socialize, and enjoy festive activities. While Holi is an ancient festival in India and Nepal, it is now celebrated in many places across the world."""    

    # #  SYNC TEST
    # ---------------------------------------------------------------------
    text_stream = iter(text)
    for sentence in streaming_sentence_detector(text_stream):
        print(sentence)
        print ("----------------------")


    print ("-----------DONE-----------")
    print ("-----------DONE-----------")


    # ASYNC TEST
    # ---------------------------------------------------------------------
    class AsyncIterable:
        def __init__(self, iterable):
            self.iterable = iterable

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                value = next(self.iterable)
            except StopIteration:
                raise StopAsyncIteration
            await asyncio.sleep(0)  # This makes this method asynchronous
            return value


    async def async_test():
        # ASYNC
        import asyncio
        text_stream = AsyncIterable(iter(text))
        async for sentence in streaming_sentence_detector_async(text_stream):
            print(sentence)
            print ("----------------------")        
        
        

    asyncio.run(async_test())
    