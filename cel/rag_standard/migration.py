"""
Migration utilities for transitioning from cel.rag to cel.rag_standard
"""

from typing import Dict, Any, List, Optional
from loguru import logger as log

from cel.rag.stores.vector_store import VectorStore as LegacyVectorStore
from cel.rag_standard.stores.vector_store import VectorStore as StandardVectorStore


def migrate_store(
    legacy_store: LegacyVectorStore,
    standard_store: StandardVectorStore,
    batch_size: int = 100,
    callback=None
) -> Dict[str, Any]:
    """
    Migrate data from a legacy vector store to a standard vector store
    
    Args:
        legacy_store: The legacy vector store to migrate from
        standard_store: The standard vector store to migrate to
        batch_size: The number of vectors to migrate in each batch
        callback: Optional callback function to report progress
        
    Returns:
        Dict with migration statistics
    """
    log.info("Starting migration from legacy store to standard store")
    
    # Get all vectors from the legacy store
    # This is a simplified example - in a real implementation,
    # you would need to implement a way to get all vectors from the legacy store
    # For example, you might need to implement a method to list all IDs
    
    # For demonstration purposes, we'll assume we have a way to get all IDs
    # In a real implementation, you would need to implement this
    try:
        # This is a placeholder - you would need to implement a way to get all IDs
        # from your legacy store
        all_ids = legacy_store.get_all_ids()
    except AttributeError:
        log.warning("Legacy store does not have a get_all_ids method")
        log.warning("Migration will only work for stores that implement this method")
        return {"error": "Legacy store does not have a get_all_ids method"}
    
    total_vectors = len(all_ids)
    migrated_vectors = 0
    failed_vectors = 0
    
    log.info(f"Found {total_vectors} vectors to migrate")
    
    # Migrate vectors in batches
    for i in range(0, total_vectors, batch_size):
        batch_ids = all_ids[i:i+batch_size]
        
        for id in batch_ids:
            try:
                # Get vector from legacy store
                vector_register = legacy_store.get_vector(id)
                
                # Upsert to standard store
                standard_store.upsert(
                    id=vector_register.id,
                    vector=vector_register.vector,
                    text=vector_register.text,
                    metadata=vector_register.metadata
                )
                
                migrated_vectors += 1
            except Exception as e:
                log.error(f"Failed to migrate vector {id}: {e}")
                failed_vectors += 1
        
        # Report progress
        progress = (i + len(batch_ids)) / total_vectors * 100
        log.info(f"Migration progress: {progress:.2f}% ({i + len(batch_ids)}/{total_vectors})")
        
        if callback:
            callback(progress, migrated_vectors, failed_vectors)
    
    log.info(f"Migration complete. Migrated {migrated_vectors} vectors, failed {failed_vectors} vectors")
    
    return {
        "total_vectors": total_vectors,
        "migrated_vectors": migrated_vectors,
        "failed_vectors": failed_vectors,
        "success_rate": migrated_vectors / total_vectors * 100 if total_vectors > 0 else 0
    }


def create_migration_guide():
    """
    Create a migration guide for users transitioning from cel.rag to cel.rag_standard
    """
    guide = """
# Migration Guide: cel.rag to cel.rag_standard

## Overview

This guide will help you migrate your code from the legacy `cel.rag` package to the new `cel.rag_standard` package.

## Key Changes

1. **Improved Type Hints**: The new package uses more comprehensive type hints for better IDE support and type checking.
2. **Better Error Handling**: The new implementation includes more robust error handling with detailed error messages.
3. **Consistent API**: The API has been standardized for better consistency and predictability.
4. **New Features**: The new implementation includes additional features such as the `clear()` method for vector stores.

## Migration Steps

### 1. Update Imports

Replace:
```python
from cel.rag.stores.vector_store import VectorStore, VectorRegister
from cel.rag.stores.chroma.chroma_store import ChromaStore
from cel.rag.text2vec.utils import Embedding
```

With:
```python
from cel.rag_standard.stores import VectorStore, VectorRegister, ChromaStore
from cel.rag_standard.text2vec import Embedding
```

### 2. Update Code

The API is largely compatible, but there are some changes to be aware of:

- The `VectorRegister` class now includes an optional `distance` field
- The `search()` method now has a default value of 1 for the `top_k` parameter
- The `VectorStore` interface now includes a `clear()` method

### 3. Migrate Data (Optional)

If you want to migrate your existing data to the new implementation, you can use the migration utility:

```python
from cel.rag_standard.migration import migrate_store
from cel.rag.stores.chroma.chroma_store import ChromaStore as LegacyChromaStore
from cel.rag_standard.stores.chroma import ChromaStore as StandardChromaStore

# Initialize your stores
legacy_store = LegacyChromaStore(...)
standard_store = StandardChromaStore(...)

# Migrate data
result = migrate_store(legacy_store, standard_store)
print(f"Migration complete: {result}")
```

## Example

### Before:

```python
from cel.rag.stores.chroma.chroma_store import ChromaStore
from cel.rag.text2vec.utils import Embedding

# Initialize store
store = ChromaStore(text2vec_provider, collection_name="my_collection")

# Search
results = store.search("my query", top_k=5)
for result in results:
    print(f"ID: {result.id}, Text: {result.text}, Distance: {result.distance}")
```

### After:

```python
from cel.rag_standard.stores import ChromaStore
from cel.rag_standard.text2vec import Embedding

# Initialize store
store = ChromaStore(text2vec_provider, collection_name="my_collection")

# Search
results = store.search("my query", top_k=5)
for result in results:
    print(f"ID: {result.id}, Text: {result.text}, Distance: {result.distance}")
```

## Need Help?

If you encounter any issues during migration, please open an issue on our GitHub repository.
"""
    
    return guide 