from typing import Optional, List, Dict, Any, Union

import httpx
from .base import BaseLLMProvider


class OpenAIFactory(BaseLLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gpt-4o",
        default_embedding_model: str = "text-embedding-3-small",
        base_url: str = "https://api.openai.com/v1",
        organization: Optional[str] = None,
    ):
        super().__init__(
            api_key=api_key, base_url=base_url, default_model=default_model
        )
        self.default_embedding_model = default_embedding_model
        self.organization = organization

    def _get_headers(self) -> Dict[str, str]:
        """Construct headers for API requests."""
        headers = super()._get_headers()
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        return headers

    def analyze_image(
        self,
        image: Union[str, bytes],
        prompt: str = "What's in this image?",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze an image from a URL or a local file."""
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
        return self.create_completion(messages, model=model or self.default_model)

    def create_embeddings(
        self,
        input: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create embeddings using OpenAI's API."""
        url = f"{self.base_url}/embeddings"
        data = {
            "input": input,
            "model": model or self.default_embedding_model,
            **kwargs,
        }

        with httpx.Client() as client:
            response = client.post(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            return response.json()

    async def create_embeddings_async(
        self,
        input: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create embeddings asynchronously using OpenAI's API."""
        url = f"{self.base_url}/embeddings"
        data = {
            "input": input,
            "model": model or self.default_embedding_model,
            **kwargs,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            return response.json()
