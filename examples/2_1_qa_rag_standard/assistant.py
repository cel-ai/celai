"""
Q&A Assistant with RAG
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
from cel.rag_standard.providers.markdown import MarkdownProvider
from cel.rag_standard.stores import ChromaStore
from cel.rag_standard.text2vec import OpenAIEmbedding


# Setup prompt
prompt = "You are a Q&A Assistant. Called Celia.\
You can help a user to send money.\
Keep responses short and to the point.\
Don't use markdown formatting in your responses."
    
prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
# NOTE: Make sure to provide api key in the environment variable `OPENAI_API_KEY`
# add this line to your .env file: OPENAI_API_KEY=your-key
# or uncomment the next line and replace `your-key` with your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-key.."
ast = MacawAssistant(prompt=prompt_template)


# Configure the RAG model using the new RAG standard implementation
# Initialize the markdown provider
md_provider = MarkdownProvider()

# Initialize the embedding model
embedding = OpenAIEmbedding()

# Initialize the vector store
store = ChromaStore(
    persist_directory="./chroma_db",
    collection_name="demo",
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)

# Load and process the markdown file
content = md_provider.load_file("examples/2_qa_rag/qa.md")
chunks = md_provider.split_content(content, chunk_size=1000, overlap=200)

# Add documents to the store
for i, chunk in enumerate(chunks):
    metadata = {
        "source": "qa.md",
        "chunk_index": i,
        "total_chunks": len(chunks)
    }
    store.add_documents(
        documents=[chunk],
        metadatas=[metadata]
    )

# Register the RAG model with the assistant
ast.set_rag_retrieval(store)


# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    # webhook_url=os.environ.get("WEBHOOK_URL"),
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
gateway.run(enable_ngrok=True)

