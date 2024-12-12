import pytest
from cel.connectors.telegram.telegram_connector import TelegramConnector
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


@pytest.fixture
def connector():
    # Create Telegram Connector
    return TelegramConnector(token="123:ASD")

    
def test_lead(connector):

    lead = ConversationLead(connector=connector)
    
    d = lead.to_dict()
    
    assert d.get("connector_name") == connector.name()
    assert d.get("metadata") == None
    
def test_telegram_lead(connector):
    
    lead = TelegramLead("chat_id/123", metadata={}, connector=connector)
    
    d = lead.to_dict()
    
    assert d.get("connector_name") == connector.name()
    assert d.get("metadata") == {}
    assert d.get("chat_id") == "chat_id/123"
    
def test_telegram_lead_from_dict(connector):
    
    lead = TelegramLead("chat_id/123", metadata={}, connector=connector)
    
    d = lead.to_dict()
    
    assert d.get("connector_name") ==  connector.name()
    assert d.get("metadata") == {}
    assert d.get("chat_id") == "chat_id/123"
    
    lead2 = TelegramLead.from_dict(d)
    
    assert lead2.chat_id == "chat_id/123"
    assert lead2.metadata == {}
    assert lead2.connector_name == connector.name()
    
def test_telegram_lead_from_message(connector):
    
    lead = TelegramLead.from_telegram_message(sample_message, connector=connector)
    
    assert lead.chat_id == "1320141991"
    assert lead.metadata == {
        'message_id': "123",
        'date': 1716850049,
        'raw': sample_message
    }
    assert lead.connector_name == connector.name()
    assert lead.conversation_from.name == 'John Doe'
    assert lead.conversation_from.id == "1320141991"
