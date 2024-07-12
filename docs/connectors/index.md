# Introduction

Welcome to the Cel.ai Connectors documentation. This page provides an overview of the connectors supported by Cel.ai and instructions on how to create custom connectors.

## What Are Connectors?

Cel.ai is a Python framework designed to accelerate the development of omnichannel virtual assistants. Connectors in Cel.ai are responsible for translating the messaging schema or API of various platforms to Cel.ai's agnostic message format. This allows the assistant to interact with different messaging platforms seamlessly.

## Supported Connectors

Cel.ai comes with out-of-the-box support for the following connectors:

- **WhatsApp**
- **Telegram**
- **VAPI.com**
- **CLI**

<!-- 
## Supported Connectors

Cel.ai comes with out-of-the-box support for the following connectors:

### WhatsApp Connector

The WhatsApp connector translates messages between WhatsApp and Cel.ai. It uses the phone number as the user identifier.

**Example:**

```python
    wsp = WhatsappConnector(token=os.getenv("WHATSAPP_TOKEN"), 
                        phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID"),
                        verify_token="123456",
                        endpoint_prefix="/whatsapp",
                        stream_mode=StreamMode.FULL)
```

### Telegram Connector

The Telegram connector translates messages between Telegram and Cel.ai. It uses the `chat_id` as the user identifier.

**Example:**

```python
from celai.connectors import TelegramConnector

telegram_connector = TelegramConnector(api_key='your_api_key')
```

### VAPI.com Connector

The VAPI.com connector translates messages between VAPI.com and Cel.ai. It uses the `user_id` provided by VAPI.com as the user identifier.

**Example:**

```python
from celai.connectors import VapiConnector

vapi_connector = VapiConnector(api_key='your_api_key')
```

### CLI Connector

The CLI connector allows for interaction with Cel.ai via the command line interface. It uses the `pid_id` as the user identifier.

**Example:**

```python
from celai.connectors import CLIConnector

cli_connector = CLIConnector()
```

## Creating Custom Connectors

To create a custom connector, you need to implement the `BaseConnector` class provided by Cel.ai. This class requires you to define methods for translating messages to and from Cel.ai's message format.

**Example:**

```python
from celai.connectors import BaseConnector

class CustomConnector(BaseConnector):
    def __init__(self, custom_param):
        self.custom_param = custom_param

    def send_message(self, message):
        # Translate Cel.ai message to platform-specific message
        pass

    def receive_message(self, platform_message):
        # Translate platform-specific message to Cel.ai message
        pass
```

## Message Encoding

Cel.ai uses its own agnostic message encoding format. This allows the assistant to interact with different messaging platforms without worrying about the specific message format of each platform.

## User Identification

Each platform has its own mechanism for identifying users. Cel.ai connectors handle this by translating the platform-specific user identifiers to a format that Cel.ai can understand.

- **WhatsApp:** Phone number
- **Telegram:** `chat_id`
- **VAPI.com:** `user_id`
- **CLI:** `pid_id`

## Conclusion

Cel.ai connectors provide a seamless way to integrate various messaging platforms with your virtual assistant. Whether you are using the out-of-the-box connectors or creating your own custom connector, Cel.ai makes it easy to manage message translation and user identification.

For more detailed information, please refer to the [Cel.ai API documentation](#). -->
