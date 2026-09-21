import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from cel.gateway.http_callbacks import HttpCallbackProvider
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message_gateway_context import MessageGatewayContext


@pytest.fixture
def lead():
    return ConversationLead()


@pytest.fixture
def provider():
    return HttpCallbackProvider(endpoint="callback")


@pytest.fixture
def client(provider):
    app = FastAPI()
    provider.setup(MessageGatewayContext(
        router=APIRouter(),
        webhook_url="http://testserver",
        app=app,
    ))
    # TestClient does not follow redirects so the RedirectResponse stays visible.
    return TestClient(app, follow_redirects=False)


def test_two_leads_sharing_a_handler_get_independent_callbacks(provider, client):
    """Regression: the registry used to be keyed by id(handler), so registering
    the same handler for a second lead overwrote the first one."""
    calls = []

    def handler(lead, params):
        calls.append(lead.get_session_id())

    lead_a = ConversationLead()
    lead_b = ConversationLead()

    url_a = provider.create_callback(lead_a, handler)
    url_b = provider.create_callback(lead_b, handler)

    assert url_a != url_b
    assert len(provider.handlers) == 2

    assert client.get(url_a).status_code == 200
    assert client.get(url_b).status_code == 200
    assert calls == [lead_a.get_session_id(), lead_b.get_session_id()]


def test_single_use_callback_is_consumed_when_the_handler_returns_a_value(provider, client, lead):
    """Regression: the early `return res` skipped the single_use pop, leaving a
    payment/signature link replayable for its whole TTL."""

    def handler(lead, params):
        return {"receipt": "ok"}

    url = provider.create_callback(lead, handler, single_use=True)

    first = client.get(url)
    assert first.status_code == 200
    assert first.json() == {"receipt": "ok"}

    second = client.get(url)
    assert second.status_code == 401
    assert provider.handlers == {}


def test_single_use_callback_is_consumed_when_the_handler_returns_nothing(provider, client, lead):
    def handler(lead, params):
        return None

    url = provider.create_callback(lead, handler, single_use=True)

    assert client.get(url).status_code == 200
    assert client.get(url).status_code == 401


def test_multi_use_callback_survives_repeated_calls(provider, client, lead):
    def handler(lead, params):
        return {"ok": True}

    url = provider.create_callback(lead, handler, single_use=False)

    assert client.get(url).status_code == 200
    assert client.get(url).status_code == 200
    assert len(provider.handlers) == 1


def test_redirect_is_honoured_when_the_handler_returns_a_value(provider, client, lead):
    """Regression: the early `return res` also skipped the RedirectResponse."""

    def handler(lead, params):
        return {"ignored": True}

    url = provider.create_callback(lead, handler, redirect_url="https://example.com/thanks")

    response = client.get(url)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/thanks"


def test_handler_receives_query_params(provider, client, lead):
    received = {}

    async def handler(lead, params):
        received.update(params)

    url = provider.create_callback(lead, handler)

    assert client.get(url, params={"status": "paid"}).status_code == 200
    assert received == {"status": "paid"}


def test_failing_handler_does_not_leak_a_reusable_link(provider, client, lead):
    def handler(lead, params):
        raise RuntimeError("boom")

    url = provider.create_callback(lead, handler, single_use=True)

    assert client.get(url).status_code == 401
    assert provider.handlers == {}


def test_remove_callback_cancels_every_link_for_the_handler(provider, client, lead):
    def handler(lead, params):
        return {"ok": True}

    url_a = provider.create_callback(ConversationLead(), handler)
    url_b = provider.create_callback(ConversationLead(), handler)

    assert provider.remove_callback(handler) is True
    assert provider.handlers == {}
    assert client.get(url_a).status_code == 401
    assert client.get(url_b).status_code == 401
    assert provider.remove_callback(handler) is False
