import pytest
from cel.rag.text2vec.cached_openai import CachedOpenAIEmbedding
import dotenv

dotenv.load_dotenv()


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



# def test_do(client):
#     for i in range(5):
#         client.text2vec(f'test:{i}')
#     assert 1==1
    
def test_do2(client: CachedOpenAIEmbedding):
    # test with texts
    res = client.texts2vec(texts)
    assert len(res) == len(texts)