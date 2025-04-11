# RAG Standard Implementation

## Overview

The RAG (Retrieval-Augmented Generation) Standard is a modular framework for implementing retrieval-augmented generation systems. It provides a standardized way to:

1. Load and process documents from various sources
2. Split documents into chunks suitable for embedding
3. Generate embeddings for text using different embedding models
4. Store and retrieve embeddings from vector databases
5. Use retrieved information to augment LLM responses

## Architecture

The RAG Standard is organized into the following components:

```
rag_standard/
├── providers/         # Document providers (Markdown, PDF, etc.)
├── slicers/           # Document chunking strategies
├── text2vec/          # Text-to-vector conversion (embeddings)
├── stores/            # Vector storage implementations
└── __init__.py        # Package initialization
```

## Components

### Providers

Providers are responsible for loading documents from various sources and formats:

- **MarkdownProvider**: Loads and processes markdown files
- **PDFProvider**: Loads and processes PDF documents
- **TextProvider**: Loads and processes plain text files

### Slicers

Slicers are responsible for splitting documents into chunks suitable for embedding:

- **CharacterSlicer**: Splits text by character count
- **ParagraphSlicer**: Splits text by paragraphs
- **TokenSlicer**: Splits text by token count

### Text2Vec

Text2Vec components handle the conversion of text to vector embeddings:

- **OpenAIEmbedding**: Uses OpenAI's embedding models
- **HuggingFaceEmbedding**: Uses HuggingFace embedding models
- **LocalEmbedding**: Uses locally hosted embedding models

### Stores

Stores handle the storage and retrieval of embeddings:

- **ChromaStore**: Uses ChromaDB for vector storage
- **PineconeStore**: Uses Pinecone for vector storage
- **FAISSStore**: Uses FAISS for vector storage

## Usage Example

Here's a simple example of how to use the RAG Standard:

```python
from cel.rag_standard.providers.markdown import MarkdownProvider
from cel.rag_standard.text2vec import OpenAIEmbedding
from cel.rag_standard.stores.chroma import ChromaStore

# Initialize components
provider = MarkdownProvider(base_path="./docs")
embedding = OpenAIEmbedding(api_key="your-api-key")
store = ChromaStore(
    persist_directory="./chroma_db",
    collection_name="knowledge_base",
    openai_api_key="your-api-key"
)

# Load and process documents
documents = provider.load_directory("knowledge_base")
for file_path, content in documents.items():
    chunks = provider.split_content(content, chunk_size=1000, overlap=200)
    for i, chunk in enumerate(chunks):
        metadata = {
            "source": file_path,
            "chunk_index": i,
            "total_chunks": len(chunks)
        }
        store.add_documents(
            documents=[chunk],
            metadatas=[metadata]
        )

# Search for relevant information
results = store.search(
    query="What is the RAG Standard?",
    n_results=5
)

# Use the results to augment an LLM response
# (This part would be handled by your LLM integration)
```

## Implementation Details

### ChromaStore

The ChromaStore class provides a simple interface to ChromaDB for vector storage:

```python
class ChromaStore:
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "default_collection",
        openai_api_key: Optional[str] = None,
        openai_model: str = "text-embedding-3-small"
    ):
        # Initialize ChromaDB client and collection
        
    def add_documents(
        self,
        documents: List[str],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        # Add documents to the collection
        
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Any]]:
        # Search for documents similar to the query
```

### OpenAIEmbedding

The OpenAIEmbedding class handles text-to-vector conversion using OpenAI's embedding models:

```python
class OpenAIEmbedding:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small"
    ):
        # Initialize OpenAI embedding
        
    def get_embedding_function(self):
        # Get the ChromaDB embedding function
        
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # Embed a list of texts
        
    def embed_query(self, query: str) -> List[float]:
        # Embed a single query text
```

### MarkdownProvider

The MarkdownProvider class handles loading and processing markdown files:

```python
class MarkdownProvider:
    def __init__(self, base_path: Optional[str] = None):
        # Initialize the markdown provider
        
    def load_file(self, file_path: str) -> str:
        # Load a markdown file
        
    def load_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, str]:
        # Load all markdown files in a directory
        
    def split_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        # Split markdown content into chunks
        
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        # Extract metadata from markdown content
        
    def process_file(self, file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        # Process a markdown file into chunks with metadata
```

## Best Practices

1. **Chunking**: Choose appropriate chunk sizes based on your embedding model and use case. Smaller chunks (500-1000 characters) work well for most models.

2. **Overlap**: Include overlap between chunks to maintain context across chunk boundaries.

3. **Metadata**: Include relevant metadata with each chunk to help with filtering and retrieval.

4. **Embedding Models**: Choose embedding models that are well-suited to your domain and language.

5. **Vector Stores**: Select vector stores based on your scale, performance requirements, and deployment environment.

## Future Enhancements

1. **More Providers**: Add support for more document types (HTML, Word, etc.)
2. **Advanced Slicing**: Implement more sophisticated chunking strategies
3. **Hybrid Search**: Combine vector search with keyword search
4. **Caching**: Add caching for embeddings to improve performance
5. **Evaluation**: Add tools for evaluating RAG system performance 