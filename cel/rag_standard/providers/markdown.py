import os
from typing import List, Dict, Any, Optional, Union
from loguru import logger as log
import re
from pathlib import Path


class MarkdownProvider:
    """Provider for loading and processing markdown files for RAG"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the markdown provider
        
        Args:
            base_path: Base path for markdown files (if None, will use current directory)
        """
        self.base_path = base_path or os.getcwd()
        log.info(f"Initialized MarkdownProvider with base path: {self.base_path}")
    
    def load_file(self, file_path: str) -> str:
        """
        Load a markdown file
        
        Args:
            file_path: Path to the markdown file (relative to base_path)
            
        Returns:
            Content of the markdown file
        """
        full_path = os.path.join(self.base_path, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            log.info(f"Loaded markdown file: {file_path}")
            return content
        except Exception as e:
            log.error(f"Error loading markdown file {file_path}: {str(e)}")
            raise
    
    def load_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, str]:
        """
        Load all markdown files in a directory
        
        Args:
            directory_path: Path to the directory (relative to base_path)
            recursive: Whether to recursively load files in subdirectories
            
        Returns:
            Dictionary mapping file paths to their content
        """
        full_dir_path = os.path.join(self.base_path, directory_path)
        result = {}
        
        if recursive:
            for root, _, files in os.walk(full_dir_path):
                for file in files:
                    if file.endswith('.md'):
                        rel_path = os.path.relpath(os.path.join(root, file), self.base_path)
                        result[rel_path] = self.load_file(rel_path)
        else:
            for file in os.listdir(full_dir_path):
                if file.endswith('.md'):
                    rel_path = os.path.join(directory_path, file)
                    result[rel_path] = self.load_file(rel_path)
        
        log.info(f"Loaded {len(result)} markdown files from {directory_path}")
        return result
    
    def split_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split markdown content into chunks
        
        Args:
            content: Markdown content to split
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of content chunks
        """
        # First split by headers to keep related content together
        header_splits = re.split(r'(^|\n)#{1,6}\s+', content)
        
        chunks = []
        current_chunk = ""
        
        for i in range(1, len(header_splits), 2):
            header = header_splits[i]
            section_content = header_splits[i+1] if i+1 < len(header_splits) else ""
            
            # If adding this section would exceed chunk size, save current chunk and start a new one
            if len(current_chunk) + len(header) + len(section_content) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                # Include some overlap from the previous chunk
                current_chunk = current_chunk[-overlap:] if overlap > 0 else ""
            
            # Add header and content to current chunk
            current_chunk += f"# {header}{section_content}"
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        # If we still have chunks that are too large, split them further
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by paragraphs
                paragraphs = re.split(r'\n\n+', chunk)
                current_para_chunk = ""
                
                for para in paragraphs:
                    if len(current_para_chunk) + len(para) + 2 > chunk_size and current_para_chunk:
                        final_chunks.append(current_para_chunk)
                        current_para_chunk = current_para_chunk[-overlap:] if overlap > 0 else ""
                    
                    current_para_chunk += para + "\n\n"
                
                if current_para_chunk:
                    final_chunks.append(current_para_chunk)
        
        log.info(f"Split content into {len(final_chunks)} chunks")
        return final_chunks
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from markdown content (front matter)
        
        Args:
            content: Markdown content
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        # Check for YAML front matter
        front_matter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if front_matter_match:
            front_matter = front_matter_match.group(1)
            # Simple YAML parsing (not comprehensive)
            for line in front_matter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        
        # Extract title from first heading if not in metadata
        if 'title' not in metadata:
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                metadata['title'] = title_match.group(1)
        
        return metadata
    
    def process_file(self, file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """
        Process a markdown file into chunks with metadata
        
        Args:
            file_path: Path to the markdown file
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of dictionaries with chunk content and metadata
        """
        content = self.load_file(file_path)
        metadata = self.extract_metadata(content)
        chunks = self.split_content(content, chunk_size, overlap)
        
        result = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = i
            chunk_metadata['total_chunks'] = len(chunks)
            chunk_metadata['source_file'] = file_path
            
            result.append({
                'content': chunk,
                'metadata': chunk_metadata
            })
        
        return result
