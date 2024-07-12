# PromptTemplate
import pytest
from examples.lab_template_prompt import PromptTemplate
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message


@pytest.mark.asyncio
async def test_prompt_template():
    
    async def get_contacts_async(lead: ConversationLead):
        return ["Juan", "Pedro", "Maria"]
    
    def get_balance(lead: ConversationLead, message: Message):
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

    p = PromptTemplate(prompt, lead=ConversationLead())
    res = await p.compile(state)
    
    assert res == """Hola, Juan. Tienes 5 mensajes nuevos.
Tiene los siguientes contactos: ["Juan", "Pedro", "Maria"].
Su saldo es: 
{"checking": 1000, "savings": 5000}"""