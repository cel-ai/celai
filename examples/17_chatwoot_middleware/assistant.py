# LOAD ENV VARIABLES
import os
import time
import json
from loguru import logger as log
# Load .env variables
from dotenv import load_dotenv





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
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.assistants.function_context import FunctionContext
from cel.assistants.request_context import RequestContext
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.middlewares.chatwoot.middleware import ChatwootMiddleware

from datetime import datetime
date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Setup prompt
prompt = """You are an AI Assistant called Jane.
Today: {date}
"""


woot = ChatwootMiddleware(
    base_url=os.environ.get("CHATWOOT_URL"),
    access_key=os.environ.get("CHATWOOT_ACCESS_KEY"), 
    account_id=os.environ.get("CHATWOOT_ACCOUNT_ID"), 
    inbox_name="demo_api_channel",
    auto_create_inbox=True
)



prompt_template = PromptTemplate(prompt, initial_state={
        # Today full date and time
        "date": date,
    })

ast = MacawAssistant(prompt=prompt_template, state={})



@ast.event('message')
async def handle_message(session, ctx: RequestContext):
    
    if ctx.message.text.startswith("echo:"):
        #  split the message by space
        parts = ctx.message.text.split(":")
        # get the second part of the message
        await ctx.send_text_message("Echo: " + parts[1])
        return ctx.cancel_ai_response()

    if ctx.message.text.startswith("private:"):
        #  split the message by space
        parts = ctx.message.text.split(":")
        # get the second part of the message
        await ctx.send_text_message("Private: " + parts[1], is_private=True)
        return ctx.cancel_ai_response()


# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    assistant=ast,
    host="127.0.0.1", port=5004
)

# For this example, we will use the Telegram connector
conn = TelegramConnector(
    token=os.environ.get("TELEGRAM_TOKEN"), 
    stream_mode=StreamMode.FULL
)

# Register the connector with the gateway
gateway.register_connector(conn)

# Register the middleware with the gateway
gateway.register_middleware(woot)

# Then start the gateway and begin processing messages
gateway.run(enable_ngrok=True)

