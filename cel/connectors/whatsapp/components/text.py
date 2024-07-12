
from .component import Component



#  {
#     "type": "text",
#     "text": "replacement_text"
#   }
class Text(Component):
    def __init__(self, text: str) -> None:
        self.text = text

    def __str__(self):
        return f'{{"type": "text", "text": "{self.text}"}}'

    def __repr__(self):
        return f"TextComponent(text={self.text})"

    def __eq__(self, other):
        return self.text == other.text
    

if __name__ == "__main__":
    text = Text("replacement_text")
    print(text)
    # Expected output: '{"type": "text", "text": "replacement_text"}'

