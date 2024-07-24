# Introduction

Welcome to the Cel.ai Connectors documentation. This page provides an overview of the connectors supported by Cel.ai and instructions on how to create custom connectors.

## What Are Connectors?

Cel.ai is a Python framework designed to accelerate the development of omnichannel virtual assistants. 
Connectors in Cel.ai are responsible for translating back and forth between the platform-specific message format and Cel.ai's agnostic message format.
So connectors are a decpoupling layer between the messaging platform and Cel.ai's message format.

Each connector is responsible for handling the specifics of a particular messaging platform, and register in Message Gateway the required endpoints to receive messages from the platform.


## Webhook Overview

Message Gateway is the core component of Cel.ai that handles the communication between the assistant and the connectors. It is responsible for processing incoming messages, invoking the assistant, and sending responses back to the connectors.

Message Gateway runs a single FastAPI server that listens for incoming messages for all registered connectors. When a connector registers into the gateway, it provides the routes that the gateway should listen to for incoming messages.

<p align="center">
  <img src="../assets/celia_fastapi.png" width="80%" />
</p>

So in order to receive messages from a messaging platform, you need a public URL that the platform can send messages to. This is where a webhook comes into play. Usually messaging platforms require a public HTTPS endpoint to send messages to your assistant.

You can use tools like ngrok to create a secure tunnel to your local server, providing a public URL that can be used to receive webhooks and other HTTP requests from external services. Take a look at the [Webhook URL with ngrok](./webhook_url.md) guide to learn how to set up ngrok and expose your local server to the internet securely.

Some users have reported that they have been able to use [pinggy.io](https://pinggy.io/) to create a public URL for their local server. You can try it out and see if it works for you.

???+ warning "Whatsapp and ngrok"

    Whatsapp may not work with **ngrok** free tier. Today 24 June 2024 only works with **ngrok paid tier**.


## Supported Connectors

Cel.ai comes with out-of-the-box support for the following connectors:

- **WhatsApp**
- **Telegram**
- **VAPI.com**
- **CLI**
