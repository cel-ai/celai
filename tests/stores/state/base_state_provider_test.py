import inspect

import pytest

from cel.stores.state.base_state_provider import BaseChatStateProvider
from cel.stores.state.state_inmemory_provider import InMemoryStateProvider
from cel.stores.state.state_redis_provider import RedisChatStateProvider

ASYNC_METHODS = [
    "set_key_value",
    "get_key_value",
    "clear_store",
    "clear_all_stores",
    "get_store",
    "set_store",
]


@pytest.mark.parametrize("name", ASYNC_METHODS)
def test_abc_declares_accessors_as_coroutines(name):
    """Regression: the ABC declared these as sync while every implementation was
    async, so anyone writing a provider from the ABC got the contract wrong."""
    assert inspect.iscoroutinefunction(getattr(BaseChatStateProvider, name))


@pytest.mark.parametrize("provider", [InMemoryStateProvider, RedisChatStateProvider])
@pytest.mark.parametrize("name", ASYNC_METHODS)
def test_shipped_providers_match_the_contract(provider, name):
    assert inspect.iscoroutinefunction(getattr(provider, name))


def test_get_key_stays_synchronous():
    assert not inspect.iscoroutinefunction(BaseChatStateProvider.get_key)
