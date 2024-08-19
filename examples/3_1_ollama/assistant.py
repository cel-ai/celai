"""
Cryptocurrency price with Ollama + llama3-groq-tool-use
-------------------------------------

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

Run Ollama:
-----------
0. Install Ollama on your machine by following the instructions on the official site
    https://ollama.com/

1. Start the Ollama server by running the following command in the terminal:
    ```ollama run llama3-groq-tool-use```
    
2. Install embedding model by running the following command in the terminal:
    ```ollama pull mxbai-embed-large```

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
from cel.assistants.macaw.macaw_settings import MacawSettings
from cel.rag.text2vec.cached_ollama import CachedOllamaEmbedding

from utils import get_crypto_price
from langchain_ollama import ChatOllama



# Setup prompt
# prompt = """You a are a friendly AI assistant Celai.  
# You must help with crypto questions. 
# Response in customer's language.
# Short answers are must."""

prompt = """Eres un asistente de inteligencia artificial amigable, Celai.
Debes ayudar con las preguntas sobre criptomonedas.
Responde en el idioma del cliente.
Las respuestas breves son obligatorias.
Customer's default currency: usd
"""

prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
# --------------------------------------------------
# Set the core, blend, and insights models to llama3-groq-tool-use
# This is a custom model that is trained on the llama3 dataset for tool use
# The model is trained to understand tool use cases
agent_settings = MacawSettings(
    core_model='llama3-groq-tool-use', 
    blend_model='llama3-groq-tool-use',
    insights_model='llama3-groq-tool-use'
)
# Create the assistant using LLM ChatOllama
ast = MacawAssistant(
    prompt=prompt_template, 
    llm=ChatOllama,
    settings=agent_settings
)
# --------------------------------------------------


# Configure the RAG model using the MarkdownRAG provider
# by default it uses the CachedOpenAIEmbedding for text2vec
# and ChromaStore for storing the vectors
mdm = MarkdownRAG(
    "demo", 
    file_path="examples/3_1_ollama/qa.md", 
    split_table_rows=True,
    text2vec=CachedOllamaEmbedding()
)
# Load from the markdown file, then slice the content, and store it.
mdm.load()
# Register the RAG model with the assistant
ast.set_rag_retrieval(mdm)


# Tool - Create Order
# In order to declare a function, you need to use the @ast.function decorator
# The function name should be unique and should not contain spaces
# Description should be a short description of what the function does, 
# this is very important for the assistant to understand the function
# --------------------------------------------------------------------
@ast.function('get_cryptocurrency_price', 'Get the price of any cryptocurrency', params=[
    Param('asset_name', 'string', 'The full name of the cryptocurrency, e.g. bitcoin, cardano, ethereum, etc. Dont abbreviate'),
    Param('currency', 'string', 'The currency to get the price in, e.g. usd, aud, gdb, etc.')
])
async def get_cryptocurrency_price(session, params, ctx: FunctionContext):        
    try:
        log.warning(f"Getting the price of {params['asset_name']} in {params.get('currency', 'usd')}")
        prices = await get_crypto_price(params['asset_name'], params.get('currency', 'usd'))
        return FunctionContext.response_text(f"{params['asset_name'].upper()}: ${prices}",
                        request_mode=RequestMode.SINGLE)
        
    except Exception as e:
        log.error(f"Error getting price: {e}")
        return FunctionContext.response_text(f"Sorry, I couldn't get the price of {params['asset_name']}",
                        request_mode=RequestMode.SINGLE)
# --------------------------------------------------------------------




# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
webhook_url = os.environ.get("WEBHOOK_URL")
gateway = MessageGateway(
    webhook_url= webhook_url,
    assistant=ast,
    host="127.0.0.1", port=5004,
    # message_enhancer=SmartMessageEnhancerOpenAI()
)

# For this example, we will use the Telegram connector
conn = TelegramConnector(
    token=os.environ.get("TELEGRAM_TOKEN"), 
    stream_mode=StreamMode.FULL
)
# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run()

