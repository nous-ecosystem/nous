from typing import List, Dict, Any, Union
from src.llm.providers.base import BaseLLMProvider


class GroqFactory(BaseLLMProvider):
    """Factory class for interacting with Groq's API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.groq.com/v1",
        default_model: str = "llama-3.1-70b-versatile",
        vision_model: str = "llama-3.2-90b-vision-preview",
        tool_model: str = "llama3-groq-70b-8192-tool-use-preview",
    ):
        """Initialize the Groq client."""
        super().__init__(
            api_key=api_key, base_url=base_url, default_model=default_model
        )
        self.vision_model = vision_model
        self.tool_model = tool_model

    def analyze_image(
        self, image: Union[str, bytes], prompt: str = "What's in this image?"
    ) -> Dict[str, Any]:
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
        return self.create_completion(messages, model=self.vision_model)

    def process_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        available_functions: Dict[str, callable],
    ) -> str:
        """Process a conversation with tool usage."""
        return super().process_with_tools(messages, tools, available_functions)
