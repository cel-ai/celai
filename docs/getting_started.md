# Getting Started

Welcome to the Cel.ai documentation! This guide will help you get started with creating your first omnichannel virtual assistant using the Cel.ai framework.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.11 or higher
- pip (Python package installer)

## Installation

To install Cel.ai, you can use pip. Run the following command in your terminal:

```bash
pip install celai
```

## Creating Your First Assistant

Follow these steps to create your first virtual assistant with Cel.ai.

### Step 1: Initialize Your Project

Create a new directory for your project and navigate into it:

```bash
mkdir my_celai_assistant
cd my_celai_assistant
```

### Step 2: Create a Virtual Environment

It's a good practice to use a virtual environment for your project. Run the following commands to create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install Cel.ai

With your virtual environment activated, install Cel.ai:

```bash
pip install celai
```

### Step 4: Create Your Assistant Script

If you are using Macaw Assistant, you need to add a environment variable `OPENAI_API_KEY` with your OpenAI API key.

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

For simplicity, we will create a basic assistant that uses the CLI connector to interact with the assistant via the command line interface.
Create a new Python file, `assistant.py`, and open it in your favorite text editor. Add the following code to set up a basic assistant:

```python title="main.py"
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

# For this example, we will use the Telegram connector
conn = CliConnector(
    stream_mode=StreamMode.FULL
)
# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run()
```

### Step 5: Run Your Assistant

Save your `main.py` file and run it using the following command:

```bash
python main.py
```

Then you can interact with your assistant through the command line interface.
Just type your message and press Enter to send it to the assistant.
