import asyncio
from dataclasses import dataclass
import json
from loguru import logger as log
from cel.assistants.function_response import FunctionResponse
from cel.assistants.macaw.custom_chat_models.chat_open_router import ChatOpenRouter
from cel.assistants.macaw.macaw_inference_context import MacawNlpInferenceContext
from cel.assistants.macaw.macaw_history_adapter import MacawHistoryAdapter
from cel.assistants.macaw.macaw_utils import map_functions_to_tool_messages
from cel.assistants.stream_content_chunk import StreamContentChunk
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessageChunk
from langchain_core.messages import (
    SystemMessage,
    message_to_dict,
    messages_from_dict,
)
from langsmith import traceable

DEFAULT_PROMPT = "Create an assistant funny and sarcastic, dark humor chatbot."
LLM_DEFAULT_KWARGS = {
    "model": "gpt-4o",
    "temperature": 0,
    "max_tokens": None,
    "timeout": 20,
    "max_retries": 3,
    "streaming": True,
    "verbose": True
}

@dataclass
class MacawFunctionCall:
    name: str
    args: dict
    id: str     

@traceable
async def process_new_message(ctx: MacawNlpInferenceContext, message: str, on_function_call=None):
    assert isinstance(ctx, MacawNlpInferenceContext),\
        "ctx must be an instance of MacawNlpInferenceContext"
    assert isinstance(message, str),\
        "message must be a string"

    
    history_store = MacawHistoryAdapter(ctx.history_store)
    
    # Create settings
    settings = {**LLM_DEFAULT_KWARGS}
    settings["model"] = ctx.settings.core_model
    settings["temperature"] = ctx.settings.core_temperature
    settings["max_tokens"] = ctx.settings.core_max_tokens
    settings["timeout"] = ctx.settings.core_timeout
    settings["max_retries"] = ctx.settings.core_max_retries
    # **{"model": "mistralai/mixtral-8x7b-instruct"}
    # merge kwargs
    ctx.llm = ctx.llm or ChatOpenAI
    llm = ctx.llm(
        **{**settings, **(ctx.llm_kwargs or {})}
    )

    try:
        # Toolling
        functions = ctx.functions
        if functions is not None and len(functions) > 0:
            mapfuncs = map_functions_to_tool_messages(functions)
            llm_with_tools = llm.bind_tools(mapfuncs)
        else:
            llm_with_tools = llm
    except Exception as e:
        if isinstance(e, NotImplementedError):
            log.error(f"Error binding tools: Functions not implemented")
        else:
            log.error(f"Error binding tools: {e}")
        llm_with_tools = llm    
    
    # Build State
    # ------------------------------------------------------------------------
    stored_state = await ctx.state_store.get_store(ctx.lead.get_session_id())
    # Initial state  
    init_state = ctx.init_state or {}
    # Current state
    current_state = {**init_state, **(stored_state or {})}

    # Compile prompt
    # ------------------------------------------------------------------------
    prompt = await ctx.prompt.compile(current_state, ctx.lead)
    
    # RAG
    # ------------------------------------------------------------------------
    if ctx.rag_retriever:
        rag_response = ctx.rag_retriever.search(message, ctx.settings.core_rag_knn)
        if rag_response:
            for vr in rag_response:
                prompt += f"\n{vr.text or ''}"

    
    # Prompt > System Message
    messages = [SystemMessage(prompt)]
    
    # Load messages from store
    msgs = await history_store.get_last_messages(
        ctx.lead, 
        ctx.settings.core_history_window_length) or []
    # Map to BaseMessages and append to messages
    messages.extend(msgs)
    
    # Add the human message
    input_msg = HumanMessage(message)
    messages.append(input_msg)
    
    
    # Impact on history store, on the background
    asyncio.create_task(
        history_store.append_to_history(ctx.lead, input_msg)
    )
    
    response = None
    async for delta in llm_with_tools.astream(messages):
        assert isinstance(delta, AIMessageChunk)
        if response is None:
            response = delta
        else:
            response += delta    
    
        # if delta.content:
        #     # Shield the content from the response
        #     yield StreamContentChunk(content=delta.content, is_partial=True)
    
    # Append the final response
    messages.append(response)
    # Impact on history store, on the background
    asyncio.create_task(history_store.append_to_history(ctx.lead, response))            


    # Allow for multiple function calls in a single message request
    for idx in range(ctx.settings.core_max_function_calls_in_message):
        if response.tool_calls:
            # Do all function calls
            for tool_call in response.tool_calls: 
                name = tool_call.get("name")
                args = tool_call.get("args")
                id = tool_call.get("id")
                log.debug(f"Function: {name} called with params: {args}")
                try:
                    mtool_call = MacawFunctionCall(name, args, id)
                    func_output: FunctionResponse = await on_function_call(ctx, mtool_call)

                    msg = ToolMessage(func_output.text, tool_call_id=id)
                    messages.append(msg)
                    # Impact on history store, on the background
                    asyncio.create_task(
                        history_store.append_to_history(
                            ctx.lead,
                            msg)
                        )
                except Exception as e:
                    log.critical(f"Error calling function: {name} with args: {args} - {e}")
                    tool_output = "In this moment I can't process this request."
                    msg = ToolMessage(tool_output, tool_call_id=id)
                    messages.append(msg)
                    # Impact on history store, on the background
                    asyncio.create_task(
                        history_store.append_to_history(
                            ctx.lead,
                            msg)
                        )
                    break

            # Process response
            response = llm_with_tools.invoke(messages)
        else:
            yield StreamContentChunk(content=response.content, is_partial=True)
            break
        


@traceable
async def blend_message(ctx: MacawNlpInferenceContext, message: str):
    """Blend a message using the conversation context."""
    
    assert isinstance(ctx, MacawNlpInferenceContext),\
        "ctx must be an instance of MacawNlpInferenceContext"
    assert isinstance(message, str),\
        "message must be a string"
        
    history_store = MacawHistoryAdapter(ctx.history_store)
    
    # Create settings
    settings = {**LLM_DEFAULT_KWARGS}
    settings["model"] = ctx.settings.blend_model
    settings["temperature"] = 0.0
    settings["max_tokens"] = ctx.settings.blend_max_tokens
    settings["timeout"] = ctx.settings.blend_timeout
    settings["max_retries"] = ctx.settings.blend_max_retries
    
    # merge kwargs
    ctx.llm = ctx.llm or ChatOpenAI
    llm = ctx.llm(
        **{**settings, **(ctx.llm_kwargs or {})}
    )


    # Load messages from store
    msgs = await history_store.get_last_messages(
        ctx.lead, 
        ctx.settings.blend_history_window_length) or []
    # Map to BaseMessages and append to messages
    
    dialog = ""
    for msg in msgs:
        dialog += f"{msg.type}: {msg.content}\n"

    prompt1 = f"Given this conversation:\n{dialog}"
    prompt2 = ("Elaborate this response in context to the user"
               "(translate if needed to users lang, dont use markdown,"
               f"dont include assistan: or user: labels): {message}")

    # Prompt > System Message
    messages = [SystemMessage(prompt1), SystemMessage(prompt2)]

    res = llm.invoke(messages)

    return res.content

@traceable
async def process_insights(ctx: MacawNlpInferenceContext, targets: dict = {}, history_length: int = 10):
    """ Get insights from the conversation history """
    
    assert isinstance(ctx, MacawNlpInferenceContext),\
        "ctx must be an instance of MacawNlpInferenceContext"
    assert isinstance(targets, dict),\
        "targets must be a dictionary"

    if not targets:
        return None
        
    history_store = MacawHistoryAdapter(ctx.history_store)
    
    # Create settings
    settings = {**LLM_DEFAULT_KWARGS}
    settings["model"] = ctx.settings.insights_model
    settings["temperature"] = 0.0
    settings["max_tokens"] = ctx.settings.insights_max_tokens
    settings["timeout"] = ctx.settings.insights_timeout
    settings["max_retries"] = ctx.settings.insights_max_retries
    
    # merge kwargs
    llm = ChatOpenAI(
        **settings
    )


    # Load messages from store
    msgs = await history_store.get_last_messages(
        ctx.lead, 
        ctx.settings.insights_history_window_length) or []
    # Map to BaseMessages and append to messages
    
    dialog = ""
    for msg in msgs:
        dialog += f"{msg.type}: {msg.content}\n"

    entities = ""
    for target in targets:
        entities += f"{target}: {targets.get(target)}\n"
        
    prompt = f"""Given this conversation: 
{dialog}
Extract insights for the following entities:
{entities}
Build a json (don't use markdown), skip keys with empty values, use the following format:
{{"entity1": "value1", "entity2": "value2"}}"""

    # Prompt > System Message
    messages = [SystemMessage(prompt)]

    try:
        res = await llm.ainvoke(messages)
        return json.loads(res.content)    
    except Exception as e:
        log.error(f"Error processing insights: {e}")
        return None