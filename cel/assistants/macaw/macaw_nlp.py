import asyncio
from dataclasses import dataclass
import json
import traceback
from loguru import logger as log
from cel.assistants.function_response import FunctionResponse
from cel.assistants.macaw.custom_chat_models.chat_open_router import ChatOpenRouter
from cel.assistants.macaw.macaw_inference_context import MacawNlpInferenceContext
from cel.assistants.macaw.macaw_history_adapter import MacawHistoryAdapter
from cel.assistants.macaw.macaw_utils import get_last_n_elements, map_functions_to_tool_messages
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
    try:
        stored_state = await ctx.state_store.get_store(ctx.lead.get_session_id()) or {}    
        # TODO: Remove this when the self.init_state is removed
        stored_state.update(ctx.init_state or {})
    except Exception as e:
        raise ValueError("Macaw NLP: Error getting stored state") from e



    # Compile prompt
    # ------------------------------------------------------------------------  
    try: 
        prompt = await ctx.prompt.compile(stored_state, ctx.lead, message=message)
    except Exception as e:
        raise ValueError("Macaw NLP: Error compiling prompt") from e
    
    # RAG
    # ------------------------------------------------------------------------
    
    # Prompt > System Message
    history = [SystemMessage(prompt)]

    # Load messages from store before RAG retrieval
    msgs = await history_store.get_history(ctx.lead) or []

    # append to messages
    history.extend(msgs)

    # Add the human message
    input_msg = HumanMessage(message)
    
    # New messages buffer is a list of messages to be added to the history
    # If everything goes well, we will append this list to the history
    # at the end of the process
    new_messages = [input_msg]
    
    # Slice the messages 
    try:
        history = get_last_n_elements(history, ctx.settings.core_history_window_length)
    except Exception as e:
        log.critical(f"Error get_last_n_elements: {e}")
        # TODO: if we fail to get the last n elements, we should not process the message?
        # We should return an error message to the user?
        # or keep on processing the whole history?
        # For now, we keep on processing the whole history

    if ctx.rag_retriever:
        rag_response = ctx.rag_retriever.search(message, ctx.settings.core_rag_knn, history + new_messages)
        if rag_response:
            for vr in rag_response:
                prompt += f"\n{vr.text or ''}" 

    response = None
    try:
        # Process LLM invoke in a stream
        async for delta in llm_with_tools.astream(history + new_messages):
            assert isinstance(delta, AIMessageChunk)
            if response is None:
                response = delta
            else:
                response += delta
                
            # Yield the response if it's not a tool call
            if not response.tool_calls:
                yield StreamContentChunk(content=delta.content, is_partial=True)
                
                
        # Now we have the full response
        # Append Response to history (only memory)
        new_messages.append(response)
        
        # if it's a tool call
        if response.tool_calls:
            # We have tool calls, we need to process them
            # Handle multiple function calls and chained calls 
            # We use a for... to handle chained function calls until 
            # the max number of calls is reached
            # easy way to avoid infinite loop$
                
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
                            func_output = await on_function_call(ctx, mtool_call)
                            
                            response_text = None
                            if isinstance(func_output, FunctionResponse):
                                response_text = func_output.text
                            elif isinstance(func_output, str):
                                response_text = func_output
                            else:
                                response_text = "Data not found"

                            msg = ToolMessage(response_text, tool_call_id=id)
                            new_messages.append(msg)
                            log.debug(f"History udpated: func: {name} called with params: {args} -> {response_text}")

                        except Exception as e:
                            log.critical(f"Error calling function: {name} with args: {args} - {e}")
                            tool_output = "In this moment I can't process this request."
                            msg = ToolMessage(tool_output, tool_call_id=id)
                            new_messages.append(msg)

                            # break
                            # NOTE: If one function fails, the rest of the functions are not called?
                            # This is a design decision, we can change it later.
                            # ----------
                            # NOTE: Removed due broken behavior. If one function fails, the history ends badly. 
                            # ToolCall messages end with no ToolMessage. It's better to have a message with the error.

                    # Process response
                    response = llm_with_tools.invoke(history + new_messages)
                    new_messages.append(response)
                else:
                    yield StreamContentChunk(content=response.content, is_partial=True)
                    break
                
            # TODO: This validation may not be needed
            # -----------------------------------------------
            # # Here we have finished the loop and we got the whole list of new_messages to be stored in the history
            # # Last step is to verify that the new_messages list is valid and store it in the history
            # # Validating the list is important to avoid storing invalid messages sequences in the history
            # # Corrupted history can lead to a blocking error for this user in the future
            # # First message must be a HumanMessage
            # if new_messages[0].type != "human":
            #     raise ValueError("Macaw NLP process_message: First message must be a HumanMessage")
            
            # # Second message must be a AIMessageChunk
            # # with additional arguments for tool calls
            # if not isinstance(new_messages[1], AIMessageChunk):
            #     raise ValueError("Macaw NLP process_message: Second message must be a AIMessageChunk")
            # else:
            #     if not new_messages[1].tool_calls:
            #         raise ValueError("Macaw NLP process_message: Second message must have tool calls")
                
            # tool_calls = new_messages[1].tool_calls
            
            # # Each message from 2 to n-1 must be a ToolMessage
            # for msg in new_messages[2:-1]:
            #     if not isinstance(msg, ToolMessage):
            #         raise ValueError("Macaw NLP process_message: Messages from 2 to n-1 must be ToolMessages")
            
            # # The number of tool calls must be the same as the number of ToolMessages
            # if len(tool_calls) != (len(new_messages)-2):
            #     raise ValueError("Macaw NLP process_message: Number of tool calls must be the same as the number of ToolMessages") 

            
            # TODO: add support for storing batch messages
            for msg in new_messages:
                await history_store.append_to_history(ctx.lead, msg)

            log.debug(f"Validated history store udpated with tool calls: {len(new_messages)} messages stored, session: {ctx.lead.get_session_id()}")
        else:
            # No tool calls, we can store the new_messages in the history
            # TODO: add support for storing batch messages
            for msg in new_messages:
                await history_store.append_to_history(ctx.lead, msg)
            log.debug(f"History store udpated: {len(new_messages)} messages stored, session: {ctx.lead.get_session_id()}")

            
    except Exception as e:
        # Leave the unhandled user message in the history?????
        # TODO: Check if this is the correct behavior
        await history_store.append_to_history(ctx.lead, response)
        
        raise ValueError("Macaw NLP: Error processing message") from e

        
    


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