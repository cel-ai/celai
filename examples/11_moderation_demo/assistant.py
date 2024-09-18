"""
Hello World AI Assistant Example
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
- NGROK_AUTH_TOKEN: The ngrok authentication token for creating a public URL for your local server.
- TELEGRAM_TOKEN: The Telegram bot token for the assistant. You can get this from the BotFather on Telegram.
- OPENAI_API_KEY: The OpenAI API key for the assistant.

Then run this script to see a basic AI assistant in action.

Note:
-----
Please ensure you have the Cel.ai framework installed in your Python environment prior to running this script.
"""
# LOAD ENV VARIABLES
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
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.middlewares.moderation.openai_mod_endpoint import OpenAIEndpointModerationMiddleware, OpenAIEndpointModerationMiddlewareEvents
from cel.middlewares.in_mem_blacklist import InMemBlackListMiddleware
from cel.gateway.request_context import RequestContext
from cel.assistants.macaw.macaw_settings import MacawSettings

mod = OpenAIEndpointModerationMiddleware(enable_expiration=False) 
blacklist = InMemBlackListMiddleware(
    # return a messaje when the user is blacklisted
    # with emojis
    reject_message="🚫 Lo siento pero no puedo ayudarte en este momento 🚫"
)

# Setup prompt
prompt = """You are an AI assistant. Called Celia. You can help a user to buy Bitcoins."""
prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
# NOTE: Make sure to provide api key in the environment variable `OPENAI_API_KEY`
# add this line to your .env file: OPENAI_API_KEY=your-key
# or uncomment the next line and replace `your-key` with your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-key.."
ast = MacawAssistant(
    prompt=prompt_template
)

@ast.event(OpenAIEndpointModerationMiddlewareEvents.on_message_flagged)
def handler_on_message_flagged(session, ctx: RequestContext, data):
    count = data['count'] 
    log.critical(f"Message flagged counting: {count}")
    if count > 2:
        log.critical(f"Message flagged more than 3 times")
        # TODO: Ban user
        blacklist.add_to_black_list(ctx.lead.get_session_id(), ttl=20)
    else:
        if count > 4:
            log.critical(f"Message flagged more than 1 time")
            blacklist.add_to_black_list(ctx.lead.get_session_id(), ttl=60)
        


# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    assistant=ast,
    host="127.0.0.1", port=5004
)

# For this example, we will use the Telegram connector
conn = TelegramConnector(
    token=os.environ.get("TELEGRAM_TOKEN"), 
    # Try to set the stream mode to SENTENCE for a more natural conversation
    # SENTENCE mode will send the message to the user every time a sentence is completed
    stream_mode=StreamMode.FULL
)           
# Register the connector with the gateway
gateway.register_connector(conn)



gateway.register_middleware(mod)
gateway.register_middleware(blacklist)

# Then start the gateway and begin processing messages
gateway.run(enable_ngrok=True)


