# LOAD ENV VARIABLES
import os
import time
import json
from loguru import logger as log
# Load .env variables
from dotenv import load_dotenv

from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.model.message_gateway_context import MessageGatewayContext


load_dotenv()


# REMOVE THIS BLOCK IF YOU ARE USING THIS SCRIPT AS A TEMPLATE
# -------------------------------------------------------------
import sys
from pathlib import Path
# Add parent directory to path
path = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(path.parents[1]))
# -------------------------------------------------------------

# Import Cel.ai modules
from cel.connectors.telegram import TelegramConnector
from cel.gateway.message_gateway import MessageGateway, StreamMode
from cel.message_enhancers.smart_message_enhancer_openai import SmartMessageEnhancerOpenAI
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.assistants.function_context import FunctionContext
from cel.assistants.request_context import RequestContext
from cel.gateway.http_callbacks import HttpCallbackProvider

conn = TelegramConnector(
    token="123:ASD"
)

lead = TelegramLead(
    connector=conn,
    chat_id="123456789"
)

cm = HttpCallbackProvider(
    chat_url="https://www.google.com",
    endpoint="callback",
    http_verb="GET"
)


def on_startup(context: MessageGatewayContext):
    
    async def handle_callback(lead: TelegramLead, data: dict):
        log.warning(f"Callback received from {lead} with data: {data}")
        
        
    cm.setup(context)
    url = cm.create_callback(lead, 
                             handle_callback, 
                             ttl=20, 
                             single_use=True,
                             redirect_url="https://www.google.com")
    
    log.warning(f"Callback URL: {url}?data=SARASA123")




gateway = MessageGateway(
    assistant=MacawAssistant(),
    on_startup=on_startup
)

gateway.run(enable_ngrok=True)