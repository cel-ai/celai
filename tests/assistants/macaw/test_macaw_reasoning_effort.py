"""Contract for reasoning_effort when Macaw binds tools (process_new_message LLM kwargs)."""

from cel.assistants.macaw.macaw_nlp import (
    maybe_set_reasoning_effort_none,
    model_supports_reasoning_effort,
)


def _core_llm_settings_with_tools(functions, model: str = "gpt-6-luna") -> dict:
    settings = {"model": model}
    maybe_set_reasoning_effort_none(settings, has_tools=bool(functions))
    return settings


def test_model_supports_reasoning_effort_gpt6_luna():
    assert model_supports_reasoning_effort("gpt-6-luna")
    assert model_supports_reasoning_effort("openai/gpt-6-luna")


def test_model_supports_reasoning_effort_gpt4o_false():
    assert not model_supports_reasoning_effort("gpt-4o")
    assert not model_supports_reasoning_effort("gpt-4o-mini")
    assert not model_supports_reasoning_effort("gpt-3.5-turbo")


def test_reasoning_effort_none_when_tools_present_supported_model():
    settings = _core_llm_settings_with_tools([object()], model="gpt-6-luna")
    assert settings["reasoning_effort"] == "none"


def test_no_reasoning_effort_with_tools_gpt4o():
    settings = _core_llm_settings_with_tools([object()], model="gpt-4o")
    assert "reasoning_effort" not in settings


def test_no_reasoning_effort_without_tools():
    settings = _core_llm_settings_with_tools(None, model="gpt-6-luna")
    assert "reasoning_effort" not in settings
