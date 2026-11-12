"""Contract for reasoning_effort when Macaw binds tools (process_new_message LLM kwargs)."""


def _core_llm_settings_with_tools(functions, model: str = "gpt-6-luna") -> dict:
    settings = {"model": model}
    if functions:
        settings["reasoning_effort"] = "none"
    return settings


def test_reasoning_effort_none_when_tools_present():
    settings = _core_llm_settings_with_tools([object()])
    assert settings["reasoning_effort"] == "none"


def test_no_reasoning_effort_without_tools():
    settings = _core_llm_settings_with_tools(None)
    assert "reasoning_effort" not in settings
