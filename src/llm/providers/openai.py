from typing import Optional, Union, List, Dict, Any
from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str,
        organization: Optional[str] = None,
        default_model: str = "gpt-4",
        tool_model: str = "gpt-4-turbo-preview",
        base_url: str = "https://api.openai.com/v1",
    ):
        super().__init__(api_key, base_url, default_model)
        if organization:
            self.headers["OpenAI-Organization"] = organization
        self.tool_model = tool_model

    async def analyze_image(
        self,
        image: Union[str, bytes],
        prompt: str = "What's in this image?",
        model: Optional[str] = None,
    ) -> str:
        base64_image = self._encode_image(image)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ]
        return await self.chat(messages, model)

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
