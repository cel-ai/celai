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

