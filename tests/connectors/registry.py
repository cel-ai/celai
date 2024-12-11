import pytest
from cel.connectors.telegram.telegram_connector import TelegramConnector
from cel.connectors.whatsapp.whatsapp_connector import WhatsappConnector
from cel.gateway.model.base_connector import BaseConnector

@pytest.mark.asyncio
async def test_registry():
    
    conns = BaseConnector.get_all_connectors()
    assert len(conns) == 0
    
    # Create TelegramConnector instance
    conn1 = TelegramConnector(
        token="123:ASD"
    )
    conns = BaseConnector.get_all_connectors()
    assert len(conns) == 1

    conn2 = TelegramConnector(
        token="321:QWE"
    )
    conns = BaseConnector.get_all_connectors()
    assert len(conns) == 2

    conn3 = WhatsappConnector(
        token="123:ASD",
        phone_number_id="123",
        verify_token="123"
    )
    conns = BaseConnector.get_all_connectors()
    assert len(conns) == 3
    
    # Test get_connector_by_name
    conn = BaseConnector.get_connector_by_name(conn2.name())
    
    assert conn == conn2