# WhatsApp Connector

The `Whatsapp Connector` is a component of the Cel.ai framework that allows seamless integration with the WhatsApp Cloud API. This connector translates messages between WhatsApp and Cel.ai's agnostic message format, enabling the development of virtual assistants that can interact with users on WhatsApp.

## Initialization

To initialize the `Whatsapp Connector`, you need to provide the Meta Access Token, Phone Number ID, and a verification token. Optionally, you can also specify an endpoint prefix and stream mode.

### Parameters

- `token` (str): The Meta Access Token. This is required.
- `phone_number_id` (str): The Meta Phone Number ID. This is required.
- `verify_token` (str): The verification token used for webhook verification. This is required.
- `endpoint_prefix` (str, optional): The prefix for the webhook endpoint. Defaults to `"/whatsapp"`.
- `stream_mode` (StreamMode, optional): The mode for streaming messages. Defaults to `StreamMode.SENTENCE`. See [Stream Modes](./stream_mode.md) for more information.


### Example

```python
from cel.connectors.whatsapp.whatsapp_connector import WhatsappConnector

wsp = WhatsappConnector(token=os.getenv("WHATSAPP_TOKEN"), 
                    phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID"),
                    verify_token="123456",
                    endpoint_prefix="/whatsapp",
                    stream_mode=StreamMode.FULL)
```

## Attributes

- `token` (str): The Meta Access Token.
- `phone_number_id` (str): The Meta Phone Number ID.
- `base_url` (str): The base URL for the WhatsApp Cloud API.
- `url` (str): The full URL for sending messages.
- `verify_token` (str): The verification token. Setup this token in the WhatsApp Cloud API settings.
- `endpoint_prefix` (str): The prefix for the webhook endpoint.
- `stream_mode` (StreamMode): The mode for streaming messages.
- `verification_handler` (callable): The handler for verification requests.


## Whatsapp Assistant 


```py title='main.py'
# Import Cel.ai modules
from cel.gateway.message_gateway import MessageGateway, StreamMode
from cel.message_enhancers.smart_message_enhancer_openai import SmartMessageEnhancerOpenAI
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.connectors.whatsapp.whatsapp_connector import WhatsappConnector


# Setup prompt
prompt = """You are an AI assistant. Called Celia. You can help a user to buy Bitcoins."""
prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
ast = MacawAssistant(
    prompt=prompt_template
)

# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    webhook_url=os.environ.get("WEBHOOK_URL"),
    assistant=ast,
    host="127.0.0.1", port=5004,
    message_enhancer=SmartMessageEnhancerOpenAI(),
    delivery_rate_control=False
)

wsp = WhatsappConnector(token=os.getenv("WHATSAPP_TOKEN"), 
                    phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID"),
                    verify_token="123456",
                    stream_mode=StreamMode.FULL)

# Register the connector with the gateway
gateway.register_connector(wsp)

# Then start the gateway and begin processing messages
gateway.run()
```


## Notes

- Ensure that the `WHATSAPP_TOKEN` Meta Access Token and `WHATSAPP_PHONE_NUMBER_ID` Phone Number ID are valid and have the necessary permissions to interact with the WhatsApp Cloud API.
- Get the `WHATSAPP_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID` from the WhatsApp Business API settings.
- The verification token is used to verify the webhook endpoint with WhatsApp. Make sure it matches the token you set in the WhatsApp Cloud API settings.



This documentation provides an overview of the `WhatsappConnector` and how to initialize and use it within the Cel.ai framework. For more detailed information, refer to the Cel.ai official documentation.
