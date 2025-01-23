# LOAD ENV VARIABLES
import os
import time
from loguru import logger as log
# Load .env variables
from dotenv import load_dotenv

from cel.assistants.request_context import RequestContext
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
from cel.rag.providers.markdown_rag import MarkdownRAG
from cel.assistants.function_context import FunctionContext
from cel.assistants.function_response import RequestMode
from cel.assistants.common import Param
from custom_message_enhancer_openai import CustomMessageEnhancerOpenAI

from datetime import datetime
# date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    


# Setup prompt
prompt = """You are an assistant that helps with sending cross-border money transfers, 
also known as remittances. When greeting the customer, 
ask if they would like to send money, as this is usually the most likely scenario. 
If the customer wants to send money, first ask which country they are sending it to.
The amount to be sent should be in US dollars. 
The most common amounts are: 100, 200, 300, 500, 1000.

Permitted destination countries:
- Mexico
- Colombia
- Argentina
- Venezuela

"""


prompt_template = PromptTemplate(prompt, initial_state={
        # Today full date and time
        "date": get_current_date,
    })


ast = MacawAssistant(prompt=prompt_template, state={})



@ast.event('message')
async def handle_message(session, ctx: RequestContext):
    async with ctx.state_manager() as state:
        count = state.get("count", 0)
        count += 1
        state["count"] = count
        log.warning(f"Message count: {count}")



# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    assistant=ast,
    host="127.0.0.1", port=5004,
    message_enhancer=CustomMessageEnhancerOpenAI()
)

# For this example, we will use the Telegram connector
conn = TelegramConnector(
    token=os.environ.get("TELEGRAM_TOKEN"), 
    stream_mode=StreamMode.FULL
)
# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run(enable_ngrok=True)


