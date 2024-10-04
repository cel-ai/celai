<!-- A centered logo of celia -->
<!-- <p align="center">
  <img src="https://raw.githubusercontent.com/cel-ai/celai/30b489b21090e3c3f00ffea66d0ae4ac812bd839/cel/assets/celia_logo.png" width="250" />
</p> -->
<p align="center">
  <img src="https://raw.githubusercontent.com/cel-ai/celai/d11d1c81f8193e3de580f6a21376a246fa2d473f/cel/assets/celai_connectors.png" width="500" />
</p>

# Introduction


Cel.ai is a AI Driven Communication Platform. Designed to accelerate the development of omnichannel virtual assistants. Whether you need to integrate with messaging platforms like WhatsApp, Telegram, or VoIP services such as VAPI.com, Cel.ai provides the tools and flexibility to get your assistant up and running quickly.

Don't waste time building on top of hosted platforms that limit your control and flexibility. Cel.ai is designed to be self-hosted, giving you the freedom to customize and extend the platform to meet your needs.

Supported Connectors:
- WhatsApp
- Telegram
- VAPI.ai
- Chatwoot

Off the shelf, Cel.ai provides a powerful tools such as:

- Multi Asssitant Router
  - Logic Router based on state variables
  - Agentic Router based on user itent and context
  - Semantic Router (coming soon)
- Tooling
- Events: `message`, `image`, `new_conversation`, and more
- Powered by Langchain
- Langsmith user tracing
- Moderation Middlewares
- Blacklist Middlewares
- Invitations
- Ngrok native integration
- User Sequential Message Processing


[Documentation](https://cel-ai.github.io/celai/)

## Install

pip install from github:
```bash
pip install celai
```
## Getting Started

Let's create a simple assistant that can be accessed via Telegram. First, you'll need to create a new Telegram bot and get the API token. You can do this by following the instructions in the [Telegram documentation](https://core.telegram.org/bots#6-botfather).

This example uses OpenAI's GPT-4o model to create a simple assistant that can help users buy Bitcoins. To use the OpenAI API, you'll need to sign up for an API key on the [OpenAI website](https://platform.openai.com/). 

## Configure Environment Variables

Make sure to set the `OPENAI_API_KEY` environment variable with your OpenAI API key:

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
```

Then you can create a new Python script with the following code, don't forget to
replace `<YOUR_TELEGRAM_TOKEN>` with the token you received from Telegram:

```python
# Import Cel.ai modules
import os
from cel.connectors.telegram import TelegramConnector
from cel.gateway.message_gateway import MessageGateway
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate


# Setup prompt
prompt = """You are an AI assistant. Called Celia. You can help a user to buy Bitcoins."""
prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant
# Macaw is a Langchain-based assistant that can be 
# used to create a wide variety of assistants
ast = MacawAssistant(prompt=prompt_template)

gateway = MessageGateway(
    assistant=ast,
    host="127.0.0.1", port=5004,
)

# For this example, we will use the Telegram connector
conn = TelegramConnector(
    token="<YOUR_TELEGRAM_TOKEN>"
)
                         
# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
# with ngrok enabled Cel.ai will automatically create a 
# public URL for the assistant.
gateway.run(enable_ngrok=True)
```
