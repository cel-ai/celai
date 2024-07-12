# Ideas
from cel.channels import WhatsappChannel, TelegramChannel, Channel
from cel.assistant import AssistantGateway, Assistant, Context, Message, Command, CommandResponse, Lead
from cel.agent import Lila
from cel.store import StateRedisStore, HistoryRedisStore
from cel.middleware import Middleware
from cel.rag import RedisRagProvider

# Use cases:
# - Message incoming from a channel: 
#   - Connector -> AssistantGateway -> Assistant -> Agent -> RAG -> Stores
# - Command incoming from a channel:

# Stores
store = StateStore(url='redis://localhost:6379/0', prefix='s')
history = HistoryStore(url='redis://localhost:6379/0', prefix='h')



# Build RAG
rag = RedisRagProvider('redis://localhost:6379/0')
rag.load('terms.md', 'terms')
rag.load('concepts.md', 'concepts')


# Build Agent
# RAG: There are Agent implementations for different platforms, some platforms 
# may not require a rag provider, other may require a different store
# so rag, history and stores are defined by the implementation

# sessionID: in order to keep track of the conversation and the state of the user
# stores must understand the concept of sessionID. But CahtLead is a concept of more
# high level.
agent = Lila(store, history, rag, redis='redis://localhost:6379/0')


# Assistant Definitions
# The assistant is the main class that will handle the conversation with the user
# It will define:
# - Commands: The commands that the user can send to the assistant
# - Events: The events that the assistant will handle
# - Timeout: The timeout event
# - Middleware: The middleware that will be executed before the assistant handle the message
# - Prompt: The initial prompt of the assistant
# - Initial State: The initial state of the assistant
def build_assistant():
    # Build Assistant
    prompt = """Hi, I'm your assistant. How can I help you today?"""
    initial_state = {'name': 'assistant', 'state': 'idle'}
    a = Assistant(prompt, agent, initial_state)
    
    @a.command('get_cryptocurrency_price', 
                  description='Get the price of a cryptocurrency',
                  params={'cryptocurrency': 'The cryptocurrency to get the price'})
    def help_command(lead: Lead, ctx: Context, cmd: Command):
        data = "The price of {} is $1000".format(cmd.params['cryptocurrency'])
        
        def handle_response(response):
            # Handle custom response to the user
            ctx.send_template('price', response)
            # Return none will cancel the automatic response to the user
            return None
        
        # handle_response is a function that takes the response from LLM and formats it
        return CommandResponse(data, handle_response=handle_response)
    
    @a.event('start') # start conversation
    def start_event(lead: Lead, ctx: Context, msg: Message):
        return "Hi, I'm your assistant. How can I help you today?"
    
    @a.event('message') # new message
    def message_event(lead: Lead, ctx: Context, msg: Message):
        return "I'm here to help you. Just ask me anything."
    
    @a.event('end') # end conversation
    def end_event(lead: Lead, ctx: Context, msg: Message):
        return "Goodbye! Have a nice day."
    
    @a.timeout() # timeout
    def timeout_event(lead: Lead, ctx: Context, metadata: dict):
        return "I'm sorry, I didn't understand you. Can you please repeat that?"
    
    return a


def build_channels() -> list[Channel]:
    return [
        WhatsappChannel(token='your_token', phoneid='your_phoneid'),
        TelegramChannel(token='your_token'),
    ]


assistant = build_assistant()
AssistantGateway(assistant, build_channels()).run()