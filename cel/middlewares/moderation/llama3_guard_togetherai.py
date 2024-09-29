"""
# Llama3Guard Moderation Documentation

## Overview

Llama3Guard Moderation is a component designed to detect and classify toxic messages within the Cel.ai platform. It leverages the Llama Guard 3 model, which is fine-tuned for content safety classification. This document provides an overview of how Llama3Guard Moderation works, including its hazard taxonomy, supported languages, and example usage.

## Model Details

Llama Guard 3 is a Llama-3.1-8B pretrained model, fine-tuned for content safety classification. It can classify content in both LLM inputs (prompt classification) and LLM responses (response classification). The model generates text indicating whether a given prompt or response is safe or unsafe. If unsafe, it also lists the content categories violated.

### Hazard Taxonomy and Policy

The model is trained to predict safety labels based on the MLCommons taxonomy of 13 hazards, plus an additional category for Code Interpreter Abuse. The categories are as follows:

1. **Violent Crimes**: Responses that enable, encourage, or endorse violent crimes, including unlawful violence toward people and animals.
2. **Non-Violent Crimes**: Responses that enable, encourage, or endorse non-violent crimes, including personal crimes, financial crimes, property crimes, drug crimes, weapons crimes, and cyber crimes.
3. **Sex-Related Crimes**: Responses that enable, encourage, or endorse sex-related crimes, including sex trafficking, sexual assault, sexual harassment, and prostitution.
4. **Child Sexual Exploitation**: Responses that contain, describe, enable, encourage, or endorse the sexual abuse of children.
5. **Defamation**: Responses that are both verifiably false and likely to injure a living person’s reputation.
6. **Specialized Advice**: Responses that contain specialized financial, medical, or legal advice, or that indicate dangerous activities or objects are safe.
7. **Privacy**: Responses that contain sensitive, nonpublic personal information that could undermine someone’s physical, digital, or financial security.
8. **Intellectual Property**: Responses that may violate the intellectual property rights of any third party.
9. **Indiscriminate Weapons**: Responses that enable, encourage, or endorse the creation of indiscriminate weapons, including chemical, biological, radiological, nuclear, and high-yield explosive weapons.
10. **Hate**: Responses that demean or dehumanize people based on their sensitive, personal characteristics.
11. **Suicide & Self-Harm**: Responses that enable, encourage, or endorse acts of intentional self-harm, including suicide, self-injury, and disordered eating.
12. **Sexual Content**: Responses that contain erotica.
13. **Elections**: Responses that contain factually incorrect information about electoral systems and processes.
14. **Code Interpreter Abuse**: Responses that seek to abuse code interpreters, including those that enable denial of service attacks, container escapes, or privilege escalation exploits.

### Supported Languages

Llama Guard 3 supports content safety for the following languages:
- English
- French
- German
- Hindi
- Italian
- Portuguese
- Spanish
- Thai

In this example, the `classify` function takes a response as input and returns a classification indicating whether the response is safe or unsafe. If unsafe, it also lists the violated categories.

## Conclusion

Llama3Guard Moderation is a powerful tool for detecting and classifying toxic messages within the Cel.ai platform. By leveraging the Llama Guard 3 model, it ensures content safety across multiple languages and a comprehensive hazard taxonomy.
"""

from abc import ABC
import asyncio
from dataclasses import dataclass
import os
import threading
import time
from typing import Callable
from together import Together
from cel.assistants.base_assistant import BaseAssistant
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.message import Message
from loguru import logger as log

from cel.middlewares.moderation.moderation_events import ModMiddlewareEvents

hazard_categories = {
    "S1": "Violent Crimes",
    "S2": "Non-Violent Crimes",
    "S3": "Sex-Related Crimes",
    "S4": "Child Sexual Exploitation",
    "S5": "Defamation",
    "S6": "Specialized Advice",
    "S7": "Privacy",
    "S8": "Intellectual Property",
    "S9": "Indiscriminate Weapons",
    "S10": "Hate",
    "S11": "Suicide & Self-Harm",
    "S12": "Sexual Content",
    "S13": "Elections",
    "S14": "Code Interpreter Abuse"
}

class RedFlagEntry(ABC):
    count: int = 0
    updated_at: int = 0

@dataclass
class ModerationResult(ABC):
    flagged: bool = False
    category: str = None
    description: str = None


class Llama3GuardModerationMiddleware():
    """ OpenAIEndpointModerationMiddleware is a middleware that uses OpenAI API to moderate messages.
    It uses Llama3.1 Guard 8B model to moderate messages and flags them if they are inappropriate.
    The middleware bubbles up the flagged messages to further processing using the `on_message_flagged` event.
    
    You must provide the Together API key in the environment variable:
        - TOGETHER_API_KEY: The Together API key for the assistant.
    
    Events:
        - on_message_flagged: Event that is triggered when a message is flagged by the OpenAI API.
     
    Args:
        - custom_evaluation_function: A custom function that accepts a message and returns a Moderation object.
        - on_mod_fail_continue: A boolean that determines if the middleware should continue processing if the moderation fails.
        - expire_after: An integer that determines the time in seconds after which the user flags should be reset.
        
        For more info follow https://huggingface.co/meta-llama/Llama-Guard-3-8B
    """
    
    def __init__(self,
                 custom_evaluation_function: Callable[[str], ModerationResult] = None,
                 enable_expiration: bool = False,
                 expire_after: int = 86400,
                 prunning_interval: int = 60,
                 on_mod_fail_continue: bool = True):
        
        self.custom_evaluation_function = custom_evaluation_function
        self.on_mod_fail_continue = on_mod_fail_continue
        
        assert os.environ.get('TOGETHER_API_KEY'), "TOGETHER_API_KEY is not set in the environment variables"
        self.client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))
        
        self.user_flags = {}
        self.expire_after = expire_after
        self.prunning_interval = prunning_interval
        
        if enable_expiration:
            # Asegúrate de que el bucle de eventos esté corriendo
            self.loop = asyncio.get_event_loop()
            if not self.loop.is_running():
                threading.Thread(target=self._start_event_loop, daemon=True).start()
            
            # Inicia la coroutine en segundo plano
            self.loop.call_soon_threadsafe(asyncio.create_task, self.reset_user_flags_loop()) 
                           
        
    def _start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
        
        
    async def reset_user_flags_loop(self):
        while True:
            await asyncio.sleep(self.prunning_interval)
            log.debug(f"Llama3GuardModerationMiddleware: Prunning user flags each {self.prunning_interval} seconds")
            current_time = time.time()
            expired_sessions = [
                session_id for session_id, flags in self.user_flags.items()
                if current_time - flags.updated_at > self.expire_after
            ]

            for session_id in expired_sessions:
                self.reset_user_flags(session_id)
        
        
        
        
    async def evaluate(self, text: str):
        response = self.client.chat.completions.create(
            model="meta-llama/Meta-Llama-Guard-3-8B",
            messages=[{"role": "user", "content": text}],
        )        
        res = response.choices[0].message.content
        # res = "safe" then flagged = False
        # if res = "unsafe" then flagged = True
        # when res = "unsafe" the next line will be the category of the hazard
        # for example:
        #  "unsafe"
        #  "S12"
        if res.startswith("unsafe"):
            category = res.split("\n")[1]
            desc=hazard_categories[category]
            return ModerationResult(flagged=True, category=category, description=desc)
        else:
            return ModerationResult(flagged=False)



    async def __call__(self, message: Message, connector: BaseConnector, assistant: BaseAssistant):
        
        try:
            text = message.text
            log.debug(f"Llama3GuardModerationMiddleware: {text}")
            
            result = await self.evaluate(text)
            assert isinstance(result, ModerationResult)
            
            log.debug(f"Llama3GuardModerationMiddleware: {text} -> {result.flagged}")
            
            custom_flagged = False
            if self.custom_evaluation_function:
                custom_flagged = self.custom_evaluation_function(result)
            
            if result.flagged or custom_flagged:
                session_id = message.lead.get_session_id()
                count = await self.__count_flagged(session_id)
                # append to message metadata moderation result, init metadata if not exists
                report = {
                    'flagged': result.flagged,
                    'count': count,
                    'custom_flagged': custom_flagged,
                    'results': result
                }
                message.metadata = message.metadata or {}
                message.metadata['moderation'] = report
                
                # (self, event_name: str, lead: ConversationLead, message: Message = None, connector: BaseConnector = None, data: dict= None) -> EventResponse:
                await assistant.call_event(
                    ModMiddlewareEvents.on_message_flagged, 
                    lead=message.lead, 
                    connector=connector,
                    data=report)
                
            return True
            
        except Exception as e:
            log.error(f"Llama3GuardModerationMiddleware: {e}")
            if self.on_mod_fail_continue:
                return True
            else:
                return False
            
            
    async def __count_flagged(self, session_id: str):
        if session_id in self.user_flags:
            self.user_flags[session_id].count += 1
        else:
            self.user_flags[session_id] = RedFlagEntry()
            self.user_flags[session_id].count = 1
            self.user_flags[session_id].updated_at = time.time()
            
        return self.user_flags[session_id].count
    
    
    def reset_user_flags(self, session_id: str):
        if session_id in self.user_flags:
            del self.user_flags[session_id]
        return True
    
    
    def get_user_flags(self, session_id: str):
        if session_id in self.user_flags:
            return self.user_flags[session_id]
        return None
    
