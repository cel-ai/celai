import os
import sys
from loguru import logger as log

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cel.gateway.model.conversation_lead import ConversationLead
from cel.assistants.function_response import RequestMode
from cel.gateway.request_context import RequestContext
from cel.assistants.common import Param
from cel.assistants.function_context import FunctionContext
from cel.connectors.telegram import TelegramConnector
from cel.gateway.message_gateway import MessageGateway, StreamMode
from cel.rag.providers.markdown_rag import MarkdownRAG
from cel.middlewares import \
        DeepgramSTTMiddleware,\
        GeodecodingMiddleware,\
        InMemBlackListMiddleware,\
        SessionMiddleware
from simple_assistant_cli_cmds import register_client_commands
from cel.message_enhancers.smart_message_enhancer_openai import SmartMessageEnhancerOpenAI
from cel.connectors.whatsapp.whatsapp_connector import WhatsappConnector
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate

# load env variables
from dotenv import load_dotenv
load_dotenv()

log.remove()
log.add(sys.stdout, format="<level>{level: <8}</level> | "
    "<cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")



if __name__ == "__main__":
    
    # Register blacklist middleware
    blacklist = InMemBlackListMiddleware()
    auth = SessionMiddleware()
    stt = DeepgramSTTMiddleware()
    geodecoding = GeodecodingMiddleware()
    
    insight_targets = {
        "last_conversation_topic": "Last conversation topic",
        "marital_status": "Marital status: single, married, divorced, widowed",
        "age": "Age: 0-120",
        "childrens": "Number of children: 0-10",
        "income": "Income: 0-1000000",
        "location": "Location: city, country",
        "job": "Job: occupation",
        "hobbies": "Hobbies: list of hobbies",
    }
    
    prompt = """You are a banking assistant. Called {assistant_name}. You can help a user to send money.
    The customer name is {customer_name}.
    In order to send money, the user needs to select a payment method and provide the amount to send.
    The user can also check the current price of a cryptocurrency.
    The allowed cryptocurrencies are: BTC, ETH, ADA.
    Last conversation topic:{conversation_topic} (Ask something related to this topic)
    """
    
    prompt_template = PromptTemplate(prompt)
    
    async def get_customer_name(lead: ConversationLead):
        if lead.conversation_from.name:
            return lead.conversation_from.name
        else:
            return "'unknown name'"

    
    ast = MacawAssistant(
        prompt=prompt_template, 
        insight_targets=insight_targets,
        state={
            "assistant_name": "Celia",
            "customer_name": get_customer_name
        }
    )
    
    mdm = MarkdownRAG("demo", file_path="examples/smoothy.md", split_table_rows=True)
    mdm.load()

    ast.set_rag_retrieval(mdm)
    
    
    @ast.function('choose_payment_method', 'Customer needs to select a payment method', [])
    async def handle_get_cryptocurrency_price(session, params, ctx: FunctionContext):
        log.critical(f"Got choose_payment_method call with params: {params}")
        
        available_payment_methods = ["Credit Card", 
                                     "Debit Card", 
                                     "Paypal", 
                                     "Bitcoin"]
        
        return FunctionContext.\
            response_text(f"Choose a payment method. Available methods are: {', '.join(available_payment_methods)}", 
                          request_mode=RequestMode.SINGLE)

    
    @ast.function('get_cryptocurrency_price', 'Get the current cryptocurrency price', [
        Param(name='asset', type='string', description='Cryptocurrency name eg. BTC, ETH', required=True),
        Param(name='currency', type='string', description='Currency name eg. USD, ARS', required=False, enum=['USD', 'ARS'])
    ])
    async def handle_get_cryptocurrency_price(session, params, ctx: FunctionContext):
        log.critical(f"Got get_cryptocurrency_price call with params: {params}")
        prices = {
            "BTC": 50000,
            "ETH": 3000,
            "ADA": 2.5,
        }
        asset = params.get("asset", "BTC")
        price = prices.get(params.get("asset", "BTC"), 0)
        return FunctionContext.response_text(f"The price of {asset} is {price}", request_mode=RequestMode.SINGLE)
    
    @ast.event('insights')
    async def handle_insight(session, ctx: RequestContext, data: dict):
        log.warning(f"Got insights event with data: {data}")
    
    
    @ast.event('message')
    async def handle_message(session, ctx: RequestContext):
        log.critical(f"Got message event with message!")
        
        
        if ctx.message.text == "ping":
            # test response text skipping AI response
            return RequestContext.response_text("pong", disable_ai_response=True)
        
        if "link" in ctx.message.text:
            conn = ctx.connector
            
            if conn.name() == "telegram":
                assert isinstance(conn, TelegramConnector), "Connector must be an instance of TelegramConnector"
                links = [
                    {"text": "Go to Google", "url": "https://www.google.com"},
                    {"text": "Go to Facebook", "url": "https://www.facebook.com"}
                ]
                await conn.send_link_message(ctx.lead, text="Please follow this link", links=links)
                
            if conn.name() == "whatsapp":
                assert isinstance(conn, WhatsappConnector), "Connector must be an instance of WhatsappConnector"
                links = [
                    {"text": "Go to Google", "url": "https://www.google.com"},
                    {"text": "Go to Facebook", "url": "https://www.facebook.com"}
                ]
                await conn.send_link_message(ctx.lead, text="Please follow this link", links=links)
                
            return RequestContext.response_text("Message type link sent", disable_ai_response=True)
                
        
        if "select" in ctx.message.text:
            conn = ctx.connector
            splited = ctx.message.text.split(" ")
            num = 1
            if len(splited) < 2:
                num = 3
            else:   
                num = int(splited[-1])
            
            options = [f"Option {i}" for i in range(1, num+1)]
            
            if conn.name() == "telegram":
                assert isinstance(conn, TelegramConnector), "Connector must be an instance of TelegramConnector"
                await conn.send_select_message(ctx.lead, "Select an option", options=options)
                return RequestContext.cancel_response()
                
            if conn.name() == "whatsapp":
                assert isinstance(conn, WhatsappConnector), "Connector must be an instance of WhatsappConnector"
                await conn.send_select_message(ctx.lead, "Select an option", options=options)
                return RequestContext.cancel_response()

            return RequestContext.response_text("", disable_ai_response=True)
        
        if "echo:" in ctx.message.text:
            # Test echoing the message
            text = ctx.message.text.replace("echo:", "")
            await MessageGateway.send_text_message(ctx.lead, text)
            return RequestContext.response_text("Message echoed", disable_ai_response=True)
        
        
        if "blend:" in ctx.message.text:
            # Test blending into conversation context 
            text = ctx.message.text.replace("blend:", "")
            return RequestContext.response_text(text, blend=True)
        
        if "banme" in ctx.message.text:
            # Add user to blacklist and return a response
            blacklist.add_to_black_list(ctx.lead.get_session_id(), 
                                        InMemBlackListMiddleware(reason="User requested to be banned"))
            return RequestContext.response_text("You are now banned", disable_ai_response=True)


    register_client_commands(ast)

    gateway = MessageGateway(
        webhook_url=os.environ.get("WEBHOOK_URL"),
        assistant=ast,
        host="127.0.0.1", port=5004,
        message_enhancer=SmartMessageEnhancerOpenAI()
    )
    
    gateway.register_middleware(auth)
    gateway.register_middleware(stt)
    gateway.register_middleware(geodecoding)
    # gateway.register_middleware(blacklist)
    
    conn = TelegramConnector(token=os.environ.get("TELEGRAM_TOKEN"), 
                             stream_mode=StreamMode.FULL)
    gateway.register_connector(conn)
    
    
    conn2 = WhatsappConnector(token=os.getenv("WHATSAPP_TOKEN"), 
                        phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID"),
                        verify_token="123456",
                        endpoint_prefix="/whatsapp",
                        stream_mode=StreamMode.FULL)
    gateway.register_connector(conn2)
    
    gateway.run()
