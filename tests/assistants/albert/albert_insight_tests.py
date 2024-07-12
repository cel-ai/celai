import pytest
from cel.assistants.albert.albert_assistant import AlbertAssistant
from cel.gateway.request_context import RequestContext
from cel.gateway.model.conversation_lead import ConversationLead

# load envs
from dotenv import load_dotenv
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
    
    assistant = AlbertAssistant(insight_targets=insight_targets)
    
    @assistant.event('insigths')
    async def handle_insight(session, ctx: RequestContext, data: dict):
        global insights_from_event
        insights_from_event = data    
        
    await assistant.engine.add_user_message(lead, "Hola mi nombre es Juan")
    await assistant.engine.add_assistant_message(lead, "Hola Juan, como estas?")
    await assistant.engine.add_user_message(lead, "Bien! quiero enviar dinero a mi hijo")
    await assistant.engine.add_assistant_message(lead, "Claro! Cuanto dinero quieres enviar?")
    await assistant.engine.add_user_message(lead, "Mi esposa dijo que le debia enviar $100")
    
    insights = await assistant.do_insights(lead, history_length=20)
    
    assert insights is not None
    assert insights.get("marital_status") is not None
    assert insights.get("childrens") is not None
    assert insights_from_event is not None
