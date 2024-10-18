
# PromptTemplate Class Documentation

The `PromptTemplate` class provides a mechanism to dynamically compile a string template with placeholders, using state data that can be static values or callable functions, including asynchronous functions. This is particularly useful in applications like chatbots or interactive prompt systems where template customization is required based on dynamic data sources or processing.

## Class Definition

```python
class PromptTemplate:
    def __init__(self, prompt: str)
```

### Methods

#### `__init__(self, prompt: str)`

Initializes a new instance of the `PromptTemplate` with a given prompt that contains placeholders.

- **Parameters:**
  - `prompt` (str): A string containing placeholders in the format `{key}`.

#### `async compile(self, state: Dict, lead: ConversationLead, message: str) -> str`

Compiles the prompt with the supplied state data, resolving each placeholder with the respective value from the state. Values in the state dictionary can be static or callable. Callable objects can also be asynchronous functions.

- **Parameters:**
  - `state` (Dict): A dictionary where keys are placeholder names and values are the data or callable that returns data.
  - `lead` (ConversationLead): An instance of `ConversationLead` used for accessing conversation-specific data.
  - `message` (str): The message context used in callable functions when compiling the template.

- **Returns:**
  - `str`: The compiled string with all placeholders replaced by their corresponding values.

- **Example:**
  
```python
    async def get_contacts_async(lead: ConversationLead):
        return ["Juan", "Pedro", "Maria"]
    
    def get_balance(lead: ConversationLead, message: str):
        return {
            "checking": 1000,
            "savings": 5000
        }
    
    prompt = """Hola, {name}. Tienes {messages} mensajes nuevos.
    Tiene los siguientes contactos: {contacts}.
    Su saldo es: 
    {balance}"""
    
    state = {
        "name": "Juan",
        "messages": lambda: 5,
        "contacts": get_contacts_async,
        "balance": get_balance
    }
    
    template = PromptTemplate(prompt)
    result = await template.compile(state, lead, "Hola")
  ```

#### `async call_function(self, func: Callable, message: Optional[str] = None, current_state: Optional[dict] = None, lead: Optional[ConversationLead] = None) -> str`

Executes the given function with dynamic arguments based on the provided context, which includes the lead, message, and state. Handles both synchronous and asynchronous functions. 

- **Parameters:**
  - `func` (Callable): The function to be invoked with specific arguments.
  - `message` (str, optional): Contextual message to pass as an argument, if applicable.
  - `current_state` (dict, optional): Current state that might be needed inside the function.
  - `lead` (ConversationLead, optional): Required context containing the lead data required to call the function.

- **Returns:**
  - `str`: Result from the function call as a JSON string if it's a dictionary, or a simple string.

- **Example:**
  
```python
  async def custom_function(lead: ConversationLead, session_id: str):
      return {"data": "Result"}
  
  response = await template.call_function(custom_function, lead=lead)
```

### Considerations

- Ensure that any callable within the `state` dictionary correctly handles the parameters it expects.
- Use `asyncio` for handling asynchronous operations efficiently.
- Handle exceptions within the `call_function` to avoid abrupt failures.

This class can be extended and modified to handle more complex scenarios and additional data processing requirements. It forms a core component in scenarios demanding template-based dynamic content generation. 
