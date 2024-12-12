from fastapi import FastAPI, Request
from starlette.testclient import TestClient
from starlette.datastructures import Headers
import pytest

from cel.connectors.telegram.model.telegram_lead import TelegramLead
from cel.gateway.message_gateway import MessageGateway
from cel.gateway.model.message import Message
from cel.gateway.http_callbacks import HttpCallbackProvider

BASE_URL = "https://example.com"


def leadme(lead_dict: dict):
    # Get all known classes from celai package that are a subclass of ConversationLead



@pytest.mark.asyncio
async def test_callbacks_link1():
    # Crear una instancia de la clase
    middleware = HttpCallbackProvider(
        endpoint="gcalendar",
        http_verb="GET"
    )

    mg = MessageGateway(
        assistant=None,
        webhook_url=BASE_URL,
    )

    # Prueba el método __call__
    lead = TelegramLead("123")
    
    # mock a fastapi application
    app = FastAPI()
    client = TestClient(app)
    
    middleware.setup(app)
    middleware.on_startup(gateway=mg)
    
    link = middleware.create_callback(lead)
    
    endpoint = link.replace(BASE_URL, "")  
    
    res = client.get(endpoint)
    
    res_json = res.json()
    
    
    assert True
    