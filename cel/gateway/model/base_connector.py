from fastapi import APIRouter
from typing import Any
from .message_gateway_context import MessageGatewayContext


class ConnectorsRegistry(type):
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if not hasattr(cls, '_instances'):
            cls._instances = []  # Crear solo en BaseLead

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        # Añadir instancia a BaseLead._instances
        BaseConnector._instances.append(instance)
        return instance
    
    def get_connector_by_name(cls, name):
        for instance in cls._instances:
            if instance.name() == name:
                return instance
        return None
    
    def get_all_connectors(cls):
        return cls._instances or []
    

class BaseConnector(metaclass=ConnectorsRegistry):

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
    
    async def send_link_message(self, 
                            lead, 
                            text: str, 
                            links: list, 
                            metadata: dict = {}, 
                            is_partial: bool = True):
        raise NotImplementedError