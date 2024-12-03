from typing import Union, Optional, List, Dict, Any
from .base import BaseLLMProvider


class GroqProvider(BaseLLMProvider):
    """Factory class for interacting with Groq's API."""

    def __init__(
        self,
        api_key: str,
        default_model: str = "llama-3.1-70b-versatile",
        tool_model: str = "llama3-groq-70b-8192-tool-use-preview",
        base_url: str = "https://api.groq.com/v1",
    ):
        """Initialize the Groq client."""
        super().__init__(api_key, base_url, default_model)
        self.vision_model = "llama-3.2-90b-vision-preview"
        self.tool_model = tool_model

    async def analyze_image(
        self,
        image: Union[str, bytes],
        prompt: str = "What's in this image?",
        model: Optional[str] = None,
    ) -> str:
        """Analyze an image from a URL or a local file."""
        base64_image = self._encode_image(image)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": base64_image}},
                ],
            }
        ]
        return await self.chat(messages, model or self.vision_model)

    async def use_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        available_functions: Dict[str, callable],
    ) -> str:
        """Convenience method for tool use with default tool model."""
        return await self.chat_with_tools(
            messages, tools, available_functions, model=self.tool_model
        )
