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

# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    webhook_url=os.environ.get("WEBHOOK_URL"),
    assistant=ast,
    host="127.0.0.1", port=5004,
    message_enhancer=SmartMessageEnhancerOpenAI(),
    
    # Activate the delivery rate control to prevent 
    # the assistant from sending too many messages too quickly
    # This only works when the connector is in SENTENCE mode
    # delivery_rate_control=True
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

# Then start the gateway and begin processing messages
gateway.run()

