# cel/assistants/router/concierge_router.py
from __future__ import annotations

from typing import AsyncGenerator, Dict, List, Any
from loguru import logger as log
from langsmith import traceable
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from cel.assistants.router.agentic_router import AgenticRouter
from cel.assistants.base_assistant import BaseAssistant
from cel.assistants.function_response import FunctionResponse
from cel.assistants.stream_content_chunk import StreamContentChunk
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message

class ConciergeRouter(AgenticRouter):
    """
    The ConciergeRouter is a router that orchestrates the conversation between multiple agents.
    """

    ACTIVE_AGENT_KEY = "active_agent"
    TRANSFER_FLAG_KEY = "transfer_requested"
    MAX_TRANSFER_PER_TURN = 1                # prevents infinite loops

    DEFAULT_PROMPT = (
        "You are an orchestration agent.\n"
        "Your job is to decide which agent to run based on the current state "
        "of the user and what they've asked to do.\n"
        "You do not need to figure out dependencies between agents; the agents "
        "will handle that themselves.\n"
        "Here are the agents you can choose from:\n{agent_context_str}\n\n"
        "Here is the recent conversation:\n{dialog_str}\n\n"
        "Please assist the user and transfer them as needed.\n"
        "Return **only** the name of the agent."
        "If you are not sure, please select the default agent."
        "Default agent: {default_agent_name}"
    )

    def __init__(
        self,
        assistants: List[BaseAssistant],
        history_store=None,
        state_store=None,
        history_length: int = 5,
        llm=None,
        default_assistant: int = 0,
    ):
        super().__init__(
            assistants=assistants,
            history_store=history_store,
            state_store=state_store,
            history_length=history_length,
            llm=llm,
        )
        self._default_assistant = default_assistant
        # inject transfer tool into all agents
        for ast in self._assistants:
            self._inject_request_transfer_tool(ast)

    def _inject_request_transfer_tool(self, assistant: BaseAssistant) -> None:
        @assistant.function(
            name="request_transfer",
            desc="Useful to transfer the conversation to another agent.",
            params=[],
        )
        async def _request_transfer(session: str = None, **_) -> FunctionResponse:
            state = await self._state_store.get_store(session) or {}
            state[self.TRANSFER_FLAG_KEY] = True
            await self._state_store.set_store(session, state)
            log.debug(f"[ConciergeRouter] Transfer flag set by {assistant.name}")
            return FunctionResponse(text="")

    async def _get_active(self, session: str) -> str | None:
        state = await self._state_store.get_store(session) or {}
        return state.get(self.ACTIVE_AGENT_KEY)

    async def _set_active(self, session: str, name: str | None):
        state = await self._state_store.get_store(session) or {}
        if name is None:
            state.pop(self.ACTIVE_AGENT_KEY, None)
        else:
            state[self.ACTIVE_AGENT_KEY] = name
        state.pop(self.TRANSFER_FLAG_KEY, None)
        await self._state_store.set_store(session, state)

    async def _transfer_pending(self, session: str) -> bool:
        state = await self._state_store.get_store(session) or {}
        return bool(state.get(self.TRANSFER_FLAG_KEY))

    @traceable
    async def _infer_best_assistant(
        self, lead: ConversationLead, user_msg: str
    ) -> BaseAssistant:
        llm = self._llm or ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=64)

        agent_context_str = "\n".join(
            f"{ast.name}: {ast.description}" for ast in self._assistants
        )

        dialog_entries = await self.build_dialog(lead, user_msg)
        dialog_str = await self.format_dialog_to_plain_text(dialog_entries)

        system_prompt = self.DEFAULT_PROMPT.format(
            agent_context_str=agent_context_str,
            dialog_str=dialog_str,
            default_agent_name=self._assistants[self._default_assistant].name
        )

        res = await llm.ainvoke([SystemMessage(system_prompt), HumanMessage(user_msg)])
        agent_name = (res.content or "").strip()

        for ast in self._assistants:
            if ast.name.lower() == agent_name.lower():
                return ast

        log.warning(
            f"[ConciergeRouter] Unknown agent '{agent_name}', defaulting to "
            f"'{self._current_assistant.name}'."
        )
        return self._current_assistant

    @traceable
    async def _pick_agent(self, lead: ConversationLead, user_msg: str) -> BaseAssistant:
        active = await self._get_active(lead.get_session_id())
        if active:
            for ast in self._assistants:
                if ast.name == active:
                    return ast
            log.warning(f"Active agent '{active}' not found, re-inferring.")

        best = await self._infer_best_assistant(lead, user_msg)
        await self._set_active(lead.get_session_id(), best.name)
        return best

    async def new_message(
        self, message: Message, local_state: Dict[str, Any] | None = None
    ) -> AsyncGenerator[StreamContentChunk, None]:
        """
        If the agent requests a transfer, its output is discarded and the
        new agent responds immediately.
        """

        lead = message.lead
        session = lead.get_session_id()
        transfers = 0

        while transfers <= self.MAX_TRANSFER_PER_TURN:
            agent = await self._pick_agent(lead, message.text)
            log.debug(f"[ConciergeRouter] Active agent → {agent.name}")

            # buffer output in case of transfer
            buffer: List[StreamContentChunk] = []
            async for chunk in agent.new_message(message, local_state or {}):
                buffer.append(chunk)

            if await self._transfer_pending(session):
                # Discard response and prepare new agent
                log.info(f"[ConciergeRouter] Transfer triggered by {agent.name}")
                await self._set_active(session, None)          # clear flags
                transfers += 1
                continue                                       # retry with new agent
            else:
                # No transfer → send accumulated content to user
                for chunk in buffer:
                    yield chunk
                break
