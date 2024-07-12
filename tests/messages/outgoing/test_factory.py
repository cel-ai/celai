from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing.outgoing_message_factory import outgoing_message_from_dict
from cel.gateway.model.outgoing.outgoing_message_text import OutgoingTextMessage
import dotenv

dotenv.load_dotenv()


    
def test_factory_text():

    lead = ConversationLead()
    sample = {
        "lead": lead,
        "type": "text",
        "content": "message content",
    }
    
    res = outgoing_message_from_dict(sample)
    
    assert isinstance(res, OutgoingTextMessage)
    assert res.type == "text"
    assert res.content == "message content"
    assert res.lead == lead
    
    
    
def test_factory_select():
    lead = ConversationLead()
    sample = {
        "lead": lead,
        "type": "select",
        "content": "message content",
        "options": ["option1", "option2"]
    }
    
    res = outgoing_message_from_dict(sample)
    
    assert res.type == "select"
    assert res.content == "message content"
    assert res.lead == lead
    assert res.options == ["option1", "option2"]
    

def test_factory_link():
    lead = ConversationLead()
    sample = {
        "lead": lead,
        "type": "link",
        "content": "message content",
        "links": [{"text": "link text", "url": "https://example.com"}]
    }
    
    res = outgoing_message_from_dict(sample)
    
    assert res.type == "link"
    assert res.content == "message content"
    assert res.lead == lead
    assert res.links[0]["url"] == "https://example.com"