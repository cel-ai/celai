<!-- A centered logo of celia -->
<p align="center">
  <img src="https://raw.githubusercontent.com/cel-ai/celai/30b489b21090e3c3f00ffea66d0ae4ac812bd839/cel/assets/celia_logo.png" width="250" />
</p>


# Introduction


Cel.ai is a powerful Python framework designed to accelerate the development of omnichannel virtual assistants. Whether you need to integrate with platforms like WhatsApp, Telegram, or VoIP services such as VAPI.com, Cel.ai provides the tools and flexibility to get your assistant up and running quickly.

[Documentation](https://cel-ai.github.io/celai/)

## Install

pip install from github:
```bash
pip install git+https://github.com/cel-ai/celai
```
## Getting Started

Create a new Python file, `assistant.py`, and open it in your favorite text editor. Add the following code to set up a basic assistant:


```python
# Import Cel.ai modules
from cel.connectors.cli.cli_connector import CliConnector
from cel.gateway.message_gateway import MessageGateway, StreamMode
from cel.message_enhancers.smart_message_enhancer_openai import SmartMessageEnhancerOpenAI
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate

# Setup prompt
prompt = """You are an AI assistant. Called Celia. You can help a user to buy Bitcoins."""
prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
ast = MacawAssistant(
    prompt=prompt_template
)

# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(ast)

# For this example, we will use the CLI connector
conn = CliConnector(
    stream_mode=StreamMode.FULL
)
# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run()
```
