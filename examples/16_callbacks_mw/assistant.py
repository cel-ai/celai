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
from cel.message_enhancers.smart_message_enhancer_openai import SmartMessageEnhancerOpenAI
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.assistants.function_context import FunctionContext
from cel.assistants.request_context import RequestContext
from cel.middlewares.callbacks.callback_middleware import CallbackdMiddleware

from datetime import datetime
date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Setup prompt
prompt = """You are an AI Assistant called Jane.
Today: {date}
"""
# https://localhost:5004/ouath2_calendar?code=4/0AX4XfWgq
# endpoint_path = "/ouath2_calendar"
# endpoint_verbs = ["GET"]


callback_middleware = CallbackdMiddleware(
    # endpoints = {
    #     'calendar_event': {
    #         'path': endpoint_path,
    #         'verbs': endpoint_verbs
    #     }
    # },
)


# callbackurl = callback_middleware.generate_url(lead, data)

prompt_template = PromptTemplate(prompt, initial_state={
        # Today full date and time
        "date": date,
    })


ast = MacawAssistant(prompt=prompt_template, state={})


# # in-context
@ast.callback('calendar_event')
async def handle_calendar_event(session, ctx: RequestContext, data):
    token = data['state']
    async with ctx.state_manager() as state:
        state['calendar_token'] = token
    
    ctx.response_text(f"Calendar token saved: {token}")
    
    ctx.connector.send_text_message("Gracias por tu pago!")
    
    return ctx.cancel_ai_response()


@ast.event('message')
async def handle_message(session, ctx: RequestContext):
    if ctx.message.text == "link":
        # TODO: generate a link to the calendar
        log.debug(f"Link request for:{ctx.lead.conversation_from.name}")
        url = callback_middleware.generate_callback_url(ctx.lead, 100)
        ctx.send_text_message(f"Link: {url}")
        return ctx.cancel_ai_response()


# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    assistant=ast,
    host="127.0.0.1", port=5004,
    message_enhancer=SmartMessageEnhancerOpenAI()
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

