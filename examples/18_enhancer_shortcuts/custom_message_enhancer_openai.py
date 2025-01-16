import json
from langchain_openai import ChatOpenAI
from loguru import logger as log
from langsmith import traceable
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.outgoing import OutgoingMessage,\
                                            outgoing_message_from_dict,\
                                            OutgoingLinkMessage,\
                                            OutgoingSelectMessage,\
                                            OutgoingTextMessage



        
class CustomMessageEnhancerOpenAI:

    
    def __init__(self, model="gpt-3.5-turbo", only_full_messages=True, **kwargs):
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            streaming=False,
            **kwargs
        )
        self.only_full_messages = only_full_messages

        self.prompt = f"""You will convert this plain text message into an object structure,
according to what the message wants to communicate.
If the messages asks or sujects to the user something, try to generate a message of type input_select with 
the information from the text.
The options must be extracted from the text as posibles actions choices.
Opstions must be as short as possible.
The result must be a JSON.
                
Available message templates:
    {OutgoingSelectMessage.description()}
"""
                
    async def __call__(self, lead: ConversationLead, 
                  text: str, 
                  is_partial: bool = True) -> OutgoingMessage:

        @traceable        
        async def smart_message_adapter():
            if is_partial and self.only_full_messages:
                log.debug(f"Skiping partial message: {text}")
                return OutgoingTextMessage(
                    lead=lead,
                    content=text
                )
            
            assert isinstance(lead, ConversationLead), \
                "lead must be an instance of ConversationLead"
            
            try:
                log.debug(f"Enhancing message: {text}")
                messages = [
                    (
                        "system",
                        f"{self.prompt}",
                    ),
                    ("system", f"Text to convert: {text}"),
                ]
                ai_msg = await self.llm.ainvoke(messages)
                log.debug(f"genAI enhanced message: {ai_msg}")
                # try to load json
                msg = json.loads(ai_msg.content)
                msg["lead"]=lead
                res = outgoing_message_from_dict(msg)
                return res

            except Exception as e:
                log.error(f"Error in enhance: {e}")
                
                # if there is an error, return a simple text message
                return OutgoingTextMessage(
                    lead=lead,
                    content=text
                )
                
        return await smart_message_adapter()


