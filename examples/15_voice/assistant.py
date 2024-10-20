"""
STT/TTS with Cel.ai
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

- NGROK_AUTH_TOKEN: The Ngrok authentication token. You can get this from the Ngrok dashboard.
- TELEGRAM_TOKEN: The Telegram bot token for the assistant. You can get this from the BotFather on Telegram.

Also becuase this example uses the ElevenLabs and Deepgram APIs, you need to set the following environment variables:
- ELEVENLABS_API_KEY: The ElevenLabs API key for the assistant. You can get this from the ElevenLabs dashboard.
- DEEPGRAM_API_KEY: The Deepgram API key for the assistant. You can get this from the Deepgram dashboard.


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
from cel.assistants.request_context import RequestContext
from cel.voice.elevenlabs_adapter import ElevenLabsAdapter
from cel.middlewares.deepgram_stt import DeepgramSTTMiddleware


# Setup prompt
prompt = "You are an assistant called Celia. Keep responses short and to the point.\
Don't use markdown formatting in your responses."
    
prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
# NOTE: Make sure to provide api key in the environment variable `OPENAI_API_KEY`
# add this line to your .env file: OPENAI_API_KEY=your-key
# or uncomment the next line and replace `your-key` with your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-key.."
ast = MacawAssistant(prompt=prompt_template)

# Event handler for the message event
# ---------------------------------------------------------------------------
@ast.event('message')
async def handle_message(session, ctx: RequestContext):
    log.debug(f"Got message event with message!")
    
    if ctx.message.text == "ping":
        await ctx.send_text_message("pong! this is STT/TTS Sample assistant")
        return ctx.cancel_ai_response()
    
    if ctx.message.text == "talk":
        await ctx.send_voice_message("Hello, this is a voice generation test. I hope you can hear me.")
        return ctx.cancel_ai_response()


# ---------------------------------------------------------------------------

# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    webhook_url=os.environ.get("WEBHOOK_URL"),
    assistant=ast,
    host="127.0.0.1", port=5004,
    auto_voice_response=True
)

# Register STT Middleware
# Allows the assistant to process voice messages from any connector
# In this case from the Telegram connector
# The middleware uses the Deepgram API for speech-to-text conversion
# It detects voice messages and converts them to text, then adds the text
# into message text field for processing by the assistant
gateway.register_middleware(DeepgramSTTMiddleware())


# For this example, we will use the Telegram connector
conn = TelegramConnector(
    token=os.environ.get("TELEGRAM_TOKEN"), 
    stream_mode=StreamMode.FULL,
    
    # Here we use the ElevenLabsAdapter as the TTS voice provider
    # Connectors can have different voice providers
    # Due to the differences in how each platform handles voice messages
    # Cel.ai provides a way to customize the voice provider for each connector
    voice_provider=ElevenLabsAdapter(
        default_voice="N2lVS1w4EtoT3dr4eOWO"
    )
)
# Register the connector with the gateway
gateway.register_connector(conn)


# Then start the gateway and begin processing messages
# gateway.run()
gateway.run(enable_ngrok=True)

