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

Or if you want to test TogetherAI hosted llama3-guard-moderation, you can use the following environment variables:
- TOGETHERAI_API_KEY: The TogetherAI API key for the assistant.

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
from cel.middlewares.moderation.openai_mod_endpoint import OpenAIEndpointModerationMiddleware
from cel.middlewares.moderation.llama3_guard_togetherai import Llama3GuardModerationMiddleware
from cel.middlewares.moderation.moderation_events import ModMiddlewareEvents
from cel.middlewares.in_mem_blacklist import InMemBlackListMiddleware
from cel.gateway.request_context import RequestContext


# Uncomment the next line to use TogetherAI hosted llama3-guard-moderation
# --------------------------------------------------------------------------
# mod = Llama3GuardModerationMiddleware(
#     # Allow accumulation of flags expiring
#     # enable_expiration=True,
#     # Prunning interval in seconds, each 5 seconds 
#     # the middleware will check for expired flags
#     # prunning_interval=5,
#     # Expire after 5 seconds
#     # expire_after=5
# )

# OpenAI moderation middleware
# --------------------------------------------------------------------------
mod = OpenAIEndpointModerationMiddleware(
    # Allow accumulation of flags expiring
    # enable_expiration=True,
    # Prunning interval in seconds, each 5 seconds
    # the middleware will check for expired flags
    # prunning_interval=5,
    # Expire after 5 seconds
    # expire_after=5
)


# The blacklist middleware will be used to ban users
# Ban policy can be implemented in the on_message_flagged event 
blacklist = InMemBlackListMiddleware(
    # return a messaje when the user is blacklisted
    reject_message="🚫 Sorry, you are banned 🚫"
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

# Handle the on_message_flagged event rised by the moderation middleware on flagged messages
@ast.event(ModMiddlewareEvents.on_message_flagged)
def handler_on_message_flagged(session, ctx: RequestContext, data):
    count = data['count'] 
    
    log.critical(f"Message flagged counting: {count}")
    # If the message is flagged more than 3 times, ban the user for 20 seconds
    if count > 2:
        log.critical(f"Message flagged more than 3 times")
        # TODO: Ban user
        blacklist.add_to_black_list(ctx.lead.get_session_id(), ttl=20)
    else:
        # If the message is flagged more than 4 times, ban the user for 60 seconds
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


# Register the moderation middleware and the blacklist middleware
gateway.register_middleware(blacklist)
# Note that Blacklist middleware should be registered before the moderation middleware
# to prevent banned users from sending messages to further middlewares that may
# incur in inference costs
gateway.register_middleware(mod)


# Then start the gateway and begin processing messages
gateway.run(enable_ngrok=True)


