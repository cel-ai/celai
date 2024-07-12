from pathlib import Path

from cel.rag.slicers.markdown.utils import parse_markdown, Block
from ..base_slicer import Slicer, Slice
from loguru import logger as log


class MarkdownSlicer(Slicer):
    """Slice a markdown file. Each slice contains a breadcrumb, header, and text. 
    This slicer seeks for paragraphs, code blocks, blockquotes, tables, and lists.
    Then it creates a slice for each block found. 
    Recommended to use when you need pinpointed slices highly related to the document structure.
    
    For example: 
    
    ```markdown
    # Heading 1
    ## Heading 2
    This is a paragraph.
    ```
    
    Slice content:
    ```
    Heading 1 > Heading 2
    This is a paragraph.
    ```
    
    Breadcumbs are built from the headings found before the current block. 
    Usefull to keep track of the document structure in the slices.
    
    Args:
        file_path: Path to the file to load.

        encoding: File encoding to use. If `None`, the file will be loaded
        with the default system encoding.

        autodetect_encoding: Whether to try to autodetect the file encoding
            if the specified encoding fails.
            
        prefix: Prefix to add to the slice text.
        
        name: Name of the document.
        
        split_table_rows: Whether to split table rows into separate slices. Each slice contains a single breadcrumb+header+row.
        This is useful when you want to treat each row as a separate slice in the RAG model. Default is `False`.
        Recommended to set to `True` when the table is large and you want to avoid large slices.
    """

    def __init__(
        self,
        name: str,
        file_path: str | Path = None,
        content: str | None = None,
        encoding: str = None,
        prefix: str = None,
        split_table_rows: bool = False
    ):
        """Initialize with file path."""
        self.name = name
        self.file_path = file_path
        self.content = content
        self.prefix = prefix
        self.encoding = encoding
        self.split_table_rows = split_table_rows
        
        
    def __load_from_disk(self) -> str:
        
        if self.file_path is None:
            raise ValueError("No file path provided.")
        
        text = ""
        try:
            with open(self.file_path, encoding=self.encoding) as f:
                # read all content
                text = f.read()
                
        except UnicodeDecodeError:
            raise ValueError("Failed to load file with specified encoding.")
        except FileNotFoundError:
            raise ValueError(f"File not found: {self.file_path}")
        except Exception as e:
            raise ValueError(f"Failed to load file: {e}")    
        
            
        return text

    def __load(self) -> str:
        if self.content:
            return self.content
        return self.__load_from_disk()
        
        
    def slice(self) -> list[Slice]:
        slices=[]
        text = self.__load()        
        blocks = parse_markdown(text, split_table_rows=self.split_table_rows)
        
        for i, block in enumerate(blocks):
            log.debug(f"Block: {block}")
            log.debug('------------------------------------------')
        
            # concatenate breadcrumbs in a string
            bc_str = " > ".join(block.breadcrumbs or [])
        
            slice = Slice(
                id= f"{self.name}-{i}",
                text= f"{bc_str}\n{block.text}",
                metadata={
                    'type': block.type, 
                    'name': self.name,
                },
                source=self.name
            )
            slices.append(slice)
            
        return slices