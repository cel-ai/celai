# https://medium.com/@gal.peretz/openrouter-langchain-leverage-opensource-models-without-the-ops-hassle-9ffbf0016da7

import os
from typing import Optional
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


# TODO: OpenRouter Models has problems with Langchain tooling
# This LLM model wrapper throws an error when used with Langchain tooling
# specifically with bind_tools. The error is due to the fact that the
# OpenRouter models do not support tooling??? I am not sure about this.
# --------------------------------------------------------------------
class ChatOpenRouter(ChatOpenAI):
    openai_api_base: str
    openai_api_key: str
    model_name: str

    def __init__(self,
                 model: str,
                 openai_api_key: Optional[str] = None,
                 openai_api_base: str = OPENROUTER_API_BASE,
                 **kwargs):
        openai_api_key = openai_api_key or os.getenv('OPENROUTER_API_KEY')
        super().__init__(openai_api_base=openai_api_base,
                         openai_api_key=openai_api_key,
                         model_name=model, **kwargs)
        
      
def ChatOpenAIOpenRouter(**kwargs):
    return ChatOpenAI(
        **kwargs, 
        openai_api_base=OPENROUTER_API_BASE,
        openai_api_key = os.getenv('OPENROUTER_API_KEY')
    )
# --------------------------------------------------------------------
        

