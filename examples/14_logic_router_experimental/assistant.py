"""
Cel.ai Example: Logic Router Experimental
------------------------------------------

This is a simple example of an AI Assistant implemented using the Cel.ai framework.
It serves as a basic demonstration of how to get started with Cel.ai for 
creating intelligent assistants.

Framework: Cel.ai
License: MIT License

This script is part of the Cel.ai example series and is intended for educational purposes.

Usage:
------
Configure the required environment variables in a .env file in the root directory of the project.
The required environment variables are:
- NGROK_AUTHTOKEN: The Ngrok authentication token. You can get this from the Ngrok dashboard.
- TELEGRAM_TOKEN: The Telegram bot token for the assistant. You can get this from the BotFather on Telegram.
- OPENAI_API_KEY: The OpenAI API key for the assistant. You can get this from the OpenAI dashboard.

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
from cel.assistants.router.logic_router import LogicRouter
from cel.gateway.model.conversation_lead import ConversationLead
from balance_agent import build_balance_agent
from onboarding import build_onboarding_agent


# -------------------------------------------------------------------------
# Create the Logic Router
# -------------------------------------------------------------------------
# The Logic Router is a special type of assistant that routes messages 
# to other assistants allowing to handle multi-assistant system
# The Logic Router requires a list of assistants to route messages to
# and a function to select the assistant to use based on the user state
assistants = [
    # This assistant is used to onboard the user when 
    # they first start the conversation
    build_onboarding_agent(),
    # This assistant is used to handle balance enquiries
    build_balance_agent()
]


async def assistant_selector_func(lead: ConversationLead, state: dict, assistants: list):
    """ This function selects the assistant to use based on a variable in the user state """

    log.debug(f"Assistant Selector Function called with state: {state}")
    
    # NOTE: that the state is a dictionary that contains the user state
    # This functions are meant to access the state only in read mode
    # If you need to modify the state, you should do it in the assistant functions
    is_registered = state.get("is_registered", False)
    
    if not is_registered:
        log.warning("Redirect -> Onboarding Assistant")
        return assistants[0] 
    else:
        log.warning("Redirect -> Balance Assistant")
        return assistants[1]


# Instantiate the Agentic Router
ast = LogicRouter(
    assistants=assistants,
    # Set the assistant selector function to the one defined above
    # this function will route each message to the correct assistant
    # based on the user state variable: is_registered
    assistant_selector_func=assistant_selector_func
)
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------



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

# Then start the gateway and begin processing messages
gateway.run(enable_ngrok=True)


