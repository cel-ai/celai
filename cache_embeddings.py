import os
import time
import chromadb
import dotenv
from diskcache import Cache

from cel.cache import get_cache

cache = get_cache('.cache')
# cache1 = get_cache('.cache')
# cache2 = get_cache('.cache')
# cache3 = get_cache('.cache')
# cache4 = get_cache('.cache')
# same = cache1 == cache2 == cache3 == cache4
# print(same)
# cache = Cache('.cache')
# chroma_client = chromadb.Client()

# #  load .env
# dotenv.load_dotenv()

@cache.memoize(typed=True, expire=30, tag='test')
def test_function(label: str, model: str = "text-embedding-3-small") -> list[float]:
    print(f'Calculating {label}')
    time.sleep(1)
    return [1.0, 2.0, 3.0]


for i in range(5):
    res = test_function(f'{i}', 'text-embedding-3-small1')
    print(f'Reading from cache: {i}')
    print(res)
print('Done')


# import chromadb.utils.embedding_functions as embedding_functions
# openai_ef = embedding_functions.OpenAIEmbeddingFunction(
#                 api_key=os.getenv("OPENAI_API_KEY"),
#                 model_name="text-embedding-3-small"
#             )


# collection = chroma_client.create_collection(
#     name="my_collection",
#     embedding_function=openai_ef
# )


# collection.add(
#     documents=[
#         "This is a document about pineapple",
#         "This is a document about oranges"
#     ],
#     ids=["id1", "id2"]
# )



# results = collection.query(
#     query_texts=["This is a query document about apples"], # Chroma will embed this for you
#     n_results=2 # how many results to return
# )
# print(results)
