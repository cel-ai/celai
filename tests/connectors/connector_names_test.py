import pytest

from cel.connectors.cli.cli_connector import CliConnector
from cel.connectors.telegram.telegram_connector import TelegramConnector
from cel.gateway.model.base_connector import BaseConnector


@pytest.fixture(autouse=True)
def clean_registry():
    """The registry is a class-level singleton shared across tests."""
    BaseConnector._instances.clear()
    yield
    BaseConnector._instances.clear()


def test_cli_connector_has_its_own_name():
    assert CliConnector().name() == "cli"


def test_cli_does_not_squat_on_the_telegram_name():
    """Regression: CliConnector.name() returned "telegram", so the registry
    handed back the wrong connector and ConversationLead.deserialize() could not
    reattach a lead coming back from a callback."""
    cli = CliConnector()
    telegram = TelegramConnector(token="123:ASD")

    assert BaseConnector.get_connector_by_name(cli.name()) is cli
    assert BaseConnector.get_connector_by_name(telegram.name()) is telegram
    assert cli.name() != "telegram"
    assert not telegram.name().startswith(cli.name())
