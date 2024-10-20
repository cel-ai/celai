from fastapi import APIRouter
from typing import Any
from .message_gateway_context import MessageGatewayContext


class BaseConnector:

    def name(self) -> str:
        raise NotImplementedError

    def get_router(self) -> APIRouter:
        raise NotImplementedError

    def startup(self, context: MessageGatewayContext):
        raise NotImplementedError

    def shutdown(self, context: MessageGatewayContext):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError

    def resume(self):
        raise NotImplementedError

    def set_gateway(self, gateway):
        raise NotImplementedError

    async def send_text_message(self, lead, text: str, metadata: dict = {}, is_partial: bool = True):
        raise NotImplementedError
    
    async def send_voice_message(self, lead, text: str, options: dict = {}, is_partial: bool = False):
        raise NotImplementedError
    
    # Send an image message from memory
    async def send_image_message(self, lead, image: Any, filename:str, caption:str = None, metadata: dict = {}, is_partial: bool = True):
        raise NotImplementedError
    
    async def send_image_url_message(self, lead, image_url: str, caption:str = None, metadata: dict = {}, is_partial: bool = True):
        raise NotImplementedError
    
    async def send_typing_action(self, lead):
        raise NotImplementedError
    
    async def send_message(self, message):
        raise NotImplementedError