# !#/bin/bash
# this is a bash script to clear all the environment variables
# to run this script, type in the terminal: source .clear_envs.sh
# or you can also use the command: . .clear_envs.sh

# clear all the environment variables
unset REDIS_URL
unset OPENAI_API_KEY
unset OPENROUTER_API_KEY
unset DEEPGRAM_API_KEY
unset LANGCHAIN_TRACING_V2
unset LANGCHAIN_API_KEY
unset GOOGLE_GEOCODING_API_KEY
unset WHATSAPP_TOKEN
unset WHATSAPP_PHONE_NUMBER_ID
unset WHATSAPP_DISPLAY_PHONE_NUMBER
unset TELEGRAM_TOKEN
unset WEBHOOK_URL
unset HOST
unset PORT

# check if the environment variables are cleared
echo "Environment variables are cleared"




