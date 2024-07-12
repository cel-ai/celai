"""
Events and Middleware with Cel.ai
---------------------------------

This is a simple example of an AI Assistant implemented using the Cel.ai framework.
It serves as a basic demonstration of how to get started with Cel.ai for creating intelligent assistants.

Framework: Cel.ai
License: MIT License

This script is part of the Cel.ai example series and is intended for educational purposes.

Usage:
------
Configure the required environment variables in a .env file in the root directory of the project.
The required environment variables are:
- WEBHOOK_URL: The webhook URL for the assistant, you can use ngrok to create a public URL for your local server.
- TELEGRAM_TOKEN: The Telegram bot token for the assistant. You can get this from the BotFather on Telegram.

Then run this script to see a basic AI assistant in action.

Note:
-----
Please ensure you have the Cel.ai framework installed in your Python environment prior to running this script.
"""
# LOAD ENV VARIABLES
import asyncio
import os
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
from cel.gateway.request_context import RequestContext
from cel.middlewares.session_middleware import SessionMiddleware

# Setup prompt
prompt = "You are an assistant called Celia. Keep responses short and to the point.\
Don't use markdown formatting in your responses."
prompt_template = PromptTemplate(prompt)

session_middleware = SessionMiddleware()

# Create the assistant based on the Macaw Assistant 
# NOTE: Make sure to provide api key in the environment variable `OPENAI_API_KEY`
# add this line to your .env file: OPENAI_API_KEY=your-key
# or uncomment the next line and replace `your-key` with your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-key.."
ast = MacawAssistant(prompt=prompt_template)

# Core Event handler
# 'message' event is a native event that is triggered when a message is received
# ---------------------------------------------------------------------------
@ast.event('message') # Native event handler
async def handle_message(session, ctx: RequestContext):
    log.warning(f"Got message event with message!")
    # time since last request
    time_since_last_request = ctx.message.metadata.get('time_since_last_request', 0)
    log.critical(f"Time since last request: {time_since_last_request}")
    
# SessionMiddleware event handlers
# These are custom events that are triggered by the SessionMiddleware
# ---------------------------------------------------------------------------
@ast.event(SessionMiddleware.events.new_conversation) 
async def new_conversation(session, ctx: RequestContext):
    log.warning(f"New conversation started for session {session}")

@ast.event(SessionMiddleware.events.login)
async def login(session, ctx: RequestContext):
    log.warning(f"Login event for session {session}")

@ast.event(SessionMiddleware.events.logout)
async def logout(session, ctx: RequestContext):
    log.warning(f"Logout event for session {session}")
# ---------------------------------------------------------------------------

# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    webhook_url=os.environ.get("WEBHOOK_URL"),
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

gateway.register_middleware(session_middleware)

# Then start the gateway and begin processing messages
gateway.run()