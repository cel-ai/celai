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



        
class SmartMessageEnhancerOpenAI:
    """ Enhances genAI output messages using OpenAI's GPT-3.5-turbo model.
    This will translate plain text messages into message structures 
    according to what the message wants to communicate. For example, 
    a message which is prompting the user to make a choice will be converted 
    into a message of type input_select with the information from the text. 
    The result must be a JSON.
    Later input_select will be converted by the gateway into a specific platform message 
    (e.g. a Telegram keyboard or a WhatsApp quick reply with the options).
    In order exploit the full potential of channels like WhatsApp and Telegram, 
    it is important to provide the right message structure.
    
    A message enhancer must be fail safe. If the enhancer fails to generate a message,
    it should return a simple text message with the original content.
    
    This enhancer is based on OpenAI's GPT-3.5-turbo model. If you want to use a different model,
    you can change the model parameter in the constructor.
    
    If you want to use a different fundational model, you can implement a new enhancer. 
    The enhancer should implement the __call__ method in this way:
    
    ```python
        async def __call__(self, lead: ConversationLead, 
                  text: str, 
                  is_partial: bool = True) -> OutgoingMessage:
                  
            ...your code here...
    ```
    
    """
    
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

        self.prompt = f"""You will convert plain text messages into message structures,
according to what the message wants to communicate.
For example, if the message asks the user to make a choice,
you will generate a message of type input_select with the information from the text.
The result must be a JSON.
                
Available message templates:
    {OutgoingTextMessage.description()}
    {OutgoingLinkMessage.description()}
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


