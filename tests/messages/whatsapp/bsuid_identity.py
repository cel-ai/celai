import pytest
from cel.connectors.whatsapp.model.whatsapp_lead import WhatsappLead
from cel.connectors.whatsapp.phone_utils import is_bsuid
from cel.connectors.whatsapp.whatsapp_connector import WhatsappConnector
from cel.gateway.model.conversation_lead import ConversationLead


BSUID = "US.13491208655302741918"
PHONE = "16315551181"


def wrap_webhook(value: dict) -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "103048736088448",
                "changes": [
                    {
                        "value": value,
                        "field": "messages",
                    }
                ],
            }
        ],
    }


def metadata():
    return {
        "display_phone_number": "16505551111",
        "phone_number_id": "123456123",
    }


def not_opted_in_payload() -> dict:
    return wrap_webhook({
        "messaging_product": "whatsapp",
        "metadata": metadata(),
        "contacts": [
            {
                "profile": {"name": "test user name"},
                "wa_id": PHONE,
                "user_id": BSUID,
            }
        ],
        "messages": [
            {
                "id": "ABGGFlA5Fpa",
                "timestamp": "1504902988",
                "from": PHONE,
                "from_user_id": BSUID,
                "type": "text",
                "text": {"body": "this is a text message"},
            }
        ],
    })


def opted_in_phone_unavailable_payload() -> dict:
    return wrap_webhook({
        "messaging_product": "whatsapp",
        "metadata": metadata(),
        "contacts": [
            {
                "profile": {
                    "name": "test user name",
                    "username": "@testusername",
                },
                "user_id": BSUID,
            }
        ],
        "messages": [
            {
                "id": "ABGGFlA5Fpa",
                "timestamp": "1504902988",
                "from_user_id": BSUID,
                "type": "text",
                "text": {"body": "this is a text message"},
            }
        ],
    })


def opted_in_phone_available_payload() -> dict:
    return wrap_webhook({
        "messaging_product": "whatsapp",
        "metadata": metadata(),
        "contacts": [
            {
                "profile": {
                    "name": "test user name",
                    "username": "@testusername",
                },
                "wa_id": PHONE,
                "user_id": BSUID,
            }
        ],
        "messages": [
            {
                "id": "ABGGFlA5Fpa",
                "timestamp": "1504902988",
                "from": PHONE,
                "from_user_id": BSUID,
                "type": "text",
                "text": {"body": "this is a text message"},
            }
        ],
    })


@pytest.fixture
def connector():
    return WhatsappConnector(phone_number_id="123456", token="123:ASD", verify_token="1234")


def test_is_bsuid():
    assert is_bsuid("US.13491208655302741918")
    assert is_bsuid("MX.1507950994201523")
    assert is_bsuid("VE.28617078864545316")
    assert not is_bsuid("16315551181")
    assert not is_bsuid("5216621057946")
    assert not is_bsuid(None)
    assert not is_bsuid("")


def test_not_opted_in_keeps_phone_and_user_id(connector):
    lead = WhatsappLead.from_whatsapp_message(not_opted_in_payload(), connector=connector)

    assert lead.phone == PHONE
    assert lead.user_id == BSUID
    assert lead.conversation_from.phone == PHONE
    assert lead.conversation_from.id == BSUID
    assert lead.destination_fields() == {"to": PHONE}
    assert lead.get_session_id().endswith(f":{PHONE}")
    assert "username" not in (lead.conversation_from.metadata or {})


def test_opted_in_phone_unavailable_uses_recipient(connector):
    lead = WhatsappLead.from_whatsapp_message(
        opted_in_phone_unavailable_payload(), connector=connector
    )

    assert lead.phone is None
    assert lead.user_id == BSUID
    assert lead.conversation_from.phone is None
    assert lead.conversation_from.id == BSUID
    assert lead.conversation_from.metadata.get("username") == "@testusername"
    assert lead.destination_fields() == {"recipient": BSUID}
    assert lead.get_session_id().endswith(f":{BSUID}")


def test_opted_in_phone_available_prefers_to(connector):
    lead = WhatsappLead.from_whatsapp_message(
        opted_in_phone_available_payload(), connector=connector
    )

    assert lead.phone == PHONE
    assert lead.user_id == BSUID
    assert lead.conversation_from.phone == PHONE
    assert lead.conversation_from.id == BSUID
    assert lead.conversation_from.metadata.get("username") == "@testusername"
    assert lead.destination_fields() == {"to": PHONE}
    assert lead.get_session_id().endswith(f":{PHONE}")


def test_serialize_roundtrip_preserves_user_id(connector):
    lead = WhatsappLead.from_whatsapp_message(
        opted_in_phone_unavailable_payload(), connector=connector
    )
    restored = ConversationLead.deserialize(ConversationLead.serialize(lead))

    assert isinstance(restored, WhatsappLead)
    assert restored.phone is None
    assert restored.user_id == BSUID
    assert restored.destination_fields() == {"recipient": BSUID}


def test_from_dict_preserves_user_id():
    lead = WhatsappLead.from_dict({"phone": PHONE, "user_id": BSUID, "metadata": {}})
    assert lead.phone == PHONE
    assert lead.user_id == BSUID
    assert lead.destination_fields() == {"to": PHONE}


def test_destination_fields_requires_identity():
    lead = WhatsappLead(phone=None, user_id=None)
    with pytest.raises(ValueError, match="neither phone nor user_id"):
        lead.destination_fields()
