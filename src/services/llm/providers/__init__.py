from typing import Dict, Type
from ..base import LLMProvider
from .openai import OpenAIProvider
from .groq import GroqProvider
from .xai import XAIProvider

# Direct exports for shorter imports
__all__ = ["OpenAIProvider", "GroqProvider", "XAIProvider", "PROVIDER_MAP"]

# Map of provider names to their implementations
PROVIDER_MAP: Dict[str, Type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "groq": GroqProvider,
    "xai": XAIProvider,
}
