import pytest
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.assistants.macaw.macaw_history_adapter import MacawHistoryAdapter
from cel.gateway.request_context import RequestContext
from cel.gateway.model.conversation_lead import ConversationLead
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# load envs
from dotenv import load_dotenv

from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
load_dotenv()



@pytest.fixture
def lead():
    lead = ConversationLead()
    return lead



    
@pytest.mark.asyncio
async def test_insight_with_events(lead: ConversationLead):

    insight_targets = {
        "marital_status": "Marital status: single, married, divorced, widowed",
        "age": "Age: 0-120",
        "childrens": "Number of children: 0-10",
        "income": "Income: 0-1000000",
        "location": "Location: city, country",
        "job": "Job: occupation",
        "hobbies": "Hobbies: list of hobbies",
    }
    
    lead = ConversationLead()
    history_store=InMemoryHistoryProvider()
    history_adapter = MacawHistoryAdapter(history_store)
    
    # new format:
    await history_adapter.append_to_history(lead, 
                                            HumanMessage("Hola mi nombre es Juan"))
    await history_adapter.append_to_history(lead, 
                                            AIMessage("Hola Juan, como estas?"))
    await history_adapter.append_to_history(lead, 
                                            HumanMessage("Bien! quiero enviar dinero a mi hijo"))
    await history_adapter.append_to_history(lead, 
                                            AIMessage("Claro! Cuanto dinero quieres enviar?"))
    await history_adapter.append_to_history(lead, 
                                            HumanMessage("Mi esposa dijo que le debia enviar $100"))
    

    assistant = MacawAssistant(
        insight_targets=insight_targets,
        history_store=history_store
    )
    
    @assistant.event('insights')
    async def handle_insight(session, ctx: RequestContext, data: dict):
        assert data is not None
        assert isinstance(data, dict)
        
    
    insights = await assistant.do_insights(lead, history_length=20)
    
    assert insights is not None
    assert insights.get("marital_status") is not None
    assert insights.get("childrens") is not None
