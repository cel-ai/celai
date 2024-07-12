import asyncio
from dataclasses import dataclass
import json
from loguru import logger as log
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessageChunk
from langchain_core.messages import (
    SystemMessage,
    message_to_dict,
    messages_from_dict,
)
from langsmith import traceable

DEFAULT_PROMPT = "Create an assistant funny and sarcastic, dark humor chatbot."
LLM_DEFAULT_KWARGS = {
    "model": "gpt-4o",
    "temperature": 0,
    "max_tokens": None,
    "timeout": 20,
    "max_retries": 3,
    "streaming": True,
    "verbose": True
}

@dataclass
class MacawFunctionCall:
    name: str
    args: dict
    id: str     
    
 
chat_model_provider = ChatOpenAI
    
# merge kwargs
llm = chat_model_provider(
    **{**LLM_DEFAULT_KWARGS}
)