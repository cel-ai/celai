import pytest
from cel.rag.slicers.markdown import MarkdownSlicer
from cel.rag.slicers.markdown.utils import build_breadcrumbs

# @pytest.fixture
# def lead():
#     lead = ChatLead('123', 'test', 'tenant1', 'assistant1')
#     return lead

# @pytest.fixture
# def redis_client():
#     redis_client = fakeredis.FakeRedis()
#     return redis_client

# @pytest.fixture
# def store(redis_client):
#     return RedisChatStateProvider(redis_client, 's')

def test_do():
    mds = MarkdownSlicer('test', './tests/slicers/sample.md')
    slices = mds.slice()
    print(slices)
    assert 1==1
    
