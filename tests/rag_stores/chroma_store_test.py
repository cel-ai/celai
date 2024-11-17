import os
import pytest
from cel.rag.text2vec.cached_openai import CachedOpenAIEmbedding
import dotenv

dotenv.load_dotenv()

is_openai_available = 'OPENAI_API_KEY' in os.environ


texts=[
    "This is a document about pineapple",
    "This is a document about oranges",
    "This is a document about lemons",
    "This is a document about dogs",
    "This is a document about parrots",
]

@pytest.fixture
def client():
    return CachedOpenAIEmbedding()



@pytest.mark.skipif(is_openai_available, reason="Disable in Github Actions")
def test_do2(client: CachedOpenAIEmbedding):
    # test with texts
    res = client.texts2vec(texts)
    assert len(res) == len(texts)