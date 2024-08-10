import pytest
from cel.rag.stores.chroma.chroma_store import ChromaStore
from cel.rag.text2vec.cached_ollama import CachedOllamaEmbedding
import os
IS_RUNNING_IN_GITHUB_ACTION = os.getenv("GITHUB_ACTIONS") == "true"


texts=[
    "This is a document about pineapple",
    "This is a document about oranges",
    "This is a document about lemons",
    "This is a document about dogs",
    "This is a document about parrots",
]

@pytest.fixture
def client():
    text2vec = CachedOllamaEmbedding()
    return ChromaStore(text2vec, collection_name='test_collection')


    
def test_store(client):
    if IS_RUNNING_IN_GITHUB_ACTION: 
        assert True
        return
        
    for t in texts:
        index = texts.index(t)
        client.upsert_text(f"{index}", t, {'metadata': 'metadata'})
    
    res = client.search('parrots', top_k=3)
    
    # check length
    assert len(res) == 3
    # check nearest 
    assert res[0].id == '4'
    #  check order
    assert res[0].distance < res[1].distance < res[2].distance
    #  check metadata
    assert res[0].metadata == {'metadata': 'metadata'}
    
    
def test_store_get_vector(client):
    if IS_RUNNING_IN_GITHUB_ACTION: 
        assert True
        return    

    res = client.get_vector('4')
    
    assert res.id == '4'
    assert res.text == 'This is a document about parrots'
    assert res.metadata == {'metadata': 'metadata'}
    
def test_get_similar(client):
    if IS_RUNNING_IN_GITHUB_ACTION: 
        assert True
        return    
    
    res = client.get_vector('1')
    
    similar = client.get_similar(res.vector, top_k=1)
    
    assert len(similar) == 1
    assert similar[0].id == '1'
    
    
def test_delete(client):
    if IS_RUNNING_IN_GITHUB_ACTION: 
        assert True
        return
        
    for t in texts:
        index = texts.index(t)
        client.upsert_text(f"{index}", t, {'metadata': 'metadata'})
    
    client.delete('4')
    
    res = client.search('parrots', top_k=1)
    
    assert len(res) == 1
    # the nearest should not be parrots
    assert res[0].id != '4'