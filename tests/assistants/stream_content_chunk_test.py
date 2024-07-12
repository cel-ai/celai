# test StreamContentChunk
import pytest
from cel.assistants.stream_content_chunk import StreamContentChunk


@pytest.mark.asyncio
async def test_ai_content_chunk():
    a = StreamContentChunk(content="Hello", is_partial=True)
    b = StreamContentChunk(content=" World", is_partial=False)
    c = a + b
    assert c.content == "Hello World"
    assert c.is_partial is False