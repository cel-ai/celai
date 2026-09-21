import pytest
from langchain_core.messages import AIMessage, AIMessageChunk

from cel.assistants.common import FunctionDefinition, Param
from cel.assistants.macaw.macaw_inference_context import MacawNlpInferenceContext
from cel.assistants.macaw.macaw_nlp import TOOL_LOOP_FALLBACK_MESSAGE, process_new_message
from cel.assistants.macaw.macaw_settings import MacawSettings
from cel.gateway.model.conversation_lead import ConversationLead
from cel.prompt.prompt_template import PromptTemplate
from cel.stores.history.history_inmemory_provider import InMemoryHistoryProvider
from cel.stores.state.state_inmemory_provider import InMemoryStateProvider

TOOL_CALL = {"name": "get_price", "args": {"crypto": "BTC"}, "id": "call_1"}

func = FunctionDefinition(
    name="get_price",
    description="Get the current price of a cryptocurrency.",
    parameters=[Param(name="crypto", type="string", description="Ticker", required=True)],
)


class FakeLLM:
    """LLM double that always asks for the same tool call, so the agent loop
    always runs out of its function-call budget."""

    def __init__(self, final_content: str = "Here is the price.", **kwargs):
        self.final_content = final_content
        self.bound_tools = False
        self.ainvoke_calls = 0
        self.tool_calls_seen = []

    def __call__(self, **kwargs):
        return self

    def bind_tools(self, tools):
        bound = FakeLLM(final_content=self.final_content)
        bound.bound_tools = True
        bound._parent = self
        return bound

    async def astream(self, messages):
        yield AIMessageChunk(content="", tool_call_chunks=[{
            "name": TOOL_CALL["name"],
            "args": '{"crypto": "BTC"}',
            "id": TOOL_CALL["id"],
            "index": 0,
        }])

    async def ainvoke(self, messages):
        self.ainvoke_calls += 1
        if self.bound_tools:
            # Never settles: keeps requesting another tool call.
            return AIMessage(content="", tool_calls=[dict(TOOL_CALL, id=f"call_{self.ainvoke_calls}")])
        return AIMessage(content=self.final_content)


class UnboundOnlyFakeLLM(FakeLLM):
    """Same as FakeLLM but the un-bound model has nothing to say either."""

    async def ainvoke(self, messages):
        self.ainvoke_calls += 1
        if self.bound_tools:
            return AIMessage(content="", tool_calls=[dict(TOOL_CALL, id=f"call_{self.ainvoke_calls}")])
        return AIMessage(content="   ")


def build_ctx(llm, max_calls: int = 2):
    settings = MacawSettings()
    settings.core_max_function_calls_in_message = max_calls
    return MacawNlpInferenceContext(
        lead=ConversationLead(),
        prompt=PromptTemplate("You are a helpful assistant."),
        functions=[func],
        history_store=InMemoryHistoryProvider(),
        state_store=InMemoryStateProvider(),
        settings=settings,
        llm=llm,
    )


async def on_function_call(ctx, tool_call):
    return "42"


@pytest.mark.asyncio
async def test_exhausted_tool_loop_still_answers_the_user():
    """Regression: running out of core_max_function_calls_in_message with a tool
    call still pending yielded nothing at all, so the user got silence."""
    llm = FakeLLM()
    ctx = build_ctx(llm)

    chunks = [c async for c in process_new_message(ctx, "What is the price of BTC?", on_function_call)]

    assert [c.content for c in chunks] == ["Here is the price."]


@pytest.mark.asyncio
async def test_exhausted_tool_loop_falls_back_when_the_model_stays_empty():
    ctx = build_ctx(UnboundOnlyFakeLLM())

    chunks = [c async for c in process_new_message(ctx, "What is the price of BTC?", on_function_call)]

    assert [c.content for c in chunks] == [TOOL_LOOP_FALLBACK_MESSAGE]


@pytest.mark.asyncio
async def test_exhausted_tool_loop_does_not_persist_a_dangling_tool_call():
    """An AI message carrying tool_calls with no matching ToolMessage poisons the
    next turn, so it must not reach the history."""
    ctx = build_ctx(FakeLLM())

    async for _ in process_new_message(ctx, "What is the price of BTC?", on_function_call):
        pass

    history = await ctx.history_store.get_history(ctx.lead.get_session_id())
    assert history
    assert history[-1]["kwargs"].get("content") == "Here is the price."
    assert not history[-1]["kwargs"].get("tool_calls")
