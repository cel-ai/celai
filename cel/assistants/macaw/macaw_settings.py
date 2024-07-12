from dataclasses import dataclass


@dataclass
class MacawSettings:
    """ Macaw Assistant Settings 
    Core settings are used to configure the core new message processing. 
    Blend settings are used to configure the blend message processing.
    Insights settings are used to configure the insights processing.
    """
    core_model: str = "gpt-4o"
    """The model to use for the core processing."""
    core_temperature: float = 0
    """The temperature to use for the core processing"""
    core_max_tokens: int = 200
    """The max tokens to use for the core processing."""
    core_history_window_length: int = 10
    """The history window length to use for the core processing."""
    core_max_function_calls_in_message: int = 5
    """The max number of function calls recursively allowed in a single message."""
    core_max_retries: int = 3
    """The max number of retries allowed for a single message."""
    core_timeout: int = 20
    """The timeout to use for the core processing."""
    core_rag_knn: int = 3
    """The number of nearest neighbors to use for the RAG retrieval."""

    blend_model: str = "gpt-3.5-turbo"
    """The temperature to use for the blend processing"""
    blend_max_tokens: int = 200
    """The max tokens to use for the blend processing."""
    blend_history_window_length: int = 3
    """The history window length to use for the blend processing."""
    blend_timeout: int = 20
    """The timeout to use for the blend processing."""
    blend_max_retries: int = 3

    insights_enabled: bool = True
    """Whether to enable the insights processing."""
    insights_model: str = "gpt-3.5-turbo"
    """The temperature to use for the insights processing"""
    insights_max_tokens: int = 300
    """The max tokens to use for the insights processing."""
    insights_history_window_length: int = 3
    """The history window length to use for the insights processing."""
    insights_timeout: int = 20  
    """The timeout to use for the insights processing."""
    insights_max_retries: int = 3
    """The max number of retries allowed for a single message."""