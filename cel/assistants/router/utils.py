from cel.gateway.model.conversation_lead import ConversationLead
from cel.stores.history.base_history_provider import BaseHistoryProvider
from langchain.load.load import load



async def build_router_query (history_store: BaseHistoryProvider, lead: ConversationLead, text: str, length: int = 5):
    history = await history_store.get_history(lead.get_session_id())
    # Create a list of the last N messages without tools and tool_calls
    messages = []
    for h in history:
        aux = load(h)
        role = aux.type 
        text = aux.content
        
        # Skip tools and tool_calls
        if role == "tool" or role == "tool_call":
            continue
        
        messages.append({
            "role": role,
            "text": text
        })

    # Get the last N messages
    last_messages = messages[-length:]
    return last_messages


