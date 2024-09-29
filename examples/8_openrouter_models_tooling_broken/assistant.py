"""
Hello World - https://openrouter.ai/
---------------------------------

This is a simple example of an AI Assistant implemented using the Cel.ai framework.
It serves as a basic demonstration of how to get started with Cel.ai for creating intelligent assistants.
Using Openrouter.ai models.

Visit https://openrouter.ai/ for more information on Openrouter.ai
You need a valid API key to use the Openrouter.ai models.
Add the API key to the .env file as OPENROUTER_API_KEY

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
from cel.assistants.function_context import FunctionContext
from cel.assistants.function_response import RequestMode
from cel.assistants.common import Param
from cel.assistants.macaw.custom_chat_models.chat_open_router import \
    ChatOpenAIOpenRouter,\
    ChatOpenRouter
from cel.assistants.macaw.macaw_settings import MacawSettings


# Setup prompt
prompt = "You are a Q&A Assistant. Called Celia.\
You can help a user to send money.\
Keep responses short and to the point.\
Don't use markdown formatting in your responses. No contestes nada que no tenga que ver con Smoothy Inc.\
You work Smoothy Inc. is a company that specializes in creating smoothies in food trucks.\
Available products from Smoothy Inc. are:\n\
    - Smoothies\n\
    - Juices\n\
    - Smoothie bowls\n\
    - Acai bowls\n\
Smoothies can be customized with the following extra ingredients:\n\
    - Fruits: Strawberry, Banana, Mango, Pineapple, Blueberry\n\
    - Nuts\n\
    - Seeds\n"

prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
# NOTE: Make sure to provide api key in the environment variable `OPENROUTER_API_KEY`
# add this line to your .env file: OPENROUTER_API_KEY=your-key
# or uncomment the next line and replace `your-key` with your OpenAI API key
# os.environ["OPENROUTER_API_KEY"] = "your-key.."
ast = MacawAssistant(
    prompt=prompt_template,
    llm = ChatOpenAIOpenRouter,
    settings=MacawSettings(core_model="openai/gpt-4o")
)

# NOTE: tooling is not supported in some models
# --------------------------------------------------------------------
@ast.function('create_order', 'Customer creates an order', params=[
    Param('product', 'string', 'Product to order', required=True),
    Param('extra_ingredients', 'string', 'Extra ingredients for personalized order', required=True)
])
async def handle_create_order(session, params, ctx: FunctionContext):
    
    log.debug(f"Got create_order from client:{ctx.lead.conversation_from.name}\
                command with params: {params}")

    # TODO: Implement order creation logic here
    product = params['product']
    extra_ingredients = params['extra_ingredients']
    log.warning(f"Order created for product: {product} with extra ingredients: {extra_ingredients}") 

    # Response back using FunctionContext. This allows you to send a response back to genAI
    # request_mode=RequestMode.SINGLE is used to indicate that genAI must build a single response
    return FunctionContext.\
        response_text(f"Great we are preparing your order for \
            {product} with extra ingredients: {extra_ingredients}.\
            Your order will be ready in a few minutes.", 
                        request_mode=RequestMode.SINGLE)
# --------------------------------------------------------------------



# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    webhook_url=os.environ.get("WEBHOOK_URL"),
    assistant=ast,
    host="127.0.0.1", port=5004
)

# For this example, we will use the Telegram connector
conn = TelegramConnector(
    token=os.environ.get("TELEGRAM_TOKEN"), 
    # Try to set the stream mode to SENTENCE
    stream_mode=StreamMode.FULL
)
# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run()

