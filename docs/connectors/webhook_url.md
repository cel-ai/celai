# Webhook URL with ngrok

## Introduction

Ngrok is a tool that allows you to expose a local server to the internet securely. It creates a secure tunnel to your localhost, providing a public URL that can be used to receive webhooks and other HTTP requests from external services. This is particularly useful for developing and testing integrations with platforms like WhatsApp and Telegram, which require a publicly accessible HTTPS endpoint to send messages and updates.

## Why Use ngrok?

- **Secure Tunneling**: Ngrok provides a secure tunnel to your local server, ensuring that your data is encrypted.
- **Public URL**: It generates a public URL that can be accessed from anywhere, making it easy to test webhooks and other integrations.
- **Ease of Use**: Setting up ngrok is straightforward and requires minimal configuration.


## Steps to Set Up ngrok

### Step 1: Download and Install ngrok

Visit the [ngrok website](https://ngrok.com/download) and download the appropriate version for your operating system.

### Step 2: Sign Up and Authenticate

1. Sign up for a free account on the [ngrok website](https://ngrok.com/).
2. After signing up, you will receive an authentication token.
3. Open a terminal and run the following command to authenticate ngrok with your account:

    ```sh
    ngrok authtoken YOUR_AUTH_TOKEN
    ```

    Replace `YOUR_AUTH_TOKEN` with the token you received.

### Step 3: Start ngrok

1. Open a terminal.
2. Run the following command to start ngrok and create a tunnel to your local server:

    ```sh
    ngrok http 5004
    ```

3. You will see output similar to the following:

    ```plaintext
    ngrok by @inconshreveable                                                                                                      (Ctrl+C to quit)

    Session Status                online
    Account                       Your Name (Plan: Free)
    Version                       2.3.35
    Region                        United States (us)
    Web Interface                 http://127.0.0.1:4040
    Forwarding                    http://abcd1234.ngrok.io -> http://127.0.0.1:5004
    Forwarding                    https://abcd1234.ngrok.io -> http://127.0.0.1:5004

    Connections                   ttl     opn     rt1     rt5     p50     p90
                                  0       0       0.00    0.00    0.00    0.00
    ```

4. Note the `https://abcd1234.ngrok.io` URL. This is the public HTTPS URL that forwards requests to your local server running on `127.0.0.1:5004`.

### Step 4: Use the Public URL

- Use the `https://abcd1234.ngrok.io/whatsapp` URL to configure webhooks or other integrations with platforms like WhatsApp.
- Use `https://abcd1234.ngrok.io/telegram` for Telegram integrations.
- Ensure that your Cel.ai Assistant is running on local server `127.0.0.1:5004`.

## Conclusion

By following these steps, you have successfully set up ngrok to create a secure tunnel to your local server. You now have a public HTTPS URL that can be used to receive messages and updates from platforms like WhatsApp and Telegram. This setup is ideal for development and testing purposes, allowing you to work with webhooks and other integrations seamlessly.

