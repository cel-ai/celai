# LOAD ENV VARIABLES
import os
import time
from loguru import logger as log
# Load .env variables
from dotenv import load_dotenv

from cel.gateway.model.outgoing.outgoing_message_buttons import OutgoingButtonsMessage
from cel.gateway.model.outgoing.outgoing_message_select import OutgoingSelectMessage
load_dotenv(override=True)


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
from cel.assistants.request_context import RequestContext
from cel.connectors.whatsapp.whatsapp_connector import WhatsappConnector

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
    
    if ctx.message.text.startswith("select:"):
        #  split the message by space
        parts = ctx.message.text.split(":")
        # get the second part of the message
        # split ,
        parts = parts[1].split(",")
        assert isinstance(ctx.connector, WhatsappConnector)
        out = OutgoingSelectMessage(
            lead=ctx.lead,
            content="Select an option",
            options=parts,
            list_title="List Title",
            button="View Options"
        )
        await ctx.connector.send_message(out)
        return ctx.cancel_ai_response()    

    if ctx.message.text.startswith("select2:"):
        #  split the message by space
        parts = ctx.message.text.split(":")
        # get the second part of the message
        # split ,
        parts = parts[1].split(",")
        assert isinstance(ctx.connector, WhatsappConnector)
        await ctx.connector.send_select_message(
            lead=ctx.lead, 
            options=parts,
            text="Select an option",
            header="Header",
            footer="Footer",
            list_title="List Title",
            button_text="View Options"
        )
        return ctx.cancel_ai_response()
    
    if ctx.message.text.startswith("buttons:"):
        #  split the message by space
        parts = ctx.message.text.split(":")
        # get the second part of the message
        # split ,
        parts = parts[1].split(",")
        assert isinstance(ctx.connector, WhatsappConnector)
        out = OutgoingButtonsMessage(
            lead=ctx.lead,
            content="Press a button",
            options=parts
        )
        await ctx.connector.send_message(out)
        return ctx.cancel_ai_response()




# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    webhook_url=os.environ.get("WEBHOOK_URL"),
    assistant=ast,
    host="127.0.0.1", port=5005,
    # message_enhancer=CustomMessageEnhancerOpenAI()
)



conn = WhatsappConnector(
    token=os.environ.get("WHATSAPP_TOKEN"),
    phone_number_id=os.environ.get("WHATSAPP_PHONE_NUMBER_ID"),
    verify_token=os.environ.get("WHATSAPP_VERIFY_TOKEN"),
    stream_mode=StreamMode.FULL
)


# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run(enable_ngrok=False)