import pytest
from fastapi.testclient import TestClient

from cel.gateway.message_gateway import MessageGateway

API_KEY = "s3cr3t"


class SpyConnector:
    """Minimal stand-in for a connector: only records pause/resume."""

    def __init__(self):
        self.paused = False
        self.pause_calls = 0

    def pause(self):
        self.paused = True
        self.pause_calls += 1

    def resume(self):
        self.paused = False


@pytest.fixture
def connector():
    return SpyConnector()


@pytest.fixture
def client(connector):
    gateway = MessageGateway(gateway_api_key=API_KEY)
    gateway.connectors.append(connector)
    return TestClient(gateway.app)


def test_secured_route_runs_with_a_valid_key(client, connector):
    response = client.get("/gateway/pause", headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    assert connector.paused is True


def test_missing_key_is_rejected_without_running_the_route(client, connector):
    """Regression: the middleware used to call the route first and only then
    stamp a 401 on the response, so the gateway was already paused."""
    response = client.get("/gateway/pause")
    assert response.status_code == 401
    assert connector.pause_calls == 0
    assert connector.paused is False


def test_invalid_key_is_rejected_without_running_the_route(client, connector):
    response = client.get("/gateway/pause", headers={"x-api-key": "wrong"})
    assert response.status_code == 401
    assert connector.pause_calls == 0
    assert connector.paused is False


def test_unsecured_route_needs_no_key(client):
    assert client.get("/health/").status_code == 200
