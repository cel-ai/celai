"""
Hello World AI Assistant Example
---------------------------------

This is a simple example of an AI Assistant implemented using the Cel.ai framework.
It serves as a basic demonstration of how to implment an Invitation Midlleware 
in Cel.ai for creating intelligent assistants.

Framework: Cel.ai
License: MIT License

This script is part of the Cel.ai example series and is intended for educational purposes.

Usage:
------
Configure the required environment variables in a .env file in the root directory of the project.
The required environment variables are:
- NGROK_AUTH_TOKEN: The ngrok authentication token for creating a public URL for your local server.
- WEBHOOK_URL: The webhook URL for the assistant, you can use ngrok to create a public URL for your local server.
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
from cel.message_enhancers.smart_message_enhancer_openai import SmartMessageEnhancerOpenAI
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.middlewares.invitation_guard import InvitationGuardMiddleware
from cel.gateway.request_context import RequestContext

# Setup prompt
prompt = """You are an AI assistant. Called Celia. 
Keep answers short and to the point.
You can help a user to buy Bitcoins."""
prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
# NOTE: Make sure to provide api key in the environment variable `OPENAI_API_KEY`
# add this line to your .env file: OPENAI_API_KEY=your-key
# or uncomment the next line and replace `your-key` with your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-key.."
ast = MacawAssistant(
    prompt=prompt_template
)

@ast.event("")
async def handle_insight(session, ctx: RequestContext, data: dict):
    log.warning(f"Got insights event with data: {data}")



# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    assistant=ast,
    host="127.0.0.1", port=5004,
    
    # Secure Gateway API - This API holds endpoints for managing the assistant
    # From connectos to middlewares and the assistant itself
    # In order to access the API, you need to provide the gateway_api_key in the header
    # The only method that is not protected is the /health and connectos endpoints
    gateway_api_key="ASD123",
    gateway_api_key_header="x-api-key",
)

# For this example, we will use the Telegram connector
conn = TelegramConnector(
    token=os.environ.get("TELEGRAM_TOKEN"), 
    # Try to set the stream mode to SENTENCE for a more natural conversation
    # SENTENCE mode will send the message to the user every time a sentence is completed
    stream_mode=StreamMode.FULL
)

# Register Invitation Midlleware
guard = InvitationGuardMiddleware(
    # For development purposes, you can set the master key and backdoor invite
    # master key will allows you to login as an admin and gain 
    # prmissions to run client commands.
    master_key="123456",
    # Backdoor invite will allow you to bypass the invitation 
    # process and gain access to the assistant
    backdoor_invite_code="#QWERTY",
    telegram_bot_name="lola_lionel_bot",
    allow_only_invited=True
)
gateway.register_middleware(guard)

# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run(enable_ngrok=True)
