# Introduction

## Welcome to Cel.ai

Cel.ai is a powerful Python framework designed to accelerate the development of omnichannel virtual assistants. Whether you need to integrate with platforms like WhatsApp, Telegram, or VoIP services such as VAPI.com, Cel.ai provides the tools and flexibility to get your assistant up and running quickly.

## Why Cel.ai?

- **Rapid Development**: Quickly deploy AI assistants across multiple messaging platforms.
- **Flexibility**: Easily create custom connectors, middlewares and assistants.
- **Extensibility**: Use middlewares to add custom functionality, decode messages, handle security, and session management.

Explore the documentation to learn more about how Cel.ai can help you build powerful, omnichannel virtual assistants with ease.
Feel free to customize this introduction to better fit your specific needs and use cases.

## Key Features
 
- **Modular Design**: Designed with a modular architecture that allows you to easily extend and customize its functionality.
- **Asynchronous**: Built on top of the FastAPI framework, Cel.ai is designed to be asynchronous and scalable.
- **Streaming**: Supports different stream modes to optimize the user experience based on the specific requirements of the platform and the nature of the interaction. 
- **Runs on Script**: This system is designed with the principle that it can run a minimal QA/FAQ + RAG assistant in a single script without requiring databases, external services, or complex configurations.
- **Open Source**: Cel.ai is open source and actively maintained by the community.


## Overview

<p align="center">
  <img src="assets/celia_overview1.png" width="95%" />
</p>


## Key Components

### Connectors
Cel.ai comes with out-of-the-box support for several popular platforms:

- **WhatsApp**
- **Telegram**
- **VAPI.com**
- **CLI**

These connectors translate messages between the platform and Cel.ai's agnostic message format, allowing the assistant to interact with different messaging platforms seamlessly. 
Additionally, the framework allows for the creation of custom connectors, enabling seamless integration with virtually any platform.

### Middlewares
Cel.ai supports the use of middlewares to extend and customize the functionality of your virtual assistants. This allows for greater flexibility and control over how your assistant processes and responds to user interactions. Middlewares can be used to add custom logic, perform data validation, or perform authentication, rate limiting, blacklisting, and more.

You will find useful middlewares for decoding messages into a suitable format for Natural Language Processing (NLP) models. Take a look of `GeodecodingMiddleware` which decodes a message shared location into a human-readable address using the Google Maps API. 

So you can easily create your own middleware to add custom functionality to your assistant.
For example, you can create a `PDFDecodingMiddleware` to decode a PDF file shared by the user into a text format that can be processed by the assistant.


### Assistants
At the core of Cel.ai are Assistants, which handle everything from conversation history persistence to state management and Retrieval-Augmented Generation (RAG). The framework includes a built-in assistant named **Macaw**, which is implemented using LangChain. However, you can also create your own assistant using the framework or any LLM model of your choice.



