from cel.connectors.whatsapp.phone_utils import filter_phone_number, is_bsuid
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.conversation_peer import ConversationPeer


def _first(items: list) -> dict:
    if items and isinstance(items[0], dict):
        return items[0]
    return {}


class WhatsappLead(ConversationLead):

    def __init__(self, phone: str = None, user_id: str = None, **kwargs):
        super().__init__(**kwargs)
        self.phone: str = filter_phone_number(phone) if phone else None
        self.user_id: str = user_id

    def get_session_id(self):
        identity = self.phone or self.user_id or self.tmp_id
        return f"{self.connector_name}:{identity}"

    def destination_fields(self) -> dict:
        """Cloud API destination: `to` for phone, `recipient` for BSUID.

        When both are present, only `to` is sent so existing phone-based
        behavior is preserved (Meta gives `to` precedence anyway).
        """
        if self.phone:
            return {"to": self.phone}
        if self.user_id:
            return {"recipient": self.user_id}
        raise ValueError("WhatsappLead has neither phone nor user_id")

    def to_dict(self):
        data = super().to_dict()
        data['phone'] = self.phone
        data['user_id'] = self.user_id
        return data

    @classmethod
    def from_dict(cls, lead_dict):
        return WhatsappLead(
            phone=lead_dict.get("phone"),
            user_id=lead_dict.get("user_id"),
            metadata=lead_dict.get("metadata")
        )

    def __str__(self):
        return f"WhatsappLead: phone={self.phone} user_id={self.user_id}"

    @classmethod
    def from_whatsapp_message(cls, data: dict, **kwargs):
        assert isinstance(data, dict), "data must be a dictionary"

        value = ((data.get("entry") or [{}])[0].get("changes") or [{}])[0].get("value") or {}
        contact = _first(value.get("contacts") or [])
        msg = _first(value.get("messages") or [])
        profile = contact.get("profile") or {}
        meta = value.get("metadata") or {}

        wa_id = contact.get("wa_id")
        from_field = msg.get("from")
        user_id = contact.get("user_id") or msg.get("from_user_id")

        raw_phone = wa_id or from_field
        phone = None
        if raw_phone:
            if is_bsuid(raw_phone):
                user_id = user_id or raw_phone
            else:
                phone = raw_phone

        peer_metadata = {}
        if user_id:
            peer_metadata["user_id"] = user_id
        if profile.get("username"):
            peer_metadata["username"] = profile.get("username")

        metadata = {
            'phone_number_id': meta.get("phone_number_id"),
            'display_phone_number': meta.get("display_phone_number"),
            'message_id': data.get("entry")[0].get("id") if data.get("entry") else None,
            'date': value.get("timestamp"),
            'raw': data,
            'wamid': msg.get("id"),
            'user_id': user_id,
        }
        conversation_peer = ConversationPeer(
            name=profile.get("name"),
            id=user_id or phone,
            phone=filter_phone_number(phone) if phone else None,
            metadata=peer_metadata or None,
            avatarUrl=None,
            email=None
        )
        return WhatsappLead(
            phone=phone,
            user_id=user_id,
            metadata=metadata,
            conversation_from=conversation_peer,
            **kwargs
        )
