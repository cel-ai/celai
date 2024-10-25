"""
Celai 101 Tooling Example: Crypto prices + Redis
------------------------------------------

This is a simple example of an AI Assistant implemented using the Cel.ai framework.
It serves as a basic demonstration of how to get started with Cel.ai for creating intelligent assistants.

Framework: Cel.ai
License: MIT License

This script is part of the Cel.ai example series and is intended for educational purposes.

Usage:
------
Configure the required environment variables in a .env file in the root directory of the project.
The required environment variables are:
- TELEGRAM_TOKEN: The Telegram bot token for the assistant. You can get this from the BotFather on Telegram.

Then run this script to see a basic AI assistant in action.

Note:
-----
Please ensure you have the Cel.ai framework installed in your Python environment prior to running this script.
"""
# LOAD ENV VARIABLES
import os
import time
from urllib import request
from loguru import logger as log
# Load .env variables
from dotenv import load_dotenv

from cel.assistants.macaw.macaw_settings import MacawSettings
from cel.assistants.request_context import RequestContext
from cel.stores.common.list_redis_store_async import ListRedisStoreAsync
from cel.stores.history.history_redis_provider_async import RedisHistoryProviderAsync
from cel.stores.state.state_redis_provider import RedisChatStateProvider
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
from cel.gateway.model.conversation_lead import ConversationLead
from cel.assistants.function_context import FunctionContext
from cel.assistants.function_response import RequestMode
from cel.assistants.common import Param
from datetime import datetime


def date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_customer_name(lead: ConversationLead):
    return lead.conversation_from.name or "unknown"
    

# Setup prompt
prompt = """Your name is {assistant_name}. I can help you with the latest crypto prices.
Today is {date}. 
Customer's name is {customer_name}, address him by his name.
"""
    
prompt_template = PromptTemplate(prompt, initial_state={
        # Assistant name
        "assistant_name": "CryptoBot",
        # Today full date and time
        "date": date,
        # Get the customer name from the lead
        "customer_name": get_customer_name
    })





state_store = RedisChatStateProvider(redis="redis://localhost:6379/0")
histoy_store = RedisHistoryProviderAsync(ListRedisStoreAsync(
    redis="redis://default:uUUcEkbHeZKiiQKckqUpqkRKAvVGOxJQ@autorack.proxy.rlwy.net:52598", 
    key_prefix="h:ale"))

ast = MacawAssistant(
    prompt=prompt_template,
    # settings=MacawSettings(core_history_window_length=3),
    state_store=state_store,
    history_store=histoy_store
)



@ast.event('message')
async def handle_message(session, ctx: RequestContext):
    log.debug(f"Got message from client:{ctx.lead.conversation_from.name}")



# --------------------------------------------------------------------
@ast.function('get_crypto_price', 'Get the latest price of a cryptocurrency', params=[
    Param('asset', 'string', 'The cryptocurrency asset to get the price for. Example: BTC, ETH, DOGE', required=True)
])
async def handle_get_crypto_price(session, params, ctx: FunctionContext):    
    log.debug(f"Got get_crypto_price command with params: {params}")
    asset = params['asset']
    
    if asset == "ETH":
        # Emnulate a missing asset
        return None
    
    if asset == "DOGE":
        # Emnulate an error
        raise Exception("DOGE is not supported")
    
    try:
        #  Request to Coinbase API
        from util import get_crypto_price
        price = get_crypto_price(asset)
        return ctx.response_text(f"The current price of {asset} is ${price}")
    except Exception as e:
        log.error(f"Error getting crypto price: {e}")
        ctx.response_text(f"Error. Please go to https://coinbase.com/ for the latest price of {asset}")

# --------------------------------------------------------------------



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