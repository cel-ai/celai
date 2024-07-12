from pathlib import Path
import time
from halo import Halo
from loguru import logger as log
from cel.model.common import ContextMessage
from cel.rag.providers.rag_retriever import RAGRetriever
from cel.rag.slicers.base_slicer import Slice
from cel.rag.slicers.markdown.markdown import MarkdownSlicer
from cel.rag.stores.chroma.chroma_store import ChromaStore
from cel.rag.stores.vector_store import VectorRegister, VectorStore
from cel.rag.text2vec.cached_openai import CachedOpenAIEmbedding
from cel.rag.text2vec.utils import Text2VectorProvider


class MarkdownRAG(RAGRetriever):
    """Retrieve and store vectors for markdown content.

    Args:
        name (str): The name of the retriever
        file_path (str | Path): Path to the markdown file
        content (str): Markdown content
        encoding (str): Encoding of the markdown file
        prefix (str): Prefix to add to the slice ids
        split_table_rows (bool): Split table rows into separate slices
        text2vec (Text2VectorProvider): A text to vector provider
        store (VectorStore): A store to save the vectors. By default, it uses ChromaStore
        which runs on process memory.
        collection (str): The name of the collection
        metadata (dict): Metadata to add to the stored vectors
    """
    
    def __init__(self,
        name: str,
        file_path: str | Path = None,
        content: str | None = None,
        encoding: str = None,
        prefix: str = None,
        split_table_rows: bool = False,
        text2vec: Text2VectorProvider = None,
        store: VectorStore = None,
        collection: str = None,
        metadata: dict = None
        ):
            self.name = name
            self.file_path = file_path
            self.content = content
            self.prefix = prefix
            self.encoding = encoding
            self.split_table_rows = split_table_rows
            self.collection_name = collection or name
            self.text2vec = text2vec or CachedOpenAIEmbedding()
            self.store = store or ChromaStore(self.text2vec, collection_name=self.collection_name)
            self.metadata = metadata or {}
            

    def load(self):
        """Load markdown content from file_path and slice it into smaller pieces"""
        
        log.debug(f"Loading markdown content from {self.file_path}")
        spinner = Halo(text='Loading...', spinner='dots')
        spinner.start()
        
        spinner.text = 'Creating markdown slicer'
        slicer = MarkdownSlicer(
            name=self.name,
            content=self.content,
            file_path=self.file_path,
            prefix=self.prefix,
            split_table_rows=self.split_table_rows
        )
        
        spinner.text = 'Slicing markdown content...'
        log.debug('Slicing markdown content...')
        slices = slicer.slice()
        log.debug(f'Slices: {len(slices)}')
        spinner.succeed('Slicing complete')
        spinner.stop()
        

        spinner.start()
        spinner.text = 'Embedding markdown slices...'
        for slice in slices:
            idx = slices.index(slice) + 1
            spinner.text = f'Processing slice {idx}/{len(slices)}'
            self.__embed_slice(slice)
            
        spinner.succeed('Processing complete')
        spinner.stop()
        
        
    def search(self, 
               query: str, 
               top_k: int = 1, 
               history: list[ContextMessage] = None,
               state: dict = {}) -> list[VectorRegister]:
        
        res = self.store.search(query, top_k)
        return res
    
    
    
    def __embed_slice(self, slice: Slice):
        clip = slice.text[:30]
        # log.debug(f'Embedding slice {slice.id}: {clip}...')
        
        vector = self.text2vec.text2vec(slice.text)
        # log.debug(f'Vector: {vector}')
        
        # log.debug(f'Storing vector for slice {slice.id}...')
        meta = {
            **self.metadata,
            'slicer': 'markdown',
            'timestamp': time.time(),
        }
        self.store.upsert_text(slice.id, slice.text, meta)
        
        
            
