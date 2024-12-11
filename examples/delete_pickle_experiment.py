import pickle
from cel.gateway.model.conversation_lead import ConversationLead
from cel.connectors.telegram import TelegramLead
from cel.connectors.whatsapp.whatsapp_connector import WhatsappLead


# Crear instancia y serializar
lead = TelegramLead("123")
serialized_lead = pickle.dumps(lead)

# zip compress the serialized lead
compressed_lead = pickle.dumps(lead, protocol=2)

# convert to string url safe
serialized_lead = serialized_lead.hex()
compressed_lead = compressed_lead.hex()

# Convertir a bytes
serialized_lead = bytes.fromhex(serialized_lead)

# Deserializar
lead_instance = pickle.loads(serialized_lead)
print(type(lead_instance))  # <class '__main__.TelegramLead'>