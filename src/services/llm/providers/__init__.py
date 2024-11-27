from typing import Dict, Type
from ..base import LLMProvider
from .openai_provider import OpenAIProvider
from .groq_provider import GroqProvider

# Map of provider names to their implementations
PROVIDER_MAP: Dict[str, Type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "groq": GroqProvider,
}
