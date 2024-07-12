import pytest
import pytest_asyncio
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing.outgoing_message_link import OutgoingLinkMessage
from cel.gateway.model.outgoing.outgoing_message_select import OutgoingSelectMessage
from cel.gateway.model.outgoing.outgoing_message_text import OutgoingTextMessage
from cel.message_enhancers.smart_message_enhancer_openai import SmartMessageEnhancerOpenAI




@pytest_asyncio.fixture()
async def adapter() -> SmartMessageEnhancerOpenAI:
     return SmartMessageEnhancerOpenAI(model="gpt-3.5-turbo")


@pytest.mark.asyncio
async def test_enhancer_select(adapter: SmartMessageEnhancerOpenAI):
    lead = ConversationLead()
    
    text = """The text to convert:
         Choose a payment method. Available methods are:
- Cash
- Debit Card
- Credit Card"""
    
    res = await adapter(lead=lead, text=text, is_partial=False)
    
    assert isinstance(res, OutgoingSelectMessage)
    assert res.type == "select"
    assert len(res.options) == 3
    assert res.options[0] == "Cash"
    assert res.options[1] == "Debit Card"
    assert res.options[2] == "Credit Card"


@pytest.mark.asyncio
async def test_enhancer_select_2(adapter: SmartMessageEnhancerOpenAI):
    lead = ConversationLead()
    
    text = """Sí, puedo ayudarte a obtener el precio actual de las criptomonedas. 
¿Qué criptomoneda te gustaría consultar? Las opciones disponibles son BTC, ETH y ADA."""

    # Además, ¿en qué moneda te gustaría ver el precio? Las opciones son USD o ARS."""
    res = await adapter(lead=lead, text=text, is_partial=False)
    
    assert isinstance(res, OutgoingSelectMessage)
    assert res.type == "select"
    assert len(res.options) == 3
    assert res.options[0] == "BTC"
    assert res.options[1] == "ETH"
    assert res.options[2] == "ADA"


@pytest.mark.asyncio
async def test_enhancer_link(adapter: SmartMessageEnhancerOpenAI):
    lead = ConversationLead()
    
    text = """Please follow this link: https://auth.leap.com/ in order to authenticate you."""
    
    res = await adapter(lead=lead, text=text, is_partial=False)
    
    assert isinstance(res, OutgoingLinkMessage)
    assert res.type == "link"
    assert "follow" in res.content
    # links array must a contain a dictionary with url equal to https://auth.leap.com/
    assert any(link["url"] == "https://auth.leap.com/" for link in res.links)


@pytest.mark.asyncio
async def test_enhancer_text(adapter: SmartMessageEnhancerOpenAI):
    lead = ConversationLead()
    
    text = """Hi there! you have 10% discount on your next purchase."""
    
    res = await adapter(lead=lead, text=text, is_partial=False)
    
    assert isinstance(res, OutgoingTextMessage)
    assert res.type == "text"
    assert '10' in res.content
