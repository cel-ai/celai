import marko
from marko.block import Document
from abc import ABC
from dataclasses import dataclass, field

@dataclass
class Block(ABC):
    type: str
    text: str
    index: int
    breadcrumbs: list[str]

def build_breadcrumbs(doc: Document, current_index: int) -> list[str]:
    breadcrumbs = []
    current_level = float('inf')
    # iterate from current_index to the beginning of the document
    for block in reversed(doc.children[:current_index]):
        if doc.children.index(block) >= current_index:
            break
        if block.get_type().lower() == 'heading':
            level = block.level
            if level < current_level:
                current_level = level
                breadcrumbs.append(block.children[0].children)
    breadcrumbs.reverse()
    return breadcrumbs


def parse_markdown(md: str, split_table_rows: bool = False) -> list[Block]:
    from marko.md_renderer import MarkdownRenderer
    mdr = marko.Markdown(extensions=['gfm'], renderer=MarkdownRenderer)
    doc = mdr.parse(md)
    block_types = ['paragraph', 'code', 'blockquote', 'html', 'hr', 'list', 'listitem', 'table', 'tablerow', 'tablecell', 'strong', 'em', 'codespan', 'br', 'del', 'link', 'image', 'text'];

    blocks = []

    for child in doc.children:

        type = child.get_type().lower()
        
        if (type) in block_types:
            text = child.children[0].children
            child_index = doc.children.index(child)
            bc = build_breadcrumbs(doc, child_index)
            blocks.append(Block(type=type, text=text, index=child_index, breadcrumbs=bc))
            
        if type == 'table':
            table = []
            header = child.children[0].children
            rows = child.children[1:]
            
            if split_table_rows:
                header_text = ' | '.join([cell.children[0].children for cell in header])
                header_sepator = ' | '.join(['---' for cell in header])
                child_index = doc.children.index(child)
                bc = build_breadcrumbs(doc, child_index)            
                
                for row in rows:
                    row_text = ' | '.join([cell.children[0].children for cell in row.children])
                    # print(row_text)
                    table.append(f"{header_text}\n{header_sepator}\n{row_text}")
                    
                for row in table:
                    child_index = doc.children.index(child)
                    bc = build_breadcrumbs(doc, child_index)
                    blocks.append(Block(type='table', text=row, index=child_index, breadcrumbs=bc))
            else:
                table_text = mdr.render(child)
                bc = build_breadcrumbs(doc, child_index)
                blocks.append(Block(type='table', text=table_text, index=doc.children.index(child), breadcrumbs=bc))

                

    return blocks