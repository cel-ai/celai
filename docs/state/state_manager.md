# State Manager

The State Manager in Cel.ai provides a simple and efficient way to store and retrieve state information during a conversation. This feature is crucial for maintaining context and ensuring a seamless user experience.

## What is the State for?

The state in a conversation refers to the information that is relevant to the current context of the conversation. For example, if the user asks a question and the assistant needs to look up information to provide an answer, the state can be used to store the question and the information retrieved so that the assistant can refer back to it later in the conversation.

For example, if the user asks for how much money they have in their account, the assistant can store the user's account balance in the state, then Cel.ai can inject that information into the prompt before processing the inference.

`PromptTemplate` can reference any key-value pair stored in the state. For example, if the state contains the key `account_balance`, the `PromptTemplate` can reference it as `{{account_balance}}`.

## Advantages

- **Automatic State Management**: The state is automatically saved and committed when using the `async with` block.
- **Error Handling**: If an error occurs within the `async with` block, the state changes are rolled back, ensuring data integrity.
- **Simplicity**: The state is managed as a simple key-value store, making it easy to use and understand.
- **Data Persistence**: The state is persisted across multiple messages and sessions, allowing for continuity in the conversation.

## Usage

To use the State Manager, you need to access it via the `RequestContext` or `FunctionContext` object. Here is an example of how to use it within an event handler for a message event:

```python
from cel.assistants.request_context import RequestContext

@ast.event('message')
async def handle_message(session, ctx: RequestContext):
    log.debug(f"Got message event: {ctx.message}")

    # Using the state manager within an async with block
    async with ctx.state_manager() as state:
        count = state.get("count", 0)
        count += 1
        state["count"] = count
        
    # Send a response
    await ctx.connector.send_text_message(ctx.lead, f"Message count: {count}")
    return ctx.cancel_ai_response()
```

## Example

Here is a complete example demonstrating how to use the State Manager to count the number of messages received from a user:

```python
import asyncio
import os
from loguru import logger as log
from dotenv import load_dotenv
from cel.connectors.telegram import TelegramConnector
from cel.gateway.message_gateway import MessageGateway, StreamMode
from cel.message_enhancers.smart_message_enhancer_openai import SmartMessageEnhancerOpenAI
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.assistants.request_context import RequestContext

# Load environment variables
load_dotenv()

# Setup prompt
prompt = "You are an assistant called Celia. Keep responses short and to the point. Don't use markdown formatting in your responses."
prompt_template = PromptTemplate(prompt)

# Create the assistant
ast = MacawAssistant(prompt=prompt_template)

# Event handler for the message event
@ast.event('message')
async def handle_message(session, ctx: RequestContext):
    log.debug(f"Got message event: {ctx.message}")

    # Using the state manager within an async with block
    async with ctx.state_manager() as state:
        count = state.get("count", 0)
        count += 1
        state["count"] = count
        
    # Send a response
    await ctx.connector.send_text_message(ctx.lead, f"Message count: {count}")
    return ctx.cancel_ai_response()

# Create the Message Gateway
gateway = MessageGateway(
    assistant=ast,
    host="127.0.0.1", port=5004,
    message_enhancer=SmartMessageEnhancerOpenAI()
)

# Use the Telegram connector
conn = TelegramConnector(
    token=os.environ.get("TELEGRAM_TOKEN

"),

 
    stream_mode=StreamMode.FULL
)
gateway.register_connector(conn)

# Start the gateway
gateway.run(enable_ngrok=True)
```

## Best Practices

- **Use `async with` Block**: Always use the `async with` block for state management to ensure automatic saving and error handling.
- **Avoid Manual State Saving**: While you can manually save the state using `await state.save_state()`, it is recommended to rely on the `async with` block for simplicity and reliability.
- **Handle Errors Gracefully**: If an error occurs within the `async with` block, the state changes will be rolled back, ensuring data integrity.

By following these best practices, you can effectively manage state in your Cel.ai assistant, providing a robust and seamless user experience.

alejamp: crea un archivo .md con eso

GitHub Copilot: ### Plan

1. Create a new Markdown file named `assistant.md`.
2. Copy the provided Python code and comments into the Markdown file.
3. Format the content appropriately using Markdown syntax.

### Code

```markdown
# State Management with Cel.ai

This is a simple example of an AI Assistant implemented using the Cel.ai framework. It serves as a basic demonstration of how to get started with Cel.ai for creating intelligent assistants.

**Framework**: Cel.ai  
**License**: MIT License

This script is part of the Cel.ai example series and is intended for educational purposes.

## Usage

Configure the required environment variables in a `.env` file in the root directory of the project. The required environment variables are:
- `WEBHOOK_URL`: The webhook URL for the assistant, you can use ngrok to create a public URL for your local server.


-

 `TELEGRAM_TOKEN`: The Telegram bot token for the assistant. You can get this from the BotFather on Telegram.

Then run this script to see a basic AI assistant in action.

**Note**: Please ensure you have the Cel.ai framework installed in your Python environment prior to running this script.

## Code

```python
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
# This example demonstrates how to use the state manager to store and retrieve state
# Count the number of messages received from the user and send a response with the count
# ---------------------------------------------------------------------------
@ast.event('message')
async def handle_message(session, ctx: RequestContext):
    log.debug(f"Got message event: {ctx.message}")

    # State Manager: Celai provides a simple way to store and retrieve state
    # for the conversation. The state is accessible via ctx.state_manager()
    # For example: ctx.state_manager() returns an AsyncStateManager object
    # which can be used to store and retrieve state for the conversation.
    async with ctx.state_manager() as state:
        count = state.get("count", 0)
        count += 1
        state["count"] = count
        # Add more logic and changes to the state here
        # For example: state["key"] = value
        # The state is a simple key-value store that can be used to store
        # any data related to the conversation.
        
    # Once you leave the async with block, the state will be automatically saved
    # and committed to the state store.
    
    # You can still access the state outside the async with block
    # but you won't be able to save changes to the state automatically
    # If you need to save changes to the state outside the async with block
    # you can call: await state.save_state()
    
    # We strongly recommend using the async with block for state management
    
    # If a error occurs inside the async with block, the state will not be saved
    # and the changes will be rolled back.So you can safely use the async with block
    
    # Send a response
    await ctx.connector.send_text_message(ctx.lead, f"Message count: {count}")
    return ctx.cancel_ai_response()
# ---------------------------------------------------------------------------

# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
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

# Then start the gateway and begin processing messages
# gateway.run()
gateway.run(enable_ngrok=True)
```
```

Save this content into a file named `assistant.md`.