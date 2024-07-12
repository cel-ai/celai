import pytest
from cel.gateway.model.conversation_lead import ConversationLead
from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.rag.stores.chroma.chroma_store import ChromaStore
from cel.rag.text2vec.cached_openai import CachedOpenAIEmbedding
import dotenv

dotenv.load_dotenv()

sample_message = {
       "message_id":123,
       "from":{
          "id":1320141991,
          "is_bot": False,
          "first_name":"John Doe",
          "username":"john_doe",
          "language_code":"en"
       },
       "chat":{
          "id":1320141991,
          "first_name":"John Doe",
          "username":"john_doe",
          "type":"private"
       },
       "date":1716850049,
       "text":"Hello!"
    }


# @pytest.fixture
# def fix():
#     pass

    
def test_lead():

    lead = ConversationLead()
    
    d = lead.to_dict()
    
    assert d.get("connector_name") == "unknown"
    assert d.get("metadata") == None
    
def test_telegram_lead():
    
    lead = TelegramLead("chat_id/123", metadata={})
    
    d = lead.to_dict()
    
    assert d.get("connector_name") == "telegram"
    assert d.get("metadata") == {}
    assert d.get("chat_id") == "chat_id/123"
    
def test_telegram_lead_from_dict():
    
    lead = TelegramLead("chat_id/123", metadata={})
    
    d = lead.to_dict()
    
    assert d.get("connector_name") == "telegram"
    assert d.get("metadata") == {}
    assert d.get("chat_id") == "chat_id/123"
    
    lead2 = TelegramLead.from_dict(d)
    
    assert lead2.chat_id == "chat_id/123"
    assert lead2.metadata == {}
    assert lead2.connector_name == "telegram"
    
def test_telegram_lead_from_message():
    
    lead = TelegramLead.from_telegram_message(sample_message)
    
    assert lead.chat_id == "1320141991"
    assert lead.metadata == {
        'message_id': "123",
        'date': 1716850049,
        'raw': sample_message
    }
    assert lead.connector_name == 'telegram'
    assert lead.conversation_from.name == 'John Doe'
    assert lead.conversation_from.id == "1320141991"
