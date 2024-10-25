<!-- A centered logo of celia -->
<!-- <p align="center">
  <img src="https://raw.githubusercontent.com/cel-ai/celai/30b489b21090e3c3f00ffea66d0ae4ac812bd839/cel/assets/celia_logo.png" width="250" />
</p> -->
<p align="center">
  <img src="https://raw.githubusercontent.com/cel-ai/celai/d11d1c81f8193e3de580f6a21376a246fa2d473f/cel/assets/celai_connectors.png" width="600" />
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


## Multi-Assistant Router

Cel.ai provides a powerful multi-assistant router that allows you to create complex conversational assistants easily. This architecture allows you to scale in a modular way, adding new assistants as needed. The routing can be done based on state variables, user intent, or context.

Agentic Router is the most powerful router in Cel.ai. It allows you to triage messages to different assistants based on user intent and context. It keeps prompts small and focused, allowing for more accurate responses.

Keep prompts at mininal length and focused on a single task will ensure that the user experience is optimal and the response cost are kept low.

For example, if you are building a virtual assistant for a hotel, you can have different assistants for booking/reservation, cancellation, room service, and check-out. The Agentic Router will automatically route messages to the correct assistant based on the user's intent.


<p align="center">
  <img src="https://raw.githubusercontent.com/cel-ai/celai/refs/heads/main/cel/assets/celai_router_diagram.png" width="700" />
</p>

## In Context Routing

Cel.ai provides a powerful in-context routing system. Messages are routed to the correct assistant based on the user's intent and context. 

Assistant can have its own set of prompts and responses, but share the same context. 

State and History stores are shared between all assistants, allowing for a seamless user experience. Ensuring all assistants are in sync with the user's context.


## Install

pip install from github:
```bash
pip install celai
```
## Getting Started

Let's create a simple assistant that can be accessed via Telegram. First, you'll need to create a new Telegram bot and get the API token. You can do this by following the instructions in the [Telegram documentation](https://core.telegram.org/bots#6-botfather).

This example uses OpenAI's GPT-4o model to create a simple assistant that can help users buy Bitcoins. To use the OpenAI API, you'll need to sign up for an API key on the [OpenAI website](https://platform.openai.com/). 

## Configure Environment Variables

### OpenAI API Key

Make sure to set the `OPENAI_API_KEY` environment variable with your OpenAI API key:

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
```

### Ngrok Authtoken

The easy way to get a public HTTPS URL for your assistant is to use [ngrok](https://ngrok.com/). Cel.ai has built-in support for ngrok, so you can easily delegate the public URL creation to Cel.ai. To use ngrok, you'll need a Ngrok authtoken. You can get one by signing up on the [ngrok website](https://ngrok.com/). Then set the `NGROK_AUTH_TOKEN` environment variable:

```bash
export NGRO_AUTH_TOKEN=<YOUR_NGROK_AUTH_TOKEN>
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
