import os
import chromadb
import dotenv
chroma_client = chromadb.Client()

#  load .env
dotenv.load_dotenv()

import chromadb.utils.embedding_functions as embedding_functions
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name="text-embedding-3-small"
            )


collection = chroma_client.create_collection(
    name="my_collection",
    embedding_function=openai_ef
)


collection.add(
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ],
    ids=["id1", "id2"]
)



results = collection.query(
    query_texts=["This is a query document about apples"], # Chroma will embed this for you
    n_results=2 # how many results to return
)
print(results)
