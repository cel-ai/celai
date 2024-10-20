
<p align="center">
  <img src="https://raw.githubusercontent.com/cel-ai/celai/refs/heads/main/cel/assets/celai_middlewares.png" width="700" />
</p>


### Middlewares
Cel.ai supports the use of middlewares to extend and customize the functionality of your virtual assistants. This allows for greater flexibility and control over how your assistant processes and responds to user interactions.
Middlewares can be used to add custom logic, perform data validation, or perform authentication, rate limiting, blacklisting, and more.

You will find useful middlewares for decoding messages into a suitable format for Natural Language Processing (NLP) models. Take a look of `GeodecodingMiddleware` which decodes a message shared location into a human-readable address using the Google Maps API. 

So you can easily create your own middleware to add custom functionality to your assistant.
For example, you can create a `PDFDecodingMiddleware` to decode a PDF file shared by the user then convert it into a text format that can be processed by the assistant or sent to a Embedding model for further processing.

### Message Format

The message input to the middleware is a internal message format that is agnostic to the platform. So you can code your middleware and use it across different platforms without any changes.
You can share this middleware with the community and use it in different projects.


### Available Middlewares

#### Geodecoding Middleware 
Decodes a message shared location into a human-readable address using the Google Maps API. For example, if a user shares a location in Telegram, the middleware will decode the location into a human-readable address. If you add this middleware to your assistant, you can easily orientate the inference model to the user's location. Some times high level references such as neighborhoods, cities, or monuments can be useful to the assistant to provide better responses.

#### InvitationGuard Middleware
Useful for creating a invitation system for your assistant. If you need to restrict access to your assistant, you can use this middleware to create an invitation system. It handles invitation codes in messages and allows users to claim an invitation. You can also create, revoke, and get invitations. 
    
##### Features:
- Create, revoke and get invitations
- Claim an invitation
- Handle invitation codes in messages
- Backdoor code to bypass invitation system
        
    
##### Triggered events:
- **`new_conversation`**: Event called when a new conversation is started.
- **`rejected_code`**: Event called when a user enters an invalid code.
- **`admin_login`**: Event called when a user logs in as admin.
- **`admin_logout`**: Event called when a user logs out as admin.


#### DeepgramSTT Middleware

Deepgram Speech to Text Middleware for voice messages. It wll set the `message.text` with the STT result. This function is a wrapper for the DeepgramAdapter. 
You can change the voice ID, language, and other parameters in the `DeepgramAdapter` class.
With this middleware, you can easily add incoming voice message support to your assistant.

#### Blacklist Middleware

The Blacklist Middleware allows you to block users from interacting with your assistant. You can add users to the blacklist and prevent them from sending messages to your assistant. This can be useful for handling abusive users or for restricting access to your assistant.

There are two types of blacklists middleware:
- **In-memory blacklis**t: The blacklist is stored in memory and is not persistent. This means that the blacklist will be cleared when the assistant is restarted. `InMemBlackListMiddleware`

- **Redis blacklist**: The blacklist is stored in a Redis database and is persistent. This means that the blacklist will be saved even if the assistant is restarted `RedisBlackListAsyncMiddleware`