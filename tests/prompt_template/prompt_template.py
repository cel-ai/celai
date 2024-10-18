# PromptTemplate
import pytest
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from cel.prompt.prompt_template import PromptTemplate


@pytest.fixture
def lead():
    lead = ConversationLead()
    return lead


@pytest.mark.asyncio
async def test_prompt_template(lead):
    
    async def get_contacts_async(lead: ConversationLead, state: dict, session_id: str):
        assert isinstance(lead, ConversationLead)
        assert isinstance(state, dict)
        assert isinstance(session_id, str)
        state["contacts"] = ["Juan", "Pedro", "Maria"]
        return ["Juan", "Pedro", "Maria"]
    
    def get_balance(lead: ConversationLead, message: str):
        assert isinstance(lead, ConversationLead)
        assert isinstance(message, str)
        assert message == "Hola"
        
        return {
            "checking": 1000,
            "savings": 5000
        }
    
    # Ejemplo de uso
    prompt = """Hola, {name}. Tienes {messages} mensajes nuevos.
Tiene los siguientes contactos: {contacts}.
Su saldo es: \n{balance}"""

    state = {
        "name": "Juan",
        "messages": lambda: 5,
        "contacts": get_contacts_async,
        "balance": get_balance
    }

    p = PromptTemplate(prompt)
    res = await p.compile(state, lead, "Hola")
    
    assert res == """Hola, Juan. Tienes 5 mensajes nuevos.
Tiene los siguientes contactos: ['Juan', 'Pedro', 'Maria'].
Su saldo es: 
{"checking": 1000, "savings": 5000}"""